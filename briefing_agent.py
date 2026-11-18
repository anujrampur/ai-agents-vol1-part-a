from agent_core import run_agent
from dates_helper import today
from weather_time_agent import get_weather
from calendar_agent import list_events
from todo_agent import list_tasks

CITY = "delhi"

TOOLS = {
    "get_weather": get_weather,
    "list_events": list_events,
    "list_tasks": list_tasks,
}

# The plan is data: (heading, tool name, tool input)
PLAN = [
    ("Weather", "get_weather", {"city": CITY}),
    ("Today's events", "list_events", {"day": "today"}),
    ("Tasks due today", "list_tasks", {"view": "today"}),
    ("Overdue tasks", "list_tasks", {"view": "overdue"}),
]

def briefing_brain(goal, history):
    step = len(history)

    if step < len(PLAN):                       # still gathering information
        _, action, inputs = PLAN[step]
        return {"action": action, "input": inputs}

    lines = [f"Good morning! Today is {today():%A, %d %B %Y}.", ""]
    for (heading, _, _), done in zip(PLAN, history):
        result = done["result"]
        if result.startswith("Error:"):        # one broken tool must not spoil the briefing
            result = "(not available right now)"
        lines.append(heading + ":")
        lines.append(result)
        lines.append("")
    return {"action": "finish", "answer": "\n".join(lines).strip()}

if __name__ == "__main__":
    print(run_agent("morning briefing", briefing_brain, TOOLS, verbose=False))
