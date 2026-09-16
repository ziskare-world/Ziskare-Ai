"""
Ziskare AI - Agent Toolset
==========================
Safe, modular local tools for autonomous agents, system optimization, and thermal cooling.
"""

import os
import sys
import gc
import ctypes
import shutil
import psutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List

DEFAULT_WORKSPACE = Path(os.getcwd())


def read_file(path: str, max_chars: int = 4000) -> str:
    """Read the contents of a local file safely."""
    try:
        p = Path(path)
        if not p.is_absolute():
            p = DEFAULT_WORKSPACE / p
        if not p.exists():
            return f"Error: File not found at '{path}'."
        if p.is_dir():
            return f"Error: '{path}' is a directory, not a file."
        content = p.read_text(encoding="utf-8", errors="replace")
        if len(content) > max_chars:
            return content[:max_chars] + f"\n... [Truncated: {len(content) - max_chars} characters remaining]"
        return content
    except Exception as e:
        return f"Error reading file '{path}': {str(e)}"


def write_file(path: str, content: str) -> str:
    """Write or overwrite text content to a local file."""
    try:
        p = Path(path)
        if not p.is_absolute():
            p = DEFAULT_WORKSPACE / p
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Success: Wrote {len(content)} characters to '{path}'."
    except Exception as e:
        return f"Error writing file '{path}': {str(e)}"


def list_dir(path: str = ".") -> str:
    """List contents of a directory."""
    try:
        p = Path(path)
        if not p.is_absolute():
            p = DEFAULT_WORKSPACE / p
        if not p.exists():
            return f"Error: Directory not found at '{path}'."
        if not p.is_dir():
            return f"Error: '{path}' is a file, not a directory."
        
        entries = []
        for entry in p.iterdir():
            kind = "DIR" if entry.is_dir() else "FILE"
            size = f" ({entry.stat().st_size} bytes)" if entry.is_file() else ""
            entries.append(f"[{kind}] {entry.name}{size}")
        return "\n".join(entries) if entries else "(Directory is empty)"
    except Exception as e:
        return f"Error listing directory '{path}': {str(e)}"


