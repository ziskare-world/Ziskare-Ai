"""
Example 05: Autonomous AI Agents in Ziskare AI
==============================================
Demonstrating CodeAgent, SystemAgent, TaskAgent, and AgentOrchestrator.
All agents execute 100% locally on GPU/CPU with zero network overhead.
"""

from ziskare_ai.core import ZiskareAI
from agents import CodeAgent, SystemAgent, TaskAgent, AgentOrchestrator

print("=======================================================")
print("     Ziskare AI - Autonomous Agents Showcase")
print("=======================================================\n")

# 1. Initialize shared core AI engine (1 model in VRAM)
ai = ZiskareAI()

# -----------------------------------------------------
# 2. Code Agent: Generate & Review Code
# -----------------------------------------------------
print("\n>>> 1. Running CodeAgent (Software Engineering Specialist)...")
coder = CodeAgent(ai=ai)
code_res = coder.generate_code("Write an asynchronous Python function to ping an HTTP URL with timeout.")
print("Generated Code:\n", code_res)

# -----------------------------------------------------
# 3. System Agent: Hardware Telemetry & Health Diagnosis
# -----------------------------------------------------
print("\n>>> 2. Running SystemAgent (Site Reliability & Hardware Specialist)...")
sys_agent = SystemAgent(ai=ai)
diagnosis = sys_agent.diagnose()
print("System Health Diagnosis:\n", diagnosis)

# -----------------------------------------------------
# 4. Task Agent: Autonomous ReAct Tool Calling Loop
# -----------------------------------------------------
print("\n>>> 3. Running TaskAgent (Autonomous Tool Execution Loop)...")
tasker = TaskAgent(ai=ai)
task_result = tasker.execute_task("Check the current system hardware stats and tell me the total RAM.", verbose=True)
print("\nFinal Task Result:\n", task_result["final_answer"])

# -----------------------------------------------------
# 5. Agent Orchestrator: Dynamic Routing
# -----------------------------------------------------
print("\n>>> 4. Running AgentOrchestrator (Auto-Routing Dispatcher)...")
orchestrator = AgentOrchestrator(ai=ai)

sample_query = "Why might my disk drive fill up rapidly and how can I find large files on Windows?"
route = orchestrator.route_request(sample_query)
print(f"User Query: '{sample_query}'")
print(f"Auto-routed category: {route}")
outcome = orchestrator.run(sample_query)
print(f"Handled by: {outcome['agent']}\nResponse:\n{outcome['result']}")

print("\n=======================================================")
print("  All agents executed successfully offline!")
print("=======================================================")
