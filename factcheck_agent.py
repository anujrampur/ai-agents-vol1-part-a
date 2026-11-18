import re
from chat_helper import chat_loop

# A tiny SAMPLE fact base so the agent runs offline. Each fact has a source.
FACTS = [
    {"text": "The Taj Mahal is in Agra, India.", "source": "Sample Encyclopedia"},
    {"text": "The Taj Mahal is located in the city of Agra.", "source": "Sample Travel Guide"},
    {"text": "Water boils at 100 degrees Celsius at sea level.", "source": "Sample Science Handbook"},
    {"text": "At normal sea-level pressure, water boils at 100 degrees Celsius.", "source": "Sample Encyclopedia"},
    {"text": "Python was created by Guido van Rossum.", "source": "Sample Tech Wiki"},
    {"text": "Guido van Rossum is the creator of the Python language.", "source": "Sample Encyclopedia"},
    {"text": "The capital of India is New Delhi.", "source": "Sample Encyclopedia"},
    {"text": "New Delhi is the capital city of India.", "source": "Sample Atlas"},
    {"text": "Mount Everest is about 8,849 metres tall.", "source": "Sample Atlas"},
    {"text": "The height of Mount Everest is roughly 8,849 metres.", "source": "Sample Science Handbook"},
]

STOP_WORDS = {"the", "a", "an", "is", "are", "was", "were", "of", "in", "at", "by", "to",
              "and", "it", "its", "as", "on", "for", "from", "that", "this", "has", "have", "be"}

def prepare(text):
    return re.sub(r"(?<=\d),(?=\d)", "", text)         # 8,849 becomes 8849

def tokens(text):
    words = re.findall(r"[a-z0-9]+", prepare(text).lower())
    return [word for word in words if word not in STOP_WORDS]

def numbers_in(text):
    return [float(n) for n in re.findall(r"\d+(?:\.\d+)?", prepare(text))]

def names_in(text):
    names = re.findall(r"\b[A-Z][a-z]+\b", text)
    return [name.lower() for name in names if name.lower() not in STOP_WORDS]

def close(a, b):
    return abs(a - b) <= 0.01 * max(abs(a), abs(b))     # within 1 percent

def compare(claim, fact_text):
    """Does this fact agree with the claim? Returns (True or False, reason)."""
    fact_numbers = numbers_in(fact_text)
    for number in numbers_in(claim):
        if not any(close(number, other) for other in fact_numbers):
            return False, f"the number {number:g} is not in this source"
    fact_tokens = set(tokens(fact_text))
    for name in names_in(claim):
        if name not in fact_tokens:
            return False, f"'{name}' is not in this source"
    return True, "matches"

def find_evidence(claim):
    claim_tokens = set(tokens(claim))
    if not claim_tokens:
        raise ValueError("Please type a claim to check")

    evidence = []
    for fact in FACTS:
        shared = claim_tokens & set(tokens(fact["text"]))
        if len(shared) >= 2 and len(shared) / len(claim_tokens) >= 0.5:    # relevant?
            agrees, reason = compare(claim, fact["text"])
            evidence.append({"source": fact["source"], "text": fact["text"],
                             "agrees": agrees, "reason": reason})
    return evidence

def judge(evidence):
    agree = len([e for e in evidence if e["agrees"]])
    disagree = len(evidence) - agree
    if agree >= 2 and disagree == 0:
        return "SUPPORTED"
    if agree == 1 and disagree == 0:
        return "WEAKLY SUPPORTED (only one source)"
    if agree > 0 and disagree > 0:
        return "MIXED (sources disagree)"
    return "CONTRADICTED"

TOOLS = {"find_evidence": find_evidence, "judge": judge}

NOTE = "Note: this is a learning demo with a tiny sample fact base. Check important claims with trusted sources."

def factcheck_brain(goal, history):
    claim = goal.strip()

    if not history:
        return {"action": "find_evidence", "input": {"claim": claim}}

    last = history[-1]
    if isinstance(last["result"], str) and last["result"].startswith("Error"):
        return {"action": "finish", "answer": last["result"]}

    if last["action"] == "find_evidence":
        if not last["result"]:
            return {"action": "finish",
                    "answer": f"Claim: {claim}\nVerdict: NOT ENOUGH EVIDENCE\n"
                              "I have no relevant source. That does not mean the claim is false.\n" + NOTE}
        return {"action": "judge", "input": {"evidence": last["result"]}}

    evidence = history[0]["result"]
    lines = [f"Claim: {claim}", f"Verdict: {last['result']}", "Evidence:"]
    for item in evidence:
        status = "agrees" if item["agrees"] else f"disagrees ({item['reason']})"
        lines.append(f"- [{item['source']}] {item['text']}  -> {status}")
    lines.append(NOTE)
    return {"action": "finish", "answer": "\n".join(lines)}

if __name__ == "__main__":
    chat_loop(factcheck_brain, TOOLS, "Fact-checker agent")
