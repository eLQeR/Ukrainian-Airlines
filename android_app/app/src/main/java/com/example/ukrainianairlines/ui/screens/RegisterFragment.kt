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

class RegisterFragment : Fragment() {

    private val authViewModel: AuthViewModel by viewModels()

    private lateinit var usernameInput: EditText
    private lateinit var emailInput: EditText
    private lateinit var passwordInput: EditText
    private lateinit var confirmPasswordInput: EditText
    private lateinit var registerButton: Button
    private lateinit var loginLink: Button
    private lateinit var progressBar: ProgressBar

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val root = inflater.inflate(R.layout.fragment_register, container, false)

        usernameInput = root.findViewById(R.id.username_input)
        emailInput = root.findViewById(R.id.email_input)
        passwordInput = root.findViewById(R.id.password_input)
        confirmPasswordInput = root.findViewById(R.id.confirm_password_input)
        registerButton = root.findViewById(R.id.register_button)
        loginLink = root.findViewById(R.id.login_link)
        progressBar = root.findViewById(R.id.progress_bar)

        setupUI()
        observeViewModel()

        return root
    }

    private fun setupUI() {
        registerButton.setOnClickListener {
            performRegister()
        }

        loginLink.setOnClickListener {
            findNavController().navigate(R.id.loginFragment)
        }
    }

    private fun observeViewModel() {
        authViewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
            registerButton.isEnabled = !isLoading
        }

        authViewModel.error.observe(viewLifecycleOwner) { error ->
            error?.let {
                Snackbar.make(requireView(), it, Snackbar.LENGTH_LONG).show()
                authViewModel.clearError()
            }
        }
    }

    private fun performRegister() {
        val username = usernameInput.text.toString().trim()
        val email = emailInput.text.toString().trim()
        val password = passwordInput.text.toString().trim()
        val confirmPassword = confirmPasswordInput.text.toString().trim()

        if (username.isEmpty() || email.isEmpty() || password.isEmpty() || confirmPassword.isEmpty()) {
            Snackbar.make(requireView(), "Please fill all fields", Snackbar.LENGTH_SHORT).show()
            return
        }

        if (password != confirmPassword) {
            Snackbar.make(requireView(), "Passwords do not match", Snackbar.LENGTH_SHORT).show()
            return
        }

        if (password.length < 5) {
            Snackbar.make(requireView(), "Password must be at least 5 characters", Snackbar.LENGTH_SHORT).show()
            return
        }

        authViewModel.register(username, email, password)
    }
}