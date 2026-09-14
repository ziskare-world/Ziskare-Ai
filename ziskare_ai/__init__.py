"""
Ziskare AI - Universal Offline Embedded Intelligence Engine
============================================================
Package root exposing core engine, helper functions, and REST runner.
"""

from ziskare_ai.core import ZiskareAI
from ziskare_ai.cli import get_default_ai, main
from ziskare_ai.server import run_server

__version__ = "1.0.0"
__author__ = "Ziskare World"


def ask(prompt: str, **kwargs) -> str:
    """Convenience one-liner for direct answers."""
    return get_default_ai().ask(prompt, **kwargs)


def chat(user_message: str, **kwargs):
    """Convenience wrapper for multi-turn chat."""
    return get_default_ai().chat(user_message, **kwargs)


__all__ = [
    "ZiskareAI",
    "ask",
    "chat",
    "run_server",
    "main",
    "__version__"
]
