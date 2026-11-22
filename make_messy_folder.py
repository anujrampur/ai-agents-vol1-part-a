from pathlib import Path

NAMES = [
    "holiday1.jpg", "holiday2.png", "notes.txt", "invoice_oct.pdf", "budget.xlsx",
    "sales.csv", "song.mp3", "clip.mp4", "backup.zip", "script.py",
    "slides.pptx", "readme.md", "mystery_file",
]

folder = Path("messy_folder")
folder.mkdir(exist_ok=True)

for name in NAMES:
    content = f"Sample file: {name}\n"
    (folder / name).write_bytes(content.encode("utf-8"))

print(f"Created {len(NAMES)} practice files in '{folder}'.")