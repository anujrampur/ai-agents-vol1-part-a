import re
from pathlib import Path
from search_agent import keywords
from chat_helper import chat_loop

CHUNKS = []        # short-term memory: pieces of the loaded document
DOC = {"name": None}

def chunk_text(text, max_chars=500):
    """Cut text into passages: paragraphs first, long ones split at sentences."""
    chunks = []
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = re.sub(r"\s+", " ", paragraph).strip()
        if not paragraph:
            continue
        if len(paragraph) <= max_chars:
            chunks.append(paragraph)
            continue
        current = ""
        for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
            if current and len(current) + len(sentence) + 1 > max_chars:
                chunks.append(current)
                current = sentence
            else:
                current = f"{current} {sentence}".strip()
        if current:
            chunks.append(current)
    return chunks

def read_pdf_pages(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ValueError("To read PDF files, install pypdf first:  pip install pypdf")
    reader = PdfReader(str(path))
    return [(number, page.extract_text() or "") for number, page in enumerate(reader.pages, start=1)]

def load_document(path):
    file = Path(path)
    if not file.exists():
        raise ValueError(f"File not found: {path}")

    chunks = []
    if file.suffix.lower() == ".pdf":
        for number, text in read_pdf_pages(file):
            for piece in chunk_text(text, max_chars=250):    # PDF text has no paragraph breaks
                chunks.append({"label": f"page {number}", "text": piece})
    elif file.suffix.lower() in (".txt", ".md"):
        for number, piece in enumerate(chunk_text(file.read_text(encoding="utf-8")), start=1):
            chunks.append({"label": f"section {number}", "text": piece})
    else:
        raise ValueError("I can read .txt, .md and .pdf files")

    if not chunks:
        raise ValueError("I found no text in that file (a scanned PDF has pictures, not text)")
    CHUNKS.clear()
    CHUNKS.extend(chunks)
    DOC["name"] = file.name
    return f"Loaded {file.name}: {len(chunks)} passages."

def ask_document(question, top=2):
    if not CHUNKS:
        raise ValueError("Load a document first, for example: load sample_policy.txt")
    wanted = set(keywords(question))
    if not wanted:
        raise ValueError("Please ask a question with some meaningful words")

    scored = []
    for chunk in CHUNKS:
        found = wanted & set(keywords(chunk["text"]))
        if found:
            scored.append((len(found), chunk))
    if not scored:
        return "NOT FOUND"

    scored.sort(key=lambda pair: pair[0], reverse=True)
    best_score = scored[0][0]
    best = [chunk for score, chunk in scored if score == best_score][:top]   # only the best
    lines = [f"[{DOC['name']}, {chunk['label']}] {chunk['text']}" for chunk in best]
    return {"coverage": best_score / len(wanted), "passages": lines}

TOOLS = {"load_document": load_document, "ask_document": ask_document}

HELP = "Try: 'load sample_policy.txt', then 'ask when is the shop open', or 'info'"

def doc_brain(goal, history):
    text = goal.strip()

    if history:
        result = history[-1]["result"]
        if isinstance(result, dict):                       # passages found
            intro = ("Here is what the document says:" if result["coverage"] >= 0.5
                     else "I am not sure. These are the closest passages:")
            return {"action": "finish", "answer": intro + "\n" + "\n".join(result["passages"])}
        if result == "NOT FOUND":
            return {"action": "finish",
                    "answer": "I could not find that in the document. I will not guess."}
        return {"action": "finish", "answer": result}

    match = re.match(r"load (.+)$", text, re.IGNORECASE)
    if match:
        return {"action": "load_document", "input": {"path": match.group(1)}}

    match = re.match(r"ask (.+)$", text, re.IGNORECASE)
    if match:
        return {"action": "ask_document", "input": {"question": match.group(1)}}

    if text.lower() == "info":
        return {"action": "finish",
                "answer": f"Loaded: {DOC['name']} ({len(CHUNKS)} passages)" if CHUNKS else "Nothing loaded yet."}

    return {"action": "finish", "answer": HELP}

if __name__ == "__main__":
    chat_loop(doc_brain, TOOLS, "Document Q&A agent")
