"""
Ziskare AI - Base Agent Architecture
====================================
Foundation class for all specialized AI agents.
"""

from typing import Dict, Any, List, Optional, Callable
from ziskare_ai.agents.tools import AVAILABLE_TOOLS


class BaseAgent:
    """
    Abstract foundation for all autonomous agents in Ziskare AI.
    Handles memory, tool registration, reasoning steps, and model invocation.
    """

    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        ai: Optional[Any] = None,
        tools: Optional[Dict[str, Callable]] = None,
        temperature: float = 0.3,
        silent: bool = False
    ):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt.strip()
        self.temperature = temperature
        self.silent = silent

        self._ai = ai

        # Registered tools
        self.tools: Dict[str, Callable] = tools if tools is not None else {}

        # Conversation history
        self.history: List[Dict[str, str]] = []
        self.reset()

    @property
    def ai(self):
        """Lazily load ZiskareAI model on first inference request."""
        if self._ai is None:
            from ziskare_ai.core import ZiskareAI
            self._ai = ZiskareAI(silent=self.silent)
        return self._ai

    @ai.setter
    def ai(self, value):
        self._ai = value

    def reset(self):
        """Reset conversation memory with agent system prompt."""
        self.history = [{"role": "system", "content": self.system_prompt}]

    def register_tool(self, name: str, func: Callable):
        """Register a new tool available to this agent."""
        self.tools[name] = func

    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """Invoke a registered tool safely."""
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' is not registered with agent {self.name}."
        try:
            return self.tools[tool_name](**kwargs)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"

    def get_tool_descriptions(self) -> str:
        """Produce a formatted string of tools available to this agent."""
        if not self.tools:
            return "No external tools registered."
        lines = []
        for t_name, t_func in self.tools.items():
            doc = (t_func.__doc__ or "").strip().split("\n")[0]
            lines.append(f"- {t_name}: {doc}")
        return "\n".join(lines)

    def run(
        self,
        task: str,
        max_new_tokens: int = 512,
        temperature: Optional[float] = None
    ) -> str:
        """Execute a one-shot task using the agent persona."""
        temp = temperature if temperature is not None else self.temperature
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task}
        ]

        inputs = self.ai.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt"
        ).to(self.ai.model.device)

        import torch
        with torch.inference_mode():
            outputs = self.ai.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=temp > 0,
                temperature=temp if temp > 0 else None,
                top_p=0.9 if temp > 0 else None
            )

        gen_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
        return self.ai.tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()

    def chat(
        self,
        message: str,
        max_new_tokens: int = 512,
        temperature: Optional[float] = None
    ) -> str:
        """Multi-turn interactive conversation maintaining context."""
        temp = temperature if temperature is not None else self.temperature
        self.history.append({"role": "user", "content": message})

        inputs = self.ai.tokenizer.apply_chat_template(
            self.history,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt"
        ).to(self.ai.model.device)

        import torch
        with torch.inference_mode():
            outputs = self.ai.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=temp > 0,
                temperature=temp if temp > 0 else None,
                top_p=0.9 if temp > 0 else None
            )

        gen_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
        response = self.ai.tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()
        self.history.append({"role": "assistant", "content": response})
        return response

    def __repr__(self) -> str:
        return f"<Agent: {self.name} ({self.role})>"
