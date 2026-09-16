"""
Ziskare AI - Code Agent
=======================
Specialist agent for programming, debugging, refactoring, and code review.
"""

from typing import Optional, Any
from agents.base import BaseAgent
from agents.tools import read_file, write_file

CODE_SYSTEM_PROMPT = (
    "You are the Ziskare Code Agent, an elite principal software engineer and programming specialist. "
    "Your objective is to write production-grade, highly efficient, secure, and bug-free code. "
    "Always adhere to these principles:\n"
    "1. Write clean, idiomatic code with correct typing and concise comments where necessary.\n"
    "2. Keep explanations minimal and direct; focus on the code implementation.\n"
    "3. When debugging or refactoring, highlight the exact fix clearly.\n"
    "4. Prioritize performance and edge-case handling."
)


class CodeAgent(BaseAgent):
    """
    Autonomous programming specialist.
    Capable of generating, refactoring, debugging, and inspecting source files.
    """

    def __init__(self, ai: Optional[Any] = None, silent: bool = False):
        super().__init__(
            name="CodeAgent",
            role="Principal Software Engineer",
            system_prompt=CODE_SYSTEM_PROMPT,
            ai=ai,
            tools={
                "read_file": read_file,
                "write_file": write_file
            },
            temperature=0.2,  # Lower temperature for deterministic, accurate code
            silent=silent
        )

    def generate_code(self, specification: str, language: str = "python") -> str:
        """Generate code adhering to a specification in the requested programming language."""
        task = (
            f"Write clean, production-ready {language} code for the following specification:\n"
            f"{specification}\n\n"
            f"Provide only the code block with necessary comments."
        )
        return self.run(task, max_new_tokens=600)

    def debug_code(self, code: str, error_message: str = "") -> str:
        """Analyze faulty code, pinpoint the bug, and provide the corrected code."""
        prompt = (
            f"Analyze and fix the bug in this code:\n```\n{code}\n```\n"
        )
        if error_message:
            prompt += f"Reported Error / Traceback:\n{error_message}\n\n"
        prompt += "Explain the bug in 1-2 sentences, followed by the complete corrected code."
        return self.run(prompt, max_new_tokens=600)

    def review_code(self, code: str) -> str:
        """Perform a rigorous code review checking for bugs, security vulnerabilities, and optimizations."""
        prompt = (
            f"Perform a professional code review for the following snippet:\n```\n{code}\n```\n"
            f"Provide concise feedback categorized by: Bugs/Risks, Performance, and Improvements."
        )
        return self.run(prompt, max_new_tokens=512)

    def refactor_code(self, code: str, instructions: str) -> str:
        """Refactor existing code according to instructions."""
        prompt = (
            f"Refactor the following code:\n```\n{code}\n```\n"
            f"Instructions: {instructions}\n\n"
            f"Provide the complete refactored code."
        )
        return self.run(prompt, max_new_tokens=600)

    def explain_code(self, code: str) -> str:
        """Explain the logic and architecture of a code block directly and concisely."""
        prompt = (
            f"Explain how this code works in concise bullet points:\n```\n{code}\n```"
        )
        return self.run(prompt, max_new_tokens=400)
