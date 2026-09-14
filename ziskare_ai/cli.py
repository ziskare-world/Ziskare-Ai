"""
Ziskare AI - Command-Line Interface (CLI)
=========================================
"""

import sys
from ziskare_ai.core import ZiskareAI
from ziskare_ai.server import run_server

_default_instance = None


def get_default_ai(silent: bool = False) -> ZiskareAI:
    global _default_instance
    if _default_instance is None:
        _default_instance = ZiskareAI(silent=silent)
    return _default_instance


def main():
    args = sys.argv[1:]

    # Help flag
    if "--help" in args or "-h" in args:
        print("\nZiskare AI CLI Usage:")
        print("  ziskare-ai 'your question here'     Direct answer to stdout")
        print("  ziskare-ai                         Interactive chat shell")
        print("  ziskare-ai --server [port]          Start local REST API server (default: 5005)")
        print("  ziskare-ai --help                   Show this help message\n")
        return

    # REST Server mode
    if "--server" in args:
        idx = args.index("--server")
        port = 5005
        if idx + 1 < len(args) and args[idx + 1].isdigit():
            port = int(args[idx + 1])
        run_server(port=port)
        return

    # Direct query execution
    if args:
        query = " ".join(args)
        ai = get_default_ai(silent=True)
        print(ai.ask(query), flush=True)
        return

    # Interactive Shell mode
    ai = get_default_ai(silent=False)
    print("\n" + "=" * 55, flush=True)
    print("  Ziskare AI - Interactive Shell", flush=True)
    print("  Type 'exit' or 'quit' to close.", flush=True)
    print("=" * 55 + "\n", flush=True)

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Ziskare AI: Session closed.", flush=True)
                break
            if not user_input:
                continue

            response, metrics = ai.chat(user_input)
            print(f"Ziskare AI: {response}", flush=True)
            print(f"⏱️ {metrics['time_taken']}s ({metrics['tokens']} tokens | {metrics['speed']} tok/s)\n", flush=True)
        except KeyboardInterrupt:
            print("\nExiting Ziskare AI...", flush=True)
            break


if __name__ == "__main__":
    main()
