"""
Ziskare AI - Universal Offline Embedded Intelligence Engine
============================================================
Package root exposing core engine, helper functions, REST runner, and AI agents.
"""

from ziskare_ai.cli import get_default_ai, main

__version__ = "1.0.0"
__author__ = "Ziskare World"


def ask(prompt: str, **kwargs) -> str:
    """Convenience one-liner for direct answers."""
    return get_default_ai().ask(prompt, **kwargs)


def chat(user_message: str, **kwargs):
    """Convenience wrapper for multi-turn chat."""
    return get_default_ai().chat(user_message, **kwargs)


def run_server(*args, **kwargs):
    """Convenience launcher for REST API server."""
    from ziskare_ai.server import run_server as _run
    return _run(*args, **kwargs)


def __getattr__(name: str):
    if name == "ZiskareAI":
        from ziskare_ai.core import ZiskareAI
        return ZiskareAI
    elif name in ["PromptEnhancer", "enhance_prompt"]:
        import ziskare_ai.enhancer as _enhancer_mod
        return getattr(_enhancer_mod, name)
    elif name in ["CodeAgent", "SystemAgent", "TaskAgent", "OptimizerAgent", "ImageAgent", "DesktopAgent", "AgentOrchestrator", "BaseAgent"]:
        import ziskare_ai.agents as _agents_mod
        return getattr(_agents_mod, name)
    elif name == "agents":
        import ziskare_ai.agents as _agents_mod
        return _agents_mod
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "ZiskareAI",
    "ask",
    "chat",
    "run_server",
    "main",
    "CodeAgent",
    "SystemAgent",
    "TaskAgent",
    "OptimizerAgent",
    "ImageAgent",
    "DesktopAgent",
    "AgentOrchestrator",
    "BaseAgent",
    "PromptEnhancer",
    "enhance_prompt",
    "__version__"
]
