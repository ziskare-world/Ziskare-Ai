package com.ziskare.ai.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.ziskare.ai.db.entity.Session
import com.ziskare.ai.repository.AppRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.launch

class SessionViewModel(application: Application) : AndroidViewModel(application) {
    private val repo = AppRepository(application)
    val sessions: Flow<List<Session>> = repo.getAllSessions()

    fun createSession(title: String = "New Chat"): Session {
        val session = Session(title = title)
        viewModelScope.launch { repo.insertSession(session) }
        return session
    }

    fun deleteSession(session: Session) = viewModelScope.launch { repo.deleteSession(session) }
    fun renameSession(id: String, title: String) = viewModelScope.launch { repo.renameSession(id, title) }
}
