package com.example.ukrainianairlines.ui.screens

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.ukrainianairlines.R
import com.example.ukrainianairlines.data.model.Airport
import com.example.ukrainianairlines.data.model.Route
import com.example.ukrainianairlines.data.model.Ticket

class TicketsAdapter : ListAdapter<Ticket, TicketsAdapter.TicketViewHolder>(TicketDiffCallback()) {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TicketViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_ticket, parent, false)
        return TicketViewHolder(view)
    }

    override fun onBindViewHolder(holder: TicketViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class TicketViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val passengerNameText: TextView = itemView.findViewById(R.id.passenger_name_text)
        private val seatText: TextView = itemView.findViewById(R.id.seat_text)
        private val flightRouteText: TextView = itemView.findViewById(R.id.flight_route_text)

        fun bind(ticket: Ticket) {
            passengerNameText.text = "${ticket.passenger.first_name} ${ticket.passenger.last_name}"
            seatText.text = "Row ${ticket.row}, Seat ${ticket.seat}"
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
            flightRouteText.text = if (route != null) "$source → $destination" else "Flight not available"
        }
    }

    class TicketDiffCallback : DiffUtil.ItemCallback<Ticket>() {
        override fun areItemsTheSame(oldItem: Ticket, newItem: Ticket): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Ticket, newItem: Ticket): Boolean {
            return oldItem == newItem
        }
    }
}
