"""
Open-Source Internet Video Harvester & Downloader for ShortsCreator AI.
Automatically searches, curates, and downloads high-definition copyright-free
stock videos (720p/1080p MP4) from open-source repositories (Mixkit, Wikimedia Commons, Pixabay, Pexels).
Features native bilingual Tamil & English entity resolution, anti-noise guards, and smart caching.
"""

import os
import re
import json
import random
import time
import hashlib
import urllib.parse
import urllib.request
from pathlib import Path
from typing import List, Optional, Dict, Any

from .text_match import has_term

# Time allowed for fetching new footage per video, and for any one clip
DOWNLOAD_BUDGET_SECONDS = 75.0
SINGLE_DOWNLOAD_SECONDS = 25.0
_download_deadline: Optional[float] = None

CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "backgrounds"))
USER_AGENT = "ShortsCreatorAI/2.0 (https://github.com/apravint/shorts-creator; apravint@gmail.com)"

# Comprehensive Tamil to English semantic dictionary for video queries
TAMIL_TO_ENGLISH_MAP = {
    'சென்னை': 'Chennai',
    'மெட்ரோ': 'Metro rail',
    'ரயில்': 'Train railway',
    'தமிழ்நாடு': 'Tamil Nadu',
    'இந்தியா': 'India',
    'விண்வெளி': 'Space galaxy universe',
    'செயற்கை நுண்ணறிவு': 'AI Artificial Intelligence',
    'கணினி': 'Computer technology',
    'இயற்பியல்': 'Physics science',
    'விஞ்ஞானம்': 'Science technology',
    'இயற்கை': 'Nature landscape green',
    'தோல்வி': 'struggle overcome perseverance',
    'வெற்றி': 'success victory achievement',
    'விடாமுயற்சி': 'discipline focus workout',
    'கனவு': 'dreams vision horizon',
    'எழுச்சி': 'sunrise golden hour morning',
    'சிகரம்': 'mountain peak summit',
    'கடல்': 'ocean waves sea',
    'வானம்': 'sky clouds sunset',
    'நெருப்பு': 'fire flame burning',
    'ரோபோ': 'robot futuristic android',
    'கருந்துளை': 'black hole deep space cosmic',
    'சூரியன்': 'sun solar flare sunrise',
    'உளவியல்': 'psychology human mind thinking',
    'அதிசயம்': 'wonder mystery ancient marvel',
    'மர்மம்': 'mystery enigmatic secret',
    'பழக்கம்': 'habits routine morning discipline',
    'சிந்தனை': 'thinking deep mindset philosophy',
    'உண்மை': 'truth revelation wisdom'
}

NEGATIVE_NOISE_TERMS = [
    "diagram", "newspaper", "book", "document", "stamp", "coin",
    "statue", "tombstone", "poster", "pamphlet", "receipt", "invoice",
    "etching", "engraving", "woodcut", "lithograph", "watercolor", "fresco",
    "drawing", "illustration", "sketch", "comic", "painting", "clipart",
    "costume", "cosplay", "mask"
]

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
    ],
    "motivation": [
        "https://assets.mixkit.co/videos/32809/32809-1080.mp4",
        "https://assets.mixkit.co/videos/609/609-1080.mp4",
        "https://assets.mixkit.co/videos/40972/40972-1080.mp4",
        "https://assets.mixkit.co/videos/52079/52079-1080.mp4",
        "https://assets.mixkit.co/videos/40969/40969-1080.mp4",
        "https://assets.mixkit.co/videos/4834/4834-1080.mp4"
    ],
    "city": [
        "https://assets.mixkit.co/videos/49845/49845-1080.mp4",
        "https://assets.mixkit.co/videos/49878/49878-1080.mp4",
        "https://assets.mixkit.co/videos/1606/1606-1080.mp4"
    ],
    "rain": [
        "https://assets.mixkit.co/videos/2846/2846-1080.mp4",
        "https://assets.mixkit.co/videos/25375/25375-720.mp4",
        "https://assets.mixkit.co/videos/6890/6890-720.mp4"
    ]
}

