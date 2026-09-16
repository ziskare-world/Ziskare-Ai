"""
Ziskare AI - Prompt Enhancer
============================
High-performance visual, system, and LLM prompt engineering engine.
Transforms raw, ambiguous ideas into rich, production-grade generative prompts
with fine-tuned artistic styles, camera optics, cinematic lighting, negative prompts,
and structured Chain-of-Thought instructions.
"""

import re
from typing import Dict, Any, Optional, List


# Curated Visual Styles & Engine Modifiers
STYLE_PRESETS: Dict[str, Dict[str, Any]] = {
    "photorealistic": {
        "descriptors": "photorealistic masterpiece, hyper-realistic, lifelike texture, natural skin tones, subsurface scattering, 8k resolution, raw photo",
        "camera": "shot on Sony A7R IV, 85mm f/1.4 GM lens, shallow depth of field, sharp focus, exquisite micro-details",
        "lighting": "natural golden hour daylight, soft atmospheric illumination, balanced dynamic range",
        "negative": "cartoon, illustration, painting, drawing, blurry, low resolution, plastic, distorted anatomy, oversaturated, artificial",
        "aspect_ratio": "16:9"
    },
    "cinematic": {
        "descriptors": "cinematic still, epic blockbuster aesthetic, film still from an IMAX production, anamorphic widescreen, rich depth",
        "camera": "Arri Alexa Mini, 35mm anamorphic lens, subtle film grain, dramatic wide-angle framing, depth of field",
        "lighting": "dramatic volumetric chiaroscuro lighting, subtle fog, cinematic teal and orange color grading, rim light",
        "negative": "flat lighting, amateur photo, phone camera, washed out, low contrast, oversaturated, watermark, blurry",
        "aspect_ratio": "21:9"
    },
    "cyberpunk": {
        "descriptors": "futuristic cyberpunk aesthetic, high-tech dystopian cityscape, glowing fiber-optics, holographic overlays, dark noir atmosphere",
        "camera": "50mm f/1.2 lens, reflection on wet asphalt, chromatic aberration, sharp neon focal plane",
        "lighting": "vibrant neon purple and cyan backlighting, rainy night reflections, bioluminescent glows, volumetric smog",
        "negative": "daylight, medieval, rustic, pastel colors, washed out, natural landscape, bad composition, cartoonish",
        "aspect_ratio": "16:9"
    },
    "anime": {
        "descriptors": "breathtaking anime key visual, Makoto Shinkai and Studio Ghibli inspired, vibrant color harmony, crisp clean linework",
        "camera": "cinematic anime framing, dynamic perspective, atmospheric floating dust particles",
        "lighting": "luminous sky illumination, soft sunbeams, radiant god rays, vibrant cel-shaded gradients",
        "negative": "3d render, photorealistic, uncanny valley, western comic, sketch, rough lines, muted colors, messy line art",
        "aspect_ratio": "16:9"
    },
    "fantasy": {
        "descriptors": "epic fantasy concept art, mythical grandeur, intricate ornamental details, trending on ArtStation, matte painting masterpiece",
        "camera": "grand wide panoramic vista, majestic composition, golden spiral framing",
        "lighting": "ethereal ambient glow, mystical starlight, swirling arcane illumination, atmospheric mountain mist",
        "negative": "modern, futuristic, sci-fi, vehicles, modern clothing, photorealistic, blurry, low resolution",
        "aspect_ratio": "16:9"
    },
    "unreal_engine": {
        "descriptors": "hyper-detailed 3D CGI render, Unreal Engine 5.4, Octane Render, ray-traced reflections, PBR materials, photorealistic physics",
        "camera": "virtual 3D camera, physically accurate ray tracing, ambient occlusion, crisp geometric textures",
        "lighting": "Lumen dynamic global illumination, Nanite geometry lighting, volumetric light bounce, specular highlights",
        "negative": "2d, flat drawing, sketch, low poly, bad render, noisy, pixelated, video compression artifacts",
        "aspect_ratio": "16:9"
    },
    "oil_painting": {
        "descriptors": "classical fine art oil painting, masterpiece by Rembrandt and John Singer Sargent, expressive impasto brushwork, heavy canvas texture",
        "camera": "traditional museum easel perspective, organic fine art composition",
        "lighting": "dramatic chiaroscuro, warm candlelit ambiance, rich earthy shadows, luminous varnish finish",
        "negative": "digital render, 3d, photograph, smooth airbrush, clean digital vector, modern, plastic",
        "aspect_ratio": "4:3"
    },
    "dark_moody": {
        "descriptors": "dark moody aesthetic, low-key photography, mysterious atmospheric tension, evocative silhouette, brooding tone",
        "camera": "50mm prime lens, deep blacks, tactile shadows, subtle atmospheric grain",
        "lighting": "harsh directional single-source light, deep shadow falloff, moody dusk ambiance, silhouette edge",
        "negative": "bright daylight, happy, cheerful, pastel, high key, washed out, noisy, blown out highlights",
        "aspect_ratio": "1:1"
    },
    "isometric_3d": {
        "descriptors": "delightful isometric 3D diorama, stylized miniature scene, Blender 3D render, tilt-shift miniature effect, smooth clay render",
        "camera": "orthographic isometric camera angle, 45-degree vantage, toy-like scale",
        "lighting": "soft studio ambient lighting, gentle soft shadows, warm pastel color palette",
        "negative": "flat 2d, perspective distortion, realistic human faces, grim, gritty, dark, chaotic composition",
        "aspect_ratio": "1:1"
    },
    "macro": {
        "descriptors": "extreme macro photography, microscopic precision, intricate crystal patterns, tactile surface textures, visual wonder",
        "camera": "100mm f/2.8 macro lens, 1:1 reproduction ratio, ultra-shallow depth of field, razor-sharp focal point, smooth bokeh",
        "lighting": "diffused ring-flash illumination, crisp specular glints, soft shadowless micro-lighting",
        "negative": "wide angle, landscape, blurry subject, out of focus, motion blur, noisy sensor, low resolution",
        "aspect_ratio": "1:1"
    },
    "watercolor": {
        "descriptors": "delicate watercolor painting on cold-press archival paper, wet-on-wet technique, soft pigment pooling, organic paper texture",
        "camera": "traditional botanical illustration perspective, elegant negative white space",
        "lighting": "soft natural daylight, translucent pigment layering, airy luminous feel",
        "negative": "heavy oil, digital 3d, photograph, harsh neon, opaque acrylic, muddy colors",
        "aspect_ratio": "4:3"
    },
    "minimalist": {
        "descriptors": "minimalist contemporary aesthetic, serene negative space, pure geometric balance, understated elegance, Scandinavian design",
        "camera": "clean straight-on architectural elevation, perfect horizontal alignment, balanced framing",
        "lighting": "soft diffused north-facing window light, delicate ambient gradient",
        "negative": "cluttered, busy, chaotic, high contrast, maximalist, messy, loud colors, grainy",
        "aspect_ratio": "16:9"
    }
}

