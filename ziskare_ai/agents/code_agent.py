"""
Ziskare AI - Code Agent
=======================
Specialist agent for programming, debugging, refactoring, and code review.
By default outputs pure code without comments or explanations unless explicitly requested.
"""

import re
from typing import Optional, Any
from ziskare_ai.agents.base import BaseAgent
from ziskare_ai.agents.tools import read_file, write_file

CODE_SYSTEM_PROMPT = (
    "You are the Ziskare Code Agent, an elite principal software engineer and programming specialist. "
    "Your objective is to write production-grade, highly efficient, secure, and bug-free code.\n\n"
    "CRITICAL OUTPUT RULES:\n"
    "1. BY DEFAULT, DO NOT provide any explanation, markdown conversational filler, or introductory/closing text.\n"
    "2. BY DEFAULT, DO NOT include any comments inside the code (no inline comments, docstrings, or explanatory notes).\n"
    "3. Output ONLY the code itself inside a markdown code block ```language ... ```.\n"
    "4. ONLY provide explanations or comments if the user explicitly requested 'comments', 'commented', 'explain', 'explanation', or 'documentation'."
)


class CodeAgent(BaseAgent):
    """
    Autonomous programming specialist.
    Capable of generating, refactoring, debugging, and inspecting source files.
    By default outputs pure code without comments or explanations unless requested.
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
            temperature=0.2,
            silent=silent
        )

    @staticmethod
    def _strip_comments_and_docstrings(code: str) -> str:
        """Strip inline comments and docstrings from code."""
        # Remove triple-quoted docstrings
        code = re.sub(r'"""[\s\S]*?"""', '', code)
        code = re.sub(r"'''[\s\S]*?'''", '', code)
        # Remove single line comments
        cleaned_lines = []
        for line in code.splitlines():
            clean = re.sub(r'#.*$', '', line)
            clean = re.sub(r'//.*$', '', clean)
            if clean.strip() or not cleaned_lines or cleaned_lines[-1].strip():
                cleaned_lines.append(clean.rstrip())
        # Strip leading/trailing empty lines
        while cleaned_lines and not cleaned_lines[0].strip():
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        return "\n".join(cleaned_lines)

    def run(
        self,
        task: str,
        max_new_tokens: int = 600,
        temperature: Optional[float] = None
    ) -> str:
        """
        Execute code task adhering strictly to the no-comment, no-explanation rule
        unless explicitly requested by the user.
        """
        low = task.lower()
        wants_comments = any(w in low for w in ["comment", "comments", "commented", "documented", "document"])
        wants_explanation = any(w in low for w in ["explain", "explanation", "describe", "why", "breakdown", "guide"])

        instructions = []
        if not wants_comments:
            instructions.append("Do NOT write any comments or docstrings in the code.")
        else:
            instructions.append("Include clear, helpful comments in the code.")

        if not wants_explanation:
            instructions.append("Do NOT write any explanation, introduction, or text outside the code block. Output ONLY the code.")
        else:
            instructions.append("Include a clear, concise explanation along with the code.")

        rule_block = "\n".join(f"- {inst}" for inst in instructions)
        modified_task = f"{task}\n\n[Formatting Directives]:\n{rule_block}"

        raw_res = super().run(modified_task, max_new_tokens=max_new_tokens, temperature=temperature)

        if not wants_explanation:
            # Extract code inside backticks if model included any markdown or intro text
            code_match = re.search(r'```(?:[a-zA-Z0-9_\+\#-]*\n)?([\s\S]*?)```', raw_res)
            code_body = code_match.group(1).strip() if code_match else raw_res.strip()
            lang_match = re.search(r'```([a-zA-Z0-9_\+\#-]+)', raw_res)
            lang = lang_match.group(1) if lang_match else "python"

            if not wants_comments:
                code_body = self._strip_comments_and_docstrings(code_body)

            return f"```{lang}\n{code_body}\n```"

        if not wants_comments:
            def _replace_block(m):
                content = self._strip_comments_and_docstrings(m.group(1))
                return f"```{content}```"
            return re.sub(r'```([\s\S]*?)```', _replace_block, raw_res)

        return raw_res

    def generate_code(self, specification: str, language: str = "python") -> str:
        """Generate code adhering to a specification in the requested programming language."""
        task = f"Write clean, production-ready {language} code for the following specification:\n{specification}"
        return self.run(task, max_new_tokens=600)

    def debug_code(self, code: str, error_message: str = "") -> str:
        """Analyze faulty code, pinpoint the bug, and provide the corrected code."""
        prompt = f"Fix the bug in this code:\n```\n{code}\n```\n"
        if error_message:
            prompt += f"Reported Error / Traceback:\n{error_message}\n\n"
        return self.run(prompt, max_new_tokens=600)

    def review_code(self, code: str) -> str:
        """Perform a rigorous code review checking for bugs, security vulnerabilities, and optimizations."""
        prompt = (
            f"Perform a professional code review for the following snippet:\n```\n{code}\n```\n"
            f"Explain bugs, risks, and performance improvements concisely."
        )
        return super().run(prompt, max_new_tokens=512)

    def refactor_code(self, code: str, instructions: str) -> str:
        """Refactor existing code according to instructions."""
        prompt = f"Refactor the following code:\n```\n{code}\n```\nInstructions: {instructions}"
        return self.run(prompt, max_new_tokens=600)

    def explain_code(self, code: str) -> str:
        """Explain the logic and architecture of a code block directly and concisely."""
        prompt = (
            f"Explain how this code works in concise bullet points:\n```\n{code}\n```"
        )
        return super().run(prompt, max_new_tokens=400)
