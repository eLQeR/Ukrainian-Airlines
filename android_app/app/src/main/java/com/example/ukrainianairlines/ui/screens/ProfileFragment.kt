package com.example.ukrainianairlines.ui.screens

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import com.example.ukrainianairlines.R
import com.example.ukrainianairlines.ui.viewmodels.AuthViewModel
import com.example.ukrainianairlines.ui.viewmodels.ProfileViewModel
import com.google.android.material.snackbar.Snackbar

class ProfileFragment : Fragment() {

    private val authViewModel: AuthViewModel by viewModels()
    private val profileViewModel: ProfileViewModel by viewModels()

    private lateinit var userNameText: TextView
    private lateinit var userEmailText: TextView
    private lateinit var logoutButton: Button
    private lateinit var myOrdersBtn: LinearLayout
    private lateinit var progressBar: ProgressBar

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val root = inflater.inflate(R.layout.fragment_profile, container, false)

        userNameText = root.findViewById(R.id.userName)
        userEmailText = root.findViewById(R.id.userEmail)
        logoutButton = root.findViewById(R.id.logoutBtn)
        myOrdersBtn = root.findViewById(R.id.myOrdersBtn)
        progressBar = root.findViewById(R.id.progress_bar)

        setupUI()
        observeViewModel()
        loadProfile()

        return root
    }

    private fun setupUI() {
        logoutButton.setOnClickListener {
            profileViewModel.logout()
        }

        myOrdersBtn.setOnClickListener {
            findNavController().navigate(R.id.ordersFragment)
        }
    }

    private fun observeViewModel() {
        authViewModel.isLoggedIn.observe(viewLifecycleOwner) { isLoggedIn ->
            if (!isLoggedIn) {
                navigateToLogin()
            }
        }

        profileViewModel.user.observe(viewLifecycleOwner) { user ->
            user?.let {
                userNameText.text = it.username
                userEmailText.text = it.email
                userNameText.visibility = View.VISIBLE
                userEmailText.visibility = View.VISIBLE
                logoutButton.visibility = View.VISIBLE
            }
        }

        profileViewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        }

        profileViewModel.error.observe(viewLifecycleOwner) { error ->
            error?.let {
                Snackbar.make(requireView(), it, Snackbar.LENGTH_LONG).show()
                profileViewModel.clearError()
            }
        }

        profileViewModel.logoutSuccess.observe(viewLifecycleOwner) { logoutSuccess ->
            if (logoutSuccess) {
                navigateToLogin()
            }
        }
    }

    private fun loadProfile() {
        profileViewModel.loadUserProfile()
    }

    private fun navigateToLogin() {
        findNavController().navigate(R.id.action_global_to_login)
    }
}