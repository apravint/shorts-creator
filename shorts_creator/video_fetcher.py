"""
Open-Source Internet Video Harvester & Downloader.
Automatically searches, fetches, and downloads high-definition copyright-free
stock videos (720p/1080p MP4) from open-source repositories (Mixkit, Pixabay, Pexels)
for YouTube Shorts and Animated Films.
"""

import os
import re
import random
import urllib.parse
import urllib.request
from typing import List, Optional

CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "backgrounds"))

# Verified direct open-source MP4 video URLs as immediate fallbacks
CURATED_OPEN_VIDEOS = {
    "space": [
        "https://assets.mixkit.co/videos/1610/1610-1080.mp4",
        "https://assets.mixkit.co/videos/14145/14145-720.mp4",
        "https://assets.mixkit.co/videos/18791/18791-720.mp4",
        "https://assets.mixkit.co/videos/23245/23245-1080.mp4"
    ],
    "cyberpunk": [
        "https://assets.mixkit.co/videos/34317/34317-720.mp4",
        "https://assets.mixkit.co/videos/49845/49845-1080.mp4",
        "https://assets.mixkit.co/videos/44644/44644-1080.mp4"
    ],
    "technology": [
        "https://assets.mixkit.co/videos/44644/44644-1080.mp4",
        "https://assets.mixkit.co/videos/34317/34317-720.mp4",
        "https://assets.mixkit.co/videos/24430/24430-1080.mp4"
    ],
    "nature": [
        "https://assets.mixkit.co/videos/40657/40657-1080.mp4",
        "https://assets.mixkit.co/videos/44974/44974-720.mp4",
        "https://assets.mixkit.co/videos/4834/4834-1080.mp4"
    ],
    "ocean": [
        "https://assets.mixkit.co/videos/44974/44974-720.mp4",
        "https://assets.mixkit.co/videos/4531/4531-1080.mp4",
        "https://assets.mixkit.co/videos/1199/1199-1080.mp4"
    ],
    "ancient": [
        "https://assets.mixkit.co/videos/32893/32893-720.mp4",
        "https://assets.mixkit.co/videos/40657/40657-1080.mp4",
        "https://assets.mixkit.co/videos/1610/1610-1080.mp4"
    ],
    "fire": [
        "https://assets.mixkit.co/videos/4426/4426-1080.mp4",
        "https://assets.mixkit.co/videos/1610/1610-1080.mp4"
    ],
    "money": [
        "https://assets.mixkit.co/videos/44644/44644-1080.mp4",
        "https://assets.mixkit.co/videos/49845/49845-1080.mp4"
    ]
}

# Multilingual Keyword to Category Mapping (English & Tamil)
KEYWORD_MAPPINGS = {
    "space": [
        "space", "galaxy", "universe", "planet", "stars", "alien", "mars", "moon",
        "black hole", "cosmic", "astronomy", "astronaut", "விண்வெளி", "கிரகம்", "சூரியன்",
        "நிலா", "அண்டம்", "கருந்துளை", "விண்கல்"
    ],
    "cyberpunk": [
        "cyber", "future", "hacker", "tokyo", "neon", "robot", "ai", "matrix",
        "ரோபோ", "எதிர்காலம்", "ஹேக்கிங்"
    ],
    "technology": [
        "tech", "technology", "drone", "computer", "coding", "software", "quantum",
        "தொழில்நுட்பம்", "கணினி", "ஏஐ"
    ],
    "ancient": [
        "history", "ancient", "temple", "pyramid", "war", "chola", "warrior", "monument",
        "வரலாறு", "கோயில்", "சோழர்", "பழமை", "கல்லணை", "வீரன்", "தஞ்சை"
    ],
    "ocean": [
        "ocean", "sea", "water", "waves", "beach", "ship", "sail", "fleet",
        "கடல்", "அலை", "கப்பல்", "நாவாய்"
    ],
    "nature": [
        "nature", "forest", "tree", "mountain", "jungle", "green", "landscape",
        "காடு", "இயற்கை", "மலை", "மரம்"
    ],
    "fire": [
        "fire", "flame", "burn", "red", "explosion", "தீ", "நெருப்பு", "வெப்பம்"
    ],
    "money": [
        "money", "wealth", "cash", "rich", "billionaire", "finance", "gold",
        "பணம்", "செல்வம்", "கோடீஸ்வரன்", "முதலீடு"
    ]
}


