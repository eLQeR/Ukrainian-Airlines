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

class OrdersViewModel(application: Application) : AndroidViewModel(application) {

    private val tokenManager = (application as UkrainianAirlinesApplication).tokenManager
    private val repository = UkrainianAirlinesRepository { tokenManager.getAccessToken() }

    private val _orders = MutableLiveData<List<Order>>()
    val orders: LiveData<List<Order>> = _orders

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    fun loadOrders() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null

            repository.getOrders().collect { result ->
                _isLoading.value = false
                result.onSuccess { orders ->
                    _orders.value = orders
                }.onFailure { throwable ->
                    _error.value = throwable.message ?: "Unknown error occurred"
                }
            }
        }
    }

    fun clearError() {
        _error.value = null
    }
}

