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
| **Specialized AI Agents** | Autonomous Agents | `ziskare-ai --agent [code\|system\|task\|optimize]` |
| **Laptop Cooling & RAM Flush** | Thermal Optimizer | `ziskare-ai --optimize [clean\|cool\|auto]` |
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

## 🔄 Autonomous LLM-to-Agent Bridge

You can directly give natural language prompts to the LLM. The LLM autonomously inspects your intent, calls the appropriate specialized AI agent, the agent works and performs real actions or tool executions, returns its observations to the LLM, and the LLM synthesizes and returns the final answer back to you:

```powershell
# Directly prompt the LLM from any terminal - it calls OptimizerAgent, cools hardware, and synthesizes status:
ziskare-ai "Clean my laptop cache and cool down the CPU"

# Check live diagnostics - LLM calls SystemAgent, analyzes hardware telemetry, and answers:
ziskare-ai "What is my current system hardware status and RAM?"

# Execute math / tools - LLM calls TaskAgent and returns results:
ziskare-ai "Calculate 125 * 8 + 50"
```

In Python:
```python
from ziskare_ai import ZiskareAI

ai = ZiskareAI()

# 1. Prompt LLM directly -> LLM calls agent -> agent works -> LLM synthesizes & returns:
response = ai.ask("Clean my laptop cache and optimize the laptop")
print(response)

# 2. Or access any agent directly on the LLM instance:
ai.call_agent("optimizer", "optimize")
ai.get_agent("system").diagnose()
```

---

## 🤖 Autonomous AI Agents

Ziskare AI includes a modular offline agents framework in [`ziskare_ai/agents/`](ziskare_ai/agents):

```python
from ziskare_ai.agents import CodeAgent, SystemAgent, TaskAgent, AgentOrchestrator

# 1. Code Specialist
coder = CodeAgent()
code = coder.generate_code("Write a binary search in Python")

# 2. System Operations & Health Specialist
sys_agent = SystemAgent()
report = sys_agent.diagnose()  # Live CPU, RAM, Disk, GPU analysis

# 3. Autonomous Task Agent (ReAct Loop + Safe Tools)
tasker = TaskAgent()
result = tasker.execute_task("Calculate 15 * 840 and read file ai.py")

# 4. Multi-Agent Orchestrator
orch = AgentOrchestrator()
res = orch.run("Explain how to fix 100% disk usage on Windows")
# 5. Laptop Hardware & Thermal Optimizer (Fan-Free Cooling)
from ziskare_ai import OptimizerAgent
optimizer = OptimizerAgent()
res = optimizer.optimize()       # Flushes RAM, cleans temp files, releases GPU VRAM
print(f"RAM Freed: {res['memory_flush']['freed_mb']} MB")

# Or run silent background cooling daemon while you work
optimizer.start_auto_cooling(interval_seconds=45)

# 6. AI Image Synthesis & Generative Art Agent (renders in terminal & opens)
from ziskare_ai import ImageAgent
image_agent = ImageAgent()
img_res = image_agent.generate("A majestic cybernetic tiger in a futuristic neon rainforest, 8k")
print(f"Image saved: {img_res['file_path']}")

# 7. Desktop & Laptop Operations Agent (opens files, folders, apps)
from ziskare_ai import DesktopAgent
desktop = DesktopAgent()
desktop.open("output/images")          # Opens folder in File Explorer
desktop.launch("notepad")              # Launches Windows apps
```

Or from the command line:
```powershell
# Run specialized agents directly
ziskare-ai --agent code "Write a fast hash function"
ziskare-ai --agent system "Check system status"
ziskare-ai --agent task "Calculate 125 * 38"
ziskare-ai --image "A glowing dragon over misty mountains, 8k" # Generates with animated loader & crystal-clear terminal preview
ziskare-ai --open "recent image"       # Instantly opens recently generated image
ziskare-ai --open output/images        # Open folder/file in Windows Explorer

# Interactive Multi-Turn Shell (remembers all previous conversation & tasks):
ziskare-ai
# In chat: "generate an image of a cybernetic tiger"
# In chat: "enhance the clarity of the image" (upscales & sharpens existing image)
# In chat: "open the recent image" (opens latest image in default viewer)
# In chat: "tell me about the image" (shows metadata & resolution)

# 1-Click Laptop Hardware & Thermal Optimization
ziskare-ai --optimize                  # Full cleanup: RAM flush, cache purge, thermal cooldown
ziskare-ai --optimize clean            # Clean Windows %TEMP% & pip cache
ziskare-ai --optimize cool             # Reduce CPU wattage & release GPU VRAM
ziskare-ai --optimize auto             # Silent background auto-cooling daemon
ziskare-ai --optimize bench            # Benchmark thermal status & hardware load
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
1. Double-click `install.bat`.
2. Everything is restored automatically.

*Detailed recovery documentation is available in [`docs/REINSTALL_GUIDE.md`](docs/REINSTALL_GUIDE.md).*

---

## 🗑️ Uninstallation

To cleanly remove Ziskare AI from your computer:
1. Double-click **`uninstall.bat`**.
2. The script will remove the `ziskare-ai` package from Python, delete the global CLI commands (`ziskare-ai.cmd` and `ziskare.cmd`), clean build artifacts, and prompt if you want to remove the ~3 GB model cache.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
