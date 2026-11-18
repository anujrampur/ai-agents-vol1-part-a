import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from urllib.robotparser import RobotFileParser

USER_AGENT = "LearningAgentBot/1.0 (educational project)"
TIMEOUT = 8              # seconds: never wait forever
MAX_BYTES = 500_000      # never download huge pages

def allowed_by_robots(url):
    """Ask the website's robots.txt whether our bot may fetch this page."""
    parts = urllib.parse.urlparse(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    request = urllib.request.Request(robots_url, headers={"User-Agent": USER_AGENT})
    parser = RobotFileParser()
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            text = response.read().decode("utf-8", errors="replace")
        parser.parse(text.splitlines())
    except urllib.error.HTTPError as error:
        return 400 <= error.code < 500      # no robots.txt means nothing is forbidden
    except Exception:
        return False                         # could not check, so be careful
    return parser.can_fetch(USER_AGENT, url)

def read_source(source):
    """Read text from a web address (http/https) or from a local file."""
    if source.startswith(("http://", "https://")):
        if not allowed_by_robots(source):
            raise ValueError("robots.txt does not allow this page (or could not be checked)")
        request = urllib.request.Request(source, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                raw = response.read(MAX_BYTES)
        except Exception as error:
            raise ValueError(f"Could not download the page: {error}")
        return raw.decode("utf-8", errors="replace")

    path = Path(source)
    if not path.exists():
        raise ValueError(f"File not found: {source}")
    return path.read_text(encoding="utf-8")
