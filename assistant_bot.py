import json
import os
import time
import urllib.request
from agent_core import run_agent
import notes_agent
import todo_agent
import calendar_agent
import converter_agent
import briefing_agent

HELP_TEXT = (
    "I am your personal assistant. Commands:\n"
    "/note <text>      save a note\n"
    "/notes            show your notes\n"
    "/task <text>      add a task, for example: /task pay supplier due tomorrow\n"
    "/tasks            show pending tasks\n"
    "/done <number>    mark a task as done\n"
    "/today            events and tasks for today\n"
    "/meet <details>   for example: /meet Parent talk on tomorrow at 15:00 for 30 minutes\n"
    "/convert <text>   for example: /convert 5 km to miles\n"
    "/brief            your morning briefing"
)

# command -> (brain, tools, how to build the goal text, usage hint when text is missing)
ROUTES = {
    "note":    (notes_agent.notes_brain, notes_agent.TOOLS, lambda a: f"note: {a}", "/note buy chart paper"),
    "notes":   (notes_agent.notes_brain, notes_agent.TOOLS, lambda a: "show notes", None),
    "task":    (todo_agent.todo_brain, todo_agent.TOOLS, lambda a: f"add task {a}", "/task pay supplier due tomorrow"),
    "tasks":   (todo_agent.todo_brain, todo_agent.TOOLS, lambda a: "show tasks", None),
    "done":    (todo_agent.todo_brain, todo_agent.TOOLS, lambda a: f"done {a}", "/done 1"),
    "meet":    (calendar_agent.calendar_brain, calendar_agent.TOOLS, lambda a: f"meeting {a}",
                "/meet Parent talk on tomorrow at 15:00 for 30 minutes"),
    "convert": (converter_agent.converter_brain, converter_agent.TOOLS, lambda a: f"convert {a}",
                "/convert 5 km to miles"),
}

def ask(brain, tools, goal):
    return run_agent(goal, brain, tools, verbose=False)

def handle_message(text):
    """Turn one chat message into one reply."""
    text = text.strip()
    if not text.startswith("/"):
        return "Please start with a command. Type /help to see them."

    command, _, args = text.partition(" ")
    command = command.lstrip("/").split("@")[0].lower()       # '/note@MyBot' becomes 'note'
    args = args.strip()

    if command in ("start", "help"):
        return HELP_TEXT
    if command == "today":
        events = ask(calendar_agent.calendar_brain, calendar_agent.TOOLS, "show events on today")
        tasks = ask(todo_agent.todo_brain, todo_agent.TOOLS, "what is due today")
        return f"Events:\n{events}\n\nTasks:\n{tasks}"
    if command == "brief":
        return ask(briefing_agent.briefing_brain, briefing_agent.TOOLS, "morning briefing")

    if command in ROUTES:
        brain, tools, build, usage = ROUTES[command]
        if usage and not args:
            return f"Please add some text, for example: {usage}"
        return ask(brain, tools, build(args))
    return "I do not know that command. Type /help."

class ConsoleChannel:
    """A practice chat in your terminal. No internet and no account needed."""
    chat_id = 1

    def receive(self):
        try:
            text = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            return None
        if text.lower() == "quit":
            return None
        return [(self.chat_id, text)] if text else []

    def send(self, chat_id, text):
        print("Bot:", text)

class TelegramChannel:
    """A real Telegram bot, using Telegram's Bot API over HTTPS."""

    def __init__(self, token, api="https://api.telegram.org"):
        self.base = f"{api}/bot{token}"
        self.offset = None

    def _call(self, method, payload):
        request = urllib.request.Request(
            f"{self.base}/{method}", data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=40) as response:
            return json.loads(response.read())

    def receive(self):
        payload = {"timeout": 20}                  # wait up to 20 seconds for new messages
        if self.offset is not None:
            payload["offset"] = self.offset        # "I have already seen everything before this"
        messages = []
        for update in self._call("getUpdates", payload).get("result", []):
            self.offset = update["update_id"] + 1
            message = update.get("message") or {}
            if message.get("text"):
                messages.append((message["chat"]["id"], message["text"]))
        return messages

    def send(self, chat_id, text):
        self._call("sendMessage", {"chat_id": chat_id, "text": text[:4000]})

def run_bot(channel, allowed, max_polls=None):
    polls = 0
    while max_polls is None or polls < max_polls:
        polls += 1
        try:
            incoming = channel.receive()
        except Exception as error:                 # network trouble: wait and try again
            print("Connection problem:", error)
            time.sleep(3)
            continue
        if incoming is None:
            break
        for chat_id, text in incoming:
            if not allowed:                        # first run: tell the owner their chat id
                channel.send(chat_id, f"Your chat id is {chat_id}. Set ALLOWED_CHAT_IDS to this "
                                      "number and restart me. Until then I will not do anything else.")
            elif chat_id not in allowed:
                print(f"Ignored a message from an unknown chat ({chat_id}).")
            else:
                channel.send(chat_id, handle_message(text))

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if token:
        ids = os.environ.get("ALLOWED_CHAT_IDS", "").replace(" ", "")
        allowed = {int(item) for item in ids.split(",") if item}
        print("Telegram assistant is running. Press Ctrl+C to stop.")
        try:
            run_bot(TelegramChannel(token), allowed)
        except KeyboardInterrupt:
            print("\nStopped.")
    else:
        print("Practice chat (no Telegram). Type /help, or 'quit' to stop.")
        run_bot(ConsoleChannel(), {ConsoleChannel.chat_id})

if __name__ == "__main__":
    main()
