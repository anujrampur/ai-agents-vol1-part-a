from agent_core import run_agent
from hello_agent import calculator

def check_percent(percent):
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")

def apply_discount(amount, percent):
    check_percent(percent)
    return round(amount - amount * percent / 100, 2)

def add_gst(amount, percent):
    check_percent(percent)
    return round(amount + amount * percent / 100, 2)

TOOLS = {
    "calculator": calculator,
    "apply_discount": apply_discount,
    "add_gst": add_gst,
}

def bill_brain(goal, history):
    # If the last tool failed, its result is an error message (a string).
    if history and isinstance(history[-1]["result"], str):
        return {"action": "finish",
                "answer": f"Could not complete the bill. {history[-1]['result']}"}

    step = len(history)

    if step == 0:
        expression = " + ".join(f"{qty} * {price}" for qty, price in goal["items"])
        return {"action": "calculator", "input": {"expression": expression}}

    if step == 1:
        return {"action": "apply_discount",
                "input": {"amount": history[-1]["result"],
                          "percent": goal["discount_percent"]}}

    if step == 2:
        return {"action": "add_gst",
                "input": {"amount": history[-1]["result"],
                          "percent": goal["gst_percent"]}}

    return {"action": "finish", "answer": f"Final bill: Rs {history[-1]['result']}"}

if __name__ == "__main__":
    goal = {
        "items": [(3, 40), (2, 10)],
        "discount_percent": 10,
        "gst_percent": 12,
    }
    print("Final answer:", run_agent(goal, bill_brain, TOOLS))
