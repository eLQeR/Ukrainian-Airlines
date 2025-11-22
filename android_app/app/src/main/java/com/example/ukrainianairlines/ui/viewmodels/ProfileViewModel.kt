package com.example.ukrainianairlines.ui.viewmodels

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.example.ukrainianairlines.UkrainianAirlinesApplication
import com.example.ukrainianairlines.data.model.User
import kotlinx.coroutines.launch

class ProfileViewModel(application: Application) : AndroidViewModel(application) {

    private val tokenManager = (application as UkrainianAirlinesApplication).tokenManager

    private val _user = MutableLiveData<User?>()
    val user: LiveData<User?> = _user

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    private val _logoutSuccess = MutableLiveData<Boolean>()
    val logoutSuccess: LiveData<Boolean> = _logoutSuccess

    fun loadUserProfile() {
        // For now, create a mock user. In a real app, you'd get this from the API
        _user.value = User(
            id = 1,
            username = "user@example.com",
            email = "user@example.com",
            password = ""
        )
    }

    fun logout() {
        viewModelScope.launch {
            tokenManager.clearTokens()
            _logoutSuccess.value = true
        }
    }

    fun clearError() {
        _error.value = null
    }
}
