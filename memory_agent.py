import re
from agent_core import run_agent

class Memory:
    def __init__(self, max_turns=6):
        self.facts = {}
        self.turns = []
        self.max_turns = max_turns

    def remember(self, key, value):
        self.facts[key] = value
        return f"Okay, I will remember your {key}: {value}."

    def recall(self, key):
        if key not in self.facts:
            return f"I do not know your {key} yet."
        return f"Your {key} is {self.facts[key]}."

    def add_turn(self, role, text):
        self.turns.append((role, text))
        self.turns = self.turns[-self.max_turns:]

memory = Memory()
TOOLS = {"remember": memory.remember, "recall": memory.recall}

TOPICS = "name|city|favourite colour"

def memory_brain(goal, history):
    if history:   # a tool already ran, so report its result
        return {"action": "finish", "answer": history[-1]["result"]}

    text = goal.lower().strip().rstrip("?.!")

    match = re.match(rf"my ({TOPICS}) is (.+)", text)
    if match:
        return {"action": "remember",
                "input": {"key": match.group(1), "value": match.group(2).title()}}

    match = re.match(rf"what is my ({TOPICS})", text)
    if match:
        return {"action": "recall", "input": {"key": match.group(1)}}

    return {"action": "finish",
            "answer": "Try: 'My name is Asha' or 'What is my name?'"}

def chat():
    print("Chat with the memory agent. Type 'history' to see memory, 'quit' to stop.")
    while True:
        try:
            user = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break
        if user.lower() == "quit":
            break
        if user.lower() == "history":
            print("Facts:", memory.facts)
            print("Recent turns:", memory.turns)
            continue

        memory.add_turn("user", user)
        answer = run_agent(user, memory_brain, TOOLS, verbose=False)
        memory.add_turn("agent", answer)
        print("Agent:", answer)

if __name__ == "__main__":
    chat()
