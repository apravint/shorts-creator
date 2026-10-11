"""
Animated Subtitle Engine (Hormozi / Viral Shorts Style).
Generates Advanced SubStation Alpha (.ass) subtitles with word-by-word highlights,
vibrant neon colors, thick outlines, and full Tamil & English Unicode typography.
"""

import os
from typing import List, Dict, Any


def format_ass_time(seconds: float) -> str:
    """Format seconds into ASS timestamp format: H:MM:SS.cs"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        centis = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{centis:02d}"


def split_into_bursts(text: str, max_words: int = 3) -> List[List[str]]:
    """Split a sentence into punchy 2-3 word visual bursts."""
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


def generate_ass_subtitles(
    sentences: List[str],
    total_duration: float,
    output_ass_path: str,
    lang: str = "en",
    style: str = "hormozi",
    boundaries: List[Dict[str, Any]] = None
) -> str:
    """
    Generate viral ASS subtitle file synchronized with speech duration.
    Uses Mukta Malar for guaranteed complex HarfBuzz ligature shaping (Tamil & English).
    """
    # Primary font: Mukta Malar has full native Tamil + Latin OpenType GSUB/GPOS tables
    font_name = "Mukta Malar"

    # Color Palettes (BGR Hex in ASS format: &HAABBGGRR)
    highlight_color = "&H0000FFFF"  # Neon Yellow
    if style == "neon-cyan":
        highlight_color = "&H00FFFF00"  # Cyan
    elif style == "neon-green":
        highlight_color = "&H0000FF00"  # Green
    elif style == "fire-red":
        highlight_color = "&H000045FF"  # Red / Orange

    # Spacing MUST be 0 so Tamil conjunct consonants and vowel marks never split.
    # Outline 8 + Shadow 4 gives maximum pop over moving video backgrounds.
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
Style: Default,{font_name},76,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,1,0,0,0,100,100,0,0,1,8,4,2,80,80,500,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    
    # Calculate timestamps per sentence
    total_words = sum(len(s.split()) for s in sentences if s.strip())
    if total_words == 0:
        total_words = 1
    seconds_per_word = (total_duration - 0.2) / total_words

    current_time = 0.1

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        bursts = split_into_bursts(sentence, max_words=3)
        for burst in bursts:
            burst_words_count = len(burst)
            burst_duration = max(0.6, burst_words_count * seconds_per_word)
            burst_start = current_time
            burst_end = min(total_duration, burst_start + burst_duration)

            # Word-level highlight inside the burst
            word_time_slice = burst_duration / max(1, burst_words_count)
            for idx in range(burst_words_count):
                w_start = burst_start + (idx * word_time_slice)
                w_end = min(burst_end, w_start + word_time_slice)
                
                # Active word turns highlight color, then switches back to white.
                # Preserves continuous text shaping without resetting HarfBuzz runs.
                styled_parts = []
                for j, w in enumerate(burst):
                    if j == idx:
                        styled_parts.append(f"{{\\c{highlight_color}&}}{w}{{\\c&H00FFFFFF&}}")
                    else:
                        styled_parts.append(w)
                
                line_text = " ".join(styled_parts)
                start_str = format_ass_time(w_start)
                end_str = format_ass_time(w_end)
                events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{line_text}")

            current_time = burst_end

    os.makedirs(os.path.dirname(output_ass_path), exist_ok=True)
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events) + "\n")

    return output_ass_path
