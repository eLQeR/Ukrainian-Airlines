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
import com.example.ukrainianairlines.ui.viewmodels.AuthViewModel
import com.google.android.material.snackbar.Snackbar

class LoginFragment : Fragment() {

    private val authViewModel: AuthViewModel by viewModels()

    private lateinit var usernameInput: EditText
    private lateinit var passwordInput: EditText
    private lateinit var loginButton: Button
    private lateinit var registerLink: Button
    private lateinit var progressBar: ProgressBar

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val root = inflater.inflate(R.layout.fragment_login, container, false)

        usernameInput = root.findViewById(R.id.username_input)
        passwordInput = root.findViewById(R.id.password_input)
        loginButton = root.findViewById(R.id.login_button)
        registerLink = root.findViewById(R.id.register_link)
        progressBar = root.findViewById(R.id.progress_bar)

        setupUI()
        observeViewModel()

        return root
    }

    private fun setupUI() {
        loginButton.setOnClickListener {
            performLogin()
        }

        registerLink.setOnClickListener {
            findNavController().navigate(R.id.registerFragment)
        }
    }

    private fun observeViewModel() {
        authViewModel.isLoggedIn.observe(viewLifecycleOwner) { isLoggedIn ->
            if (isLoggedIn) {
                // Navigate to profile after successful login and clear back stack
                val navOptions = androidx.navigation.NavOptions.Builder()
                    .setPopUpTo(R.id.mobile_navigation, true)
                    .build()
                findNavController().navigate(R.id.nav_profile, null, navOptions)
            }
        }

        authViewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
            loginButton.isEnabled = !isLoading
        }

        authViewModel.error.observe(viewLifecycleOwner) { error ->
            error?.let {
                Snackbar.make(requireView(), it, Snackbar.LENGTH_LONG).show()
                authViewModel.clearError()
            }
        }
    }

    private fun performLogin() {
        val username = usernameInput.text.toString().trim()
        val password = passwordInput.text.toString().trim()

        if (username.isEmpty() || password.isEmpty()) {
            Snackbar.make(requireView(), "Please fill all fields", Snackbar.LENGTH_SHORT).show()
            return
        }

        authViewModel.login(username, password)
    }
}