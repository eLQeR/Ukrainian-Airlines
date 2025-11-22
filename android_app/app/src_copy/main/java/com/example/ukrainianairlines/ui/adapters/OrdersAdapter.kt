package com.example.ukrainianairlines.ui.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView

class OrdersAdapter : RecyclerView.Adapter<OrdersAdapter.OrderViewHolder>() {
    // TODO: Replace Any with your Order model for type safety
    private var orders: List<Any> = emptyList()

    fun submitList(list: List<Any>) {
        orders = list
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): OrderViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(android.R.layout.simple_list_item_1, parent, false)
        return OrderViewHolder(view)
    }

    override fun onBindViewHolder(holder: OrderViewHolder, position: Int) {
        // Bind your order data here
    }

    override fun getItemCount(): Int = orders.size

    class OrderViewHolder(view: View) : RecyclerView.ViewHolder(view)
}
