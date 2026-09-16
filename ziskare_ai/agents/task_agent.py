"""
Ziskare AI - Autonomous Task Agent (ReAct)
==========================================
Multi-step problem solving agent with autonomous reasoning and tool execution loop.
"""

import json
import re
from typing import Optional, Dict, Any, List, Tuple
from ziskare_ai.agents.base import BaseAgent
from ziskare_ai.agents.tools import AVAILABLE_TOOLS

TASK_SYSTEM_PROMPT = """You are the Ziskare Autonomous Task Agent.
You solve problems by breaking them into steps, using tools when necessary, and delivering a final answer.

Available Tools:
- read_file(path="<path>"): Read text from a local file.
- write_file(path="<path>", content="<text>"): Write text to a file.
- list_dir(path="<path>"): List files and folders in a directory.
- get_system_stats(): Get live CPU, RAM, Disk, and GPU metrics.
- calculate(expression="<math>"): Evaluate a mathematical expression.
- run_command(command="<cmd>"): Run a safe shell command and return its output.

To use a tool, respond in this EXACT format:
Thought: <what you need to do>
Action: <tool_name>({"arg_name": "arg_value"})

When you have the final answer or do not need any more tools, respond in this EXACT format:
Thought: <your final conclusion>
Final Answer: <your direct answer>
"""


class TaskAgent(BaseAgent):
    """
    Autonomous multi-step task execution agent.
    Runs a Thought -> Action -> Observation loop until reaching Final Answer.
    """

    def __init__(self, ai: Optional[Any] = None, max_steps: int = 5, silent: bool = False):
        super().__init__(
            name="TaskAgent",
            role="Autonomous Task & Operations Specialist",
            system_prompt=TASK_SYSTEM_PROMPT,
            ai=ai,
            tools=dict(AVAILABLE_TOOLS),
            temperature=0.1,
            silent=silent
        )
        self.max_steps = max_steps

    def _parse_action(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Parses tool action from model output."""
        match = re.search(r'Action:\s*([a-zA-Z_]+)\s*\((.*)\)', text, re.DOTALL)
        if not match:
            json_match = re.search(r'Action:\s*(\{.*\})', text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    return data.get("tool") or data.get("action"), data.get("args", {})
                except Exception:
                    pass
            return None

        tool_name = match.group(1).strip()
        raw_args = match.group(2).strip()

        if raw_args.startswith("{") and raw_args.endswith("}"):
            try:
                args = json.loads(raw_args)
                return tool_name, args
            except Exception:
                pass

        args = {}
        if "=" in raw_args:
            for pair in re.finditer(r'([a-zA-Z_]+)\s*=\s*["\']([^"\']*)["\']', raw_args):
                args[pair.group(1)] = pair.group(2)
        elif raw_args:
            clean_val = raw_args.strip("\"'")
            if tool_name in ["read_file", "list_dir"]:
                args["path"] = clean_val
            elif tool_name == "calculate":
                args["expression"] = clean_val
            elif tool_name == "run_command":
                args["command"] = clean_val

        return tool_name, args

    def execute_task(self, task: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Execute an autonomous task with ReAct loop.
        Returns final answer and trace of steps.
        """
        history: List[str] = [f"User Task: {task}"]
        steps_taken: List[Dict[str, Any]] = []

        if verbose:
            print(f"\n[TaskAgent] Starting task: {task}", flush=True)

        for step in range(1, self.max_steps + 1):
            context = "\n\n".join(history)
            response = self.run(context, max_new_tokens=300)

            if verbose:
                print(f"\n--- Step {step} ---")
                print(response, flush=True)

            # Check for action first so tools are always executed
            parsed = self._parse_action(response)
            if parsed:
                tool_name, tool_args = parsed
                if verbose:
                    print(f"[Executing Tool]: {tool_name}({tool_args})", flush=True)

                obs = self.call_tool(tool_name, **tool_args)
                obs_str = str(obs)
                if len(obs_str) > 1500:
                    obs_str = obs_str[:1500] + "... [truncated]"

                if verbose:
                    print(f"[Observation]: {obs_str}", flush=True)

                steps_taken.append({
                    "step": step,
                    "tool": tool_name,
                    "args": tool_args,
                    "observation": obs_str
                })

                # Truncate response in history up to the action line so hallucinated predictions are dropped
                action_idx = response.find("Action:")
                if action_idx != -1:
                    newline_after = response.find("\n", action_idx)
                    clean_turn = response[:newline_after] if newline_after != -1 else response
                else:
                    clean_turn = response

                history.append(clean_turn)
                history.append(f"Observation: {obs_str}")
                continue

            # If no action is called, check if final answer is reached
            if "Final Answer:" in response:
                final_part = response.split("Final Answer:")[-1].strip()
                steps_taken.append({"step": step, "type": "final_answer", "content": final_part})
                return {
                    "success": True,
                    "task": task,
                    "final_answer": final_part,
                    "steps": steps_taken
                }

            history.append(response)
            if step == self.max_steps:
                return {
                    "success": True,
                    "task": task,
                    "final_answer": response,
                    "steps": steps_taken
                }
            history.append("Observation: Please state your next Action or provide Final Answer.")

        return {
            "success": False,
            "task": task,
            "final_answer": "Task reached maximum step limit before producing Final Answer.",
            "steps": steps_taken
        }
