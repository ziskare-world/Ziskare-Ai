package com.ziskare.ai

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.os.Bundle
import android.view.View
import android.webkit.PermissionRequest
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.content.edit
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText

/**
 * Ziskare AI — Native Android Client in Kotlin
 * Connects the mobile device to the laptop's offline intelligence engine
 * with zero mobile battery or compute load.
 */
class MainActivity : AppCompatActivity() {

    companion object {
        private const val PREFS_NAME = "ziskare_ai_prefs"
        private const val KEY_LAPTOP_IP = "laptop_ip"
        private const val DEFAULT_PORT = 5005
    }

    private lateinit var webView: WebView
    private lateinit var swipeRefreshLayout: SwipeRefreshLayout
    private lateinit var progressBar: ProgressBar
    private lateinit var pairingOverlay: LinearLayout
    private lateinit var etLaptopIp: TextInputEditText
    private lateinit var btnConnect: MaterialButton
    private lateinit var tvErrorStatus: TextView

    private val preferences: SharedPreferences by lazy {
        getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }

    private var pendingPermissionRequest: PermissionRequest? = null

    // Modern ActivityResult permission launcher for microphone / voice dictation
    private val audioPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            pendingPermissionRequest?.grant(pendingPermissionRequest?.resources)
        } else {
            Toast.makeText(this, "Microphone permission is required for voice chat.", Toast.LENGTH_SHORT).show()
            pendingPermissionRequest?.deny()
        }
        pendingPermissionRequest = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        initViews()
        setupWebView()
        setupBackNavigation()
        requestAudioPermissions()

        val savedIp = preferences.getString(KEY_LAPTOP_IP, "") ?: ""
        if (savedIp.isNotBlank()) {
            etLaptopIp.setText(savedIp)
            loadLaptopPipeline(savedIp)
        } else {
            showPairingOverlay("Enter your laptop's LAN IP to pair.")
        }
    }

    private fun initViews() {
        webView = findViewById(R.id.webView)
        swipeRefreshLayout = findViewById(R.id.swipeRefreshLayout)
        progressBar = findViewById(R.id.progressBar)
        pairingOverlay = findViewById(R.id.pairingOverlay)
        etLaptopIp = findViewById(R.id.etLaptopIp)
        btnConnect = findViewById(R.id.btnConnect)
        tvErrorStatus = findViewById(R.id.tvErrorStatus)

        swipeRefreshLayout.setOnRefreshListener {
            webView.reload()
        }

        btnConnect.setOnClickListener {
            val inputRaw = etLaptopIp.text?.toString()?.trim().orEmpty()
            if (inputRaw.isBlank()) {
                etLaptopIp.error = "Please enter laptop IP"
                return@setOnClickListener
            }

            // Clean input: remove protocol or port suffixes if pasted accidentally
            val cleanIp = inputRaw
                .replace("http://", "")
                .replace("https://", "")
                .split("/")[0]
                .split(":")[0]

            preferences.edit {
                putString(KEY_LAPTOP_IP, cleanIp)
            }
            loadLaptopPipeline(cleanIp)
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView() {
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            mediaPlaybackRequiresUserGesture = false
            cacheMode = WebSettings.LOAD_DEFAULT
            useWideViewPort = true
            loadWithOverviewMode = true
            setSupportZoom(false)
        }

        // Enable hardware acceleration for fluid ChatGPT animations
        webView.setLayerType(View.LAYER_TYPE_HARDWARE, null)

        webView.webViewClient = object : WebViewClient() {
            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                progressBar.visibility = View.VISIBLE
                tvErrorStatus.visibility = View.GONE
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                progressBar.visibility = View.GONE
                swipeRefreshLayout.isRefreshing = false
            }

            override fun onReceivedError(
                view: WebView?,
                request: WebResourceRequest?,
                error: WebResourceError?
            ) {
                if (request?.isForMainFrame == true) {
                    progressBar.visibility = View.GONE
                    swipeRefreshLayout.isRefreshing = false
                    showPairingOverlay("Cannot reach laptop at this IP. Make sure both devices are on the same Wi-Fi.")
                }
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                progressBar.visibility = if (newProgress == 100) View.GONE else View.VISIBLE
            }

            override fun onPermissionRequest(request: PermissionRequest?) {
                runOnUiThread {
                    request?.resources?.forEach { resource ->
                        if (PermissionRequest.RESOURCE_AUDIO_CAPTURE == resource) {
                            pendingPermissionRequest = request
                            if (ContextCompat.checkSelfPermission(
                                    this@MainActivity,
                                    Manifest.permission.RECORD_AUDIO
                                ) == PackageManager.PERMISSION_GRANTED
                            ) {
                                request.grant(request.resources)
                            } else {
                                audioPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                            }
                            return@runOnUiThread
                        }
                    }
                    request?.deny()
                }
            }
        }
    }

    private fun setupBackNavigation() {
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) {
                    webView.goBack()
                } else {
                    isEnabled = false
                    onBackPressedDispatcher.onBackPressed()
                }
            }
        })
    }

    private fun loadLaptopPipeline(hostIp: String) {
        pairingOverlay.visibility = View.GONE
        webView.visibility = View.VISIBLE
        val targetUrl = "http://$hostIp:$DEFAULT_PORT/mobile"
        webView.loadUrl(targetUrl)
    }

    private fun showPairingOverlay(errorMsg: String?) {
        webView.visibility = View.GONE
        pairingOverlay.visibility = View.VISIBLE
        if (!errorMsg.isNullOrBlank()) {
            tvErrorStatus.text = errorMsg
            tvErrorStatus.visibility = View.VISIBLE
        }
    }

    private fun requestAudioPermissions() {
        if (ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.RECORD_AUDIO
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            audioPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
        }
    }
}
