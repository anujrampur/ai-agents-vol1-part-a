import re
from storage import load_json, save_json
from dates_helper import today
from doc_agent import load_document, ask_document
from chat_helper import chat_loop

TICKET_FILE = "tickets.json"
SESSION = {"misses": 0, "loaded": False}      # short-term memory of this chat

# SAMPLE orders (invented). A real shop would read them from its own system.
ORDERS = {
    "ORD-1001": {"phone_last4": "4321", "items": "10 ruled notebooks", "status": "Out for delivery"},
    "ORD-1002": {"phone_last4": "8765", "items": "2 gel pen boxes", "status": "Packed, leaves tomorrow"},
    "ORD-1003": {"phone_last4": "1357", "items": "1 geometry box", "status": "Delivered on 10 November"},
}

ANGRY = re.compile(r"\b(angry|useless|worst|cheat|cheated|fraud|rubbish|terrible|disgusting)\b", re.IGNORECASE)

def ensure_policy():
    if not SESSION["loaded"]:
        load_document("sample_policy.txt")
        SESSION["loaded"] = True

def faq_answer(question):
    ensure_policy()
    result = ask_document(question)
    if isinstance(result, dict) and result["coverage"] >= 0.5:
        SESSION["misses"] = 0
        return "Here is what our shop policy says:\n" + "\n".join(result["passages"])
    SESSION["misses"] += 1
    return "UNSURE"

def order_status(order_id, phone_last4=None):
    order = ORDERS.get(order_id.upper())
    if order is None or phone_last4 != order["phone_last4"]:
        return "I could not match that order number and phone number. Please check them and try again."
    return f"Order {order_id.upper()} ({order['items']}): {order['status']}."

def create_ticket(summary):
    tickets = load_json(TICKET_FILE, [])
    ticket_id = f"T-{len(tickets) + 1:04d}"
    tickets.append({"id": ticket_id, "date": today().isoformat(), "summary": summary[:200], "status": "open"})
    save_json(TICKET_FILE, tickets)
    SESSION["misses"] = 0
    return (f"I have passed this to our team as ticket {ticket_id}. A person will contact you. "
            "Please do not share passwords or card numbers in this chat.")

TOOLS = {"faq_answer": faq_answer, "order_status": order_status, "create_ticket": create_ticket}

MENU = ("Hello! I am the Ravi Stationery helper. I can answer questions about returns, delivery, "
        "discounts, opening hours and payments, and check an order "
        "(type: order ORD-1001 phone 4321). Type 'human' to reach our team.")

def support_brain(goal, history):
    text = goal.strip()
    lower = text.lower()

    if history:                                         # a tool already ran
        last = history[-1]
        if last["action"] == "faq_answer" and last["result"] == "UNSURE":
            if SESSION["misses"] >= 2:                  # two misses in a row: hand over
                return {"action": "create_ticket", "input": {"summary": f"Unanswered question: {text}"}}
            return {"action": "finish",
                    "answer": "I am not sure about that. Could you ask in different words? "
                              "Or type 'human' and I will pass it to our team."}
        return {"action": "finish", "answer": last["result"]}

    if re.match(r"^(hi|hello|hey|namaste|good (morning|afternoon|evening))\b", lower):
        return {"action": "finish", "answer": MENU}

    if ANGRY.search(text):                              # an upset customer needs a person
        return {"action": "create_ticket", "input": {"summary": f"Upset customer: {text}"}}

    if re.search(r"\b(human|person|agent|complaint|refund)\b", lower):
        return {"action": "create_ticket", "input": {"summary": f"Customer asked for help: {text}"}}

    match = re.search(r"\b(ord-\d+)\b", lower)
    if match:
        phone = re.search(r"\bphone (\d{4})\b", lower)
        if not phone:
            return {"action": "finish", "answer": "To protect your privacy, please also send the last 4 digits "
                                                  "of your phone number, like this: order ORD-1001 phone 4321"}
        return {"action": "order_status", "input": {"order_id": match.group(1), "phone_last4": phone.group(1)}}

    return {"action": "faq_answer", "input": {"question": text}}

if __name__ == "__main__":
    chat_loop(support_brain, TOOLS, "Shop support agent")
