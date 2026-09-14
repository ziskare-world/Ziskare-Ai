"""
Example 03: Performance Metrics & Token Speed Benchmark
"""

from ziskare_ai import ZiskareAI

ai = ZiskareAI()

questions = [
    "What is photosynthesis?",
    "Why do leaves change color in autumn?",
    "What is the function of mitochondria?"
]

print("\n--- Ziskare AI Speed Benchmark ---\n")
for q in questions:
    result = ai.ask(q, return_metrics=True)
    print(f"Q: {q}")
    print(f"A: {result['answer']}")
    print(f"⏱️ Time: {result['time_taken']}s | Tokens: {result['tokens']} | Speed: {result['speed']} tok/s\n")
