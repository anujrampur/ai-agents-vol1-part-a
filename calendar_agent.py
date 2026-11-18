import re
from datetime import datetime, timedelta
from storage import load_json, save_json
from dates_helper import parse_date
from chat_helper import chat_loop

FILE = "events.json"
DAY_START = "09:00"
DAY_END = "18:00"

def parse_time(text):
    try:
        return datetime.strptime(text.strip(), "%H:%M").strftime("%H:%M")
    except ValueError:
        raise ValueError("Please write the time like 15:00")

def events_on(day):
    events = load_json(FILE, [])
    chosen = [event for event in events if event["start"].startswith(day)]
    return sorted(chosen, key=lambda event: event["start"])

def add_event(title, day, time, minutes=60):
    day = parse_date(day)
    minutes = int(minutes)
    if minutes <= 0:
        raise ValueError("An event must last at least 1 minute")

    start = datetime.fromisoformat(f"{day}T{parse_time(time)}")
    end = start + timedelta(minutes=minutes)
    if end.date() != start.date():
        raise ValueError("An event must end on the same day it starts")

    events = load_json(FILE, [])
    for event in events:
        other_start = datetime.fromisoformat(event["start"])
        other_end = datetime.fromisoformat(event["end"])
        if start < other_end and other_start < end:      # the overlap test
            raise ValueError(
                f"Conflicts with '{event['title']}' "
                f"({other_start:%H:%M} to {other_end:%H:%M})"
            )

    next_id = max((event["id"] for event in events), default=0) + 1
    events.append({
        "id": next_id,
        "title": title.strip(),
        "start": start.isoformat(timespec="minutes"),
        "end": end.isoformat(timespec="minutes"),
    })
    save_json(FILE, events)
    return f"Booked '{title.strip()}' on {day} from {start:%H:%M} to {end:%H:%M}."

def list_events(day="today"):
    day = parse_date(day)
    chosen = events_on(day)
    if not chosen:
        return f"No events on {day}."
    return "\n".join(
        f"{event['start'][11:16]} to {event['end'][11:16]}  {event['title']}"
        for event in chosen
    )

def find_free_slot(day, minutes=60):
    day = parse_date(day)
    cursor = datetime.fromisoformat(f"{day}T{DAY_START}")
    close = datetime.fromisoformat(f"{day}T{DAY_END}")
    needed = timedelta(minutes=int(minutes))

    for event in events_on(day):
        event_start = datetime.fromisoformat(event["start"])
        event_end = datetime.fromisoformat(event["end"])
        if event_start - cursor >= needed:      # a big enough gap before this event
            break
        cursor = max(cursor, event_end)

    if close - cursor >= needed:
        return f"{cursor:%H:%M}"
    return "none"

TOOLS = {
    "add_event": add_event,
    "list_events": list_events,
    "find_free_slot": find_free_slot,
}

HELP = ("Try: 'meeting Parent talk on tomorrow at 15:00 for 30 minutes', "
        "'show events on today', 'free slot on tomorrow for 45 minutes'")

def calendar_brain(goal, history):
    text = goal.strip()

    meeting = re.match(
        r"meeting (.+?) on (.+?) at (\d{1,2}:\d{2})(?: for (\d+) minutes?)?$",
        text, re.IGNORECASE)

    if meeting:
        title, day, time, minutes = meeting.groups()
        minutes = int(minutes) if minutes else 60

        if not history:                                   # first try to book
            return {"action": "add_event",
                    "input": {"title": title, "day": day, "time": time, "minutes": minutes}}

        last = history[-1]
        if last["action"] == "add_event":
            if last["result"].startswith("Error: Conflicts"):   # busy: look for a gap
                return {"action": "find_free_slot",
                        "input": {"day": day, "minutes": minutes}}
            return {"action": "finish", "answer": last["result"]}

        slot = last["result"]                              # result of find_free_slot
        problem = history[0]["result"].replace("Error: ", "")
        if slot == "none":
            return {"action": "finish",
                    "answer": f"I could not book '{title}': {problem}. "
                              f"There is no free {minutes}-minute slot that day."}
        return {"action": "finish",
                "answer": f"I could not book '{title}' at {time}: {problem}. "
                          f"The first free {minutes}-minute slot that day is {slot}."}

    if history:
        last = history[-1]
        if last["action"] == "find_free_slot" and not last["result"].startswith("Error"):
            if last["result"] == "none":
                return {"action": "finish", "answer": "There is no free slot of that length."}
            return {"action": "finish", "answer": f"The first free slot is at {last['result']}."}
        return {"action": "finish", "answer": last["result"]}

    match = re.match(r"show events(?: on (.+))?$", text, re.IGNORECASE)
    if match:
        return {"action": "list_events", "input": {"day": match.group(1) or "today"}}

    match = re.match(r"free slot on (.+?)(?: for (\d+) minutes?)?$", text, re.IGNORECASE)
    if match:
        minutes = int(match.group(2)) if match.group(2) else 60
        return {"action": "find_free_slot",
                "input": {"day": match.group(1), "minutes": minutes}}

    return {"action": "finish", "answer": HELP}

if __name__ == "__main__":
    chat_loop(calendar_brain, TOOLS, "Calendar agent")
