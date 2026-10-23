"""
Animated Subtitle Engine (Hormozi / Viral Shorts Style).
Generates Advanced SubStation Alpha (.ass) subtitles with:
- True millisecond word-by-word highlight synchronization
- Micro-bounce pop animations on spoken words (\\fscx, \\fscy)
- Contextual semantic emoji detection for Tamil and English
- Ultra-punchy 1-2 word rapid kinetic bursts
- Full Tamil Unicode HarfBuzz complex ligature shaping
- Multi-palette viral neon themes
"""

import os
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
    "மூளை": "🧠", "சிந்தனை": "🧠", "mind": "🧠", "mindset": "🧠", "focus": "🎯",
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
    for k, emoji in SEMANTIC_EMOJIS.items():
        if k in clean_w and len(k) >= 3:
            return emoji
    return ""


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
    palettes = {
        "hormozi": "&H00FFFF&",      # Neon Yellow
        "neon-cyan": "&HFFFF00&",    # Neon Cyan
        "neon-green": "&H00FF00&",   # Emerald Green
        "fire-red": "&H0045FF&",     # Fire Red / Orange
        "gold": "&H00D7FF&",         # Rich Gold
        "purple-neon": "&HFF00FF&",  # Cyber Purple / Magenta
        "white-classic": "&HFFFFFF&" # Crisp White
    }
    return palettes.get(style.lower(), "&H00FFFF&")


def generate_from_boundaries(
    boundaries: List[Dict[str, Any]],
    total_duration: float,
    highlight_color: str,
    max_words: int = 2
) -> List[str]:
    """
    Generate kinetic ASS subtitle events using exact Edge-TTS word boundaries with auto-emojis.
    """
    events = []
    # Filter valid words
    valid_items = [b for b in boundaries if b.get("word") and b.get("word").strip()]
    if not valid_items:
        return events

    # Group into punchy 1-2 word bursts
    bursts: List[List[Dict[str, Any]]] = []
    current_burst: List[Dict[str, Any]] = []
    for item in valid_items:
        current_burst.append(item)
        if len(current_burst) >= max_words:
            bursts.append(current_burst)
            current_burst = []
    if current_burst:
        bursts.append(current_burst)

    for b_idx, burst in enumerate(bursts):
        burst_words = [item["word"] for item in burst]
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

            # Active word has pop bounce animation (\t scale), highlight color, and contextual emoji
            styled_words = []
            for j, w in enumerate(burst_words):
                if j == w_idx:
                    emoji = get_word_emoji(w)
                    w_display = f"{w} {emoji}" if emoji else w
                    # Pop 18% larger on speech start, then settle smoothly back
                    pop_tag = "{\\c" + highlight_color + "\\t(0,60,\\fscx118\\fscy118)\\t(60,130,\\fscx100\\fscy100)}"
                    reset_tag = "{\\c&HFFFFFF&\\fscx100\\fscy100}"
                    styled_words.append(f"{pop_tag}{w_display}{reset_tag}")
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
                        emoji = get_word_emoji(w)
                        w_display = f"{w} {emoji}" if emoji else w
                        pop_tag = "{\\c" + highlight_color + "\\t(0,60,\\fscx118\\fscy118)\\t(60,130,\\fscx100\\fscy100)}"
                        reset_tag = "{\\c&HFFFFFF&\\fscx100\\fscy100}"
                        styled_parts.append(f"{pop_tag}{w_display}{reset_tag}")
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
    boundaries: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Generate viral ASS subtitle file synchronized with speech duration.
    Uses Mukta Malar for guaranteed complex HarfBuzz ligature shaping (Tamil & English).
    """
    font_name = "Mukta Malar"
    highlight_color = get_palette_color(style)

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
Style: Default,{font_name},78,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,1,0,0,0,100,100,0,0,1,9,4,2,80,80,520,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    if boundaries and len(boundaries) > 0:
        events = generate_from_boundaries(boundaries, total_duration, highlight_color, max_words=2)
    else:
        events = generate_from_sentences(sentences, total_duration, highlight_color, max_words=2)

    os.makedirs(os.path.dirname(output_ass_path), exist_ok=True)
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events) + "\n")

    return output_ass_path
