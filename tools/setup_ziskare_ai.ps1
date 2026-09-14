<#
.SYNOPSIS
    Automated Re-setup Script for Ziskare AI on Fresh Windows Installation.
.DESCRIPTION
    Installs CUDA-enabled PyTorch, Transformers, Ziskare AI engine, and global CLI commands.
#>

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       Ziskare AI - Fresh Installation / Re-Setup       " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCheck) {
    Write-Host "ERROR: Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/ (check 'Add python.exe to PATH')" -ForegroundColor Yellow
    exit 1
}
$pyVersion = python --version
Write-Host "Found: $pyVersion" -ForegroundColor Green

# 2. Check NVIDIA GPU
Write-Host "[2/5] Detecting NVIDIA GPU..." -ForegroundColor Yellow
$nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($nvidiaSmi) {
    $gpuInfo = nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
    Write-Host "Detected GPU: $gpuInfo" -ForegroundColor Green
} else {
    Write-Host "Notice: nvidia-smi not found. If your laptop has an NVIDIA GPU, ensure NVIDIA drivers are installed." -ForegroundColor DarkYellow
}

# 3. Install PyTorch with CUDA Acceleration
Write-Host "[3/5] Installing CUDA-accelerated PyTorch & Dependencies..." -ForegroundColor Yellow
Write-Host "Running pip install..." -ForegroundColor DarkGray
pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cu126 --force-reinstall
pip install transformers accelerate

# 4. Deploy Ziskare AI Engine to Site-Packages
Write-Host "[4/5] Deploying Ziskare AI engine to Python site-packages..." -ForegroundColor Yellow
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

$deployScript = @"
import sys, os, shutil

