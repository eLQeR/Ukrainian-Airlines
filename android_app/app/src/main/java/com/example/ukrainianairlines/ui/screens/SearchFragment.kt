package com.example.ukrainianairlines.ui.screens

import android.app.DatePickerDialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.AutoCompleteTextView
import android.widget.Button
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import com.example.ukrainianairlines.R
import com.example.ukrainianairlines.data.model.Airport
import com.example.ukrainianairlines.ui.viewmodels.SearchViewModel
import com.google.android.material.snackbar.Snackbar
import com.google.android.material.textfield.TextInputEditText
import java.text.SimpleDateFormat
import java.util.*

class SearchFragment : Fragment() {

    private val searchViewModel: SearchViewModel by viewModels()
    private var selectedFromAirport: Airport? = null
    private var selectedToAirport: Airport? = null
    private var selectedDepartureDate: String? = null
    private var fromAirports: List<Airport> = emptyList()
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
    private val displayDateFormat = SimpleDateFormat("dd MMM yyyy", Locale.getDefault())

    private lateinit var fromAirportInput: AutoCompleteTextView
    private lateinit var toAirportInput: AutoCompleteTextView
    private lateinit var departureDateInput: TextInputEditText
    private lateinit var searchButton: Button

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val root = inflater.inflate(R.layout.fragment_search, container, false)

        // Initialize views
        fromAirportInput = root.findViewById(R.id.from_airport_input)
        toAirportInput = root.findViewById(R.id.to_airport_input)
        departureDateInput = root.findViewById(R.id.departure_date_input)
        searchButton = root.findViewById(R.id.search_button)

        setupViews()
        observeViewModel()
        loadAirports()

        return root
    }

    private fun setupViews() {
        departureDateInput.setOnClickListener {
            showDatePicker()
        }

        searchButton.setOnClickListener {
            performSearch()
        }

        searchViewModel.loadAirports()
    }

    private fun observeViewModel() {
        searchViewModel.airports.observe(viewLifecycleOwner) { airports ->
            fromAirports = airports
            setupAirportInputs()
        }

        searchViewModel.flights.observe(viewLifecycleOwner) { flights ->
            if (flights.isNotEmpty()) {
                navigateToFlightResults()
            } else {
                Snackbar.make(requireView(), getString(R.string.no_flights_found), Snackbar.LENGTH_SHORT).show()
            }
        }

        searchViewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            searchButton.isEnabled = !isLoading
        }

        searchViewModel.error.observe(viewLifecycleOwner) { error ->
            error?.let {
                Snackbar.make(requireView(), it, Snackbar.LENGTH_LONG).show()
                searchViewModel.clearError()
            }
        }
    }

    private fun loadAirports() {
        searchViewModel.loadAirports()
    }

    private fun setupAirportInputs() {
        fromAirportInput.hint = "Select departure airport"
        toAirportInput.hint = "Select arrival airport"

        if (fromAirports.isNotEmpty()) {
            selectedFromAirport = fromAirports.find { it.name.contains("Boryspil") } ?: fromAirports[0]
            selectedToAirport = fromAirports.find { it.name.contains("Warsaw") } ?: fromAirports.getOrNull(1)

            fromAirportInput.setText(selectedFromAirport?.name ?: "")
            toAirportInput.setText(selectedToAirport?.name ?: "")
        }

        val adapter = ArrayAdapter(
            requireContext(),
            android.R.layout.simple_dropdown_item_1line,
            fromAirports
        )
        fromAirportInput.setAdapter(adapter)
        toAirportInput.setAdapter(adapter)

        fromAirportInput.setOnItemClickListener { _, _, position, _ ->
            selectedFromAirport = adapter.getItem(position)
        }

        toAirportInput.setOnItemClickListener { _, _, position, _ ->
            selectedToAirport = adapter.getItem(position)
        }
    }

    private fun showDatePicker() {
        val calendar = Calendar.getInstance()
        val datePickerDialog = DatePickerDialog(
            requireContext(),
            { _, year, month, dayOfMonth ->
                calendar.set(year, month, dayOfMonth)
                selectedDepartureDate = dateFormat.format(calendar.time)
                departureDateInput.setText(displayDateFormat.format(calendar.time))
            },
            calendar.get(Calendar.YEAR),
            calendar.get(Calendar.MONTH),
            calendar.get(Calendar.DAY_OF_MONTH)
        )
        datePickerDialog.datePicker.minDate = System.currentTimeMillis() - 1000
        datePickerDialog.show()
    }

    private fun performSearch() {
        val fromAirport = selectedFromAirport
        val toAirport = selectedToAirport
        val departureDate = selectedDepartureDate

        if (fromAirport == null || toAirport == null || departureDate == null) {
            Snackbar.make(requireView(), "Please fill all fields", Snackbar.LENGTH_SHORT).show()
            return
        }

        if (fromAirport.id == toAirport.id) {
            Snackbar.make(requireView(), "Please select different airports", Snackbar.LENGTH_SHORT).show()
            return
        }

        searchViewModel.searchFlights(
            sourceAirport = fromAirport.id,
            destinationAirport = toAirport.id,
            departureDate = departureDate
        )
    }

    private fun navigateToFlightResults() {
        // Use Bundle for navigation arguments instead of SafeArgs for now
        val bundle = Bundle().apply {
            putInt("sourceAirport", selectedFromAirport?.id ?: 0)
            putInt("destinationAirport", selectedToAirport?.id ?: 0)
            putString("departureDate", selectedDepartureDate ?: "")
        }
        findNavController().navigate(R.id.action_nav_search_to_flightResultsFragment, bundle)
    }
}