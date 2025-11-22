import android.content.Context
import android.content.SharedPreferences
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody
import org.json.JSONObject

class TokenManager(private val context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences("auth_prefs", Context.MODE_PRIVATE)

    fun getAccessToken(): String? = prefs.getString("access_token", null)

    fun saveAccessToken(token: String) {
        prefs.edit().putString("access_token", token).apply()
    }

    fun getRefreshToken(): String? = prefs.getString("refresh_token", null)

    fun saveRefreshToken(token: String) {
        prefs.edit().putString("refresh_token", token).apply()
    }

    fun refreshToken(): String? {
        val refreshToken = getRefreshToken() ?: return null
        val client = OkHttpClient()
        val url = "http://10.0.2.2:8000/api/token/refresh/" // Adjust if your endpoint differs
        val json = JSONObject().apply { put("refresh", refreshToken) }
        val body = RequestBody.create("application/json".toMediaTypeOrNull(), json.toString())
        val request = Request.Builder()
            .url(url)
            .post(body)
            .build()
        return try {
            val response = client.newCall(request).execute()
            if (response.isSuccessful) {
                val responseBody = response.body?.string()
                val obj = JSONObject(responseBody ?: "")
                val newAccess = obj.optString("access", null)
                val newRefresh = obj.optString("refresh", null)
                if (newAccess != null) saveAccessToken(newAccess)
                if (newRefresh != null) saveRefreshToken(newRefresh)
                newAccess
            } else {
                null
            }
        } catch (e: Exception) {
            null
        }
    }
}
