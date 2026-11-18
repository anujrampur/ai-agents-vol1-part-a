import json
from pathlib import Path

DATA_DIR = Path("data")

def load_json(filename, default):
    path = DATA_DIR / filename
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default

def save_json(filename, data):
    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / filename
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
