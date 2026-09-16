package com.ziskare.ai

import android.content.SharedPreferences
import android.os.Bundle
import android.widget.EditText
import android.widget.ImageButton
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.edit
import androidx.core.view.GravityCompat
import androidx.drawerlayout.widget.DrawerLayout
import androidx.fragment.app.commit
import com.ziskare.ai.db.entity.Session
import com.ziskare.ai.network.ApiClient
import com.ziskare.ai.ui.ChatFragment
import com.ziskare.ai.ui.SessionListFragment

class MainActivity : AppCompatActivity() {

    private lateinit var drawerLayout: DrawerLayout
    private lateinit var tvTitle: TextView

    private val prefs: SharedPreferences by lazy {
        getSharedPreferences(ApiClient.PREFS_NAME, MODE_PRIVATE)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        drawerLayout = findViewById(R.id.drawerLayout)
        tvTitle = findViewById(R.id.tvTitle)

        findViewById<ImageButton>(R.id.btnMenu).setOnClickListener {
            if (drawerLayout.isDrawerOpen(GravityCompat.START))
                drawerLayout.closeDrawer(GravityCompat.START)
            else
                drawerLayout.openDrawer(GravityCompat.START)
        }

        findViewById<ImageButton>(R.id.btnSettings).setOnClickListener {
            showServerSettings()
        }

        // Session list lives in the drawer
        supportFragmentManager.commit {
            replace(R.id.drawerContent, SessionListFragment { session ->
                openChat(session)
                drawerLayout.closeDrawer(GravityCompat.START)
            })
        }

        // If server not configured, show settings right away
        if (savedInstanceState == null) {
            val host = prefs.getString(ApiClient.KEY_HOST, "") ?: ""
            if (host.isBlank()) showServerSettings()
            else drawerLayout.openDrawer(GravityCompat.START)
        }
    }

    private fun openChat(session: Session) {
        tvTitle.text = session.title
        supportFragmentManager.commit {
            replace(R.id.fragmentContainer, ChatFragment.newInstance(session))
            addToBackStack(null)
        }
    }

    private fun showServerSettings() {
        val host = prefs.getString(ApiClient.KEY_HOST, "") ?: ""
        val input = EditText(this).apply {
            hint = "192.168.1.100  or  abc.ngrok.io"
            setText(host)
            setPadding(48, 24, 48, 8)
        }
        AlertDialog.Builder(this)
            .setTitle("Connect to Laptop")
            .setMessage("Enter your laptop's LAN IP (from ziskare-ai --server 5005 --public)")
            .setView(input)
            .setPositiveButton("Save") { _, _ ->
                val raw = input.text.toString().trim()
                    .replace(Regex("^https?://"), "").trimEnd('/').split("/")[0]
                if (raw.isNotBlank()) {
                    prefs.edit { putString(ApiClient.KEY_HOST, raw) }
                }
            }
            .setNegativeButton("Cancel", null)
            .setCancelable(host.isNotBlank())
            .show()
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (drawerLayout.isDrawerOpen(GravityCompat.START)) {
            drawerLayout.closeDrawer(GravityCompat.START)
        } else {
            @Suppress("DEPRECATION")
            super.onBackPressed()
        }
    }
}
