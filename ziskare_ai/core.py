"""
Ziskare AI - Core Intelligence Engine
=====================================
Hardware-accelerated, 100% offline, embedded local AI engine.
"""

import os
import time
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
        silent: bool = False
    ):
        self.model_target = local_path if local_path else model_name
        self.system_prompt = system_prompt
        self.history = []

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

    def ask(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.3,
        return_metrics: bool = False
    ):
        """
        Ask a single question directly without maintaining previous conversation context.
        """
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
                "speed": round(speed, 1)
            }

        return answer

    def chat(
        self,
        user_message: str,
        max_new_tokens: int = 256,
        temperature: float = 0.3
    ):
        """
        Multi-turn chat that maintains past conversation history.
        """
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

    def export_offline_bundle(self, destination_dir: str):
        """
        Export tokenizer and model weights to a standalone directory.
        """
        os.makedirs(destination_dir, exist_ok=True)
        print(f"[Ziskare AI] Exporting standalone model bundle to: {destination_dir}...", flush=True)
        self.tokenizer.save_pretrained(destination_dir)
        self.model.save_pretrained(destination_dir)
        print("[Ziskare AI] Export complete.", flush=True)
