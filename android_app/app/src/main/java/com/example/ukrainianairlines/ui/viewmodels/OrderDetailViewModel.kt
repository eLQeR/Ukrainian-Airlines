package com.example.ukrainianairlines.ui.viewmodels

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.example.ukrainianairlines.UkrainianAirlinesApplication
import com.example.ukrainianairlines.data.model.Order
import com.example.ukrainianairlines.data.repository.UkrainianAirlinesRepository
import kotlinx.coroutines.launch

class OrderDetailViewModel(application: Application) : AndroidViewModel(application) {

    private val tokenManager = (application as UkrainianAirlinesApplication).tokenManager
    private val repository = UkrainianAirlinesRepository { tokenManager.getAccessToken() }

    private val _order = MutableLiveData<Order?>()
    val order: LiveData<Order?> = _order

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    fun loadOrder(orderId: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null

            repository.getOrder(orderId).collect { result ->
                _isLoading.value = false
                result.onSuccess { order ->
                    _order.value = order
                }.onFailure { throwable ->
                    _error.value = throwable.message ?: "Unknown error occurred"
                }
            }
        }
    }

    fun cancelOrder(orderId: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null

            repository.cancelOrder(orderId).collect { result ->
                _isLoading.value = false
                result.onSuccess {
                    // Reload the order to get updated data
                    loadOrder(orderId)
                }.onFailure { throwable ->
                    _error.value = throwable.message ?: "Failed to cancel order"
                }
            }
        }
    }

    fun clearError() {
        _error.value = null
    }
}
