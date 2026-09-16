"""
Ziskare AI - Command-Line Interface (CLI)
=========================================
"""

import sys

_default_instance = None


def get_default_ai(silent: bool = False):
    global _default_instance
    if _default_instance is None:
        from ziskare_ai.core import ZiskareAI
        _default_instance = ZiskareAI(silent=silent)
    return _default_instance


def main():
    args = sys.argv[1:]

    # Help flag
    if "--help" in args or "-h" in args:
        print("\nZiskare AI CLI Usage:")
        print("  ziskare-ai 'your question here'                   Direct answer to stdout")
        print("  ziskare-ai                                       Interactive multi-turn chat shell (remembers everything)")
        print("  ziskare-ai --agent [code|system|task|optimize|image|desktop] Run specialized AI agent")
        print("  ziskare-ai --image 'your prompt here'             Generate AI artwork & images")
        print("  ziskare-ai --open [file/folder/app]               Open file, folder, or launch app on laptop")
        print("  ziskare-ai --optimize [clean|cool|auto|bench]     Optimize laptop RAM, clean temp files & reduce heat")
        print("  ziskare-ai --server [port]                        Start local REST API server (default: 5005)")
        print("  ziskare-ai --help                                 Show this help message\n")
        return

    # Direct open shortcut
    if "--open" in args:
        idx = args.index("--open")
        target = " ".join(args[idx + 1:]) if idx + 1 < len(args) else "output/images"
        from ziskare_ai.agents import DesktopAgent
        desk = DesktopAgent(silent=False)
        print(f"[Ziskare AI Desktop] {desk.execute_task(f'open {target}')}")
        return

    # Direct image shortcut
    if "--image" in args:
        idx = args.index("--image")
        prompt = " ".join(args[idx + 1:]) if idx + 1 < len(args) else "futuristic cyberpunk city, 8k"
        from ziskare_ai.agents import ImageAgent
        img_agent = ImageAgent(silent=False)
        img_agent.generate(prompt)
        return

    # Direct optimize shortcut (supports: ziskare-ai optimize, ziskare-ai --optimize, etc.)
    if args and args[0].lower() in ["optimize", "--optimize", "-optimize", "/optimize"]:
        subcmd = args[1].lower() if len(args) > 1 and not args[1].startswith("-") else "all"
        args = ["--agent", "optimize", subcmd]
    elif "--optimize" in args:
        idx = args.index("--optimize")
        subcmd = args[idx + 1].lower() if idx + 1 < len(args) and not args[idx + 1].startswith("-") else "all"
        args = ["--agent", "optimize", subcmd]

    # Agent mode
    if "--agent" in args:
        idx = args.index("--agent")
        agent_type = "auto"
        rem_args = []
        if idx + 1 < len(args) and not args[idx + 1].startswith("-"):
            agent_type = args[idx + 1].lower()
            rem_args = args[idx + 2:]
        else:
            rem_args = args[idx + 1:]

        from ziskare_ai.agents import (
            AgentOrchestrator,
            CodeAgent,
            SystemAgent,
            TaskAgent,
            OptimizerAgent,
            ImageAgent,
            DesktopAgent
        )

        # Special Desktop Agent handling
        if agent_type in ["desktop", "files", "folder", "open"]:
            agent = DesktopAgent(silent=False)
            task = " ".join(rem_args) if rem_args else "open output/images"
            res = agent.execute_task(task)
            print(f"\n[Ziskare AI Desktop] {res}")
            return

        # Special Image Agent handling
        if agent_type in ["image", "img", "art", "picture"]:
            agent = ImageAgent(silent=False)
            prompt = " ".join(rem_args) if rem_args else "futuristic cyberpunk city, 8k"
            agent.generate(prompt)
            return

        # Special Optimizer handling (Can run zero-model instant mode or AI diagnostic mode)
        if agent_type in ["optimize", "optimizer", "cooling"]:
            agent = OptimizerAgent(silent=True)
            cmd = rem_args[0].lower() if rem_args else "all"

            if cmd in ["clean", "temp", "cache"]:
                print("[Ziskare AI Optimizer] Purging temporary files and caches...", flush=True)
                res = agent.clean_cache()
                print(f"  Freed Disk Space: {res['freed_mb']} MB ({res['files_removed']} files removed)")
                return

            elif cmd in ["cool", "thermal", "heat"]:
                print("[Ziskare AI Optimizer] Cooling laptop hardware and reducing wattage...", flush=True)
                res = agent.reduce_heat()
                print(f"  GPU VRAM Freed: {res['gpu_vram_freed_mb']} MB")
                print(f"  Processes Throttled: {res['throttled_processes']}")
                print(f"  CPU Usage: {res['cpu_usage_percent']}% | GPU Thermal: {res['gpu_thermal']}")
                for a in res.get("actions_taken", []):
                    print(f"  - {a}")
                return

            elif cmd in ["bench", "test", "status"]:
                print("[Ziskare AI Optimizer] Running laptop hardware benchmark...", flush=True)
                b = agent.benchmark()
                print(f"  Thermal Rating: {b['thermal_status']}")
                print(f"  CPU Usage: {b['cpu_usage_percent']}%")
                print(f"  Memory: {b['memory']['used_gb']} GB / {b['memory']['total_gb']} GB ({b['memory']['percent']}%)")
                print(f"  Disk: {b['disk']['free_gb']} GB free ({b['disk']['percent']}% used)")
                print(f"  GPU: {b['gpu']} ({b['gpu_thermal']})")
                return

            elif cmd in ["auto", "daemon"]:
                print("[Ziskare AI Optimizer] Starting silent background auto-cooling daemon...", flush=True)
                msg = agent.start_auto_cooling(interval_seconds=45)
                print(f"  {msg}")
                print("  Monitoring CPU/RAM/VRAM and keeping laptop cool. Press Ctrl+C to exit.", flush=True)
                import time
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    agent.stop_auto_cooling()
                    print("\n[Ziskare AI Optimizer] Auto-cooling daemon stopped.")
                return

            else:
                # Default 'all' - Full laptop optimization
                print("=======================================================", flush=True)
                print("       Ziskare AI - Laptop Hardware & Thermal Optimizer", flush=True)
                print("=======================================================", flush=True)
                res = agent.optimize()
                c = res["cache_clean"]
                m = res["memory_flush"]
                t = res["thermal_cool"]
                tel = res["current_telemetry"]

                gpu_name = tel.get("gpu", "N/A")
                gpu_thermal = tel.get("gpu_thermal", "N/A")
                if "(" in gpu_name:
                    gpu_name = gpu_name.split("(")[0].strip()

                gpu_temp_str = gpu_thermal
                if "(" in gpu_temp_str:
                    gpu_temp_str = gpu_temp_str.split("(")[0].strip()

                cpu = tel['cpu_usage_percent']
                mem_pct = tel['memory']['percent']
                thermal_rating = "Cool & Silent" if cpu < 45 and mem_pct < 75 else "Moderate Load" if cpu < 70 else "High Load"

                print(f"[*] Cache Cleanup:  {c['freed_mb']} MB freed ({c['files_removed']} temp files cleaned)")
                print(f"[*] Memory Flush:   {m['freed_mb']} MB RAM recovered ({m['processes_optimized']} processes trimmed)")
                print(f"[*] Thermal Cooling: GPU VRAM released ({t['gpu_vram_freed_mb']} MB)")
                print("\n-------------------------------------------------------")
                print(f"  Thermal Rating: {thermal_rating}")
                print(f"  CPU Usage:      {cpu}%")
                print(f"  RAM Memory:     {tel['memory']['used_gb']} GB / {tel['memory']['total_gb']} GB ({mem_pct}%)")
                print(f"  Disk Space:     {tel['disk']['free_gb']} GB free ({tel['disk']['percent']}% used)")
                print(f"  GPU Temp:       {gpu_temp_str} ({gpu_name})")
                print("-------------------------------------------------------")
                print("  Optimization complete. Laptop running cool & silent.")
                return

        ai = get_default_ai(silent=True)

        if agent_type == "code":
            agent = CodeAgent(ai=ai)
        elif agent_type == "system":
            agent = SystemAgent(ai=ai)
        elif agent_type == "task":
            agent = TaskAgent(ai=ai)
        else:
            agent = AgentOrchestrator(ai=ai)

        # Direct prompt
        if rem_args:
            prompt = " ".join(rem_args)
            if agent_type == "system" and ("diagnos" in prompt.lower() or "status" in prompt.lower()):
                print(agent.diagnose())
            elif agent_type == "task":
                res = agent.execute_task(prompt, verbose=True)
                print(f"\nFinal Answer:\n{res['final_answer']}")
            elif hasattr(agent, "run"):
                print(agent.run(prompt))
            return

        # Interactive Agent shell
        print(f"\n=======================================================", flush=True)
        print(f"  Ziskare AI - {agent_type.capitalize()} Agent Shell", flush=True)
        print(f"  Type 'exit' or 'quit' to close.", flush=True)
        print(f"=======================================================\n", flush=True)
        while True:
            try:
                user_input = input(f"{agent_type.capitalize()}Agent> ").strip()
                if user_input.lower() in ["exit", "quit"]:
                    break
                if not user_input:
                    continue
                if agent_type == "task":
                    res = agent.execute_task(user_input, verbose=True)
                    print(f"\nResult:\n{res['final_answer']}\n")
                elif agent_type == "system" and ("diagnos" in user_input.lower() or "status" in user_input.lower()):
                    print(agent.diagnose(), "\n")
                elif hasattr(agent, "chat"):
                    print(f"Agent: {agent.chat(user_input)}\n")
                else:
                    print(f"Agent: {agent.run(user_input)}\n")
            except KeyboardInterrupt:
                break
        return

    # REST Server mode
    if "--server" in args:
        idx = args.index("--server")
        port = 5005
        if idx + 1 < len(args) and args[idx + 1].isdigit():
            port = int(args[idx + 1])
        from ziskare_ai.server import run_server
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
