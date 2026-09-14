# ⚡ Ziskare AI

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-CUDA%20Accelerated-EE4C2C?logo=pytorch&logoColor=white)
![Hardware](https://img.shields.io/badge/GPU-NVIDIA%20GeForce%20RTX-76B900?logo=nvidia&logoColor=white)
![Offline](https://img.shields.io/badge/Network-100%25%20Offline-success)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Universal, 100% Offline, Hardware-Accelerated Local Intelligence Engine for Any Application.**

[🚀 1-Click Install](#-1-click-installation) • [Ways to Use Across PC](#-ways-to-use-across-pc) • [Python API](#-python-api) • [CLI Tool](#-cli-usage) • [REST API](#-rest-api-microservice) • [Recovery](#-disaster-recovery)

</div>

---

## 🌟 Overview

**Ziskare AI** is a lightweight, zero-latency, embedded AI engine designed to run entirely locally on your machine. It requires zero cloud API keys, makes zero network requests, and executes with direct GPU acceleration on NVIDIA hardware.

By default, Ziskare AI is tuned to provide **direct, concise answers** without conversational fluff, pleasantries, or preamble.

---

## 🚀 1-Click Installation (Windows)

On any computer or freshly formatted Windows installation:
1. Clone or download this repository to your computer (e.g. `D:\ziskare-ai`).
2. **Double-click `install.bat`**.

The automated installer will:
- Check Python and NVIDIA GPU.
- Install CUDA PyTorch for your NVIDIA GPU.
- Install transformers & accelerate.
- Install `ziskare_ai` globally into Python `site-packages`.
- Register the global Windows CLI command `ziskare-ai`.
- Pre-cache and verify model weights.

---

## 💻 Ways to Use Across Your PC

*Detailed guide: [**docs/HOW_TO_USE_ACROSS_PC.md**](docs/HOW_TO_USE_ACROSS_PC.md)*

| Use Case | Method | Example |
| :--- | :--- | :--- |
| **From Any Terminal** | Global CLI | `ziskare-ai "What is 5 plus 5?"` |
| **Interactive Chat** | Shell Mode | `ziskare-ai` |
| **In Any Python Project** | Universal Package | `import ziskare_ai as zai` |
| **In Node.js / JavaScript** | Subprocess Execution | `execSync('ziskare-ai "query"')` |
| **In Web Apps / Any Language** | Local REST API | `ziskare-ai --server 5005` |
| **Windows Desktop Hotkey** | Shortcut (Ctrl+Alt+Z) | Press shortcut to open anywhere |
| **PowerShell Automation** | Pipeline / Scripts | `$ans = ziskare-ai "Summarize this: $log"` |

---

## 🐍 Python API

### 1. Instant One-Liner
```python
import ziskare_ai as zai

answer = zai.ask("What is the speed of light?")
print("Ziskare AI:", answer)
# Output: Ziskare AI: 299,792,458 meters per second.
```

### 2. Class Instance with Metrics
```python
from ziskare_ai import ZiskareAI

ai = ZiskareAI()

# Ask with performance metrics
result = ai.ask("Explain DNS in one sentence.", return_metrics=True)

print("Answer:", result["answer"])
print(f"⏱️ Time: {result['time_taken']}s | Speed: {result['speed']} tok/s")
```

### 3. Multi-Turn Chat (Context Memory)
```python
from ziskare_ai import ZiskareAI

ai = ZiskareAI()

reply, _ = ai.chat("My server runs on port 8080.")
reply, _ = ai.chat("What port was my server on?")
print("Ziskare AI:", reply)  # Output: 8080.

# Clear conversation context
ai.reset()
```

---

## 🌐 REST API Microservice

Start the built-in HTTP server:
```powershell
ziskare-ai --server 5005
```

Query from any language or frontend via `POST http://127.0.0.1:5005/ask`:
```javascript
const res = await fetch('http://127.0.0.1:5005/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ prompt: 'Explain cloud computing.' })
});
const data = await res.json();
console.log(data.answer);
```

---

## 🔄 Disaster Recovery (Fresh Windows Re-Setup)

If you format your laptop or reinstall Windows:
1. Double-click `install.bat` (or `tools/setup_ziskare_ai.bat`).
2. Everything is restored automatically.

*Detailed recovery documentation is available in [`docs/REINSTALL_GUIDE.md`](docs/REINSTALL_GUIDE.md).*

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
