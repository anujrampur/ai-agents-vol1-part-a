# Python + AI: Build 100 AI Agents

### Volume 1, Part A: Agents 1 to 25

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Agents: 25](https://img.shields.io/badge/agents-25-green.svg)
![Standard library only](https://img.shields.io/badge/dependencies-none%20required-lightgrey.svg)

<!-- When you have the cover image, save it as docs/images/cover.png and remove the comment marks around the next line:
<img src="docs/images/cover.png" width="240" alt="Book cover: Python + AI, Build 100 AI Agents">
-->

The companion code of the book **Python + AI: Build 100 AI Agents, Volume 1, Part A** by **Anuj Kumar Saxena**.

You start with a calculator that thinks in a loop, and in 25 chapters you grow it into a personal assistant that reads email, books meetings, answers customers and replies to you on your phone. Every chapter begins with a story, builds one agent step by step, and ends with a quiz, exercises and interview questions.

Everything in this part runs **on your own computer, for free**. You need no account, no password, no payment and no internet connection for the main exercises.

> The best way to learn is to type the code yourself from the book. Use these files to compare your work, or to get unstuck.

## Contents

- [Quick start](#quick-start)
- [Check that everything works](#check-that-everything-works)
- [The 25 agents](#the-25-agents)
- [Practice folders and safety](#practice-folders-and-safety)
- [Repository layout](#repository-layout)
- [Troubleshooting](#troubleshooting)
- [The book series](#the-book-series)
- [Contributing, license and contact](#contributing-license-and-contact)

## Quick start

You need **Python 3.9 or newer** (from [python.org](https://www.python.org/downloads/); on Windows tick "Add Python to PATH").

1. **Get the code.** Click the green **Code** button, then **Download ZIP**, and unzip it into a folder. (Or use Git: `git clone <this repository's address>`.)
2. **Open a terminal in that folder.**
3. **Run your first agent:**

   ```
   python hello_agent.py
   ```

   On Mac or Linux you may need `python3` instead of `python`. You should see:

   ```
   Step 1: Thought -> {'action': 'calculator', 'input': '250 + 130 + 75'}
   Step 1: Observation -> 455
   Step 2: Thought -> {'action': 'finish', 'answer': 'The answer is 455'}
   Final answer: The answer is 455
   ```

**Keep all the files in one folder.** The agents import each other, and many chapters build on files from earlier chapters.

Two optional libraries let Agents 17 and 18 read PDF and Excel files:

```
pip install pypdf openpyxl
```

More details are in [docs/setup.md](docs/setup.md).

## Check that everything works

One command runs all 25 agents with scripted typing, and compares every output with the expected output:

```
python run_all_agents.py
```

It prints `OK` or `DIFF` for each agent and takes about half a minute. It works in a temporary copy of the folder, so your own files and data are never touched. If something differs, the details are written to `differences.txt`, and all your outputs are in `my_outputs.txt`.

- Inside this script the date is frozen at 15 November 2026, so the dates are the same on every computer.
- Agents 17 and 18 need `pip install pypdf openpyxl`, otherwise they show `DIFF`.
- Want to try an agent by hand? [docs/try-it.md](docs/try-it.md) lists what to run and what to type for every agent, and [docs/expected_outputs.txt](docs/expected_outputs.txt) shows what you should see.

## The 25 agents

| Level | # | Agent | What it teaches | Main files |
|---|---|---|---|---|
| **1 Agent Basics** | 1 | Hello Agent | The think, act, observe loop, with a safe calculator | `hello_agent.py` |
| | 2 | Bill Calculator | Chaining tools: total, discount, GST | `agent_core.py`, `bill_agent.py` |
| | 3 | Weather & Time | Choosing tools by the question, time zones | `weather_time_agent.py` |
| | 4 | ReAct Reasoning | Showing a thought before every action | `react_agent.py` |
| | 5 | Short-Term Memory | Remembering facts and recent messages | `memory_agent.py` |
| **2 Everyday Assistants** | 6 | Note-Taking | Saving, searching and deleting notes in JSON | `notes_agent.py`, `storage.py`, `chat_helper.py` |
| | 7 | To-Do & Reminder | Dates, due today, overdue | `todo_agent.py`, `dates_helper.py` |
| | 8 | Calendar | Clash detection and free-slot search | `calendar_agent.py` |
| | 9 | Unit & Currency Converter | The base-unit method, sample rates | `converter_agent.py` |
| | 10 | Daily Briefing | Combining several agents into one message | `briefing_agent.py`, `seed_demo.py` |
| **3 Web & Search** | 11 | Web Search | Strict, then broad search, with sources | `search_agent.py` |
| | 12 | News Research | RSS feeds, recency, merging repeated stories | `news_agent.py`, `web_helper.py` |
| | 13 | Web Scraping | Reading title, headings, links and text from HTML | `scraper_agent.py` |
| | 14 | Price Tracker | Price history and target alerts | `price_agent.py` |
| | 15 | Fact-Checker | Evidence, verdicts and "not enough evidence" | `factcheck_agent.py` |
| **4 File & Document** | 16 | File Organizer | Plan, confirm, undo | `organizer_agent.py`, `file_helper.py` |
| | 17 | Document Q&A | Answers from TXT and PDF, with locations | `doc_agent.py` |
| | 18 | CSV & Excel Analyst | Sums, groups, filters | `table_agent.py` |
| | 19 | Report Writer | A Markdown report from a data file | `report_agent.py` |
| | 20 | Cleanup & Backup | Duplicates, backup first, trash instead of delete | `cleanup_agent.py` |
| **5 Email & Messaging** | 21 | Email Summarizer | Priorities, action items, phishing warnings | `email_agent.py` |
| | 22 | Reply Drafting | Drafts with `[BLANKS]`, never sends | `reply_agent.py` |
| | 23 | Meeting Scheduler | Finds a free slot, books after you confirm | `scheduler_agent.py` |
| | 24 | Shop Support | Answers from a policy, verifies, hands over to a human | `support_agent.py` |
| | 25 | Telegram Personal Assistant | One bot for all your agents, for its owner only | `assistant_bot.py` |

The sample data files (`sample_*.txt`, `.csv`, `.xlsx`, `.pdf`, `.html`, `.xml` and the `sample_inbox` folder) are used by the chapters. All the names, emails, orders, prices, news and facts in them are **invented for teaching**.

### A note about "AI"

In Part A, the part of each agent that decides the next step (the "brain") is made of simple rules, so that every program runs free, offline and gives the same answer each time. Everything around the brain is what a real AI agent needs: the loop, the tools, the memory, the step limit, error handling and safety checks. Language models are added in later volumes. The idea is: *swap the brain, keep the body*.

## Practice folders and safety

- The agents that **move or write files** (Agents 16, 19 and 20) should be tried on the practice folders first. Run `python make_messy_folder.py` and `python make_cleanup_practice.py` to create them. The agents refuse to work on a whole drive or on your home folder.
- Agents that change files show a **plan first** and wait for `confirm`.
- The email and chat agents write **drafts**. They never send anything by themselves.
- The Telegram bot (Agent 25) reads its token from the environment variable `TELEGRAM_BOT_TOKEN`, and answers only chats in `ALLOWED_CHAT_IDS`. **Never put a token in the code, in an issue or in a screenshot.**
- Use sample data while you learn.

## Repository layout

```
.
|-- *.py                  the 25 agents and their helper files (keep them in one folder)
|-- sample_*              sample data used by the chapters
|-- sample_inbox/         seven invented emails for Agents 21 to 23
|-- make_*.py             scripts that create practice folders and files
|-- run_all_agents.py     runs every agent and checks the output
|-- expected_outputs.json the expected outputs used by the check script
|-- requirements-optional.txt
|-- docs/                 setup guide, troubleshooting, what to type, expected outputs
`-- .github/              issue form and automatic checks
```

## Troubleshooting

| Problem | What to do |
|---|---|
| `python is not recognized` | Reinstall Python and tick "Add Python to PATH", or try `py` or `python3` |
| `ModuleNotFoundError: No module named 'agent_core'` | Put all files in one folder and run from that folder |
| `FileNotFoundError` for a sample file | You are in the wrong folder. Check with `dir` (Windows) or `ls` |
| Agent 16 or 20 says "Folder not found" | Run `make_messy_folder.py` or `make_cleanup_practice.py` first |
| `To read PDF files, install pypdf first` | `pip install pypdf` |
| Agent 3 says "No time zone found" (Windows) | `pip install tzdata` |

More answers are in [docs/troubleshooting.md](docs/troubleshooting.md). To leave a chat agent, type `quit` (Ctrl+C also works).

## The book series

This repository is the first of four, which together build 100 agents.

| Book | Levels | Agents |
|---|---|---|
| **Vol 1, Part A** (this repository) | Basics, Everyday Assistants, Web & Search, File & Document, Email & Messaging | 1 to 25 |
| Vol 1, Part B | Data & SQL, Coding, Planning & Reasoning, Multi-Agent Teams, Safe Deployment & Capstone | 26 to 50 |
| Vol 2, Part A | MCP & Tool Protocols, Agent Frameworks, Agentic RAG, Browser & Automation, Voice & Vision | 51 to 75 |
| Vol 2, Part B | Business, Education & Career, India-Focused Agents, Evaluation & Safety, Production & Capstone | 76 to 100 |

## Contributing, license and contact

- **Found a problem?** Please open an [Issue](../../issues/new/choose). See [CONTRIBUTING.md](CONTRIBUTING.md).
- **Security or privacy concern?** See [SECURITY.md](SECURITY.md).
- **License:** the code is shared under the [MIT License](LICENSE). The text, stories and illustrations of the book are not covered by this license.
- **Changes:** see [CHANGELOG.md](CHANGELOG.md).

**Author:** Anuj Kumar Saxena  
**Contact:** [anujrampur@gmail.com](mailto:anujrampur@gmail.com)

## Disclaimer

The programs are teaching examples and come without any warranty. Practise on sample files, make backups before you let a program change real files, and check results before you rely on them. Nothing here is financial, legal, medical or professional advice. Python is a trademark of the Python Software Foundation. Telegram and other product names belong to their owners and are used only to explain how things work.
