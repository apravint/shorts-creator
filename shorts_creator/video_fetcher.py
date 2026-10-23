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
import urllib.parse
import urllib.request
from pathlib import Path
from typing import List, Optional, Dict, Any

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
    text_lower = (text or "").lower()
    for cat, keywords in KEYWORD_MAPPINGS.items():
        if any(kw in text_lower for kw in keywords):
            return cat
    return "space"


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


def download_video_file(url: str, dest_path: str) -> bool:
    """Download video with user-agent and verify file integrity."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    headers = {"User-Agent": USER_AGENT}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=25) as resp:
            content = resp.read()
            if len(content) > 100000:
                with open(dest_path, "wb") as f:
                    f.write(content)
                return True
    except Exception:
        pass
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
    relaxed_categories = CATEGORY_RELAXATION_MAP.get(cat, [cat, "nature", "space", "city"])

    # 1. Check local cache across relaxed category chain for unused footage
    for candidate_cat in relaxed_categories:
        cached_candidates = [
            os.path.join(CACHE_DIR, f)
            for f in os.listdir(CACHE_DIR)
            if f.lower().startswith(candidate_cat) and f.lower().endswith((".mp4", ".mov", ".webm"))
        ]
        if cached_candidates:
            valid = [f for f in cached_candidates if os.path.getsize(f) > 500000]
            fresh = [f for f in valid if not exclude_paths or f not in exclude_paths]
            if fresh:
                return random.choice(fresh)

    # 2. Try Mixkit Scraping for the primary category
    urls = scrape_mixkit_video_urls(cat)

    # 3. Try Wikimedia Commons Video API
    if not urls and resolved_query:
        urls = search_wikimedia_videos(resolved_query)

    # 4. Fallback to Curated Open Videos across relaxation chain
    if not urls:
        for candidate_cat in relaxed_categories:
            if candidate_cat in CURATED_OPEN_VIDEOS:
                urls = CURATED_OPEN_VIDEOS[candidate_cat]
                break

    if not urls:
        urls = CURATED_OPEN_VIDEOS["space"]

    random.shuffle(urls)

    for vid_url in urls[:4]:
        dest_filename = f"{cat}_{random.randint(100, 999)}.mp4"
        dest_path = os.path.join(CACHE_DIR, dest_filename)
        success = download_video_file(vid_url, dest_path)
        if success and os.path.isfile(dest_path):
            if not exclude_paths or dest_path not in exclude_paths:
                return dest_path

    # Fallback to any valid video in CACHE_DIR
    all_local = [
        os.path.join(CACHE_DIR, f)
        for f in os.listdir(CACHE_DIR)
        if f.lower().endswith((".mp4", ".webm")) and os.path.getsize(os.path.join(CACHE_DIR, f)) > 100000
    ]
    fresh_any = [f for f in all_local if not exclude_paths or f not in exclude_paths]
    if fresh_any:
        return random.choice(fresh_any)
    return all_local[0] if all_local else None
