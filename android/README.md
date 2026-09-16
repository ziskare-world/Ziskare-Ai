# Ziskare AI — Android App & Zero-Load Mobile Pipeline

A ChatGPT-style mobile experience connecting your Android phone to your laptop's AI inference engine.

---

## Architecture Overview (Zero-Load Pipeline)

```
+------------------------------------+           Wi-Fi / LAN           +---------------------------------------------+
|           ANDROID PHONE            | <=============================> |                LAPTOP / PC                  |
|                                    |                                 |                                             |
|  - Full ChatGPT Dark-Mode UI       |   HTTP / REST API (Port 5005)   |  - Ziskare AI Offline Daemon (GPU CUDA)    |
|  - Pill input & Voice Dictation    |                                 |  - High-load PyTorch LLM Model              |
|  - Instant code block copy         |   POST /api/mobile/chat         |  - Sessions Disk: data/mobile_sessions/     |
|  - Sidebar session history         |   GET  /api/mobile/sessions     |  - Long-Term Memory: data/mobile_memory.json|
|  - Laptop Telemetry Modal          |   GET  /api/mobile/status       |  - Image Generation & Watermark Removal     |
|                                    |   GET  /api/mobile/memory       |  - Auto IP Discovery                        |
|  [RAM < 25 MB, Battery Safe]       |                                 |  [All Compute & Heat Stays on Laptop]       |
+------------------------------------+                                 +---------------------------------------------+
```

### Why this design?
1. **0% Heavy Mobile Battery Drain**: Mobile devices overheat and rapidly deplete battery when running multi-billion parameter neural networks locally. By offloading 100% of the token generation and weights to the laptop's GPU, the phone stays completely cool.
2. **Persistent Laptop Memory**: All conversation sessions, long-term memory facts, and generated images reside safely on the laptop disk (`data/mobile_sessions/*.json` and `data/mobile_memory.json`).
3. **Dual Access Options**:
   - **Method A (Instant Zero-Install PWA)**: Open Chrome or Samsung Internet on your phone and navigate to `http://<laptop-ip>:5005/mobile`. Tap "Add to Home Screen" to install it as a standalone app.
   - **Method B (Native Android Studio APK)**: Build and install the Native Android Studio project located in this `android/` directory.

---

## Method A: Instant Phone Access (No Android Studio Needed)

1. Ensure your laptop and phone are connected to the same Wi-Fi network.
2. Start the Ziskare AI server on your laptop:
   ```bash
   python -m ziskare_ai.server
   # or
   python ai.py --serve
   ```
3. The server prints your laptop's local LAN pairing address, for example:
   ```
   =======================================================
     Ziskare AI - Server & Mobile Intelligence Pipeline
     Rescue Console:  http://localhost:5005
     Mobile Web App:  http://192.168.1.100:5005/mobile
     Mobile API:      http://192.168.1.100:5005/api/mobile
     Zero-Load Mode:  Laptop stores memory & runs GPU inference
   =======================================================
   ```
4. Open Chrome / Firefox / Safari on your phone and visit:
   `http://<laptop-ip>:5005/mobile`
5. Tap the three dots (⋮) in Chrome and select **"Add to Home screen"** or **"Install App"**.
6. Enjoy a full-screen, standalone ChatGPT app on your phone with zero setup!

---

## Method B: Native Android Studio Build (100% Kotlin)

The native Android app is written in **idiomatic Kotlin** using AndroidX KTX, modern `ActivityResultContracts` for audio permissions, `OnBackPressedDispatcher`, and hardware-accelerated WebView.

### Prerequisites
- Android Studio Iguana / Jellyfish / Ladybug / Koala or newer.
- Android SDK 34 (Android 14) and Android Build Tools.
- Kotlin 1.9+.
- Android device running Android 7.0 (API 24) or higher.

### Steps to Build and Run
1. Open Android Studio.
2. Click **File -> Open...** and select the `android` folder (`D:\ziskare-ai\android`).
3. Allow Gradle to sync dependencies.
4. Connect your Android phone via USB with USB Debugging enabled, or select an Android Emulator.
5. Click the green **Run** button (`Shift + F10`).
6. When the app launches:
   - Enter your laptop's LAN IP (printed when running `python -m ziskare_ai.server`).
   - Click **Connect Pipeline**.
   - The app securely remembers your laptop IP for future launches!

---

## Key Features in Mobile App
- **ChatGPT Dark Aesthetic**: Pixel-perfect `#171717` dark theme, `#212121` cards, and `#10A37F` emerald accents.
- **Voice Dictation**: Built-in microphone button with speech-to-text.
- **Code Block Formatter**: Automatic code highlighting with a one-tap **Copy Code** button.
- **Drawer Sidebar**: Multi-session drawer to start new chats, switch between past conversations, or delete chats.
- **Laptop Telemetry Dashboard**: Tap the status pill in the header to view live laptop battery, GPU VRAM allocation, CPU usage, and memory health.
- **Memory & Personalization**: Customize how the AI addresses you and view stored persistent facts.
