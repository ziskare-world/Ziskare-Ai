"""
Ziskare AI - System Diagnostics & Ops Agent
===========================================
Specialist agent for hardware diagnostics, resource tracking, and operational troubleshooting.
"""

import json
import psutil
from typing import Optional, Dict, Any
from agents.base import BaseAgent
from agents.tools import get_system_stats, run_command

SYSTEM_SYSTEM_PROMPT = (
    "You are the Ziskare System Agent, an autonomous Site Reliability Engineer and Systems Administrator. "
    "Your specialty is analyzing live PC telemetry, hardware utilization (CPU, RAM, Disk, GPU), "
    "and troubleshooting operating system, network, and process issues. "
    "Provide crisp, structured technical assessments with practical troubleshooting steps."
)


class SystemAgent(BaseAgent):
    """
    Autonomous hardware, OS, and system operations specialist.
    """

    def __init__(self, ai: Optional[Any] = None, silent: bool = False):
        super().__init__(
            name="SystemAgent",
            role="Systems Administrator & Site Reliability Engineer",
            system_prompt=SYSTEM_SYSTEM_PROMPT,
            ai=ai,
            tools={
                "get_system_stats": get_system_stats,
                "run_command": run_command
            },
            temperature=0.2,
            silent=silent
        )

    def diagnose(self) -> str:
        """Fetch live system telemetry and provide an operational health assessment."""
        stats = get_system_stats()
        stats_str = json.dumps(stats, indent=2)

        prompt = (
            f"Analyze the following real-time system telemetry and produce a health assessment:\n"
            f"```json\n{stats_str}\n```\n"
            f"Highlight any potential bottlenecks, high memory/CPU usage, or storage constraints, "
            f"and state overall system status (Healthy/Warning/Critical)."
        )
        return self.run(prompt, max_new_tokens=400)

    def check_process(self, process_name: str) -> str:
        """Scan running processes matching a name and provide status."""
        matches = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if process_name.lower() in p.info['name'].lower():
                    matches.append({
                        "pid": p.info['pid'],
                        "name": p.info['name'],
                        "cpu_pct": p.info['cpu_percent'],
                        "mem_pct": round(p.info['memory_percent'], 2)
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if not matches:
            return f"No active processes found matching '{process_name}'."

        prompt = (
            f"Here are the active processes found matching '{process_name}':\n"
            f"```json\n{json.dumps(matches[:10], indent=2)}\n```\n"
            f"Briefly summarize their operational status and resource footprint."
        )
        return self.run(prompt, max_new_tokens=350)

    def troubleshoot(self, error_or_issue: str) -> str:
        """Troubleshoot a system, OS, or server issue with actionable remediation steps."""
        prompt = (
            f"Diagnose and resolve the following system issue:\n"
            f"Issue: {error_or_issue}\n\n"
            f"Provide: 1. Root cause hypothesis, 2. Step-by-step resolution commands, 3. Prevention tip."
        )
        return self.run(prompt, max_new_tokens=500)
