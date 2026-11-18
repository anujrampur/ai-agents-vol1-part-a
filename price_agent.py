import re
from html.parser import HTMLParser
from storage import load_json, save_json
from dates_helper import today
from web_helper import read_source
from chat_helper import chat_loop

FILE = "prices.json"
PRICE_PATTERN = re.compile(r"(?:Rs\.?|₹|INR)\s*([\d,]+(?:\.\d{1,2})?)", re.IGNORECASE)

class PriceParser(HTMLParser):
    """Collects the text of any element whose class is 'price'."""

    def __init__(self):
        super().__init__()
        self.price_text = []
        self._capture = None          # the tag we are collecting text from

    def handle_starttag(self, tag, attrs):
        classes = (dict(attrs).get("class") or "").lower().split()
        if "price" in classes and self._capture is None:
            self._capture = tag

    def handle_endtag(self, tag):
        if tag == self._capture:
            self._capture = None

    def handle_data(self, data):
        if self._capture:
            self.price_text.append(data)

def pretty(number):
    if number == int(number):
        return f"{number:,.0f}"
    return f"{number:,.2f}"

def extract_price(html):
    parser = PriceParser()
    parser.feed(html)
    # First choice: the element marked as the price. Second choice: any price in the text.
    for text in (" ".join(parser.price_text), re.sub(r"<[^>]+>", " ", html)):
        match = PRICE_PATTERN.search(text)
        if match:
            return float(match.group(1).replace(",", ""))
    raise ValueError("I could not find a price on that page")

def track_product(name, source, target=None):
    name = name.strip().lower()
    products = load_json(FILE, {})
    products[name] = {
        "source": source,
        "target": float(target) if target is not None else None,
        "history": products.get(name, {}).get("history", []),
    }
    save_json(FILE, products)
    goal = f" with target Rs {pretty(float(target))}" if target is not None else ""
    return f"Now tracking '{name}' from {source}{goal}."

def check_price(name):
    name = name.strip().lower()
    products = load_json(FILE, {})
    if name not in products:
        raise ValueError(f"I am not tracking '{name}'")
    item = products[name]

    price = extract_price(read_source(item["source"]))
    day = today().isoformat()
    history = item["history"]
    previous = history[-1] if history else None
    rechecked = False

    if previous and previous["date"] == day:       # one entry per day
        history[-1]["price"] = price
        previous = history[-2] if len(history) > 1 else None
        rechecked = True
    else:
        history.append({"date": day, "price": price})
    save_json(FILE, products)

    message = f"{name}: Rs {pretty(price)} on {day}."
    if previous is None:
        message += " No earlier day to compare with yet." if rechecked else " This is the first check."
    elif price < previous["price"]:
        message += f" Dropped by Rs {pretty(previous['price'] - price)} since {previous['date']}."
    elif price > previous["price"]:
        message += f" Went up by Rs {pretty(price - previous['price'])} since {previous['date']}."
    else:
        message += f" No change since {previous['date']}."

    if item["target"] is not None and price <= item["target"]:
        message += f" ALERT: this is at or below your target of Rs {pretty(item['target'])}."
    return message

def price_history(name):
    products = load_json(FILE, {})
    name = name.strip().lower()
    if name not in products or not products[name]["history"]:
        return f"No price history for '{name}' yet."
    return "\n".join(f"{entry['date']}: Rs {pretty(entry['price'])}"
                     for entry in products[name]["history"])

def list_tracked():
    products = load_json(FILE, {})
    if not products:
        return "You are not tracking any products yet."
    return "\n".join(f"- {name} ({item['source']})" for name, item in products.items())

TOOLS = {
    "track_product": track_product,
    "check_price": check_price,
    "price_history": price_history,
    "list_tracked": list_tracked,
}

HELP = ("Try: 'track gel pens from sample_product.html target 450', "
        "'check gel pens', 'history gel pens', 'show tracked'")

def price_brain(goal, history):
    if history:
        return {"action": "finish", "answer": history[-1]["result"]}

    text = goal.strip()

    match = re.match(r"track (.+?) from (\S+)(?: target (\d+(?:\.\d+)?))?$", text, re.IGNORECASE)
    if match:
        target = float(match.group(3)) if match.group(3) else None
        return {"action": "track_product",
                "input": {"name": match.group(1), "source": match.group(2), "target": target}}

    match = re.match(r"check (.+)", text, re.IGNORECASE)
    if match:
        return {"action": "check_price", "input": {"name": match.group(1)}}

    match = re.match(r"history (.+)", text, re.IGNORECASE)
    if match:
        return {"action": "price_history", "input": {"name": match.group(1)}}

    if text.lower() in ("show tracked", "list tracked"):
        return {"action": "list_tracked"}

    return {"action": "finish", "answer": HELP}

if __name__ == "__main__":
    chat_loop(price_brain, TOOLS, "Price tracker agent")
