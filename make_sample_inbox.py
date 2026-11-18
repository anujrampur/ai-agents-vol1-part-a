from email.message import EmailMessage
from pathlib import Path

folder = Path("sample_inbox")
folder.mkdir(exist_ok=True)

EMAILS = [
    ("Sharma Paper Supplies <accounts@sharma-paper.example>", "Invoice 1042 due Friday",
     "Mon, 09 Nov 2026 09:15:00 +0530",
     "Dear Ravi,\n\nPlease find invoice 1042 for Rs 12,500. Payment is due by Friday, 20 November. "
     "Please confirm once it is paid.\n\nRegards,\nSharma Paper Supplies"),
    ("Mrs. Verma <verma@greenfield-school.example>", "Order for 200 notebooks",
     "Tue, 10 Nov 2026 11:40:00 +0530",
     "Hello Ravi,\n\nGreenfield Public School would like to order 200 notebooks and 50 geometry boxes "
     "for the new term. Can you share a quotation and a delivery date? We need the items by 1 December.\n\n"
     "Thank you,\nMrs. Verma"),
    ("Stationery Weekly <news@stationery-weekly.example>", "This week's stationery deals",
     "Wed, 11 Nov 2026 07:00:00 +0530",
     "Great deals on pens and paper this week. Read our newsletter for more.\n\n"
     "You can unsubscribe at any time."),
    ("Neha <neha@family.example>", "Sunday call?",
     "Thu, 12 Nov 2026 18:20:00 +0530",
     "Hi Ravi,\n\nAre you free for a video call this Sunday at 6 pm? Let me know.\n\nNeha"),
    ("Mr. Khan <khan@customer.example>", "Wrong notebooks delivered",
     "Thu, 12 Nov 2026 20:05:00 +0530",
     "Hello,\n\nI ordered 10 ruled notebooks but received plain ones. This is urgent because my "
     "daughter's exam starts on Monday. Please fix this as soon as possible.\n\nMr. Khan"),
    ("Bank Support <alerts@secure-bank-check.example>", "URGENT: verify your account",
     "Fri, 13 Nov 2026 02:10:00 +0530",
     "Your account will be blocked today. Click the link http://secure-bank-check.example/login "
     "and enter your password to verify your account."),
    ("Tuition Centre Office <office@brightminds.example>", "Meeting about the bulk order",
     "Fri, 13 Nov 2026 10:30:00 +0530",
     "Dear Ravi,\n\nCould we meet on Tuesday at 4 pm to discuss the bulk order? It will take about 30 minutes.\n\n"
     "Regards,\nBright Minds Tuition Centre"),
]

for number, (sender, subject, date, body) in enumerate(EMAILS, start=1):
    message = EmailMessage()
    message["From"] = sender
    message["To"] = "Ravi <ravi@ravistationery.example>"
    message["Subject"] = subject
    message["Date"] = date
    message.set_content(body)
    if "newsletter" in body:                                   # one email also has an HTML version
        message.add_alternative(f"<html><body><p>{body}</p></body></html>", subtype="html")
    (folder / f"email{number}.eml").write_bytes(bytes(message))

print(f"Created {len(EMAILS)} sample emails in '{folder}'.")
