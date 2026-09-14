# 🏗️ Ziskare AI Technical Architecture

## 1. System Overview
Ziskare AI is designed as a self-contained, air-gapped intelligence engine that embeds local Large Language Models into host systems with minimal overhead and zero cloud dependencies.

```text
+-------------------------------------------------------------+
|                     Client Applications                     |
|  Python Scripts  |  CLI Terminal  |  Node.js / Web  |  cURL |
+--------+-----------------+---------------+-------------+----+
         |                 |               |             |
         | Python Import   | OS Shell      | HTTP JSON   |
         v                 v               v             |
+--------------------------------------------------------+----+
|                     Ziskare AI Core                         |
|  - ziskare_ai.ZiskareAI                                     |
|  - ziskare_ai.cli (Interactive & Single-shot)              |
|  - ziskare_ai.server (Built-in REST API Server)            |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                 Execution & Hardware Layer                  |
|  - PyTorch CUDA (TensorFloat-32, Float16)                   |
|  - Hugging Face Transformers Local Pipeline                 |
|  - NVIDIA GeForce RTX 3050 Tensor Cores / CPU Fallback      |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                 Model Weights & Quantization                |
|  - Qwen/Qwen2.5-1.5B-Instruct (~3 GB Local Cache)          |
|  - 100% Offline Air-Gapped Weight Storage                   |
+-------------------------------------------------------------+
```

---

## 2. Memory & VRAM Optimization
- **Model Footprint**: The 1.5B parameter model takes ~3.0 GB of VRAM in `float16` precision.
- **GPU Acceleration**:
  - Automatically checks `torch.cuda.is_available()`.
  - Enables `torch.backends.cuda.matmul.allow_tf32 = True` and `torch.backends.cudnn.allow_tf32 = True` for NVIDIA Ampere architecture.
  - Generates responses at 25–60+ tokens/second.
- **CPU Fallback**:
  - In environments without CUDA GPUs, automatically switches to `float32` CPU mode.

---

## 3. Strict Offline Protocol
To prevent latency, accidental data leaks, or network timeouts:
- `HF_HUB_OFFLINE = "1"`
- `TRANSFORMERS_OFFLINE = "1"`
- `local_files_only = True`
Every token, prompt, and response stays 100% strictly local to the machine.
