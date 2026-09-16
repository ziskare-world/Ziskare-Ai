"""
Benchmark & Quality Test for Ziskare AI Agents
==============================================
Runs live end-to-end evaluation across CodeAgent, SystemAgent, TaskAgent, and AgentOrchestrator.
Measures latency, token speed, and answer quality.
"""

import time
from ziskare_ai.core import ZiskareAI
from ziskare_ai.agents import CodeAgent, SystemAgent, TaskAgent, AgentOrchestrator

print("================================================================")
print("       ZISKARE AI - AGENTS LIVE PERFORMANCE & QUALITY TEST      ")
print("================================================================\n")

# 1. Initialize shared core engine
start = time.perf_counter()
ai = ZiskareAI()
init_time = time.perf_counter() - start
print(f"[*] Shared Engine Ready in {init_time:.2f}s on {ai.model.device}\n")

results = {}

# -------------------------------------------------------------
# TEST 1: CodeAgent - Code Generation & Bug Fixing
# -------------------------------------------------------------
print("[TEST 1/4] Testing CodeAgent (Generation & Debugging)...")
coder = CodeAgent(ai=ai)

t0 = time.perf_counter()
code_out = coder.generate_code("A Python function that checks if a string is a palindrome ignoring case and spaces.")
t_gen = round(time.perf_counter() - t0, 2)
print(f"  Code Generation ({t_gen}s):\n{code_out}\n")

buggy_code = """
def calculate_average(nums):
    total = sum(nums)
    return total / len(nums)
# Fails when nums is empty
"""
t0 = time.perf_counter()
debug_out = coder.debug_code(buggy_code, error_message="ZeroDivisionError when nums=[]")
t_dbg = round(time.perf_counter() - t0, 2)
print(f"  Bug Fixing ({t_dbg}s):\n{debug_out}\n")

results["CodeAgent"] = {"generate_sec": t_gen, "debug_sec": t_dbg}

# -------------------------------------------------------------
# TEST 2: SystemAgent - Live PC Diagnostics & SRE
# -------------------------------------------------------------
print("[TEST 2/4] Testing SystemAgent (Live Telemetry & Diagnostics)...")
sys_agent = SystemAgent(ai=ai)

t0 = time.perf_counter()
diag_out = sys_agent.diagnose()
t_diag = round(time.perf_counter() - t0, 2)
print(f"  Live System Health Diagnosis ({t_diag}s):\n{diag_out}\n")

results["SystemAgent"] = {"diagnose_sec": t_diag}

# -------------------------------------------------------------
# TEST 3: TaskAgent - Multi-Step ReAct Tool Execution
# -------------------------------------------------------------
print("[TEST 3/4] Testing TaskAgent (Autonomous Tool Loop)...")
tasker = TaskAgent(ai=ai, max_steps=4)

t0 = time.perf_counter()
# Task requiring math tool
task_out = tasker.execute_task("Calculate 128 multiplied by 16 minus 48", verbose=True)
t_task = round(time.perf_counter() - t0, 2)
print(f"\n  Task Result ({t_task}s): {task_out['final_answer']}\n")

results["TaskAgent"] = {"task_sec": t_task, "success": task_out.get("success")}

# -------------------------------------------------------------
# TEST 4: AgentOrchestrator - Classification & Routing
# -------------------------------------------------------------
print("[TEST 4/4] Testing AgentOrchestrator (Auto-Routing)...")
orch = AgentOrchestrator(ai=ai)

queries = [
    ("Write a fast SQL query to find top 5 customers", "code"),
    ("My laptop CPU is overheating, what should I check?", "system"),
    ("Calculate (450 + 550) * 0.18", "task")
]

correct_routes = 0
for q, expected in queries:
    routed = orch.route_request(q)
    match = (routed == expected)
    if match:
        correct_routes += 1
    print(f"  Query: '{q}' -> Routed to: {routed} (Expected: {expected}) [{'PASS' if match else 'CHECK'}]")

results["Orchestrator"] = {"routing_accuracy": f"{correct_routes}/{len(queries)}"}

print("\n================================================================")
print("                   BENCHMARK TEST SUMMARY                       ")
print("================================================================")
for k, v in results.items():
    print(f"  - {k}: {v}")
print("================================================================")
