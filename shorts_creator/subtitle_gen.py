"""
Animated Subtitle Engine (Hormozi / Viral Shorts Style).
Generates Advanced SubStation Alpha (.ass) subtitles with:
- True millisecond word-by-word highlight synchronization
- Micro-bounce pop animations on spoken words (\\fscx, \\fscy)
- Large on-screen hook text for the opening seconds
- Ultra-punchy 1-2 word rapid kinetic bursts
- Full Tamil Unicode HarfBuzz complex ligature shaping
- Multi-palette viral neon themes
"""

import os
import re
from typing import List, Dict, Any, Optional

# Contextual Semantic Emoji Map (Tamil & English)
SEMANTIC_EMOJIS = {
    # Victory / Success / Trophy
    "வெற்றி": "🏆", "ஜெயி": "🏆", "win": "🏆", "winner": "🏆", "victory": "🏆",
    "success": "🎯", "target": "🎯", "இலக்கு": "🎯", "champion": "🥇", "first": "🥇",
    # Fire / Passion / Motivation / Energy
    "நெருப்பு": "🔥", "வெறி": "🔥", "தீ": "🔥", "fire": "🔥", "burn": "🔥",
    "passion": "🔥", "unstoppable": "⚡", "மின்": "⚡", "lightning": "⚡", "energy": "⚡",
    # Power / Strength / Gym / Warrior
    "வீரம்": "💪", "பலம்": "💪", "உழைப்பு": "💪", "வலிமை": "💪", "strength": "💪",
    "power": "💪", "strong": "💪", "workout": "🏋️", "discipline": "🛡️", "hero": "🦸",
    # Seed / Growth / Nature / Summit
    "விதை": "🌱", "முளை": "🌱", "விருட்சம்": "🌳", "மரம்": "🌳", "grow": "🌱",
    "growth": "📈", "உயர்வு": "📈", "rising": "🌅", "சிகரம்": "🏔️", "summit": "🏔️",
    # Mindset / Focus / Brain / Secret
    "மூளை": "🧠", "சிந்தனை": "🧠", "mind": "🧠", "mindset": "🧠", "brain": "🧠", "focus": "🎯",
    "கவனம்": "🎯", "idea": "💡", "ரகசியம்": "🤫", "secret": "🤫", "think": "💡",
    # Danger / Fear / Obstacle / Fall
    "பயம்": "🛑", "தடை": "🚧", "இருள்": "🌑", "fail": "❌", "தோல்வி": "❌",
    "danger": "⚠️", "stop": "🛑", "pain": "💔", "struggle": "⚔️", "போர்": "⚔️",
    # Time / Speed / Rocket / Space
    "நேரம்": "⏳", "காலம்": "⏳", "time": "⏳", "வேகம்": "🚀", "rocket": "🚀",
    "fly": "🦅", "வானம்": "🌌", "space": "🪐", "star": "⭐", "universe": "🌌",
    # Money / Wealth / Royalty
    "பணம்": "💰", "செல்வம்": "💰", "money": "💰", "cash": "💵", "rich": "💎",
    "வைரம்": "💎", "billionaire": "👑", "ராஜா": "👑", "king": "👑",
    # Heart / Magic / Future
    "இதயம்": "❤️", "love": "❤️", "உண்மை": "✨", "magic": "✨",
    "future": "🔮", "எதிர்காலம்": "🔮"
}


def get_word_emoji(word: str) -> str:
    """Find contextual semantic emoji for a given word."""
    clean_w = word.lower().strip(".,!?:;\"'()[]")
    if clean_w in SEMANTIC_EMOJIS:
        return SEMANTIC_EMOJIS[clean_w]
    # Only Tamil matches by substring (attached suffixes); in English "king" would hit "thinking"
    for k, emoji in SEMANTIC_EMOJIS.items():
        if not k.isascii() and k in clean_w and len(k) >= 3:
            return emoji
    return ""


def clean_caption_word(word: str, uppercase: bool = True) -> str:
    """Prepare a spoken word for burn-in: strip ASS control characters and trailing soft punctuation."""
    cleaned = re.sub(r"[{}\\]", "", word).rstrip(".,;:")
    return cleaned.upper() if uppercase else cleaned


