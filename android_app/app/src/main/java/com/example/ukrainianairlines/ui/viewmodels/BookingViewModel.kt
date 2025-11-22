package com.example.ukrainianairlines.ui.viewmodels

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.example.ukrainianairlines.UkrainianAirlinesApplication
import com.example.ukrainianairlines.data.api.UkrainianAirlinesApi
import com.example.ukrainianairlines.data.model.Order
import com.example.ukrainianairlines.data.repository.UkrainianAirlinesRepository
import kotlinx.coroutines.launch

class BookingViewModel(application: Application) : AndroidViewModel(application) {

    private val tokenManager = (application as UkrainianAirlinesApplication).tokenManager
    private val repository = UkrainianAirlinesRepository { tokenManager.getAccessToken() }

    private val _orders = MutableLiveData<List<Order>>()
    val orders: LiveData<List<Order>> = _orders

    private val _currentOrder = MutableLiveData<Order?>()
    val currentOrder: LiveData<Order?> = _currentOrder

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    fun loadOrders() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            val token = tokenManager.getAccessToken()
            if (token.isNullOrEmpty()) {
                _error.value = "Authentication error: missing token. Please log in again."
                _isLoading.value = false
                return@launch
            }
            repository.getOrders().collect { result ->
                result.onSuccess { orders ->
                    _orders.value = orders
                }.onFailure { exception ->
                    _error.value = exception.message
                }
                _isLoading.value = false
            }
        }
    }

    fun createOrder(order: Order) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            repository.createOrder(order).collect { result ->
                result.onSuccess { createdOrder ->
                    _currentOrder.value = createdOrder
                    // Reload orders to include the new one
                    loadOrders()
                }.onFailure { exception ->
                    _error.value = exception.message
                }
                _isLoading.value = false
            }
        }
    }

    fun cancelOrder(orderId: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            repository.cancelOrder(orderId).collect { result ->
                result.onSuccess { cancelledOrder ->
                    _currentOrder.value = cancelledOrder
                    // Reload orders to reflect the cancellation
                    loadOrders()
                }.onFailure { exception ->
                    _error.value = exception.message
                }
                _isLoading.value = false
            }
        }
    }

    fun loadOrder(orderId: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            val token = tokenManager.getAccessToken()
            if (token.isNullOrEmpty()) {
                _error.value = "Authentication error: missing token. Please log in again."
                _isLoading.value = false
                return@launch
            }
            repository.getOrder(orderId).collect { result ->
                result.onSuccess { order ->
                    _currentOrder.value = order
                }.onFailure { exception ->
                    _error.value = exception.message
                }
                _isLoading.value = false
            }
        }
    }

    fun clearError() {
        _error.value = null
    }

    fun clearCurrentOrder() {
        _currentOrder.value = null
    }
}