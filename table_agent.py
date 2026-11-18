import csv
import re
from pathlib import Path
from chat_helper import chat_loop

TABLE = {"name": None, "columns": [], "rows": []}     # short-term memory: the loaded table

def convert(value):
    """Turn '5' into the number 5 and '2.5' into 2.5. Anything else stays text."""
    text = "" if value is None else str(value).strip()
    for kind in (int, float):
        try:
            return kind(text)
        except ValueError:
            pass
    return text

def read_rows(path):
    file = Path(path)
    if not file.exists():
        raise ValueError(f"File not found: {path}")

    suffix = file.suffix.lower()
    if suffix == ".csv":
        with open(file, newline="", encoding="utf-8-sig") as handle:
            raw_rows = list(csv.DictReader(handle))
        columns = [c.strip() for c in raw_rows[0].keys()] if raw_rows else []
    elif suffix == ".xlsx":
        try:
            from openpyxl import load_workbook
        except ImportError:
            raise ValueError("To read .xlsx files, install openpyxl first:  pip install openpyxl")
        sheet = load_workbook(file, read_only=True, data_only=True).active
        table = list(sheet.iter_rows(values_only=True))
        if not table:
            raise ValueError("The sheet is empty")
        columns = [str(c).strip() for c in table[0]]
        raw_rows = [dict(zip(columns, row)) for row in table[1:]]
    else:
        raise ValueError("I can read .csv and .xlsx files")

    if not raw_rows:
        raise ValueError("The file has no data rows")
    rows = [{str(key).strip(): convert(value) for key, value in row.items()} for row in raw_rows]
    return rows, columns

def find_column(columns, name):
    for column in columns:
        if column.lower() == name.strip().lower():
            return column
    raise ValueError(f"No column called '{name}'. Columns: {', '.join(columns)}")

def numbers(rows, column):
    values = [row[column] for row in rows if isinstance(row[column], (int, float))]
    if not values:
        raise ValueError(f"Column '{column}' has no numbers")
    return values

def calculate(values, kind):
    if kind == "sum":
        return sum(values)
    if kind == "average":
        return sum(values) / len(values)
    if kind == "min":
        return min(values)
    if kind == "max":
        return max(values)
    if kind == "count":
        return len(values)
    raise ValueError("Use sum, average, min, max or count")

def aggregate(rows, column, by, kind="sum"):
    """Group rows by one column and calculate a number for each group."""
    groups = {}
    for row in rows:
        if isinstance(row[column], (int, float)):
            groups.setdefault(row[by], []).append(row[column])
    result = [(group, calculate(values, kind)) for group, values in groups.items()]
    return sorted(result, key=lambda pair: pair[1], reverse=True)

def fmt(number):
    if float(number).is_integer():
        return f"{int(number):,}"
    return f"{number:,.2f}"

def current_table():
    if not TABLE["rows"]:
        raise ValueError("Load a table first, for example: load sample_sales.csv")
    return TABLE

def load_table(path):
    rows, columns = read_rows(path)
    TABLE["name"], TABLE["columns"], TABLE["rows"] = Path(path).name, columns, rows
    return f"Loaded {TABLE['name']}: {len(rows)} rows, {len(columns)} columns."

def describe_table():
    table = current_table()
    lines = [f"{table['name']}: {len(table['rows'])} rows"]
    for column in table["columns"]:
        example = table["rows"][0][column]
        kind = "number" if isinstance(example, (int, float)) else "text"
        lines.append(f"- {column} ({kind}, for example {example})")
    return "\n".join(lines)

def column_stat(column, kind):
    table = current_table()
    column = find_column(table["columns"], column)
    value = calculate(numbers(table["rows"], column), kind)
    return f"{kind} of {column} = {fmt(value)}"

