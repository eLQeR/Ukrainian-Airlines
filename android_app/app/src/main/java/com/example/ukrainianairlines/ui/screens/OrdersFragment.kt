package com.example.ukrainianairlines.ui.screens

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ProgressBar
import android.widget.LinearLayout
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.ukrainianairlines.R
import com.example.ukrainianairlines.ui.viewmodels.OrdersViewModel
import com.example.ukrainianairlines.ui.viewmodels.SearchViewModel
import com.google.android.material.snackbar.Snackbar

class OrdersFragment : Fragment() {
    private val ordersViewModel: OrdersViewModel by viewModels()
    private val searchViewModel: SearchViewModel by viewModels()
    private lateinit var ordersAdapter: OrdersAdapter
    private lateinit var ordersRecyclerView: RecyclerView
    private lateinit var emptyStateLayout: LinearLayout
    private lateinit var progressBar: ProgressBar
    private var flightsMap: Map<Int, com.example.ukrainianairlines.data.model.Flight> = emptyMap()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val root = inflater.inflate(R.layout.fragment_orders, container, false)

        ordersRecyclerView = root.findViewById(R.id.ordersRecyclerView)
        emptyStateLayout = root.findViewById(R.id.emptyStateLayout)
        progressBar = root.findViewById(R.id.progressBar)

        setupRecyclerView()
        observeViewModel()
        observeFlights()
        loadOrders()

        return root
    }

    private fun setupRecyclerView() {
        ordersAdapter = OrdersAdapter(flightsMap) { order ->
            val bundle = Bundle().apply {
                putInt("orderId", order.id ?: 0)
            }
            findNavController().navigate(R.id.action_ordersFragment_to_orderDetailFragment, bundle)
        }

        ordersRecyclerView.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = ordersAdapter
        }
    }

    private fun observeViewModel() {
        ordersViewModel.orders.observe(viewLifecycleOwner) { orders ->
            ordersAdapter.submitList(orders)
            updateUI(orders.isEmpty())
        }

        ordersViewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        }

        ordersViewModel.error.observe(viewLifecycleOwner) { error ->
            error?.let {
                Snackbar.make(requireView(), it, Snackbar.LENGTH_LONG).show()
                ordersViewModel.clearError()
            }
        }
    }

    private fun observeFlights() {
        searchViewModel.flights.observe(viewLifecycleOwner) { flights ->
            flightsMap = flights.associateBy { it.id }
            ordersAdapter = OrdersAdapter(flightsMap) { order ->
                val bundle = Bundle().apply {
                    putInt("orderId", order.id ?: 0)
                }
                findNavController().navigate(R.id.action_ordersFragment_to_orderDetailFragment, bundle)
            }
            ordersRecyclerView.adapter = ordersAdapter
            // Optionally re-submit current orders list
            ordersViewModel.orders.value?.let { ordersAdapter.submitList(it) }
        }
    }

    private fun loadOrders() {
        ordersViewModel.loadOrders()
    }

    private fun updateUI(isEmpty: Boolean) {
        if (isEmpty) {
            emptyStateLayout.visibility = View.VISIBLE
            ordersRecyclerView.visibility = View.GONE
        } else {
            emptyStateLayout.visibility = View.GONE
            ordersRecyclerView.visibility = View.VISIBLE
        }
    }
}
