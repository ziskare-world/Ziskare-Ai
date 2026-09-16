"""
Ziskare AI - Agent Orchestrator & Coordinator
=============================================
Routes tasks to the most suitable specialist agent while sharing a single model instance in VRAM.
"""

from typing import Optional, Dict, Any
from agents.code_agent import CodeAgent
from agents.system_agent import SystemAgent
from agents.task_agent import TaskAgent
from agents.base import BaseAgent


class AgentOrchestrator:
    """
    Coordinator and router for multi-agent workflows.
    Maintains a single shared ZiskareAI model in memory to optimize GPU VRAM.
    """

    def __init__(self, ai: Optional[Any] = None, silent: bool = False):
        if ai is not None:
            self.ai = ai
        else:
            from ziskare_ai.core import ZiskareAI
            self.ai = ZiskareAI(silent=silent)
        
        # Instantiate specialists sharing the same underlying model weights
        self.code_agent = CodeAgent(ai=self.ai, silent=True)
        self.system_agent = SystemAgent(ai=self.ai, silent=True)
        self.task_agent = TaskAgent(ai=self.ai, silent=True)
        
        self.agents: Dict[str, BaseAgent] = {
            "code": self.code_agent,
            "system": self.system_agent,
            "task": self.task_agent
        }

    def route_request(self, user_request: str) -> str:
        """
        Determine which agent is best suited to handle the request.
        Returns 'code', 'system', 'task', or 'general'.
        """
        prompt = (
            f"Classify the following request into exactly ONE category:\n"
            f"- 'code' (for programming, algorithms, debugging, code review, or scripts)\n"
            f"- 'system' (for hardware stats, CPU/RAM, processes, OS troubleshooting)\n"
            f"- 'task' (for multi-step actions, file operations, calculations, shell tasks)\n"
            f"- 'general' (for direct questions, knowledge, concepts)\n\n"
            f"Request: \"{user_request}\"\n\n"
            f"Answer with ONLY the category word (code, system, task, or general):"
        )
        cat = self.ai.ask(prompt, max_new_tokens=10, temperature=0.0).strip().lower()
        for valid in ["code", "system", "task", "general"]:
            if valid in cat:
                return valid
        return "general"

    def run(self, user_request: str, agent_override: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Execute request using either an explicit agent or by auto-routing.
        """
        target = agent_override.lower() if agent_override else self.route_request(user_request)

        if target == "code":
            result = self.code_agent.run(user_request, **kwargs)
            return {"agent": "CodeAgent", "category": target, "result": result}

        elif target == "system":
            if "diagnos" in user_request.lower() or "status" in user_request.lower() or "health" in user_request.lower():
                result = self.system_agent.diagnose()
            else:
                result = self.system_agent.run(user_request, **kwargs)
            return {"agent": "SystemAgent", "category": target, "result": result}

        elif target == "task":
            res = self.task_agent.execute_task(user_request, verbose=kwargs.get("verbose", False))
            return {"agent": "TaskAgent", "category": target, "result": res["final_answer"], "trace": res.get("steps")}

        else:
            # Fallback to direct general answer
            result = self.ai.ask(user_request, **kwargs)
            return {"agent": "ZiskareAI", "category": "general", "result": result}
