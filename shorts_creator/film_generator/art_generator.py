"""
Visual Art Generator for Animated Films.
Generates unique AI animated scene art using zero-auth high-res neural models,
with automatic resolution scaling (16:9 Cinema Widescreen or 9:16 Vertical Reel),
seed variations, and offline procedural fallback.
"""

import os
import random
import urllib.parse
import urllib.request
import subprocess
from typing import Optional
from shorts_creator.film_generator.screenplay import ANIMATION_STYLES


def generate_scene_image(
    prompt: str,
    output_path: str,
    style_key: str = "anime_shinkai",
    aspect_ratio: str = "16:9",
    seed: Optional[int] = None
) -> str:
    """
    Generate unique AI scene keyframe art.
    Aspect ratios:
    - '16:9': 1280x720 (Cinema Widescreen)
    - '9:16': 720x1280 (Vertical Short Film)
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if seed is None:
        seed = random.randint(1000, 999999)

    style_info = ANIMATION_STYLES.get(style_key, ANIMATION_STYLES["anime_shinkai"])
    full_prompt = f"{prompt}, {style_info['prompt_suffix']}"

    if aspect_ratio == "9:16":
        width, height = 720, 1280
    else:
        width, height = 1280, 720

    encoded_prompt = urllib.parse.quote(full_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}&model=flux"

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = resp.read()
            if len(data) > 5000:
                with open(output_path, "wb") as f:
                    f.write(data)
                return output_path
    except Exception as e:
        print(f"[Warning] Neural art generation network notice: {e}. Using procedural cinematic canvas.")

    # Offline / Procedural Fallback
    generate_procedural_scene_frame(output_path, width, height, style_key)
    return output_path


def generate_procedural_scene_frame(output_path: str, width: int, height: int, style_key: str):
    """Fallback generator for cinematic atmospheric frame."""
    color_map = {
        "cyberpunk": ("0x090d16", "0x3b0764"),
        "tamil_epic": ("0x451a03", "0x78350f"),
        "studio_ghibli": ("0x064e3b", "0x0284c7"),
        "dark_fantasy": ("0x0f172a", "0x1e1b4b"),
        "pixar_3d": ("0x1e3a8a", "0x0284c7"),
        "anime_shinkai": ("0x0c4a6e", "0x4c1d95")
    }
    c0, c1 = color_map.get(style_key, ("0x0f172a", "0x1e1b4b"))

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"gradients=s={width}x{height}:d=1:r=1:c0={c0}:c1={c1}:x0=0:y0=0:x1={width}:y1={height},vignette=PI/3.5",
        "-frames:v", "1",
        output_path
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        pass
