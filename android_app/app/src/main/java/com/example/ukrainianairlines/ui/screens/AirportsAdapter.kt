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

class AirportsAdapter(private val onAirportClick: (Airport) -> Unit) :
    ListAdapter<Airport, AirportsAdapter.AirportViewHolder>(AirportDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): AirportViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_airport, parent, false)
        return AirportViewHolder(view)
    }

    override fun onBindViewHolder(holder: AirportViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class AirportViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {

        private val airportNameText: TextView = itemView.findViewById(R.id.airport_name_text)
        private val cityText: TextView = itemView.findViewById(R.id.city_text)
        private val codeText: TextView = itemView.findViewById(R.id.code_text)

        init {
            itemView.setOnClickListener {
                val position = bindingAdapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    onAirportClick(getItem(position))
                }
            }
        }

        fun bind(airport: Airport) {
            airportNameText.text = airport.name
            cityText.text = airport.closest_big_city
            codeText.text = "ID: ${airport.id}"
        }
    }

    class AirportDiffCallback : DiffUtil.ItemCallback<Airport>() {
        override fun areItemsTheSame(oldItem: Airport, newItem: Airport): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Airport, newItem: Airport): Boolean {
            return oldItem == newItem
        }
    }
}