UNIVERSAL_NEGATIVE_PROMPT = (
    "blurry, low quality, distorted, deformed, watermark, text, signature, logo, "
    "bad anatomy, extra limbs, missing fingers, mutated hands, bad proportions, "
    "out of frame, cropped, low resolution, jpeg artifacts, grainy, duplicate"
)


class PromptEnhancer:
    """
    Intelligent Prompt Optimization Engine for Ziskare AI.
    Features parametric visual prompt construction, negative prompt generation,
    style tuning, and Chain-of-Thought LLM prompt engineering.
    """

    def __init__(self, ai: Optional[Any] = None):
        self.ai = ai

    def enhance_image_prompt(
        self,
        raw_prompt: str,
        style: str = "photorealistic",
        lighting: Optional[str] = None,
        camera: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Transforms a brief image idea into an extraordinary, high-detail prompt
        with engine-tuned modifiers, lighting, camera optics, and negative prompts.
        """
        clean_idea = raw_prompt.strip().strip('"\'')
        style_key = style.lower().replace(" ", "_").replace("-", "_")
        preset = STYLE_PRESETS.get(style_key, STYLE_PRESETS["photorealistic"])

        # Determine target aspect ratio
        ar = aspect_ratio or preset.get("aspect_ratio", "1:1")

        # 1. Neural LLM expansion if AI model available and requested
        neural_expansion = ""
        if use_llm and self.ai is not None:
            try:
                task = (
                    f"You are an elite AI prompt engineer for image synthesis.\n"
                    f"Expand the following concept into a visually descriptive, vivid scene:\n"
                    f"Concept: \"{clean_idea}\"\n"
                    f"Style: {style}\n\n"
                    f"Requirements: Describe the focal subject, specific textures, atmosphere, and environmental details.\n"
                    f"Output ONLY the single-paragraph enhanced description without greetings, preamble, or quotes."
                )
                if hasattr(self.ai, "ask"):
                    neural_expansion = self.ai.ask(task, max_new_tokens=140, temperature=0.4).strip().strip('"\'')
                    if ":" in neural_expansion and len(neural_expansion.split(":")[0]) < 30:
                        neural_expansion = neural_expansion.split(":", 1)[1].strip()
            except Exception:
                neural_expansion = ""

        # 2. Build composed visual prompt
        focal_core = neural_expansion if (neural_expansion and len(neural_expansion) > len(clean_idea)) else clean_idea
        
        # Assemble components
        components = [focal_core]
        
        # Add style descriptors
        components.append(preset["descriptors"])

        # Add camera optics
        chosen_cam = camera or preset.get("camera", "")
        if chosen_cam:
            components.append(chosen_cam)

        # Add lighting
        chosen_light = lighting or preset.get("lighting", "")
        if chosen_light:
            components.append(chosen_light)

        # Full enhanced prompt
        enhanced_prompt = ", ".join(c.strip(" ,.") for c in components if c.strip())

        # Build tailored negative prompt
        style_negative = preset.get("negative", "")
        negative_prompt = f"{style_negative}, {UNIVERSAL_NEGATIVE_PROMPT}".strip(" ,.")

        return {
            "original_prompt": clean_idea,
            "enhanced_prompt": enhanced_prompt,
            "negative_prompt": negative_prompt,
            "style": style_key,
            "aspect_ratio": ar,
            "camera_spec": chosen_cam,
            "lighting_spec": chosen_light,
            "mode": "visual"
        }

    def enhance_llm_prompt(
        self,
        raw_prompt: str,
        task_type: str = "general",
        role: Optional[str] = None,
        output_format: str = "structured"
    ) -> Dict[str, Any]:
        """
        Transforms raw instructions into a high-precision, production-grade LLM prompt
        using the RTF (Role-Task-Format) and Chain-of-Thought architecture.
        """
        clean_prompt = raw_prompt.strip().strip('"\'')
        low = clean_prompt.lower()

        # Infer suitable role if none provided
        if not role:
            if any(k in low for k in ["code", "script", "function", "bug", "python", "javascript", "program"]):
                role = "Senior Principal Software Engineer & Systems Architect"
            elif any(k in low for k in ["data", "analyze", "statistics", "metric", "chart"]):
                role = "Chief Data Scientist & Quantitative Analyst"
            elif any(k in low for k in ["write", "article", "blog", "story", "copy"]):
                role = "Elite Technical Writer & Content Strategist"
            elif any(k in low for k in ["design", "ui", "ux", "interface", "layout"]):
                role = "Staff Product Designer & HCI Specialist"
            elif any(k in low for k in ["optimize", "hardware", "cpu", "thermal", "performance"]):
                role = "Hardware Systems & Kernel Performance Optimization Engineer"
            else:
                role = "World-Class Domain Expert & Autonomous AI Consultant"

        # Structured Prompt Template
        enhanced_prompt = (
            f"### Role & Persona:\n"
            f"You are a {role}. Provide an authoritative, precise, and high-quality response.\n\n"
            f"### Objective & Task:\n"
            f"{clean_prompt}\n\n"
            f"### Key Guidelines & Constraints:\n"
            f"- Thoroughness: Address all implicit and explicit requirements directly.\n"
            f"- Accuracy: Ensure zero hallucinations, verified facts, and sound technical reasoning.\n"
            f"- Conciseness: Avoid polite conversational filler, apologies, or redundant preambles.\n"
            f"- Edge Cases: Anticipate common pitfalls, limitations, and performance considerations.\n\n"
            f"### Output Format:\n"
            f"Present the final response in clean, GitHub-flavored Markdown with clear headings, "
            f"bullet points for readability, and syntax-highlighted code blocks where applicable."
        )

        return {
            "original_prompt": clean_prompt,
            "enhanced_prompt": enhanced_prompt,
            "role": role,
            "task_type": task_type,
            "output_format": output_format,
            "mode": "llm"
        }

    def enhance_code_prompt(
        self,
        raw_prompt: str,
        language: str = "python",
        architecture: str = "production"
    ) -> Dict[str, Any]:
        """
        Enhance prompts specifically targeting code generation.
        """
        clean_prompt = raw_prompt.strip().strip('"\'')
        enhanced_prompt = (
            f"### Role:\n"
            f"Senior Principal {language.capitalize()} Developer & Software Architect.\n\n"
            f"### Implementation Task:\n"
            f"{clean_prompt}\n\n"
            f"### Architectural Constraints:\n"
            f"- Language Standard: Modern {language.capitalize()}.\n"
            f"- Type Safety: Comprehensive type hints and docstrings.\n"
            f"- Robustness: Production-grade exception handling and input validation.\n"
            f"- Performance: Memory-efficient idioms and optimal time complexity.\n"
            f"- Modularity: Clean, testable functions following SOLID principles.\n\n"
            f"### Expected Deliverables:\n"
            f"1. Complete, copy-paste ready implementation code.\n"
            f"2. Brief operational commentary explaining key algorithmic choices.\n"
            f"3. Practical usage example demonstrating edge cases."
        )

        return {
            "original_prompt": clean_prompt,
            "enhanced_prompt": enhanced_prompt,
            "language": language,
            "architecture": architecture,
            "mode": "code"
        }

    def enhance(self, prompt: str, mode: str = "auto", style: str = "photorealistic") -> Dict[str, Any]:
        """
        Universal entry point: automatically classifies the intent and enhances accordingly.
        """
        clean = prompt.strip()
        low = clean.lower()

        is_code = mode == "code" or any(w in low for w in ["code", "python", "javascript", "script", "function", "regex", "sql", "html", "css", "class", "algorithm", "debug", "refactor", "nginx", "logs"])
        is_llm_task = mode in ["llm", "chat", "system"] or any(low.startswith(w) for w in ["explain", "how to", "how do", "how can", "why", "what is", "analyze", "summarize", "compare", "evaluate", "translate", "guide", "advice", "review", "write an essay", "write a story", "write an article"])

        if is_code and mode != "image":
            return self.enhance_code_prompt(clean)

        if is_llm_task and mode != "image":
            return self.enhance_llm_prompt(clean)

        # Default to rich visual prompt enhancement
        for s in STYLE_PRESETS:
            if s in low or s.replace("_", " ") in low:
                style = s
                break
        cleaned_concept = re.sub(
            r'^(?:please\s+)?(?:enhance\s+(?:prompt|this\s+prompt)?(?:\s+for)?(?:\s+an?)?\s*(?:image|picture)?(?:\s+of)?)\s*',
            '', clean, flags=re.IGNORECASE
        ).strip(" :.-")
        if not cleaned_concept:
            cleaned_concept = clean
        return self.enhance_image_prompt(cleaned_concept, style=style)

    def format_display(self, result: Dict[str, Any]) -> str:
        """
        Formats the enhancement result into an informative, user-friendly markdown report.
        """
        mode = result.get("mode", "visual")

        if mode == "visual":
            return (
                f"🎨 **Ziskare Prompt Enhancer — Visual Synthesis Spec**\n\n"
                f"🔹 **Original Idea:**\n\"{result['original_prompt']}\"\n\n"
                f"✨ **Enhanced Visual Prompt:**\n```text\n{result['enhanced_prompt']}\n```\n\n"
                f"🚫 **Engine Negative Prompt:**\n```text\n{result['negative_prompt']}\n```\n\n"
                f"📐 **Recommended Config:**\n"
                f"- **Artistic Preset:** `{result['style']}`\n"
                f"- **Aspect Ratio:** `{result['aspect_ratio']}`\n"
                f"- **Camera Optics:** {result.get('camera_spec', 'Standard')}\n"
                f"- **Atmospheric Lighting:** {result.get('lighting_spec', 'Natural')}"
            )
        else:
            return (
                f"⚡ **Ziskare Prompt Enhancer — Structured Instruction Spec**\n\n"
                f"🔹 **Original Prompt:**\n\"{result['original_prompt']}\"\n\n"
                f"✨ **Production-Grade Enhanced Prompt:**\n\n{result['enhanced_prompt']}"
            )


# Standalone module-level helper function
def enhance_prompt(
    prompt: str,
    mode: str = "auto",
    style: str = "photorealistic",
    ai: Optional[Any] = None
) -> Dict[str, Any]:
    """Convenience helper to optimize prompts immediately."""
    enhancer = PromptEnhancer(ai=ai)
    return enhancer.enhance(prompt, mode=mode, style=style)
