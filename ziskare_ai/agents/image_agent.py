"""
Ziskare AI - Image Agent
========================
Specialist AI Agent for image generation, visual prompt engineering, and artistic rendering.
Supports local diffusers, zero-key neural image synthesis, and 100% offline procedural rendering.
"""

import os
import time
import math
import hashlib
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional, Any, Dict
from PIL import Image, ImageDraw

from ziskare_ai.agents.base import BaseAgent
from ziskare_ai.agents.tools import (
    DEFAULT_WORKSPACE,
    TerminalLoader,
    render_terminal_image,
    open_path
)

IMAGE_SYSTEM_PROMPT = (
    "You are the Ziskare Image Agent, an elite AI visual artist, prompt engineer, and graphics specialist. "
    "Your specialty is crafting photorealistic, artistic, and visually stunning image prompts, "
    "configuring rendering parameters, and generating high-resolution imagery."
)


class ImageAgent(BaseAgent):
    """
    Autonomous image generation and visual synthesis specialist.
    Supports local diffusers pipelines, neural cloud synthesis, and offline procedural art.
    """

    def __init__(
        self,
        ai: Optional[Any] = None,
        output_dir: Optional[str] = None,
        silent: bool = False
    ):
        super().__init__(
            name="ImageAgent",
            role="AI Visual Artist & Image Synthesizer",
            system_prompt=IMAGE_SYSTEM_PROMPT,
            ai=ai,
            tools={},
            temperature=0.3,
            silent=silent
        )
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = DEFAULT_WORKSPACE / "output" / "images"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def enhance_prompt(self, user_prompt: str, style: str = "photorealistic") -> str:
        """
        Uses the Ziskare LLM to optimize and expand a user prompt into a high-detail generative prompt.
        """
        task = (
            f"Transform the following image idea into a detailed, high-quality prompt for an image generator:\n"
            f"User Idea: \"{user_prompt}\"\n"
            f"Desired Style: {style}\n\n"
            f"Output ONLY the enhanced prompt string without explanations, quotes, or conversational preamble."
        )
        try:
            enhanced = self.run(task, max_new_tokens=150).strip().strip('"\'')
            # Clean any model preamble
            if ":" in enhanced and len(enhanced.split(":")[0]) < 30:
                enhanced = enhanced.split(":", 1)[1].strip()
            return enhanced if enhanced else user_prompt
        except Exception:
            # Fallback prompt enrichment
            return f"{user_prompt}, highly detailed, {style}, sharp focus, 8k resolution, cinematic lighting"

    def enhance_clarity(self, image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Enhance clarity, resolution, and sharpness of an existing or recently generated image.
        """
        from ziskare_ai.agents.tools import enhance_image_clarity
        return enhance_image_clarity(image_path=image_path, output_dir=str(self.output_dir))

    def generate(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        style: str = "photorealistic",
        backend: str = "auto",
        output_path: Optional[str] = None,
        enhance: bool = True,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Text description of the desired image.
            width: Image width in pixels (default 1024).
            height: Image height in pixels (default 1024).
            style: Artistic style (photorealistic, cyberpunk, anime, oil painting, fantasy, etc.).
            backend: 'auto', 'neural', 'diffusers', or 'procedural'.
            output_path: Specific filepath to save image (optional).
            enhance: Whether to enhance the prompt using LLM prompt engineering.
            seed: Random seed for reproducible generation.
        """
        if output_path:
            out_file = Path(output_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            clean_name = "".join(c if c.isalnum() else "_" for c in prompt[:25]).strip("_")
            out_file = self.output_dir / f"ziskare_{clean_name}_{timestamp}.png"

        enhanced_prompt = prompt
        if enhance:
            if not self.silent:
                print(f"[ImageAgent] Enhancing prompt with visual parameters...", flush=True)
            enhanced_prompt = self.enhance_prompt(prompt, style=style)

        backend_used = backend
        success = False
        elapsed = 0.0

        # Beautiful animated loader showing live elapsed time
        loader = TerminalLoader("Generating image")
        if not self.silent:
            loader.start()

        try:
            # 1. Try local diffusers if requested or available
            if backend in ["diffusers", "local"]:
                success = self._generate_diffusers(enhanced_prompt, width, height, out_file)
                backend_used = "diffusers"

            # 2. Auto / Neural backend
            if not success and backend in ["auto", "neural", "pollinations"]:
                success = self._generate_neural(enhanced_prompt, width, height, out_file, seed=seed)
                if success:
                    backend_used = "neural"

            # 3. Offline Procedural Fallback
            if not success:
                self._generate_procedural(enhanced_prompt, width, height, out_file)
                backend_used = "procedural"
                success = True
        finally:
            if not self.silent:
                loader.stop()
            elapsed = round(loader.elapsed, 2)

        file_size = out_file.stat().st_size if out_file.exists() else 0

        # Render ultra-clear terminal visual preview and open image on desktop
        terminal_preview = ""
        try:
            terminal_preview = render_terminal_image(str(out_file), elapsed_time=elapsed)
            if not self.silent:
                print(f"\n\033[1;32m✨ Image generated in {elapsed:.1f}s\033[0m \033[90m({width}x{height} | {backend_used})\033[0m", flush=True)
                print(terminal_preview, flush=True)
                print(f"\033[1m📁 Saved:\033[0m {out_file} ({file_size / 1024:.1f} KB)\n", flush=True)
            try:
                open_path(str(out_file))
            except Exception:
                pass
        except Exception:
            if not self.silent:
                print(f"\n[ImageAgent] Image generated in {elapsed:.1f}s -> {out_file} ({file_size / 1024:.1f} KB)", flush=True)

        return {
            "status": "success",
            "file_path": str(out_file),
            "terminal_preview": terminal_preview,
            "prompt": prompt,
            "enhanced_prompt": enhanced_prompt,
            "backend": backend_used,
            "dimensions": f"{width}x{height}",
            "size_bytes": file_size,
            "size_kb": round(file_size / 1024, 1),
            "time_taken": elapsed
        }

    def _generate_neural(
        self,
        prompt: str,
        width: int,
        height: int,
        out_path: Path,
        seed: Optional[int] = None
    ) -> bool:
        """Fetch neural image via high-quality endpoint."""
        try:
            encoded_prompt = urllib.parse.quote(prompt)
            seed_param = f"&seed={seed}" if seed is not None else ""
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true{seed_param}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                if len(data) > 500:
                    with open(out_path, "wb") as f:
                        f.write(data)
                    return True
        except Exception:
            pass
        return False

    def _generate_diffusers(
        self,
        prompt: str,
        width: int,
        height: int,
        out_path: Path
    ) -> bool:
        """Run local offline diffusers pipeline if installed."""
        try:
            from diffusers import AutoPipelineForText2Image
            import torch

            device = "cuda" if torch.cuda.is_available() else "cpu"
            pipe = AutoPipelineForText2Image.from_pretrained(
                "stabilityai/sd-turbo",
                torch_dtype=torch.float16 if device == "cuda" else torch.float32
            ).to(device)

            image = pipe(prompt=prompt, width=min(width, 512), height=min(height, 512), num_inference_steps=2).images[0]
            image.save(out_path)
            return True
        except Exception:
            return False

    def _generate_procedural(
        self,
        prompt: str,
        width: int,
        height: int,
        out_path: Path
    ):
        """
        100% Offline algorithmic art generator using PIL.
        Creates an aesthetic visual wallpaper with harmonic gradient fields and celestial geometry
        seeded by the prompt hash.
        """
        # Deterministic seed from prompt
        h = int(hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:8], 16)
        hue_base = (h % 360) / 360.0

        # Create gradient canvas
        img = Image.new("RGB", (width, height), (15, 15, 25))
        draw = ImageDraw.Draw(img)

        # Draw vertical harmonic gradient
        for y in range(height):
            ratio = y / float(height)
            r = int(25 + 180 * math.sin(ratio * math.pi + hue_base * 6.28))
            g = int(20 + 120 * math.sin(ratio * math.pi * 1.5 + 1.0))
            b = int(45 + 200 * math.cos(ratio * math.pi * 0.8))
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Central artistic focal sphere / orb
        cx, cy = width // 2, height // 2
        radius = min(width, height) // 4
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=(255, max(80, int(200 * (1 - hue_base))), 140),
            outline=(255, 240, 200),
            width=3
        )

        # Ambient celestial rings
        for i in range(1, 4):
            r_ring = radius + i * 35
            draw.ellipse(
                [cx - r_ring, cy - r_ring // 2, cx + r_ring, cy + r_ring // 2],
                outline=(220, 220, 255, 120),
                width=2
            )

        img.save(out_path, format="PNG")
