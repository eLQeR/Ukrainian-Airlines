package com.example.ukrainianairlines.ui.screens

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.ukrainianairlines.R
import com.example.ukrainianairlines.data.model.Order
import com.example.ukrainianairlines.ui.viewmodels.BookingViewModel
import com.google.android.material.snackbar.Snackbar
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class OrderDetailFragment : Fragment() {
    private val bookingViewModel: BookingViewModel by viewModels()
    private lateinit var orderIdText: TextView
    private lateinit var createdAtText: TextView
    private lateinit var statusText: TextView
    private lateinit var ticketsRecyclerView: RecyclerView
    private lateinit var ticketsAdapter: TicketsAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_order_detail, container, false)

        orderIdText = view.findViewById(R.id.order_id_text)
        createdAtText = view.findViewById(R.id.created_at_text)
        statusText = view.findViewById(R.id.status_text)
        ticketsRecyclerView = view.findViewById(R.id.tickets_recycler_view)

        setupRecyclerView()
        observeViewModel()
        val orderId = arguments?.getInt("orderId") ?: 0
        bookingViewModel.loadOrder(orderId)

        return view
    }

    private fun setupRecyclerView() {
        ticketsAdapter = TicketsAdapter()
        ticketsRecyclerView.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = ticketsAdapter
        }
    }

    private fun observeViewModel() {
        bookingViewModel.currentOrder.observe(viewLifecycleOwner) { order ->
            order?.let { displayOrder(it) }
        }

        bookingViewModel.error.observe(viewLifecycleOwner) { error ->
            error?.let {
                Snackbar.make(requireView(), it, Snackbar.LENGTH_LONG).show()
                bookingViewModel.clearError()
            }
        }
    }

    private fun displayOrder(order: Order) {
        orderIdText.text = getString(R.string.order_id_format, order.id)
        order.created_at?.let {
            val dateFormat = SimpleDateFormat("dd MMM yyyy HH:mm", Locale.getDefault())
            createdAtText.text = dateFormat.format(
                SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                    .parse(it) ?: Date()
            )
        }
        statusText.text = if (order.is_cancelled) getString(R.string.status_cancelled) else getString(R.string.status_active)
        statusText.setTextColor(
            requireContext().getColor(
                if (order.is_cancelled) android.R.color.holo_red_dark
                else android.R.color.holo_green_dark
            )
        )

        ticketsAdapter.submitList(order.tickets)
    }
}