# Semantic query relaxation chains to guarantee non-repeating footage
CATEGORY_RELAXATION_MAP = {
    "motivation": ["motivation", "city", "nature", "rain", "ocean"],
    "space": ["space", "cyberpunk", "technology"],
    "cyberpunk": ["cyberpunk", "technology", "city"],
    "technology": ["technology", "cyberpunk", "space"],
    "ancient": ["ancient", "nature", "ocean"],
    "nature": ["nature", "ocean", "rain"],
    "ocean": ["ocean", "nature", "rain"],
    "rain": ["rain", "nature", "city"],
    "money": ["money", "city", "technology"],
    "city": ["city", "technology", "rain"],
}

KEYWORD_MAPPINGS = {
    "motivation": [
        "motivation", "motivational", "mindset", "success", "discipline", "warrior", "hard work",
        "inspire", "champion", "runner", "running", "gym", "workout", "fitness", "athlete", "focus",
        "unstoppable", "never give up", "climb", "summit", "peak", "courage", "overcome", "strength",
        "strong", "perseverance", "hero", "boxer", "training", "grit",
        "வெற்றி", "உழைப்பு", "விடாமுயற்சி", "முயற்சி", "கனவு", "சிகரம்", "வீரன்", "எழுச்சி", "நம்பிக்கை"
    ],
    "rain": [
        "rain", "storm", "dark", "fog", "cloud", "thunder", "shadow", "struggle", "fall", "fail",
        "broken", "lightning", "gloom", "sad", "pain",
        "மழை", "புயல்", "இருள்", "தோல்வி", "தடை", "அடி", "விழு", "பயம்"
    ],
    "city": [
        "city", "street", "urban", "traffic", "night", "building", "tokyo", "lights", "skyline",
        "chennai", "metro", "road", "downtown",
        "நகரம்", "தெரு", "சென்னை", "மெட்ரோ"
    ],
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


def resolve_search_query(text: str) -> str:
    """Translates Tamil entities to English search anchors and sanitizes query."""
    if not text:
        return "cinematic space galaxy"

    # Match Tamil terms
    matched_en = []
    for ta_term, en_term in TAMIL_TO_ENGLISH_MAP.items():
        if ta_term in text:
            matched_en.append(en_term)

    if matched_en:
        return " ".join(matched_en[:2])

    clean = re.sub(r'[^\w\s]', ' ', text)
    words = [w for w in clean.split() if len(w) > 2]
    stopwords = {'the', 'and', 'for', 'with', 'from', 'about', 'how', 'why', 'what', 'shorts', 'video'}
    informative = [w for w in words if w.lower() not in stopwords]
    return " ".join(informative[:3]) if informative else text[:30]


def extract_search_category(text: str) -> str:
    """Analyze English and Tamil text to select the best visual category."""
    for cat, keywords in KEYWORD_MAPPINGS.items():
        if has_term(text, keywords):
            return cat
    return "nature"


def search_wikimedia_videos(query: str) -> List[str]:
    """Search Wikimedia Commons for open-source HD video files."""
    clean_q = urllib.parse.quote(f"{query} filetype:video")
    api_url = (
        f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&"
        f"gsrsearch={clean_q}&gsrnamespace=6&prop=imageinfo&iiprop=url|mime|size&gsrlimit=10"
    )
    headers = {"User-Agent": USER_AGENT}
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            video_urls = []
            for _, page in pages.items():
                title = page.get("title", "").lower()
                if any(noise in title for noise in NEGATIVE_NOISE_TERMS):
                    continue
                imageinfo = page.get("imageinfo", [])
                if imageinfo:
                    ii = imageinfo[0]
                    mime = ii.get("mime", "")
                    url = ii.get("url", "")
                    if (mime.startswith("video/") or url.endswith((".mp4", ".webm"))) and url:
                        video_urls.append(url)
            return video_urls
    except Exception:
        return []


def scrape_mixkit_video_urls(category: str) -> List[str]:
    """Scrape fresh open-source MP4 URLs from Mixkit."""
    clean_cat = category.lower().strip().replace(" ", "-")
    url = f"https://mixkit.co/free-stock-video/{urllib.parse.quote(clean_cat)}/"
    headers = {"User-Agent": USER_AGENT}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8")
            urls = list(set(re.findall(r'https://assets\.mixkit\.co/videos/\d+/\d+-(?:720|1080)\.mp4', html)))
            if urls:
                return urls
            urls = list(set(re.findall(r'https://assets\.mixkit\.co/videos/[^\"]+\.mp4', html)))
            return urls
    except Exception:
        return []


def reset_download_budget(seconds: float = DOWNLOAD_BUDGET_SECONDS) -> None:
    """Start a fresh download allowance for one video; slow networks then cost a fixed amount of time."""
    global _download_deadline
    _download_deadline = time.monotonic() + seconds


def download_video_file(url: str, dest_path: str) -> bool:
    """Download video with user-agent within the current budget, keeping only complete files."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if _download_deadline is None:
        reset_download_budget()
    headers = {"User-Agent": USER_AGENT}
    partial_path = f"{dest_path}.part"
    # A socket timeout only bounds each read, so a slow transfer needs its own deadline
    deadline = min(_download_deadline, time.monotonic() + SINGLE_DOWNLOAD_SECONDS)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp, open(partial_path, "wb") as f:
            while chunk := resp.read(256 * 1024):
                if time.monotonic() > deadline:
                    raise TimeoutError(f"Download exceeded its time allowance: {url}")
                f.write(chunk)
        if os.path.getsize(partial_path) > 100000:
            os.replace(partial_path, dest_path)
            return True
    except Exception:
        pass
    if os.path.exists(partial_path):
        os.remove(partial_path)
    return False


def get_open_source_video(
    query_or_topic: Optional[str] = None,
    preferred_category: Optional[str] = None,
    exclude_paths: Optional[set] = None
) -> Optional[str]:
    """
    Main entry point: Automatically finds and downloads a real, open-source
    high-definition video from the internet for the given topic or query.
    Employs smart query relaxation to guarantee diverse, non-repeating footage.
    Caches downloads locally in assets/backgrounds.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    resolved_query = resolve_search_query(query_or_topic or "")
    cat = preferred_category or extract_search_category(query_or_topic or "")
    relaxed_categories = CATEGORY_RELAXATION_MAP.get(cat, [cat, "nature", "city"])

    # Older caches hold the same clip under several names, so a used clip is also recognised by size
    used_sizes = {os.path.getsize(p) for p in (exclude_paths or ()) if os.path.isfile(p)}

    def is_fresh(path: str) -> bool:
        return path not in (exclude_paths or ()) and os.path.getsize(path) not in used_sizes

    def cached_fresh(candidate_cat: str) -> List[str]:
        return [
            path for path in (os.path.join(CACHE_DIR, f) for f in os.listdir(CACHE_DIR))
            if os.path.basename(path).lower().startswith(candidate_cat)
            and path.lower().endswith((".mp4", ".mov", ".webm"))
            and os.path.getsize(path) > 500000
            and is_fresh(path)
        ]

    # 1. Unused footage already cached for the topic's own category
    primary_cached = cached_fresh(cat)
    if primary_cached:
        return random.choice(primary_cached)

    if _download_deadline is None:
        reset_download_budget()
    budget_left = time.monotonic() < _download_deadline

    # 2. New on-topic footage: Mixkit, then the Wikimedia Commons Video API
    urls = scrape_mixkit_video_urls(cat) if budget_left else []
    if budget_left and not urls and resolved_query:
        urls = search_wikimedia_videos(resolved_query)

    # 3. Curated fallback for the same category
    if budget_left and not urls:
        urls = list(CURATED_OPEN_VIDEOS.get(cat, []))

    random.shuffle(urls)

    attempts = 0
    for vid_url in urls:
        # Named by URL so the same clip is never stored twice and mistaken for new footage
        dest_path = os.path.join(CACHE_DIR, f"{cat}_{hashlib.sha1(vid_url.encode()).hexdigest()[:12]}.mp4")
        if os.path.isfile(dest_path):
            if is_fresh(dest_path):
                return dest_path
            continue
        if attempts >= 2 or time.monotonic() >= _download_deadline:
            break
        attempts += 1
        if download_video_file(vid_url, dest_path) and is_fresh(dest_path):
            return dest_path

    # 4. Related categories, before repeating anything
    for candidate_cat in relaxed_categories[1:]:
        related_cached = cached_fresh(candidate_cat)
        if related_cached:
            return random.choice(related_cached)

    # 5. Nothing new is available: the caller's random in-point makes a repeat look different
    same_cat = [
        os.path.join(CACHE_DIR, f) for f in os.listdir(CACHE_DIR)
        if f.lower().startswith(cat) and f.lower().endswith((".mp4", ".mov", ".webm"))
    ]
    return random.choice(same_cat) if same_cat else None
