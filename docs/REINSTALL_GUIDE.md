# 🔄 Complete Re-Setup Guide (After Formatting Laptop)

This guide documents the exact steps to restore **Ziskare AI** on a freshly formatted Windows computer, with GPU acceleration on your **NVIDIA GeForce RTX 3050 Laptop GPU**.

---

## 💾 Phase 1: Before Formatting (Backup Checklist)

Before wiping your laptop, save these to an external USB Drive:
1. **Save This Project Folder**:
   - Copy `d:\Ziskare-space\` to your USB Drive.
2. **(Optional - Saves ~3GB download)**:
   - Copy your local model cache:
     ```text
     C:\Users\ayush\.cache\huggingface\hub\models--Qwen--Qwen2.5-1.5B-Instruct
     ```
   - Pasting this back after formatting will let you run Ziskare AI immediately without redownloading weights.

---

## 🚀 Phase 2: After Formatting Windows (One-Click Setup)

### Step 1: Install Drivers & Python
1. **NVIDIA Driver**:
   - Install the official NVIDIA Game Ready / Studio Driver for GeForce RTX 3050 from [nvidia.com/drivers](https://www.nvidia.com/Download/index.aspx) (or let Windows Update install it).
2. **Python**:
   - Download & install Python from [python.org](https://www.python.org/downloads/).
   - ⚠️ **Important**: Ensure you check the box: **`Add python.exe to PATH`** during installation.

---

### Step 2: Run the One-Click Recovery Script
1. Plug in your USB drive and copy `Ziskare-space` back to your drive (e.g. `D:\Ziskare-space`).
2. Open the [`tools/`](file:///d:/Ziskare-space/tools) folder:
3. **Double-click [`setup_ziskare_ai.bat`](file:///d:/Ziskare-space/tools/setup_ziskare_ai.bat)** 
   *(or in PowerShell run: `.\tools\setup_ziskare_ai.ps1`)*.

The automated script will:
* Check for Python & NVIDIA GPU.
* Install CUDA-accelerated PyTorch (`cu126`), `transformers`, and `accelerate`.
* Install the `ziskare_ai` package into your global Python `site-packages`.
* Register the global Windows CLI command `ziskare-ai`.

---

### Step 3: Verify Installation
Open any new PowerShell or CMD window and run:
```powershell
ziskare-ai "What is 5 plus 5?"
```
You should see:
```text
[Ziskare AI] Initializing Ziskare AI Core...
[Ziskare AI] Ziskare AI Ready in 0.8s (Device: GPU: NVIDIA GeForce RTX 3050 Laptop GPU (CUDA))
10
```

---

## 🛠️ Phase 3: Manual Command Reference (Alternative)

If you ever prefer to run the setup manually step-by-step in PowerShell:

```powershell
# 1. Install PyTorch with CUDA acceleration for RTX 3050
pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cu126 --force-reinstall

# 2. Install Hugging Face dependencies
pip install transformers accelerate

# 3. Run the automated deployment script
powershell -ExecutionPolicy Bypass -File .\tools\setup_ziskare_ai.ps1
```

---

## ❓ Troubleshooting Common Fresh-Install Issues

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `'python' is not recognized` | Python was installed without checking "Add to PATH" | Re-run Python installer $\rightarrow$ choose Modify $\rightarrow$ check "Add to PATH", or add Python to Environment Variables. |
| `Device: cpu` instead of GPU | NVIDIA driver missing or standard CPU PyTorch installed | Install NVIDIA driver, then run: `pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cu126 --force-reinstall`. |
| `Execution of scripts is disabled` | Windows PowerShell ExecutionPolicy restriction | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` or double-click `tools/setup_ziskare_ai.bat`. |
