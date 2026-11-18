import re
from pathlib import Path
from dates_helper import today
from file_helper import unique_destination
from table_agent import read_rows, find_column, numbers, calculate, aggregate, fmt
from chat_helper import chat_loop

REPORT_DIR = Path("reports")
LAST = {"file": None}          # short-term memory: the last report we wrote

def section_summary(ctx):
    lines = [f"- Rows analysed: {len(ctx['rows'])}"]
    if ctx["period"]:
        lines.append(f"- Period: {ctx['period']}")
    lines.append(f"- Total {ctx['money']}: Rs {fmt(ctx['total'])}")
    lines.append(f"- Average per row: Rs {fmt(ctx['average'])}")
    return lines

def section_best_group(ctx):
    name, value = ctx["by_group"][0]
    share = value / ctx["total"] * 100
    return [f"The strongest {ctx['group']} is **{name}** with Rs {fmt(value)} ({share:.1f}% of the total)."]

def section_top_labels(ctx):
    return [f"{number}. {name}: Rs {fmt(value)}"
            for number, (name, value) in enumerate(ctx["by_label"][:3], start=1)]

def section_group_table(ctx):
    lines = [f"| {ctx['group'].title()} | {ctx['money'].title()} (Rs) | Share |", "|---|---:|---:|"]
    for name, value in ctx["by_group"]:
        lines.append(f"| {name} | {fmt(value)} | {value / ctx['total'] * 100:.1f}% |")
    return lines

def section_notes(ctx):
    return [f"This report was generated automatically from `{ctx['file']}`. "
            "Check the numbers against your records before sharing it."]

# The report layout is data: (heading, function that writes the section)
SECTIONS = [
    ("Summary", section_summary),
    ("Best category", section_best_group),
    ("Top 3 items", section_top_labels),
    ("Breakdown", section_group_table),
    ("Notes", section_notes),
]

def build_report(path, title="Sales Report", money="revenue", group="category", label="item"):
    rows, columns = read_rows(path)
    money = find_column(columns, money)
    group = find_column(columns, group)
    label = find_column(columns, label)

    amounts = numbers(rows, money)
    date_column = next((c for c in columns if c.lower() == "date"), None)
    dates = sorted(str(row[date_column]) for row in rows) if date_column else []

    ctx = {
        "rows": rows, "file": Path(path).name, "money": money, "group": group, "label": label,
        "total": calculate(amounts, "sum"), "average": calculate(amounts, "average"),
        "by_group": aggregate(rows, money, group, "sum"),
        "by_label": aggregate(rows, money, label, "sum"),
        "period": f"{dates[0]} to {dates[-1]}" if dates else "",
    }

    lines = [f"# {title}", "", f"*Created on {today().isoformat()}*", ""]
    for heading, writer in SECTIONS:
        lines += [f"## {heading}", ""] + writer(ctx) + [""]

    REPORT_DIR.mkdir(exist_ok=True)
    target = unique_destination(REPORT_DIR / f"{Path(path).stem}_{today().isoformat()}.md")
    target.write_text("\n".join(lines), encoding="utf-8")
    LAST["file"] = target
    return (f"Report saved: {target}\n"
            f"Total {money}: Rs {fmt(ctx['total'])}. Best {group}: {ctx['by_group'][0][0]}.\n"
            "Type 'show report' to read it.")

def show_report():
    if LAST["file"] is None:
        raise ValueError("No report yet. Try: report sample_sales.csv")
    return LAST["file"].read_text(encoding="utf-8")

TOOLS = {"build_report": build_report, "show_report": show_report}

HELP = "Try: 'report sample_sales.csv', 'report sample_sales.csv titled Weekly Sales', 'show report'"

def report_brain(goal, history):
    if history:
        return {"action": "finish", "answer": history[-1]["result"]}

    text = goal.strip()

    match = re.match(r"report (\S+)(?: titled (.+))?$", text, re.IGNORECASE)
    if match:
        arguments = {"path": match.group(1)}
        if match.group(2):
            arguments["title"] = match.group(2)
        return {"action": "build_report", "input": arguments}

    if text.lower() == "show report":
        return {"action": "show_report"}

    return {"action": "finish", "answer": HELP}

if __name__ == "__main__":
    chat_loop(report_brain, TOOLS, "Report writer agent")
