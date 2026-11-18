from pathlib import Path

def human_size(num_bytes):
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} B" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024

def get_folder(folder):
    """Turn text into a safe folder path, or raise a clear error."""
    path = Path(folder).expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise ValueError(f"Folder not found: {folder}")
    if path == Path(path.anchor) or path == Path.home():
        raise ValueError("For safety, choose a sub-folder, not a whole drive or your home folder")
    return path

def unique_destination(destination):
    """Never overwrite: if the name is taken, add (1), (2), ... to it."""
    destination = Path(destination)
    if not destination.exists():
        return destination
    counter = 1
    while True:
        candidate = destination.with_name(f"{destination.stem} ({counter}){destination.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1
