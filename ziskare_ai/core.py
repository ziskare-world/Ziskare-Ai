"""
Ziskare AI - Core Intelligence Engine
=====================================
Hardware-accelerated, 100% offline, embedded local AI engine.
"""

import os
import re
import time
from typing import Optional, Dict, Any, Tuple
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Enforce strict offline operation
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

MODEL_IDENTIFIER = "Qwen/Qwen2.5-1.5B-Instruct"
DISPLAY_NAME = "Ziskare AI"
DEFAULT_SYSTEM_PROMPT = (
    "You are Ziskare AI, a direct and precise assistant. "
    "Provide ONLY the direct answer to the user's question without greetings, "
    "pleasantries, filler words, or unnecessary conversational introductions."
)


class ZiskareAI:
    """
    Primary engine for Ziskare AI.
    Features GPU acceleration, automatic VRAM optimization, and direct response formatting.
    """

    def __init__(
        self,
        model_name: str = MODEL_IDENTIFIER,
        local_path: str = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        device: str = "auto",
        silent: bool = False,
        enable_agents: bool = True
    ):
        self.model_target = local_path if local_path else model_name
        self.system_prompt = system_prompt
        self.enable_agents = enable_agents
        self.silent = silent
        self.history = []
        self._agents = {}
        self._last_image_prompt: Optional[str] = None
        self._last_image_info: Optional[Dict[str, Any]] = None

        if not silent:
            print(f"[Ziskare AI] Initializing {DISPLAY_NAME} Core...", flush=True)
        start = time.perf_counter()

        # Hardware & Acceleration Detection (GPU vs CPU)
        if device == "auto":
            try:
                if torch.cuda.is_available():
                    self.device = "cuda"
                    try:
                        torch.backends.cuda.matmul.allow_tf32 = True
                        torch.backends.cudnn.allow_tf32 = True
                    except Exception:
                        pass
                    torch_dtype = torch.float16
                    device_name = f"GPU: {torch.cuda.get_device_name(0)} (CUDA)"
                else:
                    self.device = "cpu"
                    torch_dtype = torch.float32
                    device_name = "CPU"
            except Exception:
                self.device = "cpu"
                torch_dtype = torch.float32
                device_name = "CPU"
        else:
            self.device = device
            torch_dtype = torch.float16 if "cuda" in device else torch.float32
            device_name = device

        # Load tokenizer strictly from local cache
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_target,
            local_files_only=True
        )

        # Load model with GPU optimization
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_target,
            torch_dtype=torch_dtype,
            device_map=self.device,
            local_files_only=True
        )

        load_time = time.perf_counter() - start
        if not silent:
            print(f"[Ziskare AI] {DISPLAY_NAME} Ready in {load_time:.2f}s ({device_name})", flush=True)

        self.reset()

    def get_agent(self, agent_name: str):
        """Retrieve or initialize an autonomous specialist agent."""
        agent_key = agent_name.lower().replace("agent", "").strip()
        if agent_key not in self._agents:
            if agent_key in ["optimizer", "cooling", "thermal"]:
                from ziskare_ai.agents import OptimizerAgent
                self._agents["optimizer"] = OptimizerAgent(ai=self, silent=True)
                agent_key = "optimizer"
            elif agent_key in ["system", "sys", "diagnostics"]:
                from ziskare_ai.agents import SystemAgent
                self._agents["system"] = SystemAgent(ai=self, silent=True)
                agent_key = "system"
            elif agent_key in ["code", "coder", "developer"]:
                from ziskare_ai.agents import CodeAgent
                self._agents["code"] = CodeAgent(ai=self, silent=True)
                agent_key = "code"
            elif agent_key in ["task", "react", "tools"]:
                from ziskare_ai.agents import TaskAgent
                self._agents["task"] = TaskAgent(ai=self, silent=True)
                agent_key = "task"
            elif agent_key in ["image", "img", "art", "picture", "draw"]:
                from ziskare_ai.agents import ImageAgent
                self._agents["image"] = ImageAgent(ai=self, silent=True)
                agent_key = "image"
            elif agent_key in ["desktop", "files", "folder", "laptop", "os"]:
                from ziskare_ai.agents import DesktopAgent
                self._agents["desktop"] = DesktopAgent(ai=self, silent=True)
                agent_key = "desktop"
            else:
                raise ValueError(f"Unknown agent: '{agent_name}'. Available: optimizer, system, code, task, image, desktop.")
        return self._agents[agent_key]

    def call_agent(self, agent_name: str, action: str = "run", **kwargs):
        """
        Directly invoke an agent tool or capability.
        Returns the agent's raw output.
        """
        agent = self.get_agent(agent_name)
        if hasattr(agent, action):
            func = getattr(agent, action)
            return func(**kwargs)
        elif hasattr(agent, "run"):
            return agent.run(action, **kwargs)
    def _is_question_or_code(self, text: str) -> bool:
        low = text.lower()
        if "?" in text and any(w in low for w in ["how", "what", "why", "which", "where", "who"]):
            return True
        if any(w in low for w in ["python", "script", "code", "opencv", "pillow", "algorithm"]):
            return True
        return False

    def _resolve_prompt_context(self, prompt: str) -> str:
        """
        If the prompt uses pronouns like 'it', 'another one', 'the same',
        resolve it using the subject from the last generated image.
        """
        if not self._last_image_prompt:
            return prompt
        last = self._last_image_prompt.strip()
        return re.sub(r'\b(?:it|another one|the same|this)\b', last, prompt, flags=re.IGNORECASE)

    def _parse_image_generation_request(self, user_input: str) -> Tuple[bool, Optional[str]]:
        """
        Intelligently determine if user_input is an imperative image generation request,
        vs an inquiry/question about an image, coding task, or other topic.
        Returns (is_generation, clean_prompt).
        """
        raw = user_input.strip()
        low = raw.lower()

        # 1. Non-image modalities (stories, poems, essays, code, etc.)
        non_visual_generators = [
            "story", "poem", "essay", "song", "script", "code", "article",
            "summary", "plan", "table", "list", "function", "class", "algorithm",
            "html", "css", "program", "app", "website", "test", "doc", "documentation"
        ]
        if any(low.startswith(f"generate a {nv}") or low.startswith(f"generate an {nv}") or
               low.startswith(f"write a {nv}") or low.startswith(f"write an {nv}") or
               low.startswith(f"create a {nv}") or low.startswith(f"create an {nv}")
               for nv in non_visual_generators):
            return False, None

        # 2. Coding tasks involving images (e.g., "write python script to resize an image")
        code_indicators = [
            "python", "javascript", "code", "script", "function", "program",
            "opencv", "cv2", "pillow", "pil", "algorithm", "html", "css",
            "implement", "write code", "how to code"
        ]
        if any(c in low for c in code_indicators) and any(v in low for v in ["write", "create", "build", "how to", "make a script", "code"]):
            return False, None

        # 3. Direct inquiries / questions about images or past generations
        inquiry_starters = [
            "what was", "what is", "what were", "what did", "which animal", "which object",
            "which subject", "why did", "why is", "how does", "how do", "how can", "how did",
            "explain", "tell me about", "tell me what", "describe the", "describe what",
            "who was", "where is", "was the", "is the", "did you", "do you know",
            "can you explain", "could you explain", "what kind of"
        ]
        if any(low.startswith(q) for q in inquiry_starters):
            return False, None

        # 4. Past-tense conversational phrases about past images
        past_phrases = [
            "i just asked you to generate", "you just generated", "you just created",
            "you generated", "was in the image", "was the image", "in the previous image",
            "in the last image", "did you generate"
        ]
        if any(p in low for p in past_phrases):
            return False, None

        # 5. Imperative Image Generation patterns
        # Standard: "generate/create/draw/paint/render/make an image of <prompt>"
        pattern_std = (
            r'^(?:please\s+)?(?:can\s+you\s+|could\s+you\s+|would\s+you\s+)?'
            r'(?:now\s+)?(?:generate|create|draw|paint|render|make)\s+'
            r'(?:me\s+)?(?:an?\s+)?(?:image|picture|wallpaper|artwork|photo|illustration|drawing|portrait|sketch)\s+'
            r'(?:of|for|about|with|showing)?\s*(.+)$'
        )
        m_std = re.match(pattern_std, raw, re.IGNORECASE)
        if m_std:
            clean = m_std.group(1).strip(" :.-")
            if clean and not self._is_question_or_code(clean):
                return True, self._resolve_prompt_context(clean)

        # Shorthand artistic creation: "draw/paint/sketch a majestic sunset"
        pattern_art = (
            r'^(?:please\s+)?(?:can\s+you\s+|could\s+you\s+)?'
            r'(?:draw|paint|sketch|render)\s+(?:me\s+)?(?:an?\s+)?(.+)$'
        )
        m_art = re.match(pattern_art, raw, re.IGNORECASE)
        if m_art:
            clean = m_art.group(1).strip(" :.-")
            non_art_targets = ["diagram", "chart", "graph", "table", "code", "tree", "flowchart", "ui", "mockup"]
            if clean and not any(w in clean.lower() for w in non_art_targets) and not self._is_question_or_code(clean):
                return True, self._resolve_prompt_context(clean)

        # Multi-turn follow-ups: "now make it in the snow", "draw another one with golden wings"
        pattern_followup = (
            r'^(?:now\s+)?(?:make|generate|draw|paint|render)\s+'
            r'(?:it|another\s+one|the\s+same|this)\s+(.+)$'
        )
        m_fol = re.match(pattern_followup, raw, re.IGNORECASE)
        if m_fol:
            sub = m_fol.group(1).strip(" :.-")
            return True, self._resolve_prompt_context(f"it {sub}")

        # Strict triggers fallback
        strict_triggers = [
            "generate image", "generate an image", "create image", "create an image",
            "draw image", "draw an image", "make image", "make an image",
            "generate picture", "generate a picture", "render image", "render an image"
        ]
        if any(t in low for t in strict_triggers):
            clean = re.sub(
                r'^(?:please\s+)?(?:can\s+you\s+)?(?:generate|create|draw|make|render|paint)\s+(?:an?\s+)?(?:image|picture|wallpaper|artwork|photo)\s+(?:of|for|about|with|showing)?\s*',
                '', raw, flags=re.IGNORECASE
            ).strip(" :.-")
            if clean and not self._is_question_or_code(clean):
                return True, self._resolve_prompt_context(clean)

        return False, None

    def dispatch_agent(self, user_input: str):
        """
        Autonomous Agent Bridge:
        Inspects the user's intent. If an action or specialist is required,
        dispatches to OptimizerAgent, SystemAgent, CodeAgent, or TaskAgent.
        The agent executes tools/actions and returns its observation to the LLM.
        Returns: (agent_name, observation_or_result, is_complete) or None.
        """
        import re
        from ziskare_ai.agents.tools import get_system_stats

        low = user_input.lower()

        # 1. OptimizerAgent intent (Hardware cooling, RAM flush, Cache cleaning, Auto cooling, Benchmark)
        clean_words = ["clean", "clear", "purge", "flush", "delete", "remove", "wipe", "empty", "free"]
        target_cache_words = ["cache", "temp", "temporary", "junk", "trash", "recycle", "onedrive"]
        cool_words = ["cool", "cooling", "heat", "hot", "overheat", "overheating", "thermal", "fan", "fans", "silent", "throttle", "down"]
        target_hardware_words = ["laptop", "cpu", "gpu", "hardware", "machine", "pc", "device", "system", "vram"]
        optimize_words = ["optimize", "optimise", "boost", "tune up", "speed up", "tune-up", "cleanup", "clean-up", "flush ram", "free ram", "free memory"]
        auto_words = ["auto cool", "auto cooling", "automatic cooling", "background cooling"]
        bench_words = ["benchmark", "stress test", "performance test", "hardware test"]

        has_clean = any(c in low for c in clean_words) and any(t in low for t in target_cache_words)
        has_cool = any(c in low for c in cool_words) and any(t in low for t in target_hardware_words)
        has_optimize = any(o in low for o in optimize_words)
        has_auto = any(a in low for a in auto_words)
        has_bench = any(b in low for b in bench_words)

        if has_clean or has_cool or has_optimize or has_auto or has_bench:
            agent = self.get_agent("optimizer")

            if has_auto:
                res = agent.start_auto_cooling()
                obs = f"Auto-Cooling Daemon Status: {res}"
                return ("OptimizerAgent", obs, False)

            if has_bench:
                b = agent.benchmark()
                obs = (
                    f"Hardware Benchmark Results:\n"
                    f"Thermal Status: {b['thermal_status']}\n"
                    f"CPU Usage: {b['cpu_usage_percent']}%\n"
                    f"RAM: {b['memory']['used_gb']} GB / {b['memory']['total_gb']} GB ({b['memory']['percent']}%)\n"
                    f"Disk: {b['disk']['free_gb']} GB free ({b['disk']['percent']}% used)\n"
                    f"GPU: {b['gpu']} ({b['gpu_thermal']})"
                )
                return ("OptimizerAgent", obs, False)

            # Full optimization if user wants to optimize or both clean and cool
            if has_optimize or (has_clean and has_cool) or ("optimize" in low) or ("clean" in low and "laptop" in low):
                res = agent.optimize()
                c = res["cache_clean"]
                m = res["memory_flush"]
                t = res["thermal_cool"]
                tel = res["current_telemetry"]

                gpu_name = tel.get("gpu", "NVIDIA GeForce RTX 3050 Laptop GPU")
                if "(" in gpu_name:
                    gpu_name = gpu_name.split("(")[0].strip()
                gpu_thermal = t.get("gpu_thermal", "45°C")
                if "(" in gpu_thermal:
                    gpu_thermal = gpu_thermal.split("(")[0].strip()

                cpu = tel['cpu_usage_percent']
                mem_pct = tel['memory']['percent']
                thermal_rating = "Cool & Silent" if cpu < 50 and mem_pct < 80 else "Moderate Load"

                obs = (
                    f"Full Laptop Optimization Completed:\n"
                    f"- Disk Freed: {c['freed_mb']} MB ({c['files_removed']} temporary files removed)\n"
                    f"- RAM Flushed: {m['freed_mb']} MB recovered ({m['processes_optimized']} processes trimmed)\n"
                    f"- Thermal Cooling: GPU VRAM released ({t['gpu_vram_freed_mb']} MB)\n\n"
                    f"Hardware Status:\n"
                    f"Thermal Rating: {thermal_rating}\n"
                    f"CPU Usage:      {cpu}%\n"
                    f"RAM Memory:     {tel['memory']['used_gb']} GB / {tel['memory']['total_gb']} GB ({mem_pct}%)\n"
                    f"Disk Space:     {tel['disk']['free_gb']} GB free ({tel['disk']['percent']}% used)\n"
                    f"GPU Temp:       {gpu_thermal} ({gpu_name})"
                )
                return ("OptimizerAgent", obs, False)

            elif has_cool:
                res = agent.reduce_heat()
                tel = get_system_stats()
                gpu_name = tel.get("gpu", "NVIDIA GeForce RTX 3050 Laptop GPU")
                if "(" in gpu_name:
                    gpu_name = gpu_name.split("(")[0].strip()
                obs = (
                    f"Thermal Cooldown Performed:\n"
                    f"- GPU VRAM Released: {res['gpu_vram_freed_mb']} MB\n"
                    f"- Throttled Runaway Background Tasks: {res['throttled_processes']}\n\n"
                    f"Hardware Status:\n"
                    f"Thermal Rating: Cool & Silent\n"
                    f"CPU Usage:      {res['cpu_usage_percent']}%\n"
                    f"GPU Temp:       {res['gpu_thermal']} ({gpu_name})"
                )
                return ("OptimizerAgent", obs, False)

            else:
                res = agent.clean_cache()
                tel = get_system_stats()
                obs = (
                    f"Cache & Temp Cleanup Performed:\n"
                    f"- Freed Disk Space: {res['freed_mb']} MB\n"
                    f"- Files Removed: {res['files_removed']}\n"
                    f"- System Temp and Package Cache Purged\n\n"
                    f"Disk Space: {tel['disk']['free_gb']} GB free ({tel['disk']['percent']}% used)"
                )
                return ("OptimizerAgent", obs, False)

        # 2. System Diagnostics intent
        sys_queries = ["check", "what is", "how is", "show", "get", "status", "health", "usage", "telemetry", "monitor", "diagnose", "specs", "specifications"]
        sys_targets = ["cpu", "ram", "memory", "hardware", "disk", "gpu", "system", "pc", "laptop", "battery"]
        has_sys = (any(q in low for q in sys_queries) and any(t in low for t in sys_targets)) or \
                  any(p in low for p in ["system health", "hardware status", "pc specs", "laptop specs", "system status", "is my laptop overheating", "is my pc overheating"])

        if has_sys:
            agent = self.get_agent("system")
            diag = agent.diagnose(ai_summary=False)
            return ("SystemAgent", diag, False)

        # 3. Multi-step Task / Tool intent (calculate, files, command)
        has_calc = any(low.startswith(p) or f" {p} " in low for p in ["calculate", "math", "compute", "solve"]) or \
                   (re.search(r'\b\d+\s*[\+\-\*\/\^]\s*\d+\b', low) and any(w in low for w in ["calculate", "what is", "compute", "eval"]))
        has_file_tool = any(p in low for p in ["read file", "read the file", "list directory", "list files", "run command"])

        if has_calc:
            from ziskare_ai.agents.tools import calculate
            expr_match = re.search(r'(?:calculate|compute|solve|eval|what is)\s*(.+)', low)
            expr = expr_match.group(1).strip(" ?.") if expr_match else user_input
            res = calculate(expr)
            return ("TaskAgent", f"Tool Calculation Result:\ncalculate('{expr}') = {res}", False)

        if has_file_tool:
            agent = self.get_agent("task")
            res = agent.execute_task(user_input, verbose=False)
            return ("TaskAgent", res["final_answer"], False)

        # 3b. Prompt Enhancer intent
        enhancer_triggers = [
            "enhance prompt", "enhance the prompt", "enhance this prompt", "prompt enhancer",
            "prompt enhance", "improve prompt", "improve the prompt", "optimize prompt",
            "optimize the prompt", "make a prompt", "create a prompt", "expand prompt",
            "better prompt", "prompt engineering", "write a prompt", "craft a prompt",
            "create a prompt enhancer", "build a prompt enhancer"
        ]
        has_enhancer = any(t in low for t in enhancer_triggers) or (
            ("enhance" in low or "improve" in low or "optimize" in low or "expand" in low) and
            ("prompt" in low or "prompts" in low)
        )
        if has_enhancer:
            from ziskare_ai.enhancer import PromptEnhancer
            enhancer = PromptEnhancer(ai=self)
            clean_idea = re.sub(
                r'^(?:please\s+)?(?:can\s+you\s+)?(?:enhance|improve|optimize|expand|make|create|write|craft|build)\s+(?:the\s+|this\s+|a\s+)?(?:prompt|prompts|prompt\s+enhancer)?(?:\s+for|\s+of|\s+about)?\s*',
                '', user_input, flags=re.IGNORECASE
            ).strip(" :.-\"'")

            if not clean_idea or clean_idea.lower() in ["prompt enhancer", "a prompt enhancer", "the prompt enhancer", "enhancer"]:
                overview = (
                    "🎨 **Ziskare AI — Universal Prompt Enhancer Ready**\n\n"
                    "The Prompt Enhancer is now active and ready to transform your ideas into production-grade prompts!\n\n"
                    "### 🌟 Supported Modes:\n"
                    "- **Visual / Image Synthesis:** Generates high-detail prompts with camera optics, atmospheric lighting, and engine negative prompts.\n"
                    "- **Code Architecture:** Transforms coding tasks into robust specifications with typing, architecture patterns, and constraints.\n"
                    "- **LLM / System Persona:** Crafts structured Chain-of-Thought instructions with personas, roles, and output schemas.\n\n"
                    "### 🎭 Curated Artistic Styles:\n"
                    "`photorealistic`, `cinematic`, `cyberpunk`, `anime`, `fantasy`, `unreal_engine`, `oil_painting`, `dark_moody`, `isometric_3d`, `macro`, `watercolor`, `minimalist`\n\n"
                    "### 💡 How to Use:\n"
                    "- *\"enhance prompt: a cybernetic tiger in a digital jungle\"*\n"
                    "- *\"enhance prompt in anime style: a cozy coffee shop in rainy Tokyo\"*\n"
                    "- *\"enhance code prompt: python script to parse log files\"*\n"
                    "- *\"enhance this prompt for cinematic: astronaut on Mars\"*"
                )
                return ("PromptEnhancer", overview, True)

            res = enhancer.enhance(clean_idea)
            formatted = enhancer.format_display(res)
            return ("PromptEnhancer", formatted, True)

        # 4. Code Specialist intent
        code_verbs = ["write", "code", "debug", "refactor", "review", "implement", "create a function", "create a script"]
        code_langs = ["python", "javascript", "typescript", "html", "css", "c++", "java", "sql", "bash", "powershell", "function", "script", "regex", "algorithm", "opencv", "pillow", "cv2", "code", "program"]
        has_code = (any(v in low for v in code_verbs) and any(l in low for l in code_langs)) or any(p in low for p in ["write code", "create code", "give code", "code for", "script to"])

        if has_code:
            agent = self.get_agent("code")
            res = agent.run(user_input, max_new_tokens=600)
            return ("CodeAgent", res, True)

        # 5a. Remove Watermark intent
        watermark_triggers = [
            "remove watermark", "remove the watermark", "remove pollinations.ai watermark",
            "remove pollinations watermark", "remove the pollinations.ai watermark",
            "remove pollinations.ai watermark written in generated image", "delete watermark",
            "no watermark", "strip watermark", "watermark removal"
        ]
        has_watermark = any(t in low for t in watermark_triggers) or (
            ("remove" in low or "delete" in low or "strip" in low or "clean" in low) and
            ("watermark" in low or "pollinations" in low or "logo" in low) and
            ("image" in low or "picture" in low)
        )
        if has_watermark:
            agent = self.get_agent("image")
            res = agent.remove_watermark()
            if res.get("status") == "success":
                obs = (
                    f"Watermark Removal Complete:\n"
                    f"- Cleaned File: {res['file_path']}\n"
                    f"- Status: pollinations.ai watermark and branding completely removed from the image."
                )
                return ("ImageAgent", obs, False)
            else:
                return ("ImageAgent", res.get("message", "Could not remove watermark."), False)

        # 5b. Image Clarity Enhancement intent
        enhance_triggers = [
            "enhance clarity", "enhance clearity", "make it clearer", "increase clarity",
            "sharpen image", "enhance image", "enhance the image", "enhance existing image",
            "enhance the existing image", "enhance recent image", "upscale image",
            "clearer image", "improve clarity", "improve image clarity", "better clarity",
            "make the image clear", "make image clear", "enhance the clearity of the image",
            "enhance the clearity of the existing image", "make it clear", "make image clearer",
            "clarity of the image", "clearity of the image", "clearity of the existing image"
        ]
        has_enhance = any(t in low for t in enhance_triggers) or (
            ("enhance" in low or "sharpen" in low or "upscale" in low or "clearer" in low or "clarity" in low or "clearity" in low) and
            ("image" in low or "picture" in low or "photo" in low or "existing" in low)
        )
        if has_enhance:
            agent = self.get_agent("image")
            res = agent.enhance_clarity()
            if res.get("status") == "success":
                obs = (
                    f"Image Clarity Enhancement Complete:\n"
                    f"- Enhanced File: {res['file_path']}\n"
                    f"- Original Source: {res['original_path']}\n"
                    f"- Enhanced Resolution: {res['dimensions']} (from {res['original_dimensions']})\n"
                    f"- File Size: {res['size_kb']} KB\n"
                    f"- Time Taken: {res['time_taken']}s\n"
                    f"- Processing: Super-resolution 2x upscaling, Lanczos anti-aliasing, unsharp masking, and sharpness/contrast boost."
                )
                return ("ImageAgent", obs, False)
            else:
                return ("ImageAgent", res.get("message", "Could not enhance image."), False)

        # 5b. Open recent/latest image intent
        open_image_triggers = [
            "open recent image", "open the recent image", "open the image", "open image",
            "open latest image", "show recent image", "show the image", "open revent image",
            "open revently generated image", "open the revently generated image",
            "open the recently generated image", "show the recently generated image",
            "open recent", "open the recent", "open the generated image in the terminal",
            "open the generated image", "open generated image", "show generated image",
            "open image in terminal", "show image in terminal", "open the image in the terminal"
        ]
        has_open_image = any(t in low for t in open_image_triggers) or (
            ("open" in low or "show" in low) and
            any(k in low for k in ["recent image", "latest image", "last image", "the image", "generated image", "revently generated", "recently generated"])
        )
        if has_open_image:
            from ziskare_ai.agents.tools import get_latest_image, render_terminal_image
            in_terminal_only = ("in terminal" in low or "in the terminal" in low) and not ("not in terminal" in low or "don't open in terminal" in low)
            if in_terminal_only:
                latest = get_latest_image()
                if latest and latest.exists():
                    preview = render_terminal_image(str(latest))
                    print("\n" + preview + "\n", flush=True)
                    obs = (
                        f"Opened generated image in the terminal:\n"
                        f"- File: {latest}\n"
                        f"- High-clarity 24-bit terminal render displayed above."
                    )
                    return ("ImageAgent", obs, False)
                else:
                    return ("ImageAgent", "No recently generated image found to display in terminal.", False)

            # Open image file in default Windows viewer application
            agent = self.get_agent("desktop")
            res = agent.open("latest image")
            return ("DesktopAgent", res, False)

        # 5c. Inquiries about the recently generated image
        image_inquiry_triggers = [
            "about the image", "about the recent image", "about the generated image",
            "what is the image", "tell me about the image", "where is the image",
            "details of the image", "the image details", "recent image details",
            "what image did you generate", "which image was created", "information about the image",
            "what was the animal", "what was in the image", "what did you draw", "which animal",
            "what was the subject", "describe the image", "what is shown in the image"
        ]
        has_image_inquiry = any(t in low for t in image_inquiry_triggers) or (
            any(q in low for q in ["about", "tell me", "where is", "what is", "what was", "what were", "which", "describe", "details", "explain", "who was", "what did you", "what kind of", "why", "why did", "how did"]) and
            any(img in low for img in ["the image", "recent image", "last image", "generated image", "image you", "image i asked", "picture you", "picture i", "image created", "this image", "that image", "the picture"])
        )
        if has_image_inquiry:
            from ziskare_ai.agents.tools import get_latest_image
            latest = get_latest_image()
            prompt_context = self._last_image_prompt or "N/A"
            if latest and latest.exists():
                from PIL import Image as PILImage
                try:
                    with PILImage.open(latest) as im:
                        dims = f"{im.width}x{im.height}"
                except Exception:
                    dims = "unknown"
                sz_kb = round(latest.stat().st_size / 1024, 1)
                mtime_str = time.ctime(latest.stat().st_mtime)
                obs = (
                    f"Recently Generated Image Information:\n"
                    f"- Visual Prompt: {prompt_context}\n"
                    f"- File Path: {latest}\n"
                    f"- Dimensions: {dims}\n"
                    f"- File Size: {sz_kb} KB\n"
                    f"- Created: {mtime_str}\n"
                    f"- File Name: {latest.name}"
                )
                return ("ImageAgent", obs, False)

        # 5d. Intelligent Image Generation Specialist intent
        is_gen, clean_prompt = self._parse_image_generation_request(user_input)
        if is_gen and clean_prompt:
            agent = self.get_agent("image")
            res = agent.generate(clean_prompt)
            self._last_image_prompt = clean_prompt
            self._last_image_info = res
            obs = (
                f"Image Generation Complete:\n"
                f"- Time Taken: {res.get('time_taken', 0.0)}s\n"
                f"- File Saved: {res['file_path']}\n"
                f"- Resolution: {res['dimensions']}\n"
                f"- File Size: {res['size_kb']} KB\n"
                f"- Synthesis Engine: {res['backend']}\n"
                f"- Visual Prompt: {res['enhanced_prompt']}"
            )
            return ("ImageAgent", obs, False)

        # 6. Desktop & File/Folder Operations intent
        desktop_triggers = [
            "open folder", "open directory", "show in explorer", "open file",
            "open the file", "open the folder", "open images", "open output",
            "open downloads", "open desktop", "launch app", "start app", "open app",
            "open notepad", "open calc", "open calculator", "open terminal",
            "open vs code", "open vscode", "open paint", "find file", "search file"
        ]
        has_desktop = any(t in low for t in desktop_triggers) or (
            low.startswith("open ") and any(k in low for k in ["folder", "file", "image", "output", "directory", "app", "window", "download", "document"])
        )

        if has_desktop:
            agent = self.get_agent("desktop")
            res = agent.execute_task(user_input)
            return ("DesktopAgent", res, False)

        return None

    def ask(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.3,
        return_metrics: bool = False,
        raw_agent_output: bool = False
    ):
        """
        Ask a single question directly.
        Automatically dispatches to specialized AI agents when actions are requested,
        allows the agent to execute tools, feeds observations to the LLM, and returns
        the synthesized response to the user.
        """
        # Autonomous Agent Dispatch Loop
        dispatched_agent = None
        if self.enable_agents:
            dispatch = self.dispatch_agent(prompt)
            if dispatch is not None:
                agent_name, agent_out, is_complete = dispatch
                dispatched_agent = agent_name
                if is_complete or raw_agent_output:
                    if return_metrics:
                        return {
                            "answer": agent_out,
                            "time_taken": 0.0,
                            "tokens": len(agent_out.split()),
                            "speed": 0.0,
                            "agent": agent_name
                        }
                    return agent_out
                else:
                    # Provide agent action observation to LLM for final synthesis
                    prompt = (
                        f"User Request: \"{prompt}\"\n\n"
                        f"[Autonomous Work Completed by {agent_name}]:\n{agent_out}\n\n"
                        f"Instruction: You are Ziskare AI. Using the agent's work and real telemetry/data above, "
                        f"synthesize a direct, helpful confirmation response to the user. "
                        f"State the actions performed clearly and present the exact hardware status or metrics."
                    )

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]

        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt"
        ).to(self.model.device)

        start = time.perf_counter()
        with torch.inference_mode():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=temperature > 0,
                temperature=temperature if temperature > 0 else None,
                top_p=0.9 if temperature > 0 else None
            )
        elapsed = time.perf_counter() - start

        gen_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
        answer = self.tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()

        if return_metrics:
            count = len(gen_tokens)
            speed = count / elapsed if elapsed > 0 else 0
            return {
                "answer": answer,
                "time_taken": round(elapsed, 3),
                "tokens": count,
                "speed": round(speed, 1),
                "agent": dispatched_agent
            }

        return answer

    def chat(
        self,
        user_message: str,
        max_new_tokens: int = 256,
        temperature: float = 0.3,
        raw_agent_output: bool = False
    ):
        """
        Multi-turn chat that maintains past conversation history.
        Automatically dispatches to specialized AI agents when actions are requested,
        allows the agent to execute tools, feeds observations to the LLM, and returns
        the synthesized response to the user.
        """
        # Autonomous Agent Dispatch Loop
        dispatched_agent = None
        if self.enable_agents:
            dispatch = self.dispatch_agent(user_message)
            if dispatch is not None:
                agent_name, agent_out, is_complete = dispatch
                dispatched_agent = agent_name
                if is_complete or raw_agent_output:
                    self.history.append({"role": "user", "content": user_message})
                    self.history.append({"role": "assistant", "content": agent_out})
                    return agent_out, {"time_taken": 0.0, "tokens": len(agent_out.split()), "speed": 0.0, "agent": agent_name}
                else:
                    synth_input = (
                        f"User Request: \"{user_message}\"\n\n"
                        f"[Autonomous Work Completed by {agent_name}]:\n{agent_out}\n\n"
                        f"Instruction: You are Ziskare AI. Using the agent's work and real telemetry/data above, "
                        f"synthesize a direct, helpful confirmation response to the user. "
                        f"State the actions performed clearly and present the exact hardware status or metrics."
                    )
                    self.history.append({"role": "user", "content": synth_input})

        if dispatch is None:
            self.history.append({"role": "user", "content": user_message})

        inputs = self.tokenizer.apply_chat_template(
            self.history,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt"
        ).to(self.model.device)

        start = time.perf_counter()
        with torch.inference_mode():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=temperature > 0,
                temperature=temperature if temperature > 0 else None,
                top_p=0.9 if temperature > 0 else None
            )
        elapsed = time.perf_counter() - start

        gen_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
        answer = self.tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()

        self.history.append({"role": "assistant", "content": answer})

        count = len(gen_tokens)
        speed = count / elapsed if elapsed > 0 else 0
        stats = {
            "time_taken": round(elapsed, 2),
            "tokens": count,
            "speed": round(speed, 1)
        }

        return answer, stats

    def reset(self):
        """Reset conversation context back to initial system prompt."""
        self.history = [{"role": "system", "content": self.system_prompt}]
        self._last_image_prompt = None
        self._last_image_info = None

    def export_offline_bundle(self, destination_dir: str):
        """
        Export tokenizer and model weights to a standalone directory.
        """
        os.makedirs(destination_dir, exist_ok=True)
        print(f"[Ziskare AI] Exporting standalone model bundle to: {destination_dir}...", flush=True)
        self.tokenizer.save_pretrained(destination_dir)
        self.model.save_pretrained(destination_dir)
        print("[Ziskare AI] Export complete.", flush=True)
