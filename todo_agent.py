import re
from storage import load_json, save_json
from dates_helper import parse_date, today
from chat_helper import chat_loop

FILE = "tasks.json"

def add_task(title, due=None):
    if not title.strip():
        raise ValueError("A task needs a title")
    due_date = parse_date(due) if due else None
    tasks = load_json(FILE, [])
    next_id = max((task["id"] for task in tasks), default=0) + 1
    tasks.append({"id": next_id, "title": title.strip(), "due": due_date, "done": False})
    save_json(FILE, tasks)
    extra = f" (due {due_date})" if due_date else ""
    return f"Added task {next_id}: {title.strip()}{extra}"

def complete_task(task_id):
    tasks = load_json(FILE, [])
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            save_json(FILE, tasks)
            return f"Marked task {task_id} as done: {task['title']}"
    raise ValueError(f"No task with id {task_id}")

def list_tasks(view="pending"):
    tasks = load_json(FILE, [])
    now = today().isoformat()

    if view == "pending":
        chosen = [t for t in tasks if not t["done"]]
    elif view == "done":
        chosen = [t for t in tasks if t["done"]]
    elif view == "today":
        chosen = [t for t in tasks if not t["done"] and t["due"] == now]
    elif view == "overdue":
        chosen = [t for t in tasks if not t["done"] and t["due"] and t["due"] < now]
    else:
        raise ValueError("view must be pending, done, today or overdue")

    if not chosen:
        names = {"pending": "pending tasks", "done": "completed tasks",
                 "today": "tasks due today", "overdue": "overdue tasks"}
        return f"No {names[view]}."

    lines = []
    for task in chosen:
        mark = "x" if task["done"] else " "
        due = f" (due {task['due']})" if task["due"] else ""
        lines.append(f"{task['id']}. [{mark}] {task['title']}{due}")
    return "\n".join(lines)

TOOLS = {
    "add_task": add_task,
    "complete_task": complete_task,
    "list_tasks": list_tasks,
}

HELP = ("Try: 'add task pay supplier due tomorrow', 'show tasks', "
        "'what is due today', 'overdue', 'done 1'")

def todo_brain(goal, history):
    if history:
        return {"action": "finish", "answer": history[-1]["result"]}

    text = goal.strip()
    lower = text.lower()

    match = re.match(r"add task (.+?)(?: due (.+))?$", text, re.IGNORECASE)
    if match:
        return {"action": "add_task",
                "input": {"title": match.group(1), "due": match.group(2)}}

    match = re.match(r"(?:done|complete task) (\d+)", lower)
    if match:
        return {"action": "complete_task", "input": {"task_id": int(match.group(1))}}

    if lower in ("show tasks", "show pending"):
        return {"action": "list_tasks", "input": {"view": "pending"}}
    if lower == "show done":
        return {"action": "list_tasks", "input": {"view": "done"}}
    if "due today" in lower:
        return {"action": "list_tasks", "input": {"view": "today"}}
    if "overdue" in lower:
        return {"action": "list_tasks", "input": {"view": "overdue"}}

    return {"action": "finish", "answer": HELP}

if __name__ == "__main__":
    chat_loop(todo_brain, TOOLS, "To-do and reminder agent")
