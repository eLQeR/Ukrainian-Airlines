package com.example.ukrainianairlines.ui.screens

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.RecyclerView
import com.example.ukrainianairlines.R
import com.example.ukrainianairlines.ui.adapters.OrdersAdapter
import kotlinx.coroutines.launch

class OrdersFragment : Fragment() {

    private lateinit var ordersAdapter: OrdersAdapter
    private lateinit var ordersRecyclerView: RecyclerView
    private lateinit var emptyTextView: LinearLayout

    // TODO: Replace Any? with your actual API implementation
    private val api: Any? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_orders, container, false)
        ordersRecyclerView = view.findViewById(R.id.ordersRecyclerView)
        emptyTextView = view.findViewById(R.id.emptyStateLayout)
        ordersAdapter = OrdersAdapter() // Remove lambda parameter
        ordersRecyclerView.adapter = ordersAdapter

        fetchOrders()

        return view
    }

    private fun fetchOrders() {
        viewLifecycleOwner.lifecycleScope.launch {
            // TODO: Replace this block with your actual API call and response handling
            val orders: List<Any> = emptyList() // Replace with actual orders from API
            ordersAdapter.submitList(orders)
            if (orders.isEmpty()) {
                ordersRecyclerView.visibility = View.GONE
                emptyTextView.visibility = View.VISIBLE
            } else {
                ordersRecyclerView.visibility = View.VISIBLE
                emptyTextView.visibility = View.GONE
            }
        }
    }
}
