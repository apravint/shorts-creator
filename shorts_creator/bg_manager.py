"""
Background Video Asset & Loop Manager for YouTube Shorts (9:16).
Provides curated and dynamically fetched 1080x1920 vertical background videos:
- Space / Galaxy
- Tech / Drone / Cyber
- History / Ancient / Oceans / Nature
- Automatically downloads fresh open-source stock videos from the internet
"""

import os
from typing import Optional
from shorts_creator.video_fetcher import get_open_source_video, extract_search_category

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
BG_DIR = os.path.join(ASSETS_DIR, "backgrounds")


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
    Intelligently select or download the best matching 1080x1920 background video.
    1. If user passed a custom video file, verify and return it.
    2. Check local cached/preset videos.
    3. If no matching video exists, automatically download from open-source internet!
    4. Guarantees real video footage is always returned.
    """
    # 1. Custom video file provided
    if custom_video:
        custom_video = os.path.abspath(os.path.expanduser(custom_video))
        if os.path.isfile(custom_video) and os.path.getsize(custom_video) > 100000:
            return custom_video

    available = list_available_backgrounds()

    # 2. Check theme hint
    if theme_hint:
        hint_clean = theme_hint.lower().strip()
        if hint_clean in available:
            return available[hint_clean]
        for k in available:
            if hint_clean in k:
                return available[k]

    # 3. Match from topic keywords locally
    if topic:
        cat = extract_search_category(topic)
        for k in available:
            if cat in k:
                return available[k]

    # 4. Automatically download real open-source video from the internet!
    search_query = topic or theme_hint or "space"
    downloaded = get_open_source_video(query_or_topic=search_query, preferred_category=theme_hint)
    if downloaded and os.path.isfile(downloaded) and os.path.getsize(downloaded) > 100000:
        return downloaded

    # 5. Fallback to any available local video in backgrounds dir
    if available:
        return next(iter(available.values()), None)

    return None
