import hashlib
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from file_helper import human_size, get_folder, unique_destination
from chat_helper import chat_loop

BACKUP_DIR = Path("backups")
TRASH_NAME = "_trash"
PENDING = {"folder": None, "moves": []}          # a clean-up plan waiting for "confirm"

def all_files(folder):
    """Every file inside the folder (and sub-folders), except our own trash."""
    files = []
    for path in sorted(folder.rglob("*")):
        if path.is_file() and TRASH_NAME not in path.relative_to(folder).parts:
            files.append(path)
    return files

def file_hash(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def duplicate_groups(folder):
    """Group identical files. Cheap check first (size), exact check second (hash)."""
    by_size = {}
    for path in all_files(folder):
        size = path.stat().st_size
        if size > 0:
            by_size.setdefault(size, []).append(path)

    groups = []
    for paths in by_size.values():
        if len(paths) < 2:
            continue
        by_hash = {}
        for path in paths:
            by_hash.setdefault(file_hash(path), []).append(path)
        groups += [sorted(same) for same in by_hash.values() if len(same) > 1]
    return sorted(groups)

def find_duplicates(folder):
    path = get_folder(folder)
    groups = duplicate_groups(path)
    if not groups:
        return "No duplicate files found."
    lines, wasted = [], 0
    for number, group in enumerate(groups, start=1):
        size = group[0].stat().st_size
        wasted += size * (len(group) - 1)
        lines.append(f"Group {number} ({len(group)} identical files, {human_size(size)} each):")
        lines.append(f"  keep:      {group[0].relative_to(path)}")
        lines += [f"  duplicate: {other.relative_to(path)}" for other in group[1:]]
    lines.append(f"Space used by duplicates: {human_size(wasted)}")
    return "\n".join(lines)

def find_large(folder, min_mb=10):
    path = get_folder(folder)
    limit = float(min_mb) * 1024 * 1024
    big = sorted((p for p in all_files(path) if p.stat().st_size >= limit),
                 key=lambda p: p.stat().st_size, reverse=True)
    if not big:
        return f"No files of {min_mb} MB or more."
    return "\n".join(f"{human_size(p.stat().st_size):>9}  {p.relative_to(path)}" for p in big[:10])

def find_old(folder, days=365):
    path = get_folder(folder)
    cutoff = datetime.now() - timedelta(days=int(days))
    old = sorted((p for p in all_files(path) if datetime.fromtimestamp(p.stat().st_mtime) < cutoff),
                 key=lambda p: p.stat().st_mtime)
    if not old:
        return f"No files older than {days} days."
    return "\n".join(f"{datetime.fromtimestamp(p.stat().st_mtime):%Y-%m-%d}  {p.relative_to(path)}"
                     for p in old[:10])

def backup_folder(folder):
    path = get_folder(folder)
    if BACKUP_DIR.resolve() == path or BACKUP_DIR.resolve().is_relative_to(path):
        raise ValueError("Choose a folder that does not contain the 'backups' folder")
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target = unique_destination(BACKUP_DIR / f"{path.name}_{stamp}.zip")     # never overwrite
    archive = shutil.make_archive(str(target.with_suffix("")), "zip",
                                  root_dir=path.parent, base_dir=path.name)
    return f"Backup saved: {BACKUP_DIR / Path(archive).name} ({human_size(Path(archive).stat().st_size)})"

def plan_clean(folder):
    path = get_folder(folder)
    moves = []
    for group in duplicate_groups(path):
        for extra in group[1:]:                        # keep the first, move the rest
            destination = unique_destination(path / TRASH_NAME / extra.name)
            moves.append((str(extra), str(destination)))
    if not moves:
        return "No duplicates to clean."
    PENDING["folder"], PENDING["moves"] = str(path), moves
    lines = [f"  {Path(src).relative_to(path)}  ->  {TRASH_NAME}/" for src, _ in moves]
    return (f"PLAN: move {len(moves)} duplicate files to '{TRASH_NAME}' (nothing is deleted):\n"
            + "\n".join(lines)
            + "\nA backup is made first. Type 'confirm' to go ahead, or 'cancel'.")

def apply_clean():
    if not PENDING["moves"]:
        raise ValueError("There is no plan waiting. Type 'plan clean <folder>' first")
    backup_message = backup_folder(PENDING["folder"])        # the safety net comes first
    trash = Path(PENDING["folder"]) / TRASH_NAME
    trash.mkdir(exist_ok=True)
    for source, destination in PENDING["moves"]:
        shutil.move(source, destination)
    count = len(PENDING["moves"])
    PENDING["folder"], PENDING["moves"] = None, []
    return f"{backup_message}\nMoved {count} duplicate files to {trash.name}. Nothing was deleted."

def cancel_clean():
    PENDING["folder"], PENDING["moves"] = None, []
    return "Plan cancelled. Nothing was changed."

TOOLS = {
    "find_duplicates": find_duplicates,
    "find_large": find_large,
    "find_old": find_old,
    "backup_folder": backup_folder,
    "plan_clean": plan_clean,
    "apply_clean": apply_clean,
    "cancel_clean": cancel_clean,
}

HELP = ("Try: 'duplicates cleanup_practice', 'large cleanup_practice over 1', "
        "'old cleanup_practice over 365', 'backup cleanup_practice', "
        "'plan clean cleanup_practice', 'confirm', 'cancel'")

def cleanup_brain(goal, history):
    if history:
        return {"action": "finish", "answer": history[-1]["result"]}

    text = goal.strip()
    lower = text.lower()

    match = re.match(r"plan clean (.+)$", text, re.IGNORECASE)
    if match:
        return {"action": "plan_clean", "input": {"folder": match.group(1)}}

    match = re.match(r"duplicates (.+)$", text, re.IGNORECASE)
    if match:
        return {"action": "find_duplicates", "input": {"folder": match.group(1)}}

    match = re.match(r"large (.+?)(?: over (\d+(?:\.\d+)?))?$", text, re.IGNORECASE)
    if match:
        arguments = {"folder": match.group(1)}
        if match.group(2):
            arguments["min_mb"] = float(match.group(2))
        return {"action": "find_large", "input": arguments}

    match = re.match(r"old (.+?)(?: over (\d+))?$", text, re.IGNORECASE)
    if match:
        arguments = {"folder": match.group(1)}
        if match.group(2):
            arguments["days"] = int(match.group(2))
        return {"action": "find_old", "input": arguments}

    match = re.match(r"backup (.+)$", text, re.IGNORECASE)
    if match:
        return {"action": "backup_folder", "input": {"folder": match.group(1)}}

    if lower == "confirm":
        return {"action": "apply_clean"}
    if lower == "cancel":
        return {"action": "cancel_clean"}

    return {"action": "finish", "answer": HELP}

if __name__ == "__main__":
    chat_loop(cleanup_brain, TOOLS, "Cleanup and backup agent")
