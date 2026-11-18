import re
from datetime import date, datetime, timedelta
from pathlib import Path
from dates_helper import today
from email_agent import load_inbox, list_inbox, get_email, classify, clean_body
from calendar_agent import events_on, add_event
from reply_agent import SIGNATURE, DRAFT_DIR
from file_helper import unique_destination
from chat_helper import chat_loop

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
PENDING = {"meeting": None}               # a booking waiting for your "confirm"

def resolve_day(word):
    """today, tomorrow, a weekday name (the next one) or YYYY-MM-DD, as YYYY-MM-DD."""
    word = word.strip().lower()
    if word == "today":
        return today().isoformat()
    if word == "tomorrow":
        return (today() + timedelta(days=1)).isoformat()
    if word in WEEKDAYS:
        ahead = (WEEKDAYS.index(word) - today().weekday()) % 7 or 7     # never today itself
        return (today() + timedelta(days=ahead)).isoformat()
    try:
        return date.fromisoformat(word).isoformat()
    except ValueError:
        raise ValueError(f"I do not understand the day '{word}'. "
                         "Use today, tomorrow, a weekday name or YYYY-MM-DD.")

def parse_when(text):
    """Find a day, a time and a length in a sentence. Returns a dictionary, or None."""
    lower = text.lower()
    day_match = re.search(r"\b(today|tomorrow|" + "|".join(WEEKDAYS) + r"|\d{4}-\d{2}-\d{2})\b", lower)
    time_match = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", lower)
    if time_match:
        hour, minute = int(time_match.group(1)), int(time_match.group(2) or 0)
        if time_match.group(3) == "pm" and hour != 12:
            hour += 12
        if time_match.group(3) == "am" and hour == 12:
            hour = 0
    else:
        clock = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", lower)
        if not clock:
            return None
        hour, minute = int(clock.group(1)), int(clock.group(2))
    if not day_match:
        return None
    length = re.search(r"(?:about|for)\s+(\d+)\s*minutes?", lower)
    return {"day": resolve_day(day_match.group(1)), "time": f"{hour:02d}:{minute:02d}",
            "minutes": int(length.group(1)) if length else 60}

def find_request(number):
    email = get_email(number)
    when = parse_when(clean_body(email["body"]))
    if when is None:
        return "NO_REQUEST"
    kind = "Call" if "call" in email["body"].lower() else "Meeting"
    when["title"] = f"{kind} with {email['sender_name']}"
    when["who"] = email["sender_name"]
    return when

def conflict_with(day, start, end):
    for event in events_on(day):
        other_start = datetime.fromisoformat(event["start"])
        other_end = datetime.fromisoformat(event["end"])
        if start < other_end and other_start < end:           # the overlap test from Agent 8
            return event, other_start, other_end
    return None

def check_slot(day, time, minutes):
    start = datetime.fromisoformat(f"{day}T{time}")
    clash = conflict_with(day, start, start + timedelta(minutes=int(minutes)))
    if clash is None:
        return "FREE"
    event, other_start, other_end = clash
    return f"BUSY: {event['title']} ({other_start:%H:%M} to {other_end:%H:%M})"

def find_next_slot(day, time, minutes, latest="20:00"):
    """Look for a free slot starting at the asked time, then every 30 minutes."""
    start = datetime.fromisoformat(f"{day}T{time}")
    limit = datetime.fromisoformat(f"{day}T{latest}")
    length = timedelta(minutes=int(minutes))
    while start + length <= limit:
        if conflict_with(day, start, start + length) is None:
            return f"{start:%H:%M}"
        start += timedelta(minutes=30)
    return "none"

def describe(day, time):
    return f"{date.fromisoformat(day):%A %d %B} at {time}"

def propose_meeting(title, day, time, minutes, who, asked_time):
    if time == "none":
        PENDING["meeting"] = None
        return f"{who} asked for {describe(day, asked_time)}, but I found no free slot that evening. Nothing was booked."
    PENDING["meeting"] = {"title": title, "day": day, "time": time, "minutes": int(minutes), "who": who}
    if time == asked_time:
        reply = f"{describe(day, time)} works for me. I look forward to it."
        note = "That time is free."
    else:
        reply = (f"Thank you. I am not free at {asked_time}, but {describe(day, time)} works for me. "
                 "Would that be fine?")
        note = f"{asked_time} is busy. This is the first free slot after it."
    return (f"PROPOSAL (nothing is booked yet):\n  {title}\n  {describe(day, time)}, {minutes} minutes\n"
            f"  {note}\n  Reply draft: \"{reply}\"\n"
            "Type 'confirm' to book it and save the reply draft, or 'cancel'.")

