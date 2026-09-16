package com.ziskare.ai.repository

import android.content.Context
import com.ziskare.ai.db.AppDatabase
import com.ziskare.ai.db.entity.Message
import com.ziskare.ai.db.entity.Session
import kotlinx.coroutines.flow.Flow

class AppRepository(context: Context) {
    private val db = AppDatabase.getInstance(context)
    private val sessionDao = db.sessionDao()
    private val messageDao = db.messageDao()

    fun getAllSessions(): Flow<List<Session>> = sessionDao.getAllSessions()
    suspend fun insertSession(session: Session) = sessionDao.insert(session)
    suspend fun deleteSession(session: Session) {
        sessionDao.delete(session)
        messageDao.deleteForSession(session.id)
    }
    suspend fun renameSession(id: String, title: String) = sessionDao.updateTitle(id, title)
    suspend fun touchSession(id: String) = sessionDao.touchSession(id, System.currentTimeMillis())

    fun getMessages(sessionId: String): Flow<List<Message>> = messageDao.getMessages(sessionId)
    suspend fun getMessagesOnce(sessionId: String): List<Message> = messageDao.getMessagesOnce(sessionId)
    suspend fun insertMessage(msg: Message) = messageDao.insert(msg)
}
