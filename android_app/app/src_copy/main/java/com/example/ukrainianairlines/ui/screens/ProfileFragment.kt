package com.example.ukrainianairlines.ui.screens

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import com.example.ukrainianairlines.R
import com.example.ukrainianairlines.ui.viewmodels.AuthViewModel
import com.google.android.material.snackbar.Snackbar

class ProfileFragment : Fragment() {

    private val authViewModel: AuthViewModel by viewModels()

    private lateinit var userNameText: TextView
    private lateinit var userEmailText: TextView
    private lateinit var logoutButton: Button

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val root = inflater.inflate(R.layout.fragment_profile, container, false)

        userNameText = root.findViewById(R.id.userName)
        userEmailText = root.findViewById(R.id.userEmail)
        logoutButton = root.findViewById(R.id.logoutBtn)

        setupUI()
        observeViewModel()
        updateUI()

        return root
    }

    private fun setupUI() {
        logoutButton.setOnClickListener {
            authViewModel.logout()
        }
    }

    private fun observeViewModel() {
        authViewModel.isLoggedIn.observe(viewLifecycleOwner) { isLoggedIn ->
            updateUI()
        }

        authViewModel.error.observe(viewLifecycleOwner) { error ->
            error?.let {
                Snackbar.make(requireView(), it, Snackbar.LENGTH_LONG).show()
                authViewModel.clearError()
            }
        }
    }

    private fun updateUI() {
        val isLoggedIn = authViewModel.isLoggedIn.value ?: false

        if (isLoggedIn) {
            // Show user info and logout button
            userNameText.text = "John Doe" // TODO: Get from user data
            userEmailText.text = "john.doe@example.com" // TODO: Get from user data
            logoutButton.visibility = View.VISIBLE
        } else {
            // Navigate to login if not logged in
            navigateToLogin()
        }
    }

    private fun navigateToLogin() {
        findNavController().navigate(R.id.action_global_to_login)
    }

    private fun navigateToRegister() {
        findNavController().navigate(R.id.registerFragment)
    }
}