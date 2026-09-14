# ⚡ Ziskare AI

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-CUDA%20Accelerated-EE4C2C?logo=pytorch&logoColor=white)
![Hardware](https://img.shields.io/badge/GPU-NVIDIA%20GeForce%20RTX-76B900?logo=nvidia&logoColor=white)
![Offline](https://img.shields.io/badge/Network-100%25%20Offline-success)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Universal, 100% Offline, Hardware-Accelerated Local Intelligence Engine for Any Application.**

[Features](#-key-features) • [Installation](#-installation) • [Python API](#-python-api) • [CLI Tool](#-cli-usage) • [REST API](#-rest-api-microservice) • [Cross-Language](#-cross-language-integration) • [Recovery](#-disaster-recovery)

</div>

---

## 🌟 Overview

**Ziskare AI** is a lightweight, zero-latency, embedded AI engine designed to run entirely locally on your machine. It requires zero cloud API keys, makes zero network requests, and executes with direct GPU acceleration on NVIDIA hardware.

By default, Ziskare AI is tuned to provide **direct, concise answers** without conversational fluff, pleasantries, or preamble.

---

## ⚡ Key Features

- 🔒 **100% Air-Gapped & Offline**: Strict `HF_HUB_OFFLINE=1`. Your queries and data never leave your computer.
- 🚀 **Hardware Accelerated**: Automatically engages NVIDIA CUDA GPUs (TensorFloat-32 & Float16 precision for RTX 30-series Tensor Cores).
- 🧩 **Universal Access**:
  - **Python Library**: `import ziskare_ai as zai` anywhere on your computer.
  - **Global CLI**: Run `ziskare-ai "your question"` from any terminal.
  - **REST API Microservice**: Built-in HTTP server (`ziskare-ai --server 5005`) for Node.js, C#, Java, Go, or web apps.
- 🎯 **No Conversational Filler**: Eliminates polite intros and pleasantries, providing pure direct answers.
- 🧠 **Smart Context Management**: Supports both one-off queries (`.ask`) and multi-turn conversational memory (`.chat`).

---

## 📦 Installation

### Standard Setup:
```bash
# Clone the repository
git clone https://github.com/ziskare-world/Ziskare-Ai.git
cd Ziskare-Ai

# Install requirements
pip install -r requirements.txt

# Install Ziskare AI globally
pip install -e .
```

### NVIDIA GPU Acceleration (Recommended):
For NVIDIA GeForce RTX GPUs, install CUDA-enabled PyTorch:
```bash
pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cu126 --force-reinstall
```

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

### 4. Custom System Prompt (e.g., Strict JSON Formatter)
```python
from ziskare_ai import ZiskareAI

json_ai = ZiskareAI(
    system_prompt="You are a strict data formatter. Output ONLY valid JSON matching the user's request."
)

data = json_ai.ask("List 3 primary colors in a JSON array")
print(data)  # ["red", "blue", "yellow"]
```

---

## 💻 CLI Usage

Once installed, the `ziskare-ai` command is accessible from **any terminal, PowerShell, or CMD**:

### Direct Question Answering:
```powershell
ziskare-ai "What is 5 plus 5?"
# Output: 10
```

### Interactive Chat Shell:
```powershell
ziskare-ai
```

### Launch Local REST API Microservice:
```powershell
ziskare-ai --server 5005
```

---

## 🌐 REST API Microservice

Run Ziskare AI as a background service:
```powershell
ziskare-ai --server 5005
```

### Endpoints:
| Method | Route | Body | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/ask` | `{"prompt": "..."}` | Single-turn direct answer with speed metrics. |
| `POST` | `/chat` | `{"message": "..."}` | Multi-turn conversational chat with memory. |
| `POST` | `/reset` | None | Clears conversational memory. |
| `GET` | `/health` | None | Health check and device status. |

---

## 🔌 Cross-Language Integration

### In Node.js / JavaScript (CLI Execution):
```javascript
const { execSync } = require('child_process');

function askZiskare(prompt) {
  return execSync(`ziskare-ai "${prompt}"`).toString().trim();
}

console.log("Ziskare AI:", askZiskare("What is Docker?"));
```

### In Web Applications (REST API `fetch`):
```javascript
const response = await fetch('http://127.0.0.1:5005/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ prompt: 'Explain cloud computing in one sentence.' })
});
const data = await response.json();
console.log(data.answer);
```

---

## 🔄 Disaster Recovery (Fresh Windows Re-Setup)

If you format your laptop or reinstall Windows:
1. Run [`tools/setup_ziskare_ai.bat`](tools/setup_ziskare_ai.bat) (or `tools/setup_ziskare_ai.ps1`).
2. The automated script restores CUDA PyTorch, deploys the package, and registers global CLI commands.

*Detailed recovery documentation is available in [`docs/REINSTALL_GUIDE.md`](docs/REINSTALL_GUIDE.md).*

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