def group_stat(column, by, kind="sum"):
    table = current_table()
    column = find_column(table["columns"], column)
    by = find_column(table["columns"], by)
    pairs = aggregate(table["rows"], column, by, kind)
    if not pairs:
        raise ValueError(f"Column '{column}' has no numbers")
    lines = [f"{kind} of {column} by {by}:"]
    lines += [f"- {group}: {fmt(value)}" for group, value in pairs]
    return "\n".join(lines)

def show_row(row, limit=4):
    return ", ".join(f"{key}={value}" for key, value in list(row.items())[:limit])

def top_rows(column, n=3):
    table = current_table()
    column = find_column(table["columns"], column)
    candidates = [row for row in table["rows"] if isinstance(row[column], (int, float))]
    best = sorted(candidates, key=lambda row: row[column], reverse=True)[:int(n)]
    return f"Top {len(best)} rows by {column}:\n" + "\n".join(
        f"{number}. {show_row(row)}, {column}={row[column]}" for number, row in enumerate(best, 1))

def filter_rows(column, op, value):
    table = current_table()
    column = find_column(table["columns"], column)
    wanted = convert(value)

    def matches(cell):
        if op == "contains":
            return str(wanted).lower() in str(cell).lower()
        if isinstance(cell, (int, float)) and isinstance(wanted, (int, float)):
            return {"=": cell == wanted, ">": cell > wanted, "<": cell < wanted,
                    ">=": cell >= wanted, "<=": cell <= wanted}[op]
        return op == "=" and str(cell).lower() == str(wanted).lower()

    found = [row for row in table["rows"] if matches(row[column])]
    if not found:
        return f"No rows where {column} {op} {wanted}."
    lines = [f"{len(found)} rows where {column} {op} {wanted}:"]
    lines += [f"- {show_row(row)}" for row in found[:5]]
    if len(found) > 5:
        lines.append(f"... and {len(found) - 5} more")
    return "\n".join(lines)

TOOLS = {
    "load_table": load_table,
    "describe_table": describe_table,
    "column_stat": column_stat,
    "group_stat": group_stat,
    "top_rows": top_rows,
    "filter_rows": filter_rows,
}

HELP = ("Try: 'load sample_sales.csv', 'describe', 'sum revenue', 'average price', "
        "'revenue by category', 'top 3 revenue', 'filter category = Pens'")

KINDS = {"sum": "sum", "total": "sum", "average": "average", "avg": "average",
         "mean": "average", "min": "min", "max": "max", "count": "count"}

def table_brain(goal, history):
    if history:
        return {"action": "finish", "answer": history[-1]["result"]}

    text = goal.strip()
    lower = text.lower()

    match = re.match(r"load (.+)$", text, re.IGNORECASE)
    if match:
        return {"action": "load_table", "input": {"path": match.group(1)}}

    if lower in ("describe", "columns"):
        return {"action": "describe_table"}

    match = re.match(r"filter (\w+) (>=|<=|=|>|<|contains) (.+)$", text, re.IGNORECASE)
    if match:
        return {"action": "filter_rows", "input": {
            "column": match.group(1), "op": match.group(2).lower(), "value": match.group(3)}}

    match = re.match(r"top (\d+) (\w+)$", lower)
    if match:
        return {"action": "top_rows", "input": {"column": match.group(2), "n": int(match.group(1))}}

    match = re.match(r"(?:(sum|total|average|avg|mean)\s+)?(\w+) by (\w+)$", lower)
    if match:
        kind = KINDS[match.group(1) or "sum"]
        return {"action": "group_stat",
                "input": {"column": match.group(2), "by": match.group(3), "kind": kind}}

    match = re.match(r"(sum|total|average|avg|mean|min|max|count)\s+(?:of\s+)?(\w+)$", lower)
    if match:
        return {"action": "column_stat",
                "input": {"column": match.group(2), "kind": KINDS[match.group(1)]}}

    return {"action": "finish", "answer": HELP}

if __name__ == "__main__":
    chat_loop(table_brain, TOOLS, "CSV and Excel analyst agent")
