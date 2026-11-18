# Troubleshooting

| Message or problem | Usual reason | What to do |
|---|---|---|
| `python is not recognized` | Python is not on the PATH | Reinstall and tick "Add Python to PATH", or try `py` or `python3` |
| `can't open file ... hello_agent.py` | The terminal is in the wrong folder | Go into the folder that holds the files (`cd`), or open a terminal from that folder |
| `ModuleNotFoundError: No module named 'agent_core'` | A needed file is missing, or you are in the wrong folder | Keep all files in one folder and run from that folder |
| `IndentationError` or `SyntaxError` | Spaces or quotation marks changed while copying | Check the indentation (4 spaces) and the quotes |
| `FileNotFoundError` for a sample file | The file is not in the current folder | Check with `dir` (Windows) or `ls` (Mac, Linux) |
| Agent 16 says "Folder not found: messy_folder" | The practice folder does not exist yet | Run `python make_messy_folder.py` first |
| Agent 20 says "Folder not found: cleanup_practice" | The practice folder does not exist yet | Run `python make_cleanup_practice.py` first |
| Agent 10 shows no events and no tasks | There is no data yet | Run `python seed_demo.py` once, then the briefing again |
| Agent 14 says "I am not tracking 'gel pens'" | You have not used `track` yet | Type `track gel pens from sample_product.html target 450` first |
| Agent 8 says "Conflicts with ..." | You already booked that time, and the data is saved | Delete the `data` folder to start fresh |
| `No time zone found` (Agent 3) | Windows has no time zone database | `pip install tzdata` |
| `To read PDF files, install pypdf first` | The optional library is missing | `pip install pypdf` |
| `To read .xlsx files, install openpyxl first` | The optional library is missing | `pip install openpyxl` |
| An agent says `Stopped: too many steps.` | The brain never reached `finish` | Compare your brain function with the book |
| `python run_all_agents.py` shows `DIFF` | Something differs from the expected output | Open `differences.txt`, and [open an issue](../../../issues/new/choose) if you cannot find the reason |

## Starting fresh

The agents save their data in a folder called `data` (and `drafts`, `reports`, `backups`). Close the programs and delete these folders to start again.

## Leaving a chat agent

Type `quit`. Ctrl+C also works.

## Still stuck?

Open an [Issue](../../../issues/new/choose) and tell us the agent number, the command you typed, your Python version, your operating system and the full error message.
