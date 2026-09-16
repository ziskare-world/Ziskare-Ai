"""
Ziskare AI - Autonomous AI Agents Package
=========================================
Modular, 100% offline, hardware-accelerated AI agents.
"""

from ziskare_ai.agents.base import BaseAgent
from ziskare_ai.agents.tools import (
    AVAILABLE_TOOLS,
    read_file,
    write_file,
    list_dir,
    open_path,
    launch_app,
    find_files,
    render_terminal_image,
    get_system_stats,
    clean_temp_files,
    flush_system_memory,
    cool_hardware_thermal,
    benchmark_laptop,
    calculate,
    run_command
)
from ziskare_ai.agents.code_agent import CodeAgent
from ziskare_ai.agents.system_agent import SystemAgent
from ziskare_ai.agents.task_agent import TaskAgent
from ziskare_ai.agents.optimizer_agent import OptimizerAgent
from ziskare_ai.agents.image_agent import ImageAgent
from ziskare_ai.agents.desktop_agent import DesktopAgent
from ziskare_ai.agents.orchestrator import AgentOrchestrator

_global_orchestrator = None


def get_orchestrator(silent: bool = False) -> AgentOrchestrator:
    """Retrieve or create singleton orchestrator sharing one model in VRAM."""
    global _global_orchestrator
    if _global_orchestrator is None:
        _global_orchestrator = AgentOrchestrator(silent=silent)
    return _global_orchestrator


def run_agent(task: str, agent: str = None) -> str:
    """Convenience one-liner to route and execute a task through the agent system."""
    orch = get_orchestrator(silent=True)
    res = orch.run(task, agent_override=agent)
    return res.get("result", "")


__all__ = [
    "BaseAgent",
    "CodeAgent",
    "SystemAgent",
    "TaskAgent",
    "OptimizerAgent",
    "ImageAgent",
    "DesktopAgent",
    "AgentOrchestrator",
    "AVAILABLE_TOOLS",
    "read_file",
    "write_file",
    "list_dir",
    "open_path",
    "launch_app",
    "find_files",
    "render_terminal_image",
    "get_system_stats",
    "clean_temp_files",
    "flush_system_memory",
    "cool_hardware_thermal",
    "benchmark_laptop",
    "calculate",
    "run_command",
    "get_orchestrator",
    "run_agent"
]
