package com.example.ukrainianairlines

import android.app.Application
import com.example.ukrainianairlines.data.preferences.TokenManager

class UkrainianAirlinesApplication : Application() {

    lateinit var tokenManager: TokenManager
        private set

    override fun onCreate() {
        super.onCreate()
        tokenManager = TokenManager(this)
    }
}