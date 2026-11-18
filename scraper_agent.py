import re
from html.parser import HTMLParser
from web_helper import read_source
from chat_helper import chat_loop

class PageParser(HTMLParser):
    """Walks through an HTML page and collects the parts we care about."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.headings = []        # (tag, text)
        self.links = []           # (text, address)
        self.text_parts = []
        self._tag = None
        self._skip = 0            # inside <script> or <style>?
        self._href = None
        self._link_text = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        self._tag = tag
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._link_text = []

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1
        if tag == "a" and self._href is not None:
            self.links.append(("".join(self._link_text).strip(), self._href))
            self._href = None
        self._tag = None

    def handle_data(self, data):
        if self._skip:
            return
        text = data.strip()
        if not text:
            return
        if self._tag == "title":
            self.title += text
        elif self._tag in ("h1", "h2", "h3"):
            self.headings.append((self._tag, text))
        if self._href is not None:
            self._link_text.append(data)
        self.text_parts.append(text)

PAGE = {"source": None, "parser": None}      # short-term memory: the loaded page

def load_page(source):
    html = read_source(source)
    parser = PageParser()
    parser.feed(html)
    PAGE["source"], PAGE["parser"] = source, parser
    return f"Loaded '{parser.title or 'untitled page'}' ({len(html)} characters)"

def current_page():
    if PAGE["parser"] is None:
        raise ValueError("Load a page first, for example: load sample_shop.html")
    return PAGE["parser"]

def page_title():
    return current_page().title or "This page has no title."

def page_headings():
    headings = current_page().headings
    if not headings:
        return "No headings found."
    return "\n".join(f"{tag.upper()}: {text}" for tag, text in headings)

def page_links():
    links = current_page().links
    if not links:
        return "No links found."
    return "\n".join(f"{text or '(no text)'} -> {href}" for text, href in links)

def page_text(max_chars=300):
    text = " ".join(current_page().text_parts)
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + "..."
    return text or "No text found."

TOOLS = {
    "load_page": load_page,
    "page_title": page_title,
    "page_headings": page_headings,
    "page_links": page_links,
    "page_text": page_text,
}

HELP = "Try: 'load sample_shop.html', 'title', 'headings', 'links', 'text'"

def scraper_brain(goal, history):
    if history:
        return {"action": "finish", "answer": history[-1]["result"]}

    text = goal.strip()
    lower = text.lower()

    match = re.match(r"load (\S+)$", text, re.IGNORECASE)
    if match:
        return {"action": "load_page", "input": {"source": match.group(1)}}

    commands = {"title": "page_title", "headings": "page_headings",
                "links": "page_links", "text": "page_text"}
    if lower in commands:
        return {"action": commands[lower]}

    return {"action": "finish", "answer": HELP}

if __name__ == "__main__":
    chat_loop(scraper_brain, TOOLS, "Web scraping agent")
