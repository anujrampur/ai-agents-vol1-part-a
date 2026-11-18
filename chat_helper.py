from agent_core import run_agent

def chat_loop(brain, tools, title, verbose=False):
    print(f"{title}  (type 'quit' to stop)")
    while True:
        try:
            user = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):      # Ctrl+C, or no more typed input
            print("\nBye!")
            break
        if user.lower() == "quit":
            break
        if not user:
            continue
        print("Agent:", run_agent(user, brain, tools, verbose=verbose))
