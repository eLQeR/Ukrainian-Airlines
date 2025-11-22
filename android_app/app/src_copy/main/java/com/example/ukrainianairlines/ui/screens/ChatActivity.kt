package com.example.ukrainianairlines.ui.screens

import android.os.Bundle
import android.widget.EditText
import android.widget.ImageButton
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.ukrainianairlines.R
import com.example.ukrainianairlines.ui.adapters.ChatAdapter
import com.example.ukrainianairlines.ui.models.Message
import com.example.ukrainianairlines.ui.network.ChatApi
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class ChatActivity : AppCompatActivity() {
    private lateinit var chatAdapter: ChatAdapter
    private lateinit var chatId: String

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chat)

        val recyclerView = findViewById<RecyclerView>(R.id.chatRecyclerView)
        val input = findViewById<EditText>(R.id.messageInput)
        val sendButton = findViewById<ImageButton>(R.id.sendButton)

        chatAdapter = ChatAdapter()
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = chatAdapter

        // Start chat session
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val response = ChatApi.startChat()
                chatId = response.chatId
                val messages = response.messages
                withContext(Dispatchers.Main) {
                    chatAdapter.submitList(messages)
                }
            } catch (e: Exception) {
                e.printStackTrace()
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@ChatActivity, "Error: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }

        sendButton.setOnClickListener {
            val message = input.text.toString().trim()
            if (message.isNotEmpty()) {
                CoroutineScope(Dispatchers.IO).launch {
                    try {
                        val reply = ChatApi.sendMessage(chatId, message)
                        withContext(Dispatchers.Main) {
                            chatAdapter.addMessage(Message("user", message))
                            chatAdapter.addMessage(Message("bot", reply))
                            input.text.clear()
                            recyclerView.scrollToPosition(chatAdapter.itemCount - 1)
                        }
                    } catch (e: Exception) {
                        e.printStackTrace()
                        withContext(Dispatchers.Main) {
                            Toast.makeText(this@ChatActivity, "Error: ${e.message}", Toast.LENGTH_LONG).show()
                        }
                    }
                }
            }
        }
    }
}
