from ziskare_ai import ZiskareAI

ai = ZiskareAI()

# 1. Single direct question
answer = ai.ask("Explain Docker in one line.")
print("Ziskare AI:", answer)

# 2. Multi-turn conversation with memory
reply, stats = ai.chat("Remember: my user id is 402.")
reply, stats = ai.chat("What was my user id?")
print("Ziskare AI:", reply)

# 3. Getting speed & tokens
result = ai.ask("Why is the sky blue?", return_metrics=True)
print("Ziskare AI:", result["answer"])
print(f"⏱️ Time: {result['time_taken']}s | Speed: {result['speed']} tok/s")
