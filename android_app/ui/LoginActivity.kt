// ...existing code...

private fun handleLoginResponse(success: Boolean) {
    if (success) {
        // ...save tokens...
        // Navigate to profile activity
        val intent = Intent(this, ProfileActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    } else {
        // ...show error...
    }
}

// ...existing code...

