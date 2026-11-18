import re
from email import policy
from email.parser import BytesParser
from datetime import datetime, timezone
from email.utils import parseaddr, parsedate_to_datetime
from pathlib import Path
from chat_helper import chat_loop

INBOX = []         # short-term memory: the loaded emails, newest first

SUSPICIOUS = re.compile(r"verify your account|click the link|click here|enter your password|"
                        r"account will be (?:blocked|suspended)", re.IGNORECASE)
PROMO = re.compile(r"\bunsubscribe\b|\bnewsletter\b", re.IGNORECASE)
URGENT = re.compile(r"\b(?:urgent|asap|immediately|as soon as possible|deadline|due|today|tomorrow)\b",
                    re.IGNORECASE)
ACTION = re.compile(r"\bplease (?:confirm|send|share|fix|reply|call|check|pay|arrange|update)\b|"
                    r"\bcan you\b|\bcould you\b|\bcould we\b|\bneed\b|\bconfirm\b|\blet me know\b|\?",
                    re.IGNORECASE)

def parse_email(path):
    with open(path, "rb") as handle:
        message = BytesParser(policy=policy.default).parse(handle)
    name, address = parseaddr(str(message["From"]))
    part = message.get_body(preferencelist=("plain", "html"))
    body = part.get_content() if part else ""
    if part is not None and part.get_content_type() == "text/html":
        body = re.sub(r"<[^>]+>", " ", body)
    try:
        sent = parsedate_to_datetime(str(message["Date"]))
    except (TypeError, ValueError):
        sent = None
    return {"sender_name": name or address, "sender_address": address,
            "subject": str(message["Subject"] or "(no subject)"),
            "sent": sent, "date": sent.date() if sent else None, "body": body.strip()}

def clean_body(body):
    """Remove greetings and everything after the closing line (Regards, Thanks...)."""
    kept = []
    for line in body.splitlines():
        text = line.strip()
        if re.match(r"^(regards|best regards|with best regards|thanks|thank you|yours sincerely|sincerely)\b",
                    text, re.IGNORECASE):
            break
        if re.match(r"^(dear|hi|hello|hey|namaste)\b[^.!?]*,?$", text, re.IGNORECASE):
            continue
        kept.append(text)
    return re.sub(r"\s+", " ", " ".join(kept)).strip()

def sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+", text) if len(s.split()) >= 3]

def classify(email):
    text = email["subject"] + " " + email["body"]
    if SUSPICIOUS.search(text):
        return "SUSPICIOUS"
    if PROMO.search(text):
        return "LOW"
    if URGENT.search(text):
        return "HIGH"
    if ACTION.search(text):
        return "MEDIUM"
    return "NORMAL"

def action_items(email, limit=3):
    return [s for s in sentences(clean_body(email["body"])) if ACTION.search(s)][:limit]

def get_email(number):
    if not INBOX:
        raise ValueError("Load an inbox first, for example: load sample_inbox")
    number = int(number)
    if not 1 <= number <= len(INBOX):
        raise ValueError(f"Choose an email number from 1 to {len(INBOX)}")
    return INBOX[number - 1]

def load_inbox(folder):
    path = Path(folder)
    if not path.is_dir():
        raise ValueError(f"Folder not found: {folder}")
    emails = [parse_email(file) for file in sorted(path.glob("*.eml"))]
    if not emails:
        raise ValueError("I found no .eml files in that folder")
    oldest = datetime.min.replace(tzinfo=timezone.utc)
    emails.sort(key=lambda e: e["sent"] or oldest, reverse=True)       # newest first
    INBOX.clear()
    INBOX.extend(emails)
    return f"Loaded {len(emails)} emails from {path}."

def list_inbox():
    if not INBOX:
        raise ValueError("Load an inbox first, for example: load sample_inbox")
    return "\n".join(f"{n}. [{classify(e)}] {e['subject']} - {e['sender_name']} ({e['date']})"
                     for n, e in enumerate(INBOX, start=1))

def read_email(number):
    e = get_email(number)
    return (f"From: {e['sender_name']} <{e['sender_address']}>\nDate: {e['date']}\n"
            f"Subject: {e['subject']}\n\n{e['body']}")

def summarize_email(number):
    e = get_email(number)
    level = classify(e)
    if level == "SUSPICIOUS":
        return (f"WARNING: this email looks suspicious ({e['subject']}).\n"
                "Do not click links, open attachments or send passwords. "
                "If you are unsure, contact the sender through a number you already trust.")
    summary = " ".join(sentences(clean_body(e["body"]))[:2])
    lines = [f"[{level}] {e['subject']} - from {e['sender_name']}", f"Summary: {summary}"]
    items = action_items(e)
    if items:
        lines.append("Needs your attention:")
        lines += [f"- {item}" for item in items]
    else:
        lines.append("No action needed.")
    return "\n".join(lines)

def digest():
    if not INBOX:
        raise ValueError("Load an inbox first, for example: load sample_inbox")
    order = ["SUSPICIOUS", "HIGH", "MEDIUM", "NORMAL", "LOW"]
    groups = {level: [] for level in order}
    for number, e in enumerate(INBOX, start=1):
        groups[classify(e)].append(f"  {number}. {e['subject']} - {e['sender_name']}")
    counts = ", ".join(f"{len(groups[level])} {level.lower()}" for level in order if groups[level])
    lines = [f"{len(INBOX)} emails: {counts}"]
    for level in order:
        if groups[level]:
            lines.append(f"{level}:")
            lines += groups[level]
    return "\n".join(lines)

TOOLS = {"load_inbox": load_inbox, "list_inbox": list_inbox, "read_email": read_email,
         "summarize_email": summarize_email, "digest": digest}

HELP = "Try: 'load sample_inbox', 'inbox', 'digest', 'read 2', 'summary 2'"

def email_brain(goal, history):
    if history:
        return {"action": "finish", "answer": history[-1]["result"]}
    text = goal.strip()
    lower = text.lower()

    match = re.match(r"load (.+)$", text, re.IGNORECASE)
    if match:
        return {"action": "load_inbox", "input": {"folder": match.group(1)}}
    if lower == "inbox":
        return {"action": "list_inbox"}
    if lower == "digest":
        return {"action": "digest"}
    match = re.match(r"read (\d+)$", lower)
    if match:
        return {"action": "read_email", "input": {"number": int(match.group(1))}}
    match = re.match(r"summary (\d+)$", lower)
    if match:
        return {"action": "summarize_email", "input": {"number": int(match.group(1))}}
    return {"action": "finish", "answer": HELP}

if __name__ == "__main__":
    chat_loop(email_brain, TOOLS, "Email summarizer agent")
