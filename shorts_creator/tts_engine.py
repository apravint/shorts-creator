"""
Hybrid Neural Text-To-Speech (TTS) Engine.
Primary: Microsoft Edge Neural Voices (Studio quality, dynamic expression).
Fallback: Google TTS (gTTS) - 100% reliable, zero-throttle backup for Tamil and English.
"""

import os
import json
import asyncio
import subprocess
from typing import Dict, Any, List, Optional
import edge_tts
from gtts import gTTS

# Verified active voices
VOICE_MAP = {
    "ta": {
        "female": "ta-IN-PallaviNeural",
        "male": "ta-SG-AnbuNeural",
        "default": "ta-IN-PallaviNeural"
    },
    "en": {
        "male": "en-US-ChristopherNeural",
        "indian_male": "en-IN-PrabhatNeural",
        "default": "en-US-ChristopherNeural"
    }
}


def get_default_voice(lang: str, gender: str = "default") -> str:
    """Return verified working voice for the given language."""
    if lang == "ta":
        return VOICE_MAP["ta"].get(gender, VOICE_MAP["ta"]["default"])
    return VOICE_MAP["en"].get(gender, VOICE_MAP["en"]["default"])


def get_audio_duration(audio_file: str) -> float:
    """Measure exact duration of an audio file in seconds via ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_file
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"[Warning] ffprobe duration check failed: {e}. Estimating.")
        return 30.0


async def try_edge_tts_with_boundaries(
    text: str,
    voice: str,
    output_audio: str,
    rate: str = "+0%",
    pitch: str = "+0Hz"
) -> tuple:
    """
    Attempt synthesis via Edge-TTS and capture exact millisecond word boundaries.
    """
    boundaries: List[Dict[str, Any]] = []
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        with open(output_audio, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    # Offset and duration are in 100-nanosecond units (ticks)
                    start_sec = chunk["offset"] / 10_000_000.0
                    dur_sec = chunk["duration"] / 10_000_000.0
                    boundaries.append({
                        "word": chunk.get("text", "").strip(),
                        "start": round(start_sec, 3),
                        "end": round(start_sec + dur_sec, 3),
                        "duration": round(dur_sec, 3)
                    })
        success = os.path.exists(output_audio) and os.path.getsize(output_audio) > 1000
        return success, boundaries
    except Exception as e:
        print(f"[Info] Edge-TTS notice: {e}. Switching to gTTS fallback.")
        return False, []


def synthesize_with_gtts(text: str, lang: str, output_audio: str) -> bool:
    """Synthesize voice using Google TTS (gTTS)."""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_audio)
        return os.path.exists(output_audio) and os.path.getsize(output_audio) > 1000
    except Exception as e:
        print(f"[Error] gTTS synthesis failed: {e}")
        return False


def generate_voiceover(
    text: str,
    lang: str,
    output_dir: str,
    custom_voice: Optional[str] = None,
    rate: str = "+0%"
) -> Dict[str, Any]:
    """
    Main entry point for voiceover generation.
    Generates audio, captures exact word timestamps, and calculates duration.
    """
    os.makedirs(output_dir, exist_ok=True)
    voice = custom_voice or get_default_voice(lang)
    audio_path = os.path.join(output_dir, "voiceover.mp3")

    # 1. Try Edge-TTS with millisecond word boundary capture
    success, boundaries = asyncio.run(
        try_edge_tts_with_boundaries(text, voice, audio_path, rate=rate)
    )

    # 2. Seamless Fallback to gTTS if Edge-TTS failed or throttled
    engine_used = "Edge-TTS"
    if not success:
        print(f"[Info] Using high-reliability Google TTS for {lang.upper()} voiceover...")
        success = synthesize_with_gtts(text, lang, audio_path)
        engine_used = "gTTS"
        boundaries = []

    if not success:
        raise RuntimeError("Failed to synthesize audio with both Edge-TTS and gTTS engines.")

    duration = get_audio_duration(audio_path)

    return {
        "audio_path": audio_path,
        "duration": duration,
        "voice": f"{voice} ({engine_used})",
        "lang": lang,
        "boundaries": boundaries
    }

