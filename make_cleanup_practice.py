import os
import time
from pathlib import Path

folder = Path("cleanup_practice")
(folder / "photos").mkdir(parents=True, exist_ok=True)
(folder / "old_stuff").mkdir(exist_ok=True)

same = "Meeting notes: order 20 notebooks and 10 pens.\n"
(folder / "notes.txt").write_text(same, encoding="utf-8")
(folder / "notes_copy.txt").write_text(same, encoding="utf-8")
(folder / "photos" / "notes_backup.txt").write_text(same, encoding="utf-8")
(folder / "unique.txt").write_text("Only one copy of this file exists.\n", encoding="utf-8")
(folder / "photos" / "big_video.bin").write_bytes(b"0" * 2_000_000)      # about 2 MB

old = folder / "old_stuff" / "ancient_list.txt"
old.write_text("A very old list.\n", encoding="utf-8")
long_ago = time.time() - 800 * 24 * 3600                                  # about 800 days ago
os.utime(old, (long_ago, long_ago))

print(f"Created practice files in '{folder}'.")
