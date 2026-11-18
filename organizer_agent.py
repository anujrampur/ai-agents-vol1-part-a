import re
import shutil
from datetime import datetime
from pathlib import Path
from file_helper import human_size, get_folder, unique_destination
from storage import load_json, save_json
from chat_helper import chat_loop

LOG_FILE = "organizer_log.json"

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt"},
    "Spreadsheets": {".xls", ".xlsx", ".csv"},
    "Presentations": {".ppt", ".pptx"},
    "Audio": {".mp3", ".wav", ".m4a"},
    "Video": {".mp4", ".mkv", ".avi", ".mov"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".py", ".js", ".html", ".css", ".json", ".ipynb"},
}

PENDING = {"folder": None, "moves": []}      # a plan waiting for your "confirm"

def category_of(path):
    suffix = path.suffix.lower()
    for category, suffixes in CATEGORIES.items():
        if suffix in suffixes:
            return category
    return "Other"

def plural(number, word):
    return word if number == 1 else word + "s"

def top_level_files(folder):
    return sorted(p for p in folder.iterdir() if p.is_file() and not p.name.startswith("."))

def scan_folder(folder):
    path = get_folder(folder)
    files = top_level_files(path)
    if not files:
        return "That folder has no files to organise."
    counts, sizes = {}, {}
    for file in files:
        category = category_of(file)
        counts[category] = counts.get(category, 0) + 1
        sizes[category] = sizes.get(category, 0) + file.stat().st_size
    lines = [f"{category}: {counts[category]} {plural(counts[category], 'file')} "
             f"({human_size(sizes[category])})" for category in sorted(counts)]
    return f"{len(files)} {plural(len(files), 'file')} in {path.name}:\n" + "\n".join(lines)

def plan_organize(folder):
    path = get_folder(folder)
    moves = []
    for file in top_level_files(path):
        destination = unique_destination(path / category_of(file) / file.name)
        moves.append((str(file), str(destination)))
    if not moves:
        return "Nothing to organise."
    PENDING["folder"], PENDING["moves"] = str(path), moves
    lines = []
    for src, dst in moves:
        line = f"{Path(src).name}  ->  {Path(dst).parent.name}/"
        if Path(dst).name != Path(src).name:
            line += f"  (saved as {Path(dst).name} so nothing is overwritten)"
        lines.append(line)
    return ("PLAN (nothing has been moved yet):\n" + "\n".join(lines) +
            "\nType 'confirm' to apply this plan, or 'cancel'.")

def apply_plan():
    if not PENDING["moves"]:
        raise ValueError("There is no plan waiting. Type 'plan <folder>' first")
    done = []
    for source, destination in PENDING["moves"]:
        Path(destination).parent.mkdir(exist_ok=True)
        shutil.move(source, destination)
        done.append([source, destination])
    log = load_json(LOG_FILE, [])
    log.append({"time": datetime.now().isoformat(timespec="seconds"), "moves": done})
    save_json(LOG_FILE, log)
    PENDING["folder"], PENDING["moves"] = None, []
    return f"Moved {len(done)} files. Type 'undo' to put them back."

def cancel_plan():
    PENDING["folder"], PENDING["moves"] = None, []
    return "Plan cancelled. Nothing was changed."

def undo_last():
    log = load_json(LOG_FILE, [])
    if not log:
        return "There is nothing to undo."
    batch = log.pop()
    restored = 0
    for source, destination in reversed(batch["moves"]):
        if Path(destination).exists():
            Path(source).parent.mkdir(exist_ok=True)
            shutil.move(destination, unique_destination(source))
            restored += 1
        folder = Path(destination).parent
        if folder.exists() and not any(folder.iterdir()):
            folder.rmdir()                      # remove the empty category folder
    save_json(LOG_FILE, log)
    return f"Put back {restored} files."

TOOLS = {
    "scan_folder": scan_folder,
    "plan_organize": plan_organize,
    "apply_plan": apply_plan,
    "cancel_plan": cancel_plan,
    "undo_last": undo_last,
}

HELP = "Try: 'scan messy_folder', 'plan messy_folder', 'confirm', 'cancel', 'undo'"

def organizer_brain(goal, history):
    if history:
        return {"action": "finish", "answer": history[-1]["result"]}

    text = goal.strip()
    lower = text.lower()

    match = re.match(r"scan (.+)$", text, re.IGNORECASE)
    if match:
        return {"action": "scan_folder", "input": {"folder": match.group(1)}}

    match = re.match(r"(?:plan|organi[sz]e) (.+)$", text, re.IGNORECASE)
    if match:
        return {"action": "plan_organize", "input": {"folder": match.group(1)}}

    if lower == "confirm":
        return {"action": "apply_plan"}
    if lower == "cancel":
        return {"action": "cancel_plan"}
    if lower == "undo":
        return {"action": "undo_last"}

    return {"action": "finish", "answer": HELP}

if __name__ == "__main__":
    chat_loop(organizer_brain, TOOLS, "File organizer agent")
