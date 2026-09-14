"""
Example 02: Multi-Turn Conversation (Preserving Context)
"""

from ziskare_ai import ZiskareAI

ai = ZiskareAI()

print("--- Multi-Turn Conversation ---")
r1, _ = ai.chat("I live in New Delhi.")
print("You: I live in New Delhi.")
print(f"Ziskare AI: {r1}\n")

r2, _ = ai.chat("What is the climate like where I live?")
print("You: What is the climate like where I live?")
print(f"Ziskare AI: {r2}\n")

# Reset memory
ai.reset()
print("Context reset.")
