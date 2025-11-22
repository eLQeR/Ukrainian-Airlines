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
import com.example.ukrainianairlines.ui.viewmodels.SearchViewModel
import com.google.android.material.snackbar.Snackbar

class AirportsFragment : Fragment() {

    private val searchViewModel: SearchViewModel by viewModels()
    private lateinit var airportsRecyclerView: RecyclerView
    private lateinit var progressBar: ProgressBar
    private lateinit var emptyStateText: TextView
    private lateinit var airportsAdapter: AirportsAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val root = inflater.inflate(R.layout.fragment_airports, container, false)

        airportsRecyclerView = root.findViewById(R.id.airports_recycler_view)
        progressBar = root.findViewById(R.id.progress_bar)
        emptyStateText = root.findViewById(R.id.empty_state_text)

        setupRecyclerView()
        observeViewModel()
        loadAirports()

        return root
    }

    private fun setupRecyclerView() {
        airportsAdapter = AirportsAdapter { airport ->
            // Navigate back with selected airport
            findNavController().popBackStack()
        }

        airportsRecyclerView.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = airportsAdapter
        }
    }

    private fun observeViewModel() {
        searchViewModel.airports.observe(viewLifecycleOwner) { airports ->
            airportsAdapter.submitList(airports)
            updateUI(airports.isEmpty())
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

    private fun loadAirports() {
        searchViewModel.loadAirports()
    }

    private fun updateUI(isEmpty: Boolean) {
        if (isEmpty) {
            emptyStateText.visibility = View.VISIBLE
            airportsRecyclerView.visibility = View.GONE
        } else {
            emptyStateText.visibility = View.GONE
            airportsRecyclerView.visibility = View.VISIBLE
        }
    }
}
