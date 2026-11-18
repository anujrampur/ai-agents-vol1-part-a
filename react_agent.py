import re
from agent_core import run_agent
from hello_agent import calculator

PRICES = {"notebook": 40, "pen": 10, "geometry box": 85}

def lookup_price(item):
    if item not in PRICES:
        raise ValueError(f"No price found for {item}")
    return PRICES[item]

TOOLS = {"lookup_price": lookup_price, "calculator": calculator}

def react_brain(goal, history):
    wanted = re.findall(r"(\d+)\s+(notebook|pen|geometry box)", goal.lower())
    if not wanted:
        return {"thought": "I cannot find any known items in the question.",
                "action": "finish",
                "answer": "Please ask about notebooks, pens or geometry boxes."}

    # What prices do we already know?
    known = {step["input"]["item"]: step["result"]
             for step in history if step["action"] == "lookup_price"}

    # Is any price still missing?
    for qty, item in wanted:
        if item not in known:
            return {"thought": f"I need the price of {item} first.",
                    "action": "lookup_price",
                    "input": {"item": item}}

    # All prices known. Has the total been calculated?
    if not any(step["action"] == "calculator" for step in history):
        expression = " + ".join(f"{qty} * {known[item]}" for qty, item in wanted)
        return {"thought": "I have all the prices. Now I can calculate the total.",
                "action": "calculator",
                "input": {"expression": expression}}

    return {"thought": "I have the total, so I can answer.",
            "action": "finish",
            "answer": f"The total cost is Rs {history[-1]['result']}."}

if __name__ == "__main__":
    question = "What is the total cost of 12 notebooks and 5 pens?"
    print("Final answer:", run_agent(question, react_brain, TOOLS))
