import re
from chat_helper import chat_loop

# A tiny pretend "web" so everything runs offline. The addresses are made up.
DEMO_PAGES = [
    {"title": "Python Lists Explained", "url": "https://example.org/python-lists",
     "snippet": "A list in Python stores many items in order. You can add, remove and slice items."},
    {"title": "Python Dictionaries for Beginners", "url": "https://example.org/python-dicts",
     "snippet": "A dictionary stores key and value pairs. Dictionaries make lookups fast."},
    {"title": "How AI Agents Work", "url": "https://example.org/ai-agents",
     "snippet": "An AI agent repeats a loop: think, act with a tool, observe the result."},
    {"title": "Introduction to JSON", "url": "https://example.org/json-intro",
     "snippet": "JSON is a text format for lists and dictionaries, used to save and share data."},
    {"title": "Stationery Shop Accounting Tips", "url": "https://example.org/shop-accounting",
     "snippet": "Track daily sales, record discounts, and keep GST bills organised."},
    {"title": "Weather and Time Zones", "url": "https://example.org/time-zones",
     "snippet": "Time zones use names like Asia/Kolkata. Daylight saving changes offsets."},
    {"title": "Python Virtual Environments", "url": "https://example.org/python-venv",
     "snippet": "A virtual environment keeps the libraries of each project separate."},
    {"title": "Web Scraping Ethics", "url": "https://example.org/scraping-ethics",
     "snippet": "Respect robots.txt, rate limits and website terms when collecting pages."},
    {"title": "Safe Calculators in Python", "url": "https://example.org/safe-calc",
     "snippet": "Avoid eval. Parse the expression with the ast module and allow only arithmetic."},
    {"title": "Saving Data with Python Files", "url": "https://example.org/python-files",
     "snippet": "Python can read and write text and JSON files so data survives restarts."},
]

STOP_WORDS = {"the", "a", "an", "is", "are", "of", "to", "in", "for", "and", "what",
              "how", "do", "does", "about", "on", "with", "can", "i", "my", "me"}

def stem(word):
    """A very simple stemmer: 'lists' and 'list' become the same word."""
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word

def keywords(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [stem(w) for w in words if w not in STOP_WORDS]

def web_search(query, mode="strict", limit=3):
    wanted = keywords(query)
    if not wanted:
        raise ValueError("Please type a few words to search for")

    scored = []
    for page in DEMO_PAGES:
        title_words = set(keywords(page["title"]))
        snippet_words = set(keywords(page["snippet"]))
        everything = title_words | snippet_words

        if mode == "strict" and not all(word in everything for word in wanted):
            continue

        score = sum(3 for word in wanted if word in title_words)
        score += sum(1 for word in wanted if word in snippet_words)
        if score > 0:
            scored.append((score, page))

    if not scored:
        return f"No results ({mode} search)."

    scored.sort(key=lambda pair: pair[0], reverse=True)
    lines = []
    for number, (score, page) in enumerate(scored[:limit], start=1):
        lines.append(f"{number}. {page['title']}\n   {page['url']}\n   {page['snippet']}")
    return "\n".join(lines)

TOOLS = {"web_search": web_search}

def search_brain(goal, history):
    query = goal.strip()

    if not history:                                   # first try: every word must match
        return {"action": "web_search", "input": {"query": query, "mode": "strict"}}

    last = history[-1]
    if last["result"].startswith("Error"):
        return {"action": "finish", "answer": last["result"]}

    if last["result"].startswith("No results"):
        if len(history) == 1:                         # second try: any word may match
            return {"action": "web_search", "input": {"query": query, "mode": "broad"}}
        return {"action": "finish",
                "answer": f"I found nothing for '{query}'. Try different words."}

    note = ""
    if last["input"]["mode"] == "broad":
        note = " (I widened the search because no page matched every word)"
    return {"action": "finish", "answer": f"Top results for '{query}'{note}:\n{last['result']}"}

if __name__ == "__main__":
    chat_loop(search_brain, TOOLS, "Web search agent")
