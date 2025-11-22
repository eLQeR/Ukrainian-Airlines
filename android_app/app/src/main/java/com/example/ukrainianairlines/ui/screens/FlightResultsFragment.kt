package com.example.ukrainianairlines.ui.screens

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ProgressBar
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.ukrainianairlines.R
import com.example.ukrainianairlines.data.model.Flight
import com.example.ukrainianairlines.ui.viewmodels.SearchViewModel
import com.google.android.material.snackbar.Snackbar

class FlightResultsFragment : Fragment() {

    private val searchViewModel: SearchViewModel by viewModels()

    private lateinit var flightsRecyclerView: RecyclerView
    private lateinit var progressBar: ProgressBar
    private lateinit var emptyStateText: TextView
    private lateinit var flightAdapter: FlightAdapter

    private var sourceAirport: Int = 0
    private var destinationAirport: Int = 0
    private var departureDate: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        arguments?.let {
            sourceAirport = it.getInt("sourceAirport", 0)
            destinationAirport = it.getInt("destinationAirport", 0)
            departureDate = it.getString("departureDate", "")
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val root = inflater.inflate(R.layout.fragment_flight_results, container, false)

        flightsRecyclerView = root.findViewById(R.id.flights_recycler_view)
        progressBar = root.findViewById(R.id.progress_bar)
        emptyStateText = root.findViewById(R.id.empty_state_text)

        setupRecyclerView()
        observeViewModel()
        loadFlights()

        return root
    }

    private fun setupRecyclerView() {
        flightAdapter = FlightAdapter { flight ->
            navigateToBooking(flight)
        }

        flightsRecyclerView.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = flightAdapter
        }
    }

    private fun observeViewModel() {
        searchViewModel.flights.observe(viewLifecycleOwner) { flights ->
            flightAdapter.submitList(flights)
            updateUI(flights.isEmpty())
        }

        searchViewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        }

        searchViewModel.error.observe(viewLifecycleOwner) { error ->
            error?.let {
                Snackbar.make(requireView(), it, Snackbar.LENGTH_LONG).show()
                searchViewModel.clearError()
            }
        }
    }

    private fun loadFlights() {
        searchViewModel.searchFlights(
            sourceAirport = sourceAirport,
            destinationAirport = destinationAirport,
            departureDate = departureDate
        )
    }

    private fun updateUI(isEmpty: Boolean) {
        if (isEmpty) {
            emptyStateText.visibility = View.VISIBLE
            flightsRecyclerView.visibility = View.GONE
        } else {
            emptyStateText.visibility = View.GONE
            flightsRecyclerView.visibility = View.VISIBLE
        }
    }

    private fun navigateToBooking(flight: Flight) {
        // Use Bundle for navigation arguments instead of SafeArgs for now
        val bundle = Bundle().apply {
            putInt("flightId", flight.id)
        }
        findNavController().navigate(R.id.action_flightResultsFragment_to_bookingFragment, bundle)
    }
}