# Source code of universal ziskare_ai engine
ziskare_code = '''\"\"\"
Ziskare AI - Universal Offline Embedded Intelligence Engine
\"\"\"
import os, sys, time, json, torch
from transformers import AutoTokenizer, AutoModelForCausalLM

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

MODEL_IDENTIFIER = "Qwen/Qwen2.5-1.5B-Instruct"
DISPLAY_NAME = "Ziskare AI"
DEFAULT_SYSTEM_PROMPT = (
    "You are Ziskare AI, a direct and precise assistant. "
    "Provide ONLY the direct answer to the user's question without greetings, "
    "pleasantries, filler words, or unnecessary conversational introductions."
)

class ZiskareAI:
    def __init__(self, model_name=MODEL_IDENTIFIER, local_path=None, system_prompt=DEFAULT_SYSTEM_PROMPT, device="auto", silent=False):
        self.model_target = local_path if local_path else model_name
        self.system_prompt = system_prompt
        self.history = []

        if not silent:
            print(f"[Ziskare AI] Initializing {DISPLAY_NAME} Core...", flush=True)
        start = time.perf_counter()

        if device == "auto":
            try:
                if torch.cuda.is_available():
                    self.device = "cuda"
                    try:
                        torch.backends.cuda.matmul.allow_tf32 = True
                        torch.backends.cudnn.allow_tf32 = True
                    except Exception:
                        pass
                    torch_dtype = torch.float16
                    device_name = f"GPU: {torch.cuda.get_device_name(0)} (CUDA)"
                else:
                    self.device = "cpu"
                    torch_dtype = torch.float32
                    device_name = "CPU"
            except Exception:
                self.device = "cpu"
                torch_dtype = torch.float32
                device_name = "CPU"
        else:
            self.device = device
            torch_dtype = torch.float16 if "cuda" in device else torch.float32
            device_name = device

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_target, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_target,
            torch_dtype=torch_dtype,
            device_map=self.device,
            local_files_only=True
        )

        load_time = time.perf_counter() - start
        if not silent:
            print(f"[Ziskare AI] {DISPLAY_NAME} Ready in {load_time:.2f}s ({device_name})", flush=True)
        self.reset()

    def ask(self, prompt, max_new_tokens=256, temperature=0.3, return_metrics=False):
        messages = [{"role": "system", "content": self.system_prompt}, {"role": "user", "content": prompt}]
        inputs = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=True, return_dict=True, return_tensors="pt").to(self.model.device)
        start = time.perf_counter()
        with torch.inference_mode():
            outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=temperature > 0, temperature=temperature if temperature > 0 else None, top_p=0.9 if temperature > 0 else None)
        elapsed = time.perf_counter() - start
        gen_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
        answer = self.tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()
        if return_metrics:
            count = len(gen_tokens)
            speed = count / elapsed if elapsed > 0 else 0
            return {"answer": answer, "time_taken": round(elapsed, 3), "tokens": count, "speed": round(speed, 1)}
        return answer

    def chat(self, user_message, max_new_tokens=256, temperature=0.3):
        self.history.append({"role": "user", "content": user_message})
        inputs = self.tokenizer.apply_chat_template(self.history, add_generation_prompt=True, tokenize=True, return_dict=True, return_tensors="pt").to(self.model.device)
        start = time.perf_counter()
        with torch.inference_mode():
            outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=temperature > 0, temperature=temperature if temperature > 0 else None, top_p=0.9 if temperature > 0 else None)
        elapsed = time.perf_counter() - start
        gen_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
        answer = self.tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()
        self.history.append({"role": "assistant", "content": answer})
        count = len(gen_tokens)
        speed = count / elapsed if elapsed > 0 else 0
        return answer, {"time_taken": round(elapsed, 2), "tokens": count, "speed": round(speed, 1)}

    def reset(self):
        self.history = [{"role": "system", "content": self.system_prompt}]

_default_instance = None
def _get_default(silent=False):
    global _default_instance
    if _default_instance is None:
        _default_instance = ZiskareAI(silent=silent)
    return _default_instance

def ask(prompt, **kwargs):
    return _get_default().ask(prompt, **kwargs)

def chat(user_message, **kwargs):
    return _get_default().chat(user_message, **kwargs)

def main():
    args = sys.argv[1:]
    if args:
        prompt = " ".join(args)
        ai = _get_default(silent=True)
        print(ai.ask(prompt))
        return
    ai = _get_default()
    print("\\n=======================================================")
    print("  Ziskare AI - Interactive Shell")
    print("  Type 'exit' or 'quit' to close.")
    print("=======================================================\\n")
    while True:
        try:
            query = input("You: ").strip()
            if query.lower() in ["exit", "quit"]:
                print("Ziskare AI: Session closed.")
                break
            if not query:
                continue
            response, metrics = ai.chat(query)
            print(f"Ziskare AI: {response}")
            print(f"⏱️ {metrics['time_taken']}s ({metrics['tokens']} tokens | {metrics['speed']} tok/s)\\n")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
'''

# Find site-packages directory
import site
site_dirs = site.getsitepackages()
site_pkg = site_dirs[-1]
pkg_dir = os.path.join(site_pkg, 'ziskare_ai')
os.makedirs(pkg_dir, exist_ok=True)

with open(os.path.join(pkg_dir, '__init__.py'), 'w', encoding='utf-8') as f:
    f.write(ziskare_code)
with open(os.path.join(pkg_dir, '__main__.py'), 'w', encoding='utf-8') as f:
    f.write(ziskare_code)
with open(os.path.join(site_pkg, 'ziskare_ai.py'), 'w', encoding='utf-8') as f:
    f.write(ziskare_code)

print("Installed ziskare_ai to:", pkg_dir)
"@

python -c "$deployScript"

# 5. Create Global CLI Commands
Write-Host "[5/5] Creating global CLI commands (ziskare-ai.cmd)..." -ForegroundColor Yellow
$pyPath = (Get-Command python).Source
$pyBin = Split-Path -Parent $pyPath
$cmdContent = "@echo off`npython -m ziskare_ai %*`n"

Set-Content -Path (Join-Path $pyBin "ziskare-ai.cmd") -Value $cmdContent -Encoding Ascii
Set-Content -Path (Join-Path $pyBin "ziskare.cmd") -Value $cmdContent -Encoding Ascii
Write-Host "Created global command in: $pyBin" -ForegroundColor Green

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "       Ziskare AI Re-Setup Completed Successfully!      " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host "You can now run: ziskare-ai" -ForegroundColor Cyan