def build_hook_event(hook_text: str, highlight_color: str, duration: float = 2.6) -> str:
    """Large on-screen hook for the opening seconds, split across two lines with the payoff highlighted."""
    words = re.sub(r"[{}\\]", "", hook_text).upper().split()
    if not words:
        return ""
    split_at = max(1, len(words) // 2)
    first, second = " ".join(words[:split_at]), " ".join(words[split_at:])
    entrance = "{\\fad(0,180)\\fscx84\\fscy84\\t(0,150,\\fscx100\\fscy100)}"
    body = f"{first}\\N{{\\c{highlight_color}}}{second}" if second else first
    return f"Dialogue: 1,{format_ass_time(0)},{format_ass_time(duration)},Hook,,0,0,0,,{entrance}{body}"


def format_ass_time(seconds: float) -> str:
    """Format seconds into ASS timestamp format: H:MM:SS.cs"""
    if seconds < 0:
        seconds = 0
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        centis = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{centis:02d}"


def split_into_bursts(text: str, max_words: int = 2) -> List[List[str]]:
    """Split text into punchy 1-2 word rapid visual bursts (Hormozi style)."""
    words = [w for w in text.split() if w.strip()]
    bursts = []
    current = []
    for w in words:
        current.append(w)
        if len(current) >= max_words:
            bursts.append(current)
            current = []
    if current:
        bursts.append(current)
    return bursts


def get_palette_color(style: str) -> str:
    """Return BGR ASS hex color string (&HBBGGRR&)."""
    # If user provided a raw ASS color or hex code
    s = style.strip()
    if s.startswith("&H") and s.endswith("&"):
        return s
    if s.startswith("#") and len(s) == 7:
        r, g, b = s[1:3], s[3:5], s[5:7]
        return f"&H{b}{g}{r}&"

    palettes = {
        "hormozi": "&H00FFFF&",      # Neon Yellow
        "neon_glow": "&HFFFF00&",    # Neon Cyan with blur glow
        "neon-cyan": "&HFFFF00&",    # Neon Cyan
        "neon-green": "&H00FF00&",   # Emerald Green
        "fire-red": "&H0045FF&",     # Fire Red / Orange
        "gold": "&H00D7FF&",         # Rich Gold
        "purple-neon": "&HFF00FF&",  # Cyber Purple / Magenta
        "sliding": "&H00FFFF&",      # Dual-line sliding window
        "white-classic": "&HFFFFFF&" # Crisp White
    }
    return palettes.get(s.lower(), "&H00FFFF&")


def generate_from_boundaries(
    boundaries: List[Dict[str, Any]],
    total_duration: float,
    highlight_color: str,
    max_words: int = 2,
    style_mode: str = "hormozi"
) -> List[str]:
    """
    Generate kinetic ASS subtitle events using exact Edge-TTS word boundaries with auto-emojis.
    Supports 'hormozi' (bounce pop), 'neon_glow' (blurred neon aura), and 'sliding' (dimmed context).
    """
    events = []
    # Filter valid words
    valid_items = [b for b in boundaries if b.get("word") and b.get("word").strip()]
    if not valid_items:
        return events

    # Group into punchy 1-2 word bursts (or 3-4 for sliding)
    words_per_burst = 3 if style_mode == "sliding" else max_words
    bursts: List[List[Dict[str, Any]]] = []
    current_burst: List[Dict[str, Any]] = []
    for item in valid_items:
        current_burst.append(item)
        if len(current_burst) >= words_per_burst:
            bursts.append(current_burst)
            current_burst = []
    if current_burst:
        bursts.append(current_burst)

    for b_idx, burst in enumerate(bursts):
        burst_words = [clean_caption_word(item["word"], uppercase=style_mode != "sliding") for item in burst]
        burst_len = len(burst)

        for w_idx in range(burst_len):
            w_item = burst[w_idx]
            w_start = max(0.0, w_item["start"])

            # Compute end time: seamlessly bridge to next word or keep short hold
            if w_idx < burst_len - 1:
                w_end = burst[w_idx + 1]["start"]
            else:
                if b_idx < len(bursts) - 1:
                    next_burst_start = bursts[b_idx + 1][0]["start"]
                    w_end = min(w_item["end"] + 0.28, next_burst_start)
                else:
                    w_end = min(total_duration, w_item["end"] + 0.35)

            if w_end <= w_start:
                w_end = w_start + 0.22

            # Active word animations based on style_mode
            styled_words = []
            for j, w in enumerate(burst_words):
                if j == w_idx:
                    if style_mode == "neon_glow":
                        # Neon blurred glow aura + 120% pop
                        pop_tag = "{\\c" + highlight_color + "\\3c" + highlight_color + "\\blur5\\t(0,60,\\fscx120\\fscy120)\\t(60,130,\\fscx100\\fscy100)}"
                        reset_tag = "{\\c&HFFFFFF&\\3c&H000000&\\blur0\\fscx100\\fscy100}"
                    elif style_mode == "sliding":
                        # Active highlighted, pop
                        pop_tag = "{\\c" + highlight_color + "\\3c&H000000&\\fscx112\\fscy112}"
                        reset_tag = "{\\c&HFFFFFF&\\fscx100\\fscy100}"
                    else:
                        # Hormozi style pop
                        pop_tag = "{\\c" + highlight_color + "\\t(0,60,\\fscx118\\fscy118)\\t(60,130,\\fscx100\\fscy100)}"
                        reset_tag = "{\\c&HFFFFFF&\\fscx100\\fscy100}"
                    styled_words.append(f"{pop_tag}{w}{reset_tag}")
                else:
                    if style_mode == "sliding" and j < w_idx:
                        # Preceding word in sliding burst is dimmed
                        styled_words.append(f"{{\\alpha&H66&}}{w}{{\\alpha&H00&}}")
                    else:
                        styled_words.append(w)

            line_text = " ".join(styled_words)
            start_str = format_ass_time(w_start)
            end_str = format_ass_time(min(total_duration, w_end))
            events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{line_text}")

    return events


def generate_from_sentences(
    sentences: List[str],
    total_duration: float,
    highlight_color: str,
    max_words: int = 2
) -> List[str]:
    """
    Fallback subtitle generator when boundary timestamps are unavailable.
    """
    events = []
    total_words = sum(len(s.split()) for s in sentences if s.strip())
    if total_words == 0:
        total_words = 1
    seconds_per_word = (total_duration - 0.2) / total_words

    current_time = 0.1
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        bursts = split_into_bursts(sentence, max_words=max_words)
        for burst in bursts:
            burst = [clean_caption_word(w) for w in burst]
            burst_words_count = len(burst)
            burst_duration = max(0.5, burst_words_count * seconds_per_word)
            burst_start = current_time
            burst_end = min(total_duration, burst_start + burst_duration)

            word_time_slice = burst_duration / max(1, burst_words_count)
            for idx in range(burst_words_count):
                w_start = burst_start + (idx * word_time_slice)
                w_end = min(burst_end, w_start + word_time_slice)

                styled_parts = []
                for j, w in enumerate(burst):
                    if j == idx:
                        pop_tag = "{\\c" + highlight_color + "\\t(0,60,\\fscx118\\fscy118)\\t(60,130,\\fscx100\\fscy100)}"
                        reset_tag = "{\\c&HFFFFFF&\\fscx100\\fscy100}"
                        styled_parts.append(f"{pop_tag}{w}{reset_tag}")
                    else:
                        styled_parts.append(w)

                line_text = " ".join(styled_parts)
                start_str = format_ass_time(w_start)
                end_str = format_ass_time(w_end)
                events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{line_text}")

            current_time = burst_end

    return events


def generate_ass_subtitles(
    sentences: List[str],
    total_duration: float,
    output_ass_path: str,
    lang: str = "en",
    style: str = "hormozi",
    boundaries: Optional[List[Dict[str, Any]]] = None,
    font_size: int = 96,
    margin_v: int = 520,
    highlight_color: Optional[str] = None,
    hook_text: Optional[str] = None
) -> str:
    """
    Generate viral ASS subtitle file synchronized with speech duration.
    Uses Mukta Malar ExtraBold for guaranteed complex HarfBuzz ligature shaping (Tamil & English).
    """
    font_name = "Mukta Malar ExtraBold"
    hl_color = get_palette_color(highlight_color or style)

    # ASS Header configuration:
    # MarginV 520 keeps text elevated above YouTube mobile Shorts UI elements (channel info, sound button)
    ass_header = f"""[Script Info]
Title: Viral YouTube Shorts Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,9,4,2,80,80,{margin_v},1
Style: Hook,{font_name},112,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,10,5,8,70,70,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    if boundaries and len(boundaries) > 0:
        events = generate_from_boundaries(boundaries, total_duration, hl_color, max_words=2, style_mode=style)
    else:
        events = generate_from_sentences(sentences, total_duration, hl_color, max_words=2)

    if hook_text:
        hook_event = build_hook_event(hook_text, hl_color, duration=min(2.6, total_duration))
        if hook_event:
            events.insert(0, hook_event)

    os.makedirs(os.path.dirname(output_ass_path) or ".", exist_ok=True)
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events) + "\n")

    return output_ass_path
