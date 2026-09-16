package com.ziskare.ai;

import android.Manifest;
import android.annotation.SuppressLint;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;

public class MainActivity extends AppCompatActivity {

    private static final String PREFS_NAME = "ziskare_ai_prefs";
    private static final String KEY_LAPTOP_IP = "laptop_ip";
    private static final int PERMISSION_REQ_RECORD_AUDIO = 101;

    private WebView webView;
    private SwipeRefreshLayout swipeRefreshLayout;
    private ProgressBar progressBar;
    private LinearLayout pairingOverlay;
    private TextInputEditText etLaptopIp;
    private MaterialButton btnConnect;
    private TextView tvErrorStatus;

    private SharedPreferences preferences;
    private PermissionRequest pendingPermissionRequest;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        preferences = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);

        initViews();
        setupWebView();
        requestAudioPermissions();

        String savedIp = preferences.getString(KEY_LAPTOP_IP, "");
        if (!savedIp.isEmpty()) {
            etLaptopIp.setText(savedIp);
            loadLaptopPipeline(savedIp);
        } else {
            showPairingOverlay("Enter your laptop's Wi-Fi IP to pair.");
        }
    }

    private void initViews() {
        webView = findViewById(R.id.webView);
        swipeRefreshLayout = findViewById(R.id.swipeRefreshLayout);
        progressBar = findViewById(R.id.progressBar);
        pairingOverlay = findViewById(R.id.pairingOverlay);
        etLaptopIp = findViewById(R.id.etLaptopIp);
        btnConnect = findViewById(R.id.btnConnect);
        tvErrorStatus = findViewById(R.id.tvErrorStatus);

        swipeRefreshLayout.setOnRefreshListener(() -> {
            if (webView != null) {
                webView.reload();
            }
        });

        btnConnect.setOnClickListener(v -> {
            String inputIp = etLaptopIp.getText() != null ? etLaptopIp.getText().toString().trim() : "";
            if (inputIp.isEmpty()) {
                etLaptopIp.setError("Please enter laptop IP");
                return;
            }
            // Strip any protocol prefix or port if entered accidentally
            inputIp = inputIp.replace("http://", "").replace("https://", "").split("/")[0].split(":")[0];
            preferences.edit().putString(KEY_LAPTOP_IP, inputIp).apply();
            loadLaptopPipeline(inputIp);
        });
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void setupWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setSupportZoom(false);

        // Hardware acceleration
        webView.setLayerType(View.LAYER_TYPE_HARDWARE, null);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                progressBar.setVisibility(View.VISIBLE);
                tvErrorStatus.setVisibility(View.GONE);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                progressBar.setVisibility(View.GONE);
                swipeRefreshLayout.setRefreshing(false);
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    progressBar.setVisibility(View.GONE);
                    swipeRefreshLayout.setRefreshing(false);
                    showPairingOverlay("Cannot reach laptop at this IP. Make sure both devices are on the same Wi-Fi.");
                }
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                if (newProgress == 100) {
                    progressBar.setVisibility(View.GONE);
                } else {
                    progressBar.setVisibility(View.VISIBLE);
                }
            }

            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                MainActivity.this.runOnUiThread(() -> {
                    for (String resource : request.getResources()) {
                        if (PermissionRequest.RESOURCE_AUDIO_CAPTURE.equals(resource)) {
                            pendingPermissionRequest = request;
                            if (ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.RECORD_AUDIO)
                                    == PackageManager.PERMISSION_GRANTED) {
                                request.grant(request.getResources());
                            } else {
                                ActivityCompat.requestPermissions(MainActivity.this,
                                        new String[]{Manifest.permission.RECORD_AUDIO},
                                        PERMISSION_REQ_RECORD_AUDIO);
                            }
                            return;
                        }
                    }
                    request.deny();
                });
            }
        });
    }

    private void loadLaptopPipeline(String hostIp) {
        pairingOverlay.setVisibility(View.GONE);
        webView.setVisibility(View.VISIBLE);
        String targetUrl = "http://" + hostIp + ":5005/mobile";
        webView.loadUrl(targetUrl);
    }

    private void showPairingOverlay(String errorMsg) {
        webView.setVisibility(View.GONE);
        pairingOverlay.setVisibility(View.VISIBLE);
        if (errorMsg != null && !errorMsg.isEmpty()) {
            tvErrorStatus.setText(errorMsg);
            tvErrorStatus.setVisibility(View.VISIBLE);
        }
    }

    private void requestAudioPermissions() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.RECORD_AUDIO},
                    PERMISSION_REQ_RECORD_AUDIO);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQ_RECORD_AUDIO) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                if (pendingPermissionRequest != null) {
                    pendingPermissionRequest.grant(pendingPermissionRequest.getResources());
                    pendingPermissionRequest = null;
                }
            } else {
                Toast.makeText(this, "Microphone permission is required for voice chat.", Toast.LENGTH_SHORT).show();
                if (pendingPermissionRequest != null) {
                    pendingPermissionRequest.deny();
                    pendingPermissionRequest = null;
                }
            }
        }
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
