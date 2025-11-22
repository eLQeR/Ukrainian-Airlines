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
import com.example.ukrainianairlines.ui.viewmodels.BookingViewModel
import com.google.android.material.snackbar.Snackbar

class BookingsFragment : Fragment() {

    private val bookingViewModel: BookingViewModel by viewModels()
    private lateinit var ordersRecyclerView: RecyclerView
    private lateinit var emptyStateText: TextView
    private lateinit var progressBar: ProgressBar
    private lateinit var ordersAdapter: OrdersAdapter
    private lateinit var userInfoText: TextView

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val root = inflater.inflate(R.layout.fragment_bookings, container, false)

        ordersRecyclerView = root.findViewById(R.id.orders_recycler_view)
        emptyStateText = root.findViewById(R.id.empty_state_text)
        progressBar = root.findViewById(R.id.progress_bar)
        userInfoText = root.findViewById(R.id.user_info_text)

        setupRecyclerView()
        observeViewModel()
        loadOrders()
        displayUserInfo()

        return root
    }

    private fun setupRecyclerView() {
        ordersAdapter = OrdersAdapter { order ->
            val bundle = Bundle().apply {
                putInt("orderId", order.id ?: 0)
            }
            findNavController().navigate(R.id.orderDetailFragment, bundle)
        }

        ordersRecyclerView.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = ordersAdapter
        }
    }

    private fun observeViewModel() {
        bookingViewModel.orders.observe(viewLifecycleOwner) { orders ->
            ordersAdapter.submitList(orders)
            updateUI(orders.isEmpty())
        }

        bookingViewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        }

        bookingViewModel.error.observe(viewLifecycleOwner) { error ->
            error?.let {
                Snackbar.make(requireView(), it, Snackbar.LENGTH_LONG).show()
                bookingViewModel.clearError()
            }
        }
    }

    private fun loadOrders() {
        bookingViewModel.loadOrders()
    }

    private fun updateUI(isEmpty: Boolean) {
        if (isEmpty) {
            emptyStateText.visibility = View.VISIBLE
            ordersRecyclerView.visibility = View.GONE
        } else {
            emptyStateText.visibility = View.GONE
            ordersRecyclerView.visibility = View.VISIBLE
        }
    }

    private fun displayUserInfo() {
        val app = requireActivity().application as com.example.ukrainianairlines.UkrainianAirlinesApplication
        val tokenManager = app.tokenManager
        val userEmail = tokenManager.getUserEmail()
        userInfoText.text = getString(R.string.logged_in_as, userEmail ?: getString(R.string.unknown_user))
    }
}