package com.example.ukrainianairlines.ui.viewmodels

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.example.ukrainianairlines.UkrainianAirlinesApplication
import com.example.ukrainianairlines.data.api.UkrainianAirlinesApi
import com.example.ukrainianairlines.data.model.AuthTokens
import com.example.ukrainianairlines.data.model.User
import com.example.ukrainianairlines.data.repository.UkrainianAirlinesRepository
import kotlinx.coroutines.launch

class AuthViewModel(application: Application) : AndroidViewModel(application) {

    private val tokenManager = (application as UkrainianAirlinesApplication).tokenManager
    private val repository = UkrainianAirlinesRepository { tokenManager.getAccessToken() }

    private val _authTokens = MutableLiveData<AuthTokens?>()
    val authTokens: LiveData<AuthTokens?> = _authTokens

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    private val _isLoggedIn = MutableLiveData<Boolean>()
    val isLoggedIn: LiveData<Boolean> = _isLoggedIn

    init {
        // Check if user is already logged in
        _isLoggedIn.value = tokenManager.hasValidToken()
        if (_isLoggedIn.value == true) {
            // Load tokens from storage
            tokenManager.getAccessToken()?.let { accessToken ->
                tokenManager.getRefreshToken()?.let { refreshToken ->
                    _authTokens.value = AuthTokens(accessToken, refreshToken)
                }
            }
        }
    }

    fun login(username: String, password: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            repository.login(username, password).collect { result ->
                result.onSuccess { tokens ->
                    _authTokens.value = tokens
                    _isLoggedIn.value = true
                    // Save tokens to shared preferences
                    tokenManager.saveTokens(tokens)
                }.onFailure { exception ->
                    _error.value = exception.message
                    _isLoggedIn.value = false
                }
                _isLoading.value = false
            }
        }
    }

    fun register(username: String, email: String, password: String) {
        val user = User(username = username, email = email, password = password)
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            repository.register(user).collect { result ->
                result.onSuccess { registeredUser ->
                    // After successful registration, you might want to auto-login
                    // For now, just show success
                    _error.value = "Registration successful! Please login."
                }.onFailure { exception ->
                    _error.value = exception.message
                }
                _isLoading.value = false
            }
        }
    }

    fun logout() {
        _authTokens.value = null
        _isLoggedIn.value = false
        // Clear tokens from shared preferences
        tokenManager.clearTokens()
    }

    fun refreshTokenIfNeeded(): Boolean {
        return if (tokenManager.isTokenExpired()) {
            tokenManager.getRefreshToken()?.let { refreshToken ->
                refreshAccessToken(refreshToken)
                true
            } ?: false
        } else {
            false
        }
    }

    private fun refreshAccessToken(refreshToken: String) {
        viewModelScope.launch {
            repository.refreshToken(refreshToken).collect { result ->
                result.onSuccess { newAccessToken ->
                    tokenManager.updateAccessToken(newAccessToken)
                    // Update the current tokens
                    _authTokens.value?.let { currentTokens ->
                        _authTokens.value = currentTokens.copy(access = newAccessToken)
                    }
                }.onFailure { exception ->
                    // Token refresh failed, user needs to login again
                    logout()
                    _error.value = "Session expired. Please login again."
                }
            }
        }
    }

    fun clearError() {
        _error.value = null
    }
}