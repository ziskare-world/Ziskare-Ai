package com.ziskare.ai.viewmodel

import android.app.Application
import android.content.Context
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.ziskare.ai.db.entity.Message
import com.ziskare.ai.network.ApiClient
import com.ziskare.ai.network.ChatRequest
import com.ziskare.ai.repository.AppRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.io.File

sealed class ChatUiState {
    object Idle : ChatUiState()
    object Loading : ChatUiState()
    object Offline : ChatUiState()
    data class Err(val msg: String) : ChatUiState()
}

class ChatViewModel(app: Application) : AndroidViewModel(app) {
    private val repo = AppRepository(app)
    private val _state = MutableStateFlow<ChatUiState>(ChatUiState.Idle)
    val uiState: StateFlow<ChatUiState> = _state

    fun getMessages(sessionId: String): Flow<List<Message>> = repo.getMessages(sessionId)

    fun sendMessage(sessionId: String, text: String) {
        viewModelScope.launch {
            // 1. Save user message immediately (visible offline)
            repo.insertMessage(Message(sessionId = sessionId, role = "user", content = text))
            repo.touchSession(sessionId)
            _state.value = ChatUiState.Loading

            try {
                val api = ApiClient.create(getApplication())
                val resp = api.chat(ChatRequest(session_id = sessionId, message = text))

                if (resp.error != null) {
                    _state.value = ChatUiState.Err(resp.error)
                } else if (resp.image_url != null) {
                    // Download image and save locally for offline access
                    val localPath = saveImage(sessionId, resp.image_url)
                    repo.insertMessage(Message(
                        sessionId = sessionId, role = "ai",
                        content = localPath ?: resp.image_url,
                        type = if (localPath != null) "IMAGE" else "TEXT"
                    ))
                    _state.value = ChatUiState.Idle
                } else {
                    repo.insertMessage(Message(sessionId = sessionId, role = "ai", content = resp.reply))
                    _state.value = ChatUiState.Idle
                }
                repo.touchSession(sessionId)
            } catch (e: Exception) {
                _state.value = ChatUiState.Offline
            }
        }
    }

    private fun saveImage(sessionId: String, url: String): String? = try {
        val ctx: Context = getApplication()
        val dir = File(ctx.filesDir, "images/$sessionId").also { it.mkdirs() }
        val file = File(dir, "${System.currentTimeMillis()}.jpg")
        file.writeBytes(java.net.URL(url).readBytes())
        file.absolutePath
    } catch (e: Exception) { null }
}
