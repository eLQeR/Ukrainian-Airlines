package com.example.ukrainianairlines.ui.viewmodels

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.example.ukrainianairlines.UkrainianAirlinesApplication
import com.example.ukrainianairlines.data.api.UkrainianAirlinesApi
import com.example.ukrainianairlines.data.model.Airport
import com.example.ukrainianairlines.data.model.Flight
import com.example.ukrainianairlines.data.model.FlightSearchResult
import com.example.ukrainianairlines.data.model.TransferOption
import com.example.ukrainianairlines.data.repository.UkrainianAirlinesRepository
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import kotlinx.coroutines.launch

class SearchViewModel(application: Application) : AndroidViewModel(application) {

    private val tokenManager = (application as UkrainianAirlinesApplication).tokenManager
    private val repository = UkrainianAirlinesRepository { tokenManager.getAccessToken() }

    private val _airports = MutableLiveData<List<Airport>>()
    val airports: LiveData<List<Airport>> = _airports

    private val _flights = MutableLiveData<List<Flight>>()
    val flights: LiveData<List<Flight>> = _flights

    private val _searchResult = MutableLiveData<FlightSearchResult?>()
    val searchResult: LiveData<FlightSearchResult?> = _searchResult

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    private val gson = Gson()

    fun loadAirports(name: String? = null, city: String? = null) {
        // Check if token needs refresh
        if (tokenManager.isTokenExpired()) {
            refreshTokenIfNeeded()
        }

        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            repository.getAirports(name, city).collect { result ->
                result.onSuccess { airports ->
                    _airports.value = airports
                }.onFailure { exception ->
                    _error.value = exception.message
                }
                _isLoading.value = false
            }
        }
    }

    fun searchFlights(
        sourceAirport: Int? = null,
        destinationAirport: Int? = null,
        departureDate: String? = null
    ) {
        // Check if token needs refresh
        if (tokenManager.isTokenExpired()) {
            refreshTokenIfNeeded()
        }

        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            _searchResult.value = null

            if (sourceAirport != null && destinationAirport != null && departureDate != null) {
                // Use the transfer ways endpoint for better search results
                repository.searchFlights(sourceAirport, destinationAirport, departureDate).collect { result ->
                    result.onSuccess { response ->
                        val searchResult = parseSearchResponse(response)
                        _searchResult.value = searchResult
                        // Also update the flights LiveData for backward compatibility
                        _flights.value = searchResult.directFlights
                    }.onFailure { exception ->
                        _error.value = exception.message
                        _flights.value = emptyList()
                    }
                }
            } else {
                // Fallback to basic flight search
                repository.getFlights(sourceAirport, destinationAirport, departureDate).collect { result ->
                    result.onSuccess { flights ->
                        _flights.value = flights
                        _searchResult.value = FlightSearchResult(directFlights = flights)
                    }.onFailure { exception ->
                        _error.value = exception.message
                        _flights.value = emptyList()
                    }
                }
            }
            _isLoading.value = false
        }
    }

    private fun parseSearchResponse(response: Map<String, Any>): FlightSearchResult {
        val result = response["result"]
        return when (result) {
            is String -> {
                // Error message or no flights found
                FlightSearchResult(message = result)
            }
            is List<*> -> {
                try {
                    val flightListType = object : TypeToken<List<Flight>>() {}.type
                    val flights = gson.fromJson<List<Flight>>(gson.toJson(result), flightListType)
                    FlightSearchResult(directFlights = flights)
                } catch (e: Exception) {
                    // Try parsing as list of lists (transfer options)
                    try {
                        val transferListType = object : TypeToken<List<List<Flight>>>() {}.type
                        val transferOptionsData = gson.fromJson<List<List<Flight>>>(gson.toJson(result), transferListType)
                        val transferOptions = transferOptionsData.map { TransferOption(it) }
                        FlightSearchResult(transferOptions = transferOptions)
                    } catch (e2: Exception) {
                        FlightSearchResult(message = "Unable to parse flight data")
                    }
                }
            }
            else -> {
                FlightSearchResult(message = "Unexpected response format")
            }
        }
    }

    private fun refreshTokenIfNeeded() {
        val refreshToken = tokenManager.getRefreshToken()
        if (refreshToken != null) {
            viewModelScope.launch {
                repository.refreshToken(refreshToken).collect { result ->
                    result.onSuccess { newAccessToken ->
                        tokenManager.updateAccessToken(newAccessToken)
                    }.onFailure { exception ->
                        // Token refresh failed, user needs to login again
                        _error.value = "Session expired. Please login again."
                    }
                }
            }
        }
    }

    fun clearError() {
        _error.value = null
    }
}