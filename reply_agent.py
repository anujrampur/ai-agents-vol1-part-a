import re
from pathlib import Path
from email_agent import INBOX, load_inbox, list_inbox, get_email, classify
from file_helper import unique_destination
from chat_helper import chat_loop

DRAFT_DIR = Path("drafts")
SIGNATURE = "Ravi\nRavi Stationery"          # change this to your own name

# What each reply says. Anything the agent cannot know is written as [CAPITAL BRACKETS].
INTENTS = {
    "confirm": ("Thank you for your email about \"{subject}\". I confirm that this is fine from my side.",
                "Confirmed, this is fine from my side."),
    "thanks":  ("Thank you for your email about \"{subject}\". I really appreciate it.",
                "Thank you, much appreciated."),
    "later":   ("Thank you for your email about \"{subject}\". I need a little more time, "
                "and I will reply properly by [DATE].",
                "Thanks. I need a little more time and will reply by [DATE]."),
    "decline": ("Thank you for your email about \"{subject}\". Unfortunately I am not able to do this. [REASON]",
                "Sorry, I am not able to do this. [REASON]"),
    "quote":   ("Thank you for your interest. I will send you the quotation you asked for by [DATE]. "
                "The prices will be [PRICES].",
                "I will send the quotation by [DATE]."),
}

TONES = {
    "polite": ("Dear {name},", "With best regards,"),
    "formal": ("Dear {name},", "Yours sincerely,"),
    "short":  ("Hi {name},", "Thanks,"),
}

def make_draft(email, intent, tone):
    long_text, short_text = INTENTS[intent]
    template = short_text if tone == "short" else long_text
    greeting, closing = TONES[tone]
    subject = email["subject"]
    body = template.format(subject=subject)
    reply_subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    text = (f"To: {email['sender_name']} <{email['sender_address']}>\n"
            f"Subject: {reply_subject}\n\n"
            f"{greeting.format(name=email['sender_name'])}\n\n{body}\n\n{closing}\n{SIGNATURE}\n")
    return text

def draft_reply(number, intent, tone="polite"):
    email = get_email(number)
    if classify(email) == "SUSPICIOUS":
        raise ValueError("This email looks suspicious, so I will not write a reply. Do not click its links.")
    if intent not in INTENTS:
        raise ValueError(f"I can draft these replies: {', '.join(INTENTS)}")
    if tone not in TONES:
        raise ValueError(f"I can use these tones: {', '.join(TONES)}")

    text = make_draft(email, intent, tone)
    DRAFT_DIR.mkdir(exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", email["subject"].lower()).strip("-")[:30]
    target = unique_destination(DRAFT_DIR / f"reply-{number}-{slug}.txt")
    target.write_text(text, encoding="utf-8")

    message = f"DRAFT (not sent). Saved as {target}\n\n{text}"
    blanks = sorted(set(re.findall(r"\[[A-Z ]+\]", text)))
    if blanks:
        message += f"\nFill in before sending: {', '.join(blanks)}"
    if classify(email) == "HIGH" and intent in ("later", "decline"):
        message += ("\nCareful: this email is marked HIGH priority. "
                    "Check that waiting or saying no is really what you want.")
    message += "\nRead it carefully, then send it yourself from your email program."
    return message

def list_drafts():
    files = sorted(DRAFT_DIR.glob("*.txt")) if DRAFT_DIR.exists() else []
    if not files:
        return "You have no drafts yet."
    return "\n".join(f"{n}. {file.name}" for n, file in enumerate(files, start=1))

def show_draft(number):
    files = sorted(DRAFT_DIR.glob("*.txt")) if DRAFT_DIR.exists() else []
    if not 1 <= int(number) <= len(files):
        raise ValueError("There is no draft with that number. Type 'drafts' to see the list")
    return files[int(number) - 1].read_text(encoding="utf-8")

TOOLS = {"load_inbox": load_inbox, "list_inbox": list_inbox, "draft_reply": draft_reply,
         "list_drafts": list_drafts, "show_draft": show_draft}

HELP = ("Try: 'load sample_inbox', 'inbox', 'draft 4 confirm', 'draft 6 quote formal', "
        "'draft 3 later short', 'drafts', 'show draft 1'")

def reply_brain(goal, history):
    if history:
        return {"action": "finish", "answer": history[-1]["result"]}
    text = goal.strip()
    lower = text.lower()

    match = re.match(r"load (.+)$", text, re.IGNORECASE)
    if match:
        return {"action": "load_inbox", "input": {"folder": match.group(1)}}
    if lower == "inbox":
        return {"action": "list_inbox"}
    match = re.match(r"draft (\d+) (\w+)(?: (\w+))?$", lower)
    if match:
        arguments = {"number": int(match.group(1)), "intent": match.group(2)}
        if match.group(3):
            arguments["tone"] = match.group(3)
        return {"action": "draft_reply", "input": arguments}
    if lower == "drafts":
        return {"action": "list_drafts"}
    match = re.match(r"show draft (\d+)$", lower)
    if match:
        return {"action": "show_draft", "input": {"number": int(match.group(1))}}
    return {"action": "finish", "answer": HELP}

if __name__ == "__main__":
    chat_loop(reply_brain, TOOLS, "Reply drafting agent")