def extract_search_category(text: str) -> str:
    """Analyze English and Tamil text to select the best visual category."""
    text_lower = (text or "").lower()
    for cat, keywords in KEYWORD_MAPPINGS.items():
        if any(kw in text_lower for kw in keywords):
            return cat
    return "space"


def scrape_mixkit_video_urls(category: str) -> List[str]:
    """Scrape fresh open-source MP4 URLs from Mixkit."""
    clean_cat = category.lower().strip().replace(" ", "-")
    url = f"https://mixkit.co/free-stock-video/{urllib.parse.quote(clean_cat)}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8")
            # Extract HD MP4 URLs
            urls = list(set(re.findall(r'https://assets\.mixkit\.co/videos/\d+/\d+-(?:720|1080)\.mp4', html)))
            if urls:
                return urls
            # Fallback to any mixkit MP4s
            urls = list(set(re.findall(r'https://assets\.mixkit\.co/videos/[^\"]+\.mp4', html)))
            return urls
    except Exception as e:
        return []


def download_video_file(url: str, dest_path: str) -> bool:
    """Download video with user-agent and verify file integrity."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            content = resp.read()
            if len(content) > 100000:  # At least 100KB
                with open(dest_path, "wb") as f:
                    f.write(content)
                return True
    except Exception as e:
        print(f"[Warning] Failed to download {url}: {e}")
    return False


def get_open_source_video(
    query_or_topic: Optional[str] = None,
    preferred_category: Optional[str] = None
) -> Optional[str]:
    """
    Main entry point: Automatically finds and downloads a real, open-source
    high-definition video from the internet for the given topic or query.
    Caches downloads locally in assets/backgrounds.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    cat = preferred_category or extract_search_category(query_or_topic or "")

    # 1. Check local cache first
    cached_candidates = [
        os.path.join(CACHE_DIR, f)
        for f in os.listdir(CACHE_DIR)
        if f.lower().startswith(cat) and f.lower().endswith((".mp4", ".mov", ".webm"))
    ]
    if cached_candidates:
        # Check that file has valid size
        valid = [f for f in cached_candidates if os.path.getsize(f) > 500000]
        if valid:
            return random.choice(valid)

    # 2. Scrape fresh video URLs from open-source web
    print(f"[cyan]🌐 Fetching open-source HD stock video for theme '{cat}' from internet...[/cyan]")
    urls = scrape_mixkit_video_urls(cat)

    # 3. Add curated fallback URLs
    if not urls:
        urls = CURATED_OPEN_VIDEOS.get(cat, CURATED_OPEN_VIDEOS["space"])

    # Shuffle for variety
    random.shuffle(urls)

    for vid_url in urls[:3]:
        dest_filename = f"{cat}_{random.randint(100, 999)}.mp4"
        dest_path = os.path.join(CACHE_DIR, dest_filename)
        success = download_video_file(vid_url, dest_path)
        if success and os.path.isfile(dest_path):
            print(f"[green]✅ Downloaded real open-source video: {dest_path} ({os.path.getsize(dest_path)//1024} KB)[/green]")
            return dest_path

    # Fallback to any existing video in CACHE_DIR
    all_local = [
        os.path.join(CACHE_DIR, f)
        for f in os.listdir(CACHE_DIR)
        if f.lower().endswith((".mp4", ".webm")) and os.path.getsize(os.path.join(CACHE_DIR, f)) > 100000
    ]
    return all_local[0] if all_local else None
