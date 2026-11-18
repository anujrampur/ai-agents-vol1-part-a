def run_agent(goal, brain, tools, max_steps=8, verbose=True):
    history = []

    for step in range(1, max_steps + 1):
        decision = brain(goal, history)                  # THINK
        if verbose:
            if "thought" in decision:
                print(f"Step {step} Thought: {decision['thought']}")
            print(f"Step {step} Action: {decision['action']} {decision.get('input', '')}")

        if decision["action"] == "finish":               # STOP
            return decision["answer"]

        tool = tools.get(decision["action"])             # ACT
        if tool is None:
            result = f"Error: unknown tool {decision['action']}"
        else:
            try:
                result = tool(**decision.get("input", {}))
            except Exception as error:
                result = f"Error: {error}"

        if verbose:
            print(f"Step {step} Observation: {result}")   # OBSERVE
        history.append({
            "action": decision["action"],
            "input": decision.get("input", {}),
            "result": result,
        })

    return "Stopped: too many steps."
