"""Run every agent of Vol 1, Part A with scripted typing, and compare with the expected output.

Usage (from the folder that holds all the code files):
    python run_all_agents.py            compare with expected_outputs.json
    python run_all_agents.py --save     save your outputs as the new expected outputs

It works in a temporary copy of your folder, so your own files and data are never touched.
Inside this script the date is frozen at 15 November 2026, so dates are the same on every computer.
"""
import difflib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED = HERE / "expected_outputs.json"
FREEZE = (2026, 11, 15)                       # a Sunday
RESET = ["data", "drafts", "reports", "backups", "messy_folder", "cleanup_practice"]

def chat(*lines):
    return list(lines) + ["quit"]

# Each run: (title, setup scripts, program, typed lines, keep data from the previous run?)
RUNS = [
    ("Agent 1 Hello Agent", [], "hello_agent.py", None),
    ("Agent 2 Bill Calculator", [], "bill_agent.py", None),
    ("Agent 3 Weather and Time", [], "weather_time_agent.py", None),
    ("Agent 4 ReAct Reasoning", [], "react_agent.py", None),
    ("Agent 5 Short-Term Memory", [], "memory_agent.py", chat(
        "My name is Anuj", "My city is Rampur", "What is my name?",
        "What is my favourite colour?", "history")),
    ("Agent 6 Note-Taking", [], "notes_agent.py", chat(
        "note: Buy chart paper", "note: Call the printer about the bill", "show notes",
        "find chart", "delete note 1", "show notes")),
    ("Agent 7 To-Do and Reminder", [], "todo_agent.py", chat(
        "add task Pay the supplier due tomorrow", "add task Order chart paper due 2026-11-10",
        "add task Clean the shelf", "show tasks", "overdue", "done 2", "show tasks",
        "add task Test due next week")),
    ("Agent 8 Calendar", [], "calendar_agent.py", chat(
        "meeting Supplier visit on tomorrow at 09:00 for 120 minutes",
        "meeting Parent talk on tomorrow at 10:30 for 30 minutes",
        "meeting Parent talk on tomorrow at 11:00 for 30 minutes",
        "show events on tomorrow", "free slot on tomorrow for 45 minutes")),
    ("Agent 9 Converter", [], "converter_agent.py", chat(
        "convert 5 km to miles", "100 c to f", "2 kg in pounds", "50 usd to inr",
        "72 f to c", "5 km to kg", "3 parsec to km")),
    ("Agent 10 Daily Briefing", ["seed_demo.py"], "briefing_agent.py", None),
    ("Agent 11 Web Search", [], "search_agent.py", chat(
        "python lists", "how do AI agents save data", "sourdough recipes")),
    ("Agent 12 News Research", [], "news_agent.py", chat(
        "load sample_news.xml", "news about school", "news about school last 3 days",
        "news about cricket")),
    ("Agent 13 Web Scraping", [], "scraper_agent.py", chat(
        "load sample_shop.html", "title", "headings", "links", "text")),
    ("Agent 14 Price Tracker, day 1 (Rs 499)", [], "price_agent.py", chat(
        "track gel pens from sample_product.html target 450", "check gel pens")),
    ("Agent 14 Price Tracker, day 2 (Rs 459)", [], "price_agent.py", chat(
        "check gel pens"), {"keep": True, "price": 459, "day": 16}),
    ("Agent 14 Price Tracker, day 3 (Rs 429)", [], "price_agent.py", chat(
        "check gel pens", "history gel pens"), {"keep": True, "price": 429, "day": 17}),
    ("Agent 15 Fact-Checker", [], "factcheck_agent.py", chat(
        "The Taj Mahal is in Agra.", "The Taj Mahal is in Delhi.",
        "Mount Everest is 7000 metres tall.", "Python was created by James Gosling.",
        "Python is a snake.")),
    ("Agent 16 File Organizer", ["make_messy_folder.py"], "organizer_agent.py", chat(
        "scan messy_folder", "plan messy_folder", "confirm", "scan messy_folder", "undo")),
    ("Agent 17 Document Q&A (text and PDF)", [], "doc_agent.py", chat(
        "load sample_policy.txt", "ask when is the shop open",
        "ask can I return a used notebook", "ask do you sell mobile phones",
        "load sample_policy.pdf", "ask what is the delivery charge")),
    ("Agent 18 CSV and Excel Analyst", [], "table_agent.py", chat(
        "load sample_sales.csv", "describe", "sum revenue", "average price",
        "revenue by category", "top 3 revenue", "filter quantity > 25", "sum colour",
        "load sample_sales.xlsx", "sum revenue")),
    ("Agent 19 Report Writer", [], "report_agent.py", chat(
        "report sample_sales.csv titled Weekly Sales Report", "show report")),
    ("Agent 20 Cleanup and Backup", ["make_cleanup_practice.py"], "cleanup_agent.py", chat(
        "duplicates cleanup_practice", "large cleanup_practice over 1",
        "old cleanup_practice over 365", "plan clean cleanup_practice", "confirm",
        "duplicates cleanup_practice")),
    ("Agent 21 Email Summarizer", ["make_sample_inbox.py"], "email_agent.py", chat(
        "load sample_inbox", "inbox", "digest", "summary 7", "summary 6", "summary 2")),
    ("Agent 22 Reply Drafting", ["make_sample_inbox.py"], "reply_agent.py", chat(
        "load sample_inbox", "draft 6 quote formal", "draft 3 later short", "draft 2 confirm")),
    ("Agent 23 Meeting Scheduler", ["make_sample_inbox.py"], "scheduler_agent.py", chat(
        "load sample_inbox", "schedule 4", "confirm",
        "book Supplier visit on tuesday at 15:45 for 60 minutes", "schedule 1")),
    ("Agent 24 Shop Support", [], "support_agent.py", chat(
        "hello", "when is the shop open", "order ORD-1001", "order ORD-1001 phone 4321",
        "order ORD-1001 phone 0000", "do you sell mobile phones",
        "what about quantum computers", "you are useless and I am angry")),
    ("Agent 25 Personal Assistant (practice chat)", [], "assistant_bot.py", chat(
        "/help", "/note Buy chart paper", "/task Pay the supplier due today", "/today",
        "/convert 5 km to miles", "hello", "/dance")),
]

