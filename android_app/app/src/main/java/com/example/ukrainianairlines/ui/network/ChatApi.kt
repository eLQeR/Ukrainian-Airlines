package com.example.ukrainianairlines.ui.network

import com.example.ukrainianairlines.ui.models.Message
import okhttp3.*
import org.json.JSONObject
import java.util.UUID

object ChatApi {
    private const val BASE_URL = "http://10.0.2.2:8000/api/v1/chats/chat/"
    private val client = OkHttpClient()

    data class ChatResponse(val chatId: String, val messages: List<Message>)

    // Create or get chat session, extract real chat_id from HTML response
    fun startChat(): ChatResponse {
        val initialChatId = UUID.randomUUID().toString()
        val request = Request.Builder()
            .url("$BASE_URL$initialChatId/")
            .get()
            .build()
        client.newCall(request).execute().use { response ->
            val body = response.body?.string() ?: ""
            // Extract real chat_id from HTML response
            val chatIdRegex = "chat_id['\"]?\\s*[:=]\\s*['\"]([a-zA-Z0-9\\-]+)['\"]".toRegex()
            val chatIdMatch = chatIdRegex.find(body)
            val realChatId = chatIdMatch?.groupValues?.get(1) ?: initialChatId
            return ChatResponse(realChatId, emptyList())
        }
    }

    // Send message to chat
    fun sendMessage(chatId: String, message: String): String {
        val formBody = FormBody.Builder()
            .add("message", message)
            .build()
        val request = Request.Builder()
            .url("$BASE_URL$chatId/")
            .post(formBody)
            .build()
        client.newCall(request).execute().use { response ->
            val body = response.body?.string() ?: ""
            if (body.trim().startsWith("<")) {
                // HTML error page, not JSON
                return "Error: Server returned HTML (possible CSRF or permission issue)"
            }
            val json = JSONObject(body)
            return json.optString("reply", "")
        }
    }
}
