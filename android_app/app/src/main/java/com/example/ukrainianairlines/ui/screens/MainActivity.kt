package com.example.ukrainianairlines.ui.screens

import android.content.Intent
import android.os.Bundle
import android.widget.ImageView
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.drawerlayout.widget.DrawerLayout
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.navigateUp
import androidx.navigation.ui.setupActionBarWithNavController
import androidx.navigation.ui.setupWithNavController
import com.example.ukrainianairlines.R
import com.example.ukrainianairlines.ui.viewmodels.AuthViewModel
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.google.android.material.navigation.NavigationView

class MainActivity : AppCompatActivity() {

    private lateinit var appBarConfiguration: AppBarConfiguration
    private val authViewModel: AuthViewModel by viewModels()
    private lateinit var drawerLayout: DrawerLayout
    private lateinit var navigationView: NavigationView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment_content_main) as NavHostFragment
        val navController = navHostFragment.navController

        // Setup bottom navigation
        val bottomNavView: BottomNavigationView = findViewById(R.id.bottom_nav_view)
        bottomNavView.setupWithNavController(navController)

        // Setup drawer navigation
        drawerLayout = findViewById(R.id.drawer_layout)
        navigationView = findViewById(R.id.nav_view)
        navigationView.setupWithNavController(navController)

        // Setup app bar
        appBarConfiguration = AppBarConfiguration(
            setOf(R.id.nav_search, R.id.nav_bookings, R.id.nav_profile), drawerLayout
        )
        setupActionBarWithNavController(navController, appBarConfiguration)

        // Observe authentication state
        authViewModel.isLoggedIn.observe(this) { isLoggedIn ->
            if (!isLoggedIn) {
                // Only navigate to login if we're not already there or on register screen
                val currentDestination = navController.currentDestination?.id
                if (currentDestination != R.id.loginFragment && currentDestination != R.id.registerFragment) {
                    navController.navigate(R.id.action_global_to_login)
                }
            }
        }

        // Copilot icon click listener
        findViewById<ImageView>(R.id.copilot_icon).setOnClickListener {
            startActivity(Intent(this, ChatActivity::class.java))
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment_content_main) as NavHostFragment
        val navController = navHostFragment.navController
        return navController.navigateUp(appBarConfiguration) || super.onSupportNavigateUp()
    }
}