import re
import difflib
import xml.etree.ElementTree as ET
from datetime import timedelta
from email.utils import parsedate_to_datetime
from web_helper import read_source
from chat_helper import chat_loop

STORIES = []       # short-term memory: the stories of the loaded feed

def clean(text):
    text = re.sub(r"<[^>]+>", "", text or "")          # remove any HTML tags
    return re.sub(r"\s+", " ", text).strip()

def first_sentence(text):
    return re.split(r"(?<=[.!?])\s", text)[0]

def load_feed(source):
    xml_text = read_source(source)
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        raise ValueError("That does not look like a valid RSS feed")

    stories = []
    for item in root.iter("item"):
        title = clean(item.findtext("title"))
        if not title:
            continue
        try:
            day = parsedate_to_datetime(item.findtext("pubDate")).date()
        except (TypeError, ValueError):
            day = None
        stories.append({
            "title": title,
            "summary": clean(item.findtext("description")),
            "link": clean(item.findtext("link")),
            "source": clean(item.findtext("source")) or "Unknown source",
            "date": day,
        })

    if not stories:
        raise ValueError("No stories found in that feed")
    STORIES.clear()
    STORIES.extend(stories)
    return f"Loaded {len(stories)} stories from {source}"

def news_digest(topic="", days=7):
    if not STORIES:
        raise ValueError("Load a feed first, for example: load sample_news.xml")

    dated = [story for story in STORIES if story["date"]]
    newest = max(story["date"] for story in dated)
    cutoff = newest - timedelta(days=int(days))        # measured from the newest story
    words = topic.lower().split()

    groups = []                                        # each group = same story, many sources
    for story in sorted(dated, key=lambda s: s["date"], reverse=True):
        if story["date"] < cutoff:
            continue
        text = (story["title"] + " " + story["summary"]).lower()
        if words and not all(word in text for word in words):
            continue
        for group in groups:
            similarity = difflib.SequenceMatcher(
                None, story["title"].lower(), group[0]["title"].lower()).ratio()
            if similarity > 0.7:
                group.append(story)
                break
        else:
            groups.append([story])

    label = f"'{topic}'" if topic else "all topics"
    if not groups:
        return f"No stories about {label} in the last {days} days of the feed."

    lines = [f"News digest: {label}, last {days} days of the feed, {len(groups)} stories"]
    for number, group in enumerate(groups, start=1):
        main = group[0]
        others = [story["source"] for story in group[1:]]
        extra = f" (also reported by {', '.join(others)})" if others else ""
        lines.append(f"{number}. {main['title']} - {main['source']}, {main['date']}{extra}")
        lines.append(f"   {first_sentence(main['summary'])}")
        lines.append(f"   {main['link']}")
    return "\n".join(lines)

TOOLS = {"load_feed": load_feed, "news_digest": news_digest}

HELP = "Try: 'load sample_news.xml', 'headlines', 'news about school', 'news about school last 3 days'"

def news_brain(goal, history):
    if history:
        return {"action": "finish", "answer": history[-1]["result"]}

    text = goal.strip()

    match = re.match(r"load (\S+)$", text, re.IGNORECASE)
    if match:
        return {"action": "load_feed", "input": {"source": match.group(1)}}

    match = re.match(r"(?:news|headlines)(?: about (.+?))?(?: last (\d+) days?)?$",
                     text, re.IGNORECASE)
    if match:
        return {"action": "news_digest",
                "input": {"topic": match.group(1) or "", "days": int(match.group(2) or 7)}}

    return {"action": "finish", "answer": HELP}

if __name__ == "__main__":
    chat_loop(news_brain, TOOLS, "News research agent")
