package com.example.ukrainianairlines.ui.screens

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.ukrainianairlines.R
import com.example.ukrainianairlines.data.model.Flight
import java.text.SimpleDateFormat
import java.util.*

class FlightAdapter(private val onFlightClick: (Flight) -> Unit) :
    ListAdapter<Flight, FlightAdapter.FlightViewHolder>(FlightDiffCallback()) {

    private val timeFormat = SimpleDateFormat("HH:mm", Locale.getDefault())
    private val dateFormat = SimpleDateFormat("dd MMM", Locale.getDefault())

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): FlightViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_flight, parent, false)
        return FlightViewHolder(view)
    }

    override fun onBindViewHolder(holder: FlightViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class FlightViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {

        private val routeText: TextView = itemView.findViewById(R.id.route_text)
        private val departureTimeText: TextView = itemView.findViewById(R.id.departure_time_text)
        private val durationText: TextView = itemView.findViewById(R.id.duration_text)
        private val arrivalTimeText: TextView = itemView.findViewById(R.id.arrival_time_text)
        private val airplaneText: TextView = itemView.findViewById(R.id.airplane_text)
        private val seatsText: TextView = itemView.findViewById(R.id.seats_text)
        private val priceText: TextView = itemView.findViewById(R.id.price_text)
        private val bookButton: Button = itemView.findViewById(R.id.book_button)

        init {
            bookButton.setOnClickListener {
                val position = bindingAdapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    onFlightClick(getItem(position))
                }
            }
        }

        fun bind(flight: Flight) {
            val route = flight.route
            val source = when {
                route?.source is Map<*, *> -> (route.source as Map<*, *>)["closest_big_city"]?.toString()
                route?.source is String -> route.source as String
                else -> "?"
            }
            val destination = when {
                route?.destination is Map<*, *> -> (route.destination as Map<*, *>)["closest_big_city"]?.toString()
                route?.destination is String -> route.destination as String
                else -> "?"
            }
            routeText.text = if (route != null) "$source 2 $destination" else "Flight not available"

            // Times
            departureTimeText.text = timeFormat.format(
                SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                    .parse(flight.departure_time ?: "") ?: Date()
            )
            arrivalTimeText.text = timeFormat.format(
                SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                    .parse(flight.arrival_time ?: "") ?: Date()
            )

            // Duration
            durationText.text = flight.time_of_flight ?: "N/A"

            // Airplane
            val airplaneName = when {
                flight.airplane is Map<*, *> -> (flight.airplane["name"] as? String)
                flight.airplane is String -> flight.airplane as String
                else -> null
            }
            airplaneText.text = airplaneName ?: "Unknown airplane"

            // Available seats
            seatsText.text = "${flight.tickets_available} seats available"

            // Price (placeholder - you might want to add price to your model)
            priceText.text = "From $299"
        }
    }

    class FlightDiffCallback : DiffUtil.ItemCallback<Flight>() {
        override fun areItemsTheSame(oldItem: Flight, newItem: Flight): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Flight, newItem: Flight): Boolean {
            return oldItem == newItem
        }
    }
}