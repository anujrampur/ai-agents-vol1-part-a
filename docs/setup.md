# Setup guide

This takes about twenty minutes, and you do it once.

## 1. Install Python

Download Python 3.9 or newer from [python.org](https://www.python.org/downloads/).

- **Windows:** on the first screen of the installer, tick **"Add Python to PATH"**.
- **Mac:** use the installer from python.org (or Homebrew).
- **Linux:** Python is usually installed already. Check below.

Open a terminal and check:

```
python --version
```

On Mac and Linux you may need `python3 --version`. You should see 3.9 or a higher number. (The book writes `python`. Use `python3` if that is what works for you.)

**How to open a terminal.** Windows: open the Start menu, type `PowerShell` and press Enter. Mac: open the Terminal app. In Visual Studio Code: menu Terminal, then New Terminal.

## 2. Get the code

**Option A: download a ZIP.** On the repository page click the green **Code** button, then **Download ZIP**. Unzip it. On Windows, right-click the ZIP and choose **Extract All**.

**Option B: use Git.**

```
git clone <this repository's address>
cd <the folder that was created>
```

## 3. Go to the folder

In the terminal, move into the folder that holds `hello_agent.py`:

```
cd path\to\the\folder
```

Tip (Windows): open the folder in File Explorer, click the address bar, type `powershell` and press Enter. A terminal opens right there.

## 4. Run your first agent

```
python hello_agent.py
```

You should see `Final answer: The answer is 455`.

## 5. Optional libraries

```
pip install pypdf openpyxl tzdata
```

If `pip` is not found, use `python -m pip install pypdf openpyxl tzdata`.

- `pypdf`: Agent 17 can read PDF files.
- `openpyxl`: Agent 18 can read Excel files.
- `tzdata`: time zone data, needed by Agent 3 on some Windows installs.

## 6. Check everything

```
python run_all_agents.py
```

## Saving your own files correctly

- Save code with the ending `.py`. In Notepad choose "All files" in the Save box, or the file may become `.py.txt`.
- Use UTF-8 encoding (the default in most editors).
- Indent with 4 spaces, and do not mix tabs and spaces.

## Leaving a chat agent

Type `quit`. Ctrl+C also works.
