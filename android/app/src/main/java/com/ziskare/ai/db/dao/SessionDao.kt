package com.ziskare.ai.db.dao

import androidx.room.*
import com.ziskare.ai.db.entity.Session
import kotlinx.coroutines.flow.Flow

@Dao
interface SessionDao {
    @Query("SELECT * FROM sessions ORDER BY lastMessageAt DESC")
    fun getAllSessions(): Flow<List<Session>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(session: Session)

    @Delete
    suspend fun delete(session: Session)

    @Query("UPDATE sessions SET title = :title WHERE id = :id")
    suspend fun updateTitle(id: String, title: String)

    @Query("UPDATE sessions SET lastMessageAt = :time WHERE id = :id")
    suspend fun touchSession(id: String, time: Long)
}
