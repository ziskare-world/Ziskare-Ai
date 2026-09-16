package com.ziskare.ai.network

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

data class ChatRequest(
    val session_id: String,
    val message: String
)

data class ChatResponse(
    val reply: String = "",
    val type: String = "text",       // "text" or "image"
    val image_url: String? = null,
    val error: String? = null
)

data class StatusResponse(
    val status: String = "ok",
    val gpu: String = "",
    val cpu: Float = 0f
)

interface ZiskareApi {
    @POST("/api/mobile/chat")
    suspend fun chat(@Body body: ChatRequest): ChatResponse

    @GET("/api/mobile/status")
    suspend fun status(): StatusResponse
}
