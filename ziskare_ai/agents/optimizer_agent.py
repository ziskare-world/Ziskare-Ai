"""
Ziskare AI - Laptop Optimizer & Thermal Cooling Agent
======================================================
Autonomous agent specialized in cache/temp cleaning, RAM trimming, thermal load reduction,
and background auto-cooling to prevent fans from spinning up during project development.
"""

import time
import threading
from typing import Optional, Dict, Any
from ziskare_ai.agents.base import BaseAgent
from ziskare_ai.agents.tools import (
    clean_temp_files,
    flush_system_memory,
    cool_hardware_thermal,
    benchmark_laptop,
    get_system_stats
)

OPTIMIZER_SYSTEM_PROMPT = (
    "You are the Ziskare Laptop Optimizer & Thermal Cooling Agent, an elite hardware performance "
    "and systems engineer. Your primary directives are:\n"
    "1. Keep the laptop running at peak efficiency by purging temporary files and cache memory.\n"
    "2. Minimize hardware thermal load and CPU power wattage so fans do not need to spin up loudly.\n"
    "3. Flush working set memory and GPU VRAM to maintain plenty of free headroom.\n"
    "Provide clear, quantified reports highlighting exact megabytes freed, processes optimized, and thermal health."
)


class OptimizerAgent(BaseAgent):
    """
    Autonomous Laptop Optimizer & Thermal Cooling Agent.
    Operates on-demand or as a background auto-cooling daemon.
    """

    def __init__(self, ai: Optional[Any] = None, silent: bool = False):
        super().__init__(
            name="OptimizerAgent",
            role="Laptop Hardware & Thermal Performance Specialist",
            system_prompt=OPTIMIZER_SYSTEM_PROMPT,
            ai=ai,
            tools={
                "clean_temp_files": clean_temp_files,
                "flush_system_memory": flush_system_memory,
                "cool_hardware_thermal": cool_hardware_thermal,
                "benchmark_laptop": benchmark_laptop,
                "get_system_stats": get_system_stats
            },
            temperature=0.2,
            silent=silent
        )
        self._auto_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def clean_cache(self) -> Dict[str, Any]:
        """Purge temporary files, Windows %TEMP%, pip cache, and Python caches."""
        return clean_temp_files()

    def flush_ram(self) -> Dict[str, Any]:
        """Flush working set memory across processes and trigger garbage collection."""
        return flush_system_memory()

    def reduce_heat(self) -> Dict[str, Any]:
        """Release GPU VRAM and throttle runaway background processes to reduce wattage and heat."""
        return cool_hardware_thermal()

    def benchmark(self) -> Dict[str, Any]:
        """Run hardware telemetry and thermal diagnostic."""
        return benchmark_laptop()

    def optimize(
        self,
        clean_disk: bool = True,
        flush_ram: bool = True,
        cool_thermal: bool = True
    ) -> Dict[str, Any]:
        """
        Full laptop optimization sequence:
        1. Clean disk caches and temporary files
        2. Flush RAM working sets
        3. Cool CPU/GPU thermal load and adjust process priorities
        """
        report: Dict[str, Any] = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}

        if clean_disk:
            report["cache_clean"] = self.clean_cache()

        if flush_ram:
            report["memory_flush"] = self.flush_ram()

        if cool_thermal:
            report["thermal_cool"] = self.reduce_heat()

        report["current_telemetry"] = get_system_stats()
        return report

    def diagnose_laptop(self) -> str:
        """Run a benchmark and generate an AI-powered diagnostic and thermal assessment."""
        bench = self.benchmark()
        import json
        bench_str = json.dumps(bench, indent=2)

        prompt = (
            f"Analyze this laptop's thermal, CPU, RAM, and GPU status:\n"
            f"```json\n{bench_str}\n```\n"
            f"Provide: 1. Current thermal rating, 2. Bottleneck analysis, 3. Recommended cooling & memory actions."
        )
        return self.run(prompt, max_new_tokens=400)

    def start_auto_cooling(self, interval_seconds: int = 60) -> str:
        """
        Start an automated background daemon that monitors memory and thermals,
        quietly optimizing the laptop while you work so fans stay off.
        """
        if self._auto_thread and self._auto_thread.is_alive():
            return "Auto-cooling daemon is already active."

        self._stop_event.clear()

        def _cooling_loop():
            while not self._stop_event.is_set():
                try:
                    # Silent optimization
                    flush_system_memory()
                    cool_hardware_thermal()
                except Exception:
                    pass
                self._stop_event.wait(interval_seconds)

        self._auto_thread = threading.Thread(target=_cooling_loop, daemon=True, name="ZiskareAutoCooling")
        self._auto_thread.start()
        return f"Auto-cooling background daemon started (monitoring every {interval_seconds}s)."

    def stop_auto_cooling(self) -> str:
        """Stop the automated background cooling daemon."""
        if self._auto_thread and self._auto_thread.is_alive():
            self._stop_event.set()
            self._auto_thread.join(timeout=3)
            return "Auto-cooling daemon stopped."
        return "Auto-cooling daemon is not running."