def apply_booking():
    meeting = PENDING["meeting"]
    if meeting is None:
        raise ValueError("There is no booking waiting. Type 'schedule <email number>' first")
    booked = add_event(meeting["title"], meeting["day"], meeting["time"], meeting["minutes"])
    DRAFT_DIR.mkdir(exist_ok=True)
    target = unique_destination(DRAFT_DIR / f"meeting-reply-{meeting['who'].split()[-1].lower()}.txt")
    target.write_text(f"Dear {meeting['who']},\n\n{describe(meeting['day'], meeting['time'])} works for me. "
                      f"I look forward to it.\n\nWith best regards,\n{SIGNATURE}\n", encoding="utf-8")
    PENDING["meeting"] = None
    return f"{booked}\nReply draft saved as {target}. Send it yourself."

def cancel_booking():
    PENDING["meeting"] = None
    return "Cancelled. Nothing was booked."

def book_event(title, day, time, minutes=60):
    return add_event(title, resolve_day(day), time, minutes)

TOOLS = {
    "load_inbox": load_inbox, "list_inbox": list_inbox, "find_request": find_request,
    "check_slot": check_slot, "find_next_slot": find_next_slot,
    "propose_meeting": propose_meeting, "apply_booking": apply_booking,
    "cancel_booking": cancel_booking, "book_event": book_event,
}

HELP = ("Try: 'load sample_inbox', 'inbox', 'schedule 4', 'confirm', 'cancel', "
        "'book Supplier visit on sunday at 17:30 for 60 minutes'")

def scheduler_brain(goal, history):
    text = goal.strip()
    lower = text.lower()
    match = re.match(r"schedule (\d+)$", lower)

    if match:
        number = int(match.group(1))
        if not history:
            return {"action": "find_request", "input": {"number": number}}

        request = history[0]["result"]
        last = history[-1]
        if request == "NO_REQUEST":
            return {"action": "finish", "answer": "I could not find a day and a time in that email."}
        if isinstance(request, str):                               # an error message
            return {"action": "finish", "answer": request}

        common = {"title": request["title"], "day": request["day"], "minutes": request["minutes"],
                  "who": request["who"], "asked_time": request["time"]}
        if last["action"] == "find_request":
            return {"action": "check_slot",
                    "input": {"day": request["day"], "time": request["time"], "minutes": request["minutes"]}}
        if last["action"] == "check_slot":
            if last["result"] == "FREE":
                return {"action": "propose_meeting", "input": dict(common, time=request["time"])}
            return {"action": "find_next_slot",
                    "input": {"day": request["day"], "time": request["time"], "minutes": request["minutes"]}}
        if last["action"] == "find_next_slot":
            return {"action": "propose_meeting", "input": dict(common, time=last["result"])}
        return {"action": "finish", "answer": last["result"]}

    if history:
        return {"action": "finish", "answer": history[-1]["result"]}

    match = re.match(r"load (.+)$", text, re.IGNORECASE)
    if match:
        return {"action": "load_inbox", "input": {"folder": match.group(1)}}
    if lower == "inbox":
        return {"action": "list_inbox"}
    if lower == "confirm":
        return {"action": "apply_booking"}
    if lower == "cancel":
        return {"action": "cancel_booking"}
    match = re.match(r"book (.+?) on (\S+) at (\d{1,2}:\d{2})(?: for (\d+) minutes?)?$", text, re.IGNORECASE)
    if match:
        return {"action": "book_event", "input": {"title": match.group(1), "day": match.group(2),
                "time": match.group(3), "minutes": int(match.group(4) or 60)}}
    return {"action": "finish", "answer": HELP}

if __name__ == "__main__":
    chat_loop(scheduler_brain, TOOLS, "Meeting scheduler agent")
