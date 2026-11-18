# Contributing

Thank you for using this repository. It is the companion code of a book, so the files must stay the same as the programs printed in the book. For that reason:

- **Reporting a problem is the most useful thing you can do.** Please open an [Issue](../../issues/new/choose) and use the bug report form.
- **Pull requests** are welcome for small fixes, such as a typo or a clear bug. Please do not send large changes or new features, because they would no longer match the book.
- A good fix keeps the code simple and readable, because the readers are beginners.

## Before you open an issue

1. Run the check script in a fresh folder: `python run_all_agents.py`
2. Note your **Python version** (`python --version`), your **operating system**, the **agent number** and the **exact command** you typed.
3. Copy the **full error message**, not only the last line.

## Before you send a pull request

- `python run_all_agents.py` must print `OK` for every agent.
- Keep the same style: plain Python, only the standard library (except the optional `pypdf` and `openpyxl`), and clear names.
- Do not add real personal data, passwords or tokens to any file.
