package com.example.ukrainianairlines.ui.screens

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.NumberPicker
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
    private lateinit var rowPicker: NumberPicker
    private lateinit var seatPicker: NumberPicker

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
        rowPicker = root.findViewById(R.id.row_picker)
        seatPicker = root.findViewById(R.id.seat_picker)
        rowPicker.minValue = 1
        rowPicker.maxValue = 10
        seatPicker.minValue = 1
        seatPicker.maxValue = 6

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

        val passenger = Passenger(
            first_name = firstName,
            last_name = lastName
        )

        val selectedRow = rowPicker.value
        val selectedSeat = seatPicker.value
        val ticket = Ticket(
            row = selectedRow,
            seat = selectedSeat,
            flight = selectedFlightId,
            passenger = passenger
        )

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