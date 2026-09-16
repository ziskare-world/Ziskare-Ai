package com.ziskare.ai.network

import android.content.Context
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object ApiClient {
    const val PREFS_NAME = "ziskare_ai_prefs"
    const val KEY_HOST = "laptop_ip"
    const val DEFAULT_PORT = 5005

    fun create(context: Context): ZiskareApi {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val host = prefs.getString(KEY_HOST, "") ?: ""
        val baseUrl = buildBaseUrl(host)

        val logging = HttpLoggingInterceptor().apply { level = HttpLoggingInterceptor.Level.BASIC }
        val client = OkHttpClient.Builder()
            .addInterceptor(logging)
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(120, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()

        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ZiskareApi::class.java)
    }

    fun buildBaseUrl(host: String): String = when {
        host.isBlank() -> "http://localhost:$DEFAULT_PORT/"
        host.startsWith("http") -> if (host.endsWith("/")) host else "$host/"
        host.contains("ngrok") -> "https://$host/"
        host.contains(":") -> "http://$host/"   // already has port
        else -> "http://$host:$DEFAULT_PORT/"
    }
}
