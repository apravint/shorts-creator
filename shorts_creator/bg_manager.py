"""
Background Video Asset & Loop Manager for YouTube Shorts (9:16).
Provides curated 1080x1920 vertical background video footage for high retention:
- Space / Galaxy (NASA high-definition cosmic nebula flythrough)
- Tech / Drone / Cyber (High-speed FPV flight & futuristic visuals)
- Custom user-supplied video footage (auto center-cropped to 9:16)
"""

import os
from typing import Optional

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
BG_DIR = os.path.join(ASSETS_DIR, "backgrounds")


# Keyword mapping to select best background video
TOPIC_KEYWORD_MAP = {
    "space": [
        "space", "galaxy", "universe", "planet", "stars", "alien", "mars", "moon",
        "black hole", "cosmic", "விண்வெளி", "கிரகம்", "சூரியன்", "நிலா", "அண்டம்"
    ],
    "tech": [
        "tech", "ai", "drone", "robot", "cyber", "future", "coding", "computer",
        "crypto", "wealth", "money", "ஹேக்கிங்", "தொழில்நுட்பம்", "பணம்", "எதிர்காலம்"
    ]
}


def list_available_backgrounds():
    """Return dict of available background video files."""
    if not os.path.isdir(BG_DIR):
        return {}
    available = {}
    for f in os.listdir(BG_DIR):
        if f.lower().endswith((".mp4", ".webm", ".mkv", ".mov")):
            key = os.path.splitext(f)[0].lower()
            available[key] = os.path.join(BG_DIR, f)
    return available


def resolve_background_video(
    topic: Optional[str] = None,
    custom_video: Optional[str] = None,
    theme_hint: Optional[str] = None
) -> Optional[str]:
    """
    Intelligently select the best matching 1080x1920 background video.
    
    1. If user passed an explicit custom video file, verify and return it.
    2. If user passed a theme hint (e.g. 'space', 'tech', 'cyber'), match it.
    3. Analyze topic keywords (in Tamil and English) to auto-select.
    4. Default to space background (highest retention & visual awe for Shorts).
    """
    # 1. Custom video file provided
    if custom_video:
        custom_video = os.path.abspath(os.path.expanduser(custom_video))
        if os.path.isfile(custom_video):
            return custom_video

    available = list_available_backgrounds()
    if not available:
        return None

    # 2. Check theme hint
    if theme_hint:
        hint_clean = theme_hint.lower().strip()
        if hint_clean in available:
            return available[hint_clean]
        if hint_clean in ("cyber", "fire", "emerald") and "tech" in available:
            return available["tech"]
        if hint_clean in ("cosmic", "stars") and "space" in available:
            return available["space"]

    # 3. Match from topic keywords
    if topic:
        topic_lower = topic.lower()
        for theme, keywords in TOPIC_KEYWORD_MAP.items():
            if any(kw in topic_lower for kw in keywords):
                if theme in available:
                    return available[theme]

    # 4. Fallback default
    if "space" in available:
        return available["space"]
    if "tech" in available:
        return available["tech"]

    # Pick first available background file
    return next(iter(available.values()), None)
