package com.ziskare.ai.db

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.ziskare.ai.db.dao.MessageDao
import com.ziskare.ai.db.dao.SessionDao
import com.ziskare.ai.db.entity.Message
import com.ziskare.ai.db.entity.Session

@Database(entities = [Session::class, Message::class], version = 1, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun sessionDao(): SessionDao
    abstract fun messageDao(): MessageDao

    companion object {
        @Volatile private var INSTANCE: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase =
            INSTANCE ?: synchronized(this) {
                Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "ziskare_ai_db"
                ).build().also { INSTANCE = it }
            }
    }
}