def get_system_stats() -> Dict[str, Any]:
    """Retrieve real-time hardware telemetry: CPU, RAM, Disk, and GPU."""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(str(Path.cwd().anchor))
    
    gpu_info = "N/A"
    gpu_temp = "N/A"
    try:
        import torch
        if torch.cuda.is_available():
            gpu_info = f"{torch.cuda.get_device_name(0)} (VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB)"
            try:
                out = subprocess.run(
                    ["nvidia-smi", "--query-gpu=temperature.gpu,utilization.gpu", "--format=csv,noheader,nounits"],
                    capture_output=True, text=True, timeout=2
                )
                if out.returncode == 0 and out.stdout.strip():
                    parts = out.stdout.strip().split(",")
                    gpu_temp = f"{parts[0].strip()}°C (Util: {parts[1].strip()}%)"
            except Exception:
                pass
    except Exception:
        pass

    return {
        "cpu_usage_percent": cpu_percent,
        "memory": {
            "total_gb": round(mem.total / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "percent": mem.percent
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent
        },
        "gpu": gpu_info,
        "gpu_thermal": gpu_temp
    }


def clean_temp_files() -> Dict[str, Any]:
    """
    Safely purges Windows temporary files, user temp directories, pip cache, and Python caches.
    Ignores locked files that are currently active in running processes.
    """
    cleaned_bytes = 0
    cleaned_files = 0
    errors = 0

    temp_paths = []
    if os.environ.get("TEMP"):
        temp_paths.append(Path(os.environ.get("TEMP")))
    if os.environ.get("LOCALAPPDATA"):
        local_app = Path(os.environ.get("LOCALAPPDATA"))
        local_temp = local_app / "Temp"
        if local_temp not in temp_paths:
            temp_paths.append(local_temp)
        crash_dumps = local_app / "CrashDumps"
        if crash_dumps.exists() and crash_dumps not in temp_paths:
            temp_paths.append(crash_dumps)
        wer_archive = local_app / "Microsoft" / "Windows" / "WER" / "ReportArchive"
        if wer_archive.exists() and wer_archive not in temp_paths:
            temp_paths.append(wer_archive)
        wer_queue = local_app / "Microsoft" / "Windows" / "WER" / "ReportQueue"
        if wer_queue.exists() and wer_queue not in temp_paths:
            temp_paths.append(wer_queue)

    win_temp = Path("C:/Windows/Temp")
    if win_temp.exists() and win_temp not in temp_paths:
        temp_paths.append(win_temp)

    for temp_dir in temp_paths:
        if not temp_dir.exists():
            continue
        try:
            entries = list(temp_dir.iterdir())
        except (PermissionError, OSError):
            continue

        for entry in entries:
            try:
                if entry.is_file() or entry.is_symlink():
                    sz = entry.stat().st_size
                    entry.unlink()
                    cleaned_bytes += sz
                    cleaned_files += 1
                elif entry.is_dir():
                    shutil.rmtree(entry, ignore_errors=True)
                    cleaned_files += 1
            except Exception:
                errors += 1

    # Purge pip cache safely
    try:
        subprocess.run(["pip", "cache", "purge"], input="y\n", text=True, capture_output=True, timeout=3)
    except Exception:
        pass

    # Clean local project __pycache__ if present
    try:
        for pyc in DEFAULT_WORKSPACE.glob("**/__pycache__"):
            if pyc.is_dir():
                shutil.rmtree(pyc, ignore_errors=True)
    except Exception:
        pass

    freed_mb = round(cleaned_bytes / (1024 * 1024), 2)
    return {
        "status": "success",
        "freed_bytes": cleaned_bytes,
        "freed_mb": freed_mb,
        "files_removed": cleaned_files,
        "skipped_in_use_files": errors
    }


def flush_system_memory() -> Dict[str, Any]:
    """
    Optimizes system working set memory using Windows native API (EmptyWorkingSet),
    triggers Python garbage collection, and flushes memory pages.
    """
    mem_before = psutil.virtual_memory()
    before_used_mb = round(mem_before.used / (1024 * 1024), 2)

    # 1. Run Python Garbage Collector
    gc.collect()

    # 2. Windows API Working Set Trimming
    trimmed_processes = 0
    if sys.platform == "win32":
        try:
            # PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION = 0x0100 | 0x0400 = 0x0500
            flags = 0x0500
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    pid = proc.info['pid']
                    if pid == 0 or pid == 4:  # System Idle / System
                        continue
                    handle = ctypes.windll.kernel32.OpenProcess(flags, False, pid)
                    if handle:
                        ctypes.windll.psapi.EmptyWorkingSet(handle)
                        ctypes.windll.kernel32.CloseHandle(handle)
                        trimmed_processes += 1
                except Exception:
                    pass
        except Exception:
            pass

    mem_after = psutil.virtual_memory()
    after_used_mb = round(mem_after.used / (1024 * 1024), 2)
    freed_mb = round(max(0, before_used_mb - after_used_mb), 2)

    return {
        "status": "success",
        "before_used_mb": before_used_mb,
        "after_used_mb": after_used_mb,
        "freed_mb": freed_mb,
        "current_memory_percent": mem_after.percent,
        "processes_optimized": trimmed_processes
    }


def cool_hardware_thermal() -> Dict[str, Any]:
    """
    Hardware Thermal Cooldown:
    1. Releases GPU VRAM caches (torch.cuda.empty_cache()).
    2. Detects high CPU processes and optimizes their process priority to minimize wattage & fan noise.
    3. Returns real-time thermal snapshot.
    """
    actions_taken: List[str] = []

    # 1. GPU VRAM Cleanup
    gpu_freed_mb = 0.0
    try:
        import torch
        if torch.cuda.is_available():
            before_alloc = torch.cuda.memory_allocated(0)
            before_reserved = torch.cuda.memory_reserved(0)
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            after_reserved = torch.cuda.memory_reserved(0)
            gpu_freed_mb = round((before_reserved - after_reserved) / (1024 * 1024), 2)
            actions_taken.append(f"Flushed GPU VRAM cache (released {gpu_freed_mb} MB).")
    except Exception:
        pass

    # 2. Process Wattage Optimization (Cooling CPU)
    throttled_procs = 0
    safe_skip = ["system", "registry", "smss.exe", "csrss.exe", "wininit.exe", "explorer.exe", "python.exe"]
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            name = (proc.info['name'] or "").lower()
            if any(skip in name for skip in safe_skip):
                continue
            cpu = proc.info.get('cpu_percent', 0.0) or 0.0
            # If a background non-essential process is eating CPU cycles, drop priority
            if cpu > 15.0:
                p = psutil.Process(proc.info['pid'])
                if sys.platform == "win32":
                    p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                    throttled_procs += 1
                    actions_taken.append(f"Reduced power priority for '{name}' (PID: {proc.info['pid']}).")
        except Exception:
            pass

    # 3. Read thermal state
    stats = get_system_stats()
    return {
        "status": "cooled",
        "gpu_vram_freed_mb": gpu_freed_mb,
        "cpu_usage_percent": stats["cpu_usage_percent"],
        "memory_percent": stats["memory"]["percent"],
        "gpu_thermal": stats.get("gpu_thermal", "N/A"),
        "actions_taken": actions_taken,
        "throttled_processes": throttled_procs
    }


def benchmark_laptop() -> Dict[str, Any]:
    """Runs a complete thermal and hardware health benchmark for the laptop."""
    stats = get_system_stats()
    
    thermal_rating = "Cool & Silent"
    cpu = stats["cpu_usage_percent"]
    mem_pct = stats["memory"]["percent"]

    if cpu > 70 or mem_pct > 85:
        thermal_rating = "High Load (Fan May Spin Up)"
    elif cpu > 40 or mem_pct > 75:
        thermal_rating = "Moderate Load"

    return {
        "status": "ready",
        "thermal_status": thermal_rating,
        "cpu_usage_percent": cpu,
        "memory": stats["memory"],
        "disk": stats["disk"],
        "gpu": stats["gpu"],
        "gpu_thermal": stats.get("gpu_thermal", "N/A")
    }


def calculate(expression: str) -> str:
    """Safely evaluate basic mathematical expressions."""
    allowed_chars = set("0123456789+-*/().,% eE")
    if not all(c in allowed_chars for c in expression.strip()):
        return "Error: Expression contains unsupported characters for arithmetic."
    try:
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Calculation error: {str(e)}"


def run_command(command: str, timeout_sec: int = 15) -> str:
    """Execute a shell command locally and capture stdout/stderr."""
    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_sec
        )
        out = proc.stdout.strip()
        err = proc.stderr.strip()
        if proc.returncode == 0:
            return out if out else "(Command executed with no output)"
        else:
            return f"Command exited with code {proc.returncode}.\nOutput: {out}\nError: {err}"
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout_sec} seconds."
    except Exception as e:
        return f"Execution error: {str(e)}"


AVAILABLE_TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_dir": list_dir,
    "get_system_stats": get_system_stats,
    "clean_temp_files": clean_temp_files,
    "flush_system_memory": flush_system_memory,
    "cool_hardware_thermal": cool_hardware_thermal,
    "benchmark_laptop": benchmark_laptop,
    "calculate": calculate,
    "run_command": run_command
}
