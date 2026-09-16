package com.ziskare.ai.db.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.UUID

@Entity(tableName = "messages")
data class Message(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val sessionId: String,
    val role: String,           // "user" or "ai"
    val content: String,        // text content or local image file path
    val type: String = "TEXT",  // "TEXT" or "IMAGE"
    val timestamp: Long = System.currentTimeMillis()
)