def run_python(work, code_or_script, text="", freeze=FREEZE, is_script=False):
    if is_script:
        command = [sys.executable, "-X", "utf8", code_or_script]
    else:
        command = [sys.executable, "-X", "utf8", "-c", code_or_script]
    done = subprocess.run(command, cwd=work, input=text, capture_output=True, text=True,
                          encoding="utf-8", timeout=120)
    return done.stdout + done.stderr

def wrapper(script, freeze):
    year, month, day = freeze
    return (
        "import runpy, sys\n"
        "from datetime import date\n"
        "import dates_helper\n"
        f"dates_helper.today = lambda: date({year}, {month}, {day})\n"
        f"sys.argv = [{script!r}]\n"
        f"runpy.run_path({script!r}, run_name='__main__')\n"
    )

def normalise(text):
    text = text.replace("\r\n", "\n").replace("\\", "/")
    text = re.sub(r"\b\d{1,2}:\d{2} [AP]M\b", "HH:MM AM", text)             # a live clock time
    text = re.sub(r"\d{8}-\d{6}", "YYYYMMDD-HHMMSS", text)                  # time stamps in backup names
    text = re.sub(r"\d{4}-\d{2}-\d{2}(?=\s+old_stuff/)", "<DATE>", text)    # age of the practice file
    text = re.sub(r"(\.zip) \([\d.]+ [KMG]?B\)", r"\1 (<SIZE>)", text)      # size of a backup zip
    return text

def make_transcript(output, typed):
    """Put the typed lines back next to the replies, so the result reads like a chat."""
    if typed is None or "You: " not in output and "Bot: " not in output:
        return output
    marker = "You: "
    parts = output.split(marker)
    lines = [parts[0].rstrip("\n")]
    for number, reply in enumerate(parts[1:]):
        typed_line = typed[number] if number < len(typed) else ""
        lines.append(f"You: {typed_line}")
        if reply.strip():
            lines.append(reply.rstrip("\n"))
    return "\n".join(lines)

def main():
    save = "--save" in sys.argv
    work = Path(tempfile.mkdtemp(prefix="agents_check_"))
    for item in HERE.iterdir():                    # work on a copy
        if item.is_file() and item.suffix != ".json" and item.name != Path(__file__).name:
            shutil.copy(item, work)
        elif item.is_dir() and item.name == "sample_inbox":
            shutil.copytree(item, work / item.name)

    results, readable = {}, []
    for entry in RUNS:
        title, setups, script, typed = entry[:4]
        options = entry[4] if len(entry) > 4 else {}
        if not options.get("keep"):
            for name in RESET:
                shutil.rmtree(work / name, ignore_errors=True)
        for setup in setups:
            run_python(work, setup, is_script=True)
        if options.get("price"):
            page = (work / "sample_product.html").read_text(encoding="utf-8")
            page = re.sub(r"(<p class=\"price\">Rs\. )[\d,.]+(</p>)", rf"\g<1>{options['price']}\2", page)
            (work / "sample_product.html").write_text(page, encoding="utf-8")
        freeze = (FREEZE[0], FREEZE[1], options.get("day", FREEZE[2]))
        text = "\n".join(typed) + "\n" if typed else ""
        output = run_python(work, wrapper(script, freeze), text)
        transcript = normalise(make_transcript(output, typed))
        results[title] = transcript
        readable.append(f"{'=' * 70}\n{title}   (run: python {script})\n{'=' * 70}\n{transcript}\n")

    shutil.rmtree(work, ignore_errors=True)
    with open(HERE / "my_outputs.txt", "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(readable))

    if save or not EXPECTED.exists():
        with open(EXPECTED, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(results, indent=1, ensure_ascii=False))
        print(f"Saved {len(results)} outputs as the expected outputs.")
        return

    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    problems = []
    print(f"Python {sys.version.split()[0]} on {sys.platform}\n")
    for title, got in results.items():
        if got == expected.get(title):
            print(f"  OK     {title}")
        else:
            print(f"  DIFF   {title}")
            problems.append((title, expected.get(title, ""), got))
    if problems:
        with open(HERE / "differences.txt", "w", encoding="utf-8", newline="\n") as handle:
            for title, want, got in problems:
                handle.write(f"### {title}\n")
                handle.writelines(difflib.unified_diff(
                    want.splitlines(True), got.splitlines(True), "expected", "yours"))
                handle.write("\n")
        print(f"\n{len(problems)} agent(s) differ. See differences.txt (and my_outputs.txt).")
        print("Your full outputs were written to my_outputs.txt")
        sys.exit(1)
    else:
        print("\nAll agents match the expected outputs.")
    print("Your full outputs were written to my_outputs.txt")

if __name__ == "__main__":
    main()
