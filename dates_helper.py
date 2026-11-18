import re
from datetime import date, timedelta

def today():
    return date.today()

def parse_date(phrase):
    """Turn 'today', 'tomorrow', 'in 3 days' or 'YYYY-MM-DD' into 'YYYY-MM-DD'."""
    phrase = phrase.strip().lower()

    if phrase == "today":
        return today().isoformat()
    if phrase == "tomorrow":
        return (today() + timedelta(days=1)).isoformat()

    match = re.fullmatch(r"in (\d+) days?", phrase)
    if match:
        return (today() + timedelta(days=int(match.group(1)))).isoformat()

    try:
        return date.fromisoformat(phrase).isoformat()
    except ValueError:
        raise ValueError(
            f"I do not understand the date '{phrase}'. "
            "Use today, tomorrow, in 3 days, or YYYY-MM-DD."
        )
