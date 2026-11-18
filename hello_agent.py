import ast
import operator
import re

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

def calculator(expression):
    """Safely calculate a simple arithmetic expression."""
    def evaluate(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](evaluate(node.left), evaluate(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -evaluate(node.operand)
        raise ValueError("Unsupported expression")

    tree = ast.parse(expression, mode="eval")
    return evaluate(tree.body)

TOOLS = {"calculator": calculator}

def demo_brain(goal, history):
    if history:
        last = history[-1]
        return {"action": "finish", "answer": f"The answer is {last['result']}"}

    match = re.search(r"[\d\(][\d\.\s\+\-\*/\(\)]*", goal)
    if match:
        return {"action": "calculator", "input": match.group().strip()}

    return {"action": "finish", "answer": "I need a calculation to work on."}

def run_agent(goal, brain=demo_brain, max_steps=5):
    history = []

    for step in range(1, max_steps + 1):
        decision = brain(goal, history)
        print(f"Step {step}: Thought -> {decision}")

        if decision["action"] == "finish":
            return decision["answer"]

        tool = TOOLS.get(decision["action"])
        if tool is None:
            result = f"Error: unknown tool {decision['action']}"
        else:
            try:
                result = tool(decision["input"])
            except Exception as error:
                result = f"Error: {error}"

        print(f"Step {step}: Observation -> {result}")
        history.append({
            "action": decision["action"],
            "input": decision.get("input"),
            "result": result,
        })

    return "Stopped: too many steps."

if __name__ == "__main__":
    goal = "Ravi sold items worth 250 + 130 + 75 rupees today. What is the total?"
    answer = run_agent(goal)
    print("Final answer:", answer)
