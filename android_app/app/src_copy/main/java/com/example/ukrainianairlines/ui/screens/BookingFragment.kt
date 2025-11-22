package com.example.ukrainianairlines.ui.screens

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import com.example.ukrainianairlines.R
import com.example.ukrainianairlines.data.model.Order
import com.example.ukrainianairlines.data.model.Passenger
import com.example.ukrainianairlines.data.model.Ticket
import com.example.ukrainianairlines.ui.viewmodels.BookingViewModel
import com.google.android.material.snackbar.Snackbar

class BookingFragment : Fragment() {

    private val bookingViewModel: BookingViewModel by viewModels()

    private lateinit var firstNameInput: EditText
    private lateinit var lastNameInput: EditText
    private lateinit var emailInput: EditText
    private lateinit var bookButton: Button
    private lateinit var progressBar: ProgressBar

    private var selectedFlightId: Int = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        arguments?.let {
            selectedFlightId = it.getInt("flightId", 0)
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val root = inflater.inflate(R.layout.fragment_booking, container, false)

        firstNameInput = root.findViewById(R.id.first_name_input)
        lastNameInput = root.findViewById(R.id.last_name_input)
        emailInput = root.findViewById(R.id.email_input)
        bookButton = root.findViewById(R.id.book_button)
        progressBar = root.findViewById(R.id.progress_bar)

        setupUI()
        observeViewModel()

        return root
    }

    private fun setupUI() {
        bookButton.setOnClickListener {
            createBooking()
        }
    }

    private fun observeViewModel() {
        bookingViewModel.currentOrder.observe(viewLifecycleOwner) { order ->
            order?.let {
                showBookingSuccess()
            }
        }

        bookingViewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
            bookButton.isEnabled = !isLoading
        }

        bookingViewModel.error.observe(viewLifecycleOwner) { error ->
            error?.let {
                Snackbar.make(requireView(), it, Snackbar.LENGTH_LONG).show()
                bookingViewModel.clearError()
            }
        }
    }

    private fun createBooking() {
        val firstName = firstNameInput.text.toString().trim()
        val lastName = lastNameInput.text.toString().trim()
        val email = emailInput.text.toString().trim()

        if (firstName.isEmpty() || lastName.isEmpty() || email.isEmpty()) {
            Snackbar.make(requireView(), "Please fill all required fields", Snackbar.LENGTH_SHORT).show()
            return
        }

        // Create passenger
        val passenger = Passenger(
            first_name = firstName,
            last_name = lastName
        )

        // Create ticket (simplified - in real app you'd select seat)
        val ticket = Ticket(
            row = 1,
            seat = 1,
            flight = com.example.ukrainianairlines.data.model.Flight(
                id = selectedFlightId,
                route = com.example.ukrainianairlines.data.model.Route(
                    id = 1,
                    source = com.example.ukrainianairlines.data.model.Airport(1, "Source", "City"),
                    destination = com.example.ukrainianairlines.data.model.Airport(2, "Dest", "City"),
                    distance = 100.0f
                ),
                airplane = com.example.ukrainianairlines.data.model.Airplane(
                    id = 1,
                    name = "Airplane",
                    rows = 10,
                    seats_in_row = 6,
                    airplane_type = com.example.ukrainianairlines.data.model.AirplaneType(1, "Type")
                ),
                departure_time = "2023-01-01T10:00:00Z",
                arrival_time = "2023-01-01T12:00:00Z"
            ),
            passenger = passenger
        )

        // Create order
        val order = Order(
            tickets = listOf(ticket)
        )

        bookingViewModel.createOrder(order)
    }

    private fun showBookingSuccess() {
        Snackbar.make(requireView(), getString(R.string.booking_confirmed), Snackbar.LENGTH_LONG).show()
        // Navigate back to bookings
        findNavController().navigate(R.id.nav_bookings)
    }
}