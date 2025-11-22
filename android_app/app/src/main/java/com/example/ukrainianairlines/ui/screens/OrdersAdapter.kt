package com.example.ukrainianairlines.ui.screens

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.ukrainianairlines.R
import com.example.ukrainianairlines.data.model.Order
import java.text.SimpleDateFormat
import java.util.*

class OrdersAdapter(private val onOrderClick: (Order) -> Unit) :
    ListAdapter<Order, OrdersAdapter.OrderViewHolder>(OrderDiffCallback()) {

    private val dateFormat = SimpleDateFormat("dd MMM yyyy", Locale.getDefault())

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): OrderViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_order, parent, false)
        return OrderViewHolder(view)
    }

    override fun onBindViewHolder(holder: OrderViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class OrderViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {

        private val orderIdText: TextView = itemView.findViewById(R.id.order_id_text)
        private val flightRouteText: TextView = itemView.findViewById(R.id.flightRoute)
        private val dateText: TextView = itemView.findViewById(R.id.date_text)
        private val orderPriceText: TextView = itemView.findViewById(R.id.orderPrice)
        private val statusText: TextView = itemView.findViewById(R.id.status_text)

        init {
            itemView.setOnClickListener {
                val position = bindingAdapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    onOrderClick(getItem(position))
                }
            }
        }

        fun bind(order: Order) {
            // Order ID
            orderIdText.text = itemView.context.getString(R.string.order_id_format, order.id)

            // Flight route - show first ticket's route if available
            if (order.tickets.isNotEmpty()) {
                val ticket = order.tickets.first()
                val route = ticket.flight?.route
                val source = when {
                    route?.source is Map<*, *> -> (route.source as Map<*, *>)["name"]?.toString()
                    route?.source is String -> route.source as String
                    else -> "?"
                }
                val destination = when {
                    route?.destination is Map<*, *> -> (route.destination as Map<*, *>)["name"]?.toString()
                    route?.destination is String -> route.destination as String
                    else -> "?"
                }
                flightRouteText.text = if (route != null) "$source 2 $destination" else "Flight not available"
            } else {
                flightRouteText.text = "No tickets"
            }

            // Created date
            order.created_at?.let {
                dateText.text = dateFormat.format(
                    SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                        .parse(it) ?: Date()
                )
            }

            // Order price - placeholder since no price in model
            orderPriceText.text = "$${order.tickets.size * 100}.00"

            // Status
            statusText.text = if (order.is_cancelled) itemView.context.getString(R.string.status_cancelled) else itemView.context.getString(R.string.status_active)
            statusText.setTextColor(
                itemView.context.getColor(
                    if (order.is_cancelled) android.R.color.holo_red_dark
                    else android.R.color.holo_green_dark
                )
            )

            // Improve visual appearance: add padding and bold for status
            statusText.setPadding(8, 8, 8, 8)
            statusText.setTypeface(null, android.graphics.Typeface.BOLD)
        }
    }

    class OrderDiffCallback : DiffUtil.ItemCallback<Order>() {
        override fun areItemsTheSame(oldItem: Order, newItem: Order): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Order, newItem: Order): Boolean {
            return oldItem == newItem
        }
    }
}