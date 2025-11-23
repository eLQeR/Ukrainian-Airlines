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
                    android.util.Log.d("SearchViewModel", "Loaded ${airports.size} airports")
                    airports.forEach { airport ->
                        android.util.Log.d("SearchViewModel", "Airport: id=${airport.id}, name=${airport.name}")
                    }
                    _airports.value = airports
                }.onFailure { exception ->
                    android.util.Log.e("SearchViewModel", "loadAirports failed", exception)
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
        // Debug logging
        android.util.Log.d("SearchViewModel", "searchFlights called with: sourceAirport=$sourceAirport, destinationAirport=$destinationAirport, departureDate=$departureDate")

        // Check if token needs refresh
        if (tokenManager.isTokenExpired()) {
            refreshTokenIfNeeded()
        }

        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            _searchResult.value = null

            if (sourceAirport != null && destinationAirport != null && departureDate != null) {
                android.util.Log.d("SearchViewModel", "Using getFlights endpoint with filters")
                repository.getFlights(sourceAirport, destinationAirport, departureDate).collect { result ->
                    result.onSuccess { flights ->
                        android.util.Log.d("SearchViewModel", "getFlights response: ${flights.size} flights")
                        _flights.value = flights
                        _searchResult.value = FlightSearchResult(directFlights = flights)
                        android.util.Log.d("SearchViewModel", "Updated flights LiveData with ${flights.size} flights")
                    }.onFailure { exception ->
                        android.util.Log.e("SearchViewModel", "getFlights failed", exception)
                        _error.value = exception.message
                        _flights.value = emptyList()
                    }
                }
            } else {
                android.util.Log.d("SearchViewModel", "Using getFlights endpoint (fallback)")
                repository.getFlights().collect { result ->
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
        android.util.Log.d("SearchViewModel", "parseSearchResponse: $response")

        // Check if this is a paginated response
        if (response.containsKey("results")) {
            try {
                val results = response["results"]
                if (results is List<*>) {
                    val flightListType = object : TypeToken<List<Flight>>() {}.type
                    val flights = gson.fromJson<List<Flight>>(gson.toJson(results), flightListType)
                    android.util.Log.d("SearchViewModel", "Parsed paginated response with ${flights.size} flights")
                    return FlightSearchResult(directFlights = flights)
                }
            } catch (e: Exception) {
                android.util.Log.e("SearchViewModel", "Error parsing paginated response", e)
            }
        }

        // Fallback to original parsing logic
        val result = response["result"]
        return when (result) {
            is String -> {
                // Error message or no flights found
                android.util.Log.d("SearchViewModel", "Got string result: $result")
                FlightSearchResult(message = result)
            }
            is List<*> -> {
                try {
                    val flightListType = object : TypeToken<List<Flight>>() {}.type
                    val flights = gson.fromJson<List<Flight>>(gson.toJson(result), flightListType)
                    android.util.Log.d("SearchViewModel", "Parsed direct flights: ${flights.size}")
                    FlightSearchResult(directFlights = flights)
                } catch (e: Exception) {
                    // Try parsing as list of lists (transfer options)
                    try {
                        val transferListType = object : TypeToken<List<List<Flight>>>() {}.type
                        val transferOptionsData = gson.fromJson<List<List<Flight>>>(gson.toJson(result), transferListType)
                        val transferOptions = transferOptionsData.map { TransferOption(it) }
                        android.util.Log.d("SearchViewModel", "Parsed transfer options: ${transferOptions.size}")
                        FlightSearchResult(transferOptions = transferOptions)
                    } catch (e2: Exception) {
                        android.util.Log.e("SearchViewModel", "Unable to parse flight data", e2)
                        FlightSearchResult(message = "Unable to parse flight data")
                    }
                }
            }
            else -> {
                android.util.Log.w("SearchViewModel", "Unexpected response format: ${result?.javaClass}")
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