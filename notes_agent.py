import re
from storage import load_json, save_json
from chat_helper import chat_loop

FILE = "notes.json"

def add_note(text):
    if not text.strip():
        raise ValueError("A note cannot be empty")
    notes = load_json(FILE, [])
    next_id = max((note["id"] for note in notes), default=0) + 1
    notes.append({"id": next_id, "text": text.strip()})
    save_json(FILE, notes)
    return f"Saved note {next_id}: {text.strip()}"

def list_notes():
    notes = load_json(FILE, [])
    if not notes:
        return "You have no notes yet."
    return "\n".join(f"{note['id']}. {note['text']}" for note in notes)

def search_notes(keyword):
    notes = load_json(FILE, [])
    found = [note for note in notes if keyword.lower() in note["text"].lower()]
    if not found:
        return f"No notes contain '{keyword}'."
    return "\n".join(f"{note['id']}. {note['text']}" for note in found)

def delete_note(note_id):
    notes = load_json(FILE, [])
    remaining = [note for note in notes if note["id"] != note_id]
    if len(remaining) == len(notes):
        raise ValueError(f"No note with id {note_id}")
    save_json(FILE, remaining)
    return f"Deleted note {note_id}."

TOOLS = {
    "add_note": add_note,
    "list_notes": list_notes,
    "search_notes": search_notes,
    "delete_note": delete_note,
}

HELP = "Try: 'note: buy chart paper', 'show notes', 'find chart', 'delete note 1'"

def notes_brain(goal, history):
    if history:
        return {"action": "finish", "answer": history[-1]["result"]}

    text = goal.strip()
    lower = text.lower()

    if lower.startswith("note:"):
        return {"action": "add_note", "input": {"text": text[5:]}}

    if lower in ("show notes", "list notes"):
        return {"action": "list_notes"}

    match = re.match(r"find (.+)", lower)
    if match:
        return {"action": "search_notes", "input": {"keyword": match.group(1)}}

    match = re.match(r"delete note (\d+)", lower)
    if match:
        return {"action": "delete_note", "input": {"note_id": int(match.group(1))}}

    return {"action": "finish", "answer": HELP}

if __name__ == "__main__":
    chat_loop(notes_brain, TOOLS, "Note-taking agent")
