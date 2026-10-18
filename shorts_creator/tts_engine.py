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
        "female_expressive": "ta-IN-PallaviNeural",
        "female_articulate": "ta-SG-VenbaNeural",
        "female_gentle": "ta-LK-SaranyaNeural",
        "female_lively": "ta-MY-KaniNeural",
        "male": "ta-IN-ValluvarNeural",
        "fast_male": "ta-SG-AnbuNeural",
        "male_malaysia": "ta-MY-SuryaNeural",
        "male_lanka": "ta-LK-KumarNeural",
        "default": "ta-IN-PallaviNeural"
    },
    "en": {
        "female": "en-US-JennyNeural",
        "female_warm": "en-US-AvaNeural",
        "female_copilot": "en-US-AvaMultilingualNeural",
        "female_crisp": "en-US-EmmaNeural",
        "female_news": "en-US-AriaNeural",
        "female_story": "en-US-AnaNeural",
        "female_indian": "en-IN-NeerjaExpressiveNeural",
        "female_british": "en-GB-SoniaNeural",
        "female_aussie": "en-AU-NatashaNeural",
        "male": "en-US-ChristopherNeural",
        "male_copilot": "en-US-AndrewMultilingualNeural",
        "male_casual": "en-US-BrianMultilingualNeural",
        "male_passionate": "en-US-GuyNeural",
        "indian_male": "en-IN-PrabhatNeural",
        "default": "en-US-JennyNeural"
    },
    "hi": {
        "female": "hi-IN-SwaraNeural",
        "male": "hi-IN-MadhurNeural",
        "default": "hi-IN-SwaraNeural"
    },
    "te": {
        "female": "te-IN-ShrutiNeural",
        "male": "te-IN-MohanNeural",
        "default": "te-IN-ShrutiNeural"
    },
    "ml": {
        "female": "ml-IN-SobhanaNeural",
        "male": "ml-IN-MidhunNeural",
        "default": "ml-IN-SobhanaNeural"
    },
    "kn": {
        "female": "kn-IN-SapnaNeural",
        "male": "kn-IN-GaganNeural",
        "default": "kn-IN-SapnaNeural"
    }
}

VOICE_ALIASES = {
    # Tamil Female Voices
    "pallavi": "ta-IN-PallaviNeural",
    "venba": "ta-SG-VenbaNeural",
    "saranya": "ta-LK-SaranyaNeural",
    "kani": "ta-MY-KaniNeural",
    "female_ta": "ta-IN-PallaviNeural",

    # Tamil Male Voices
    "valluvar": "ta-IN-ValluvarNeural",
    "anbu": "ta-SG-AnbuNeural",
    "surya": "ta-MY-SuryaNeural",
    "kumar": "ta-LK-KumarNeural",
    "male_ta": "ta-IN-ValluvarNeural",

    # English Female Voices
    "jenny": "en-US-JennyNeural",
    "ava": "en-US-AvaMultilingualNeural",
    "emma": "en-US-EmmaMultilingualNeural",
    "aria": "en-US-AriaNeural",
    "ana": "en-US-AnaNeural",
    "michelle": "en-US-MichelleNeural",
    "neerja": "en-IN-NeerjaExpressiveNeural",
    "sonia": "en-GB-SoniaNeural",
    "libby": "en-GB-LibbyNeural",
    "maisie": "en-GB-MaisieNeural",
    "natasha": "en-AU-NatashaNeural",
    "clara": "en-CA-ClaraNeural",
    "female_en": "en-US-JennyNeural",

    # English Male Voices
    "andrew": "en-US-AndrewMultilingualNeural",
    "brian": "en-US-BrianMultilingualNeural",
    "christopher": "en-US-ChristopherNeural",
    "guy": "en-US-GuyNeural",
    "eric": "en-US-EricNeural",
    "roger": "en-US-RogerNeural",
    "steffan": "en-US-SteffanNeural",
    "prabhat": "en-IN-PrabhatNeural",
    "ryan": "en-GB-RyanNeural",
    "thomas": "en-GB-ThomasNeural",
    "william": "en-AU-WilliamMultilingualNeural",
    "male_en": "en-US-ChristopherNeural",

    # VoiceStudio Sovereign Personas
    "jarvis": "en-US-ChristopherNeural",       # Calm, sophisticated AI copilot
    "samantha": "en-US-JennyNeural",           # Warm, conversationalist
    "cinema-narrator": "en-US-EricNeural",     # Resonant, deep authoritative trailer voice
    "cyber-synth": "en-US-GuyNeural",          # Glitched energetic vocoded AI
    "tamil-tech": "ta-IN-PallaviNeural",       # Technical Tamil narrator
    "tamil-female": "ta-IN-PallaviNeural",
    "tamil-male": "ta-IN-ValluvarNeural",

    # Hindi Voices
    "swara": "hi-IN-SwaraNeural",
    "madhur": "hi-IN-MadhurNeural",

    # Telugu Voices
    "shruti": "te-IN-ShrutiNeural",
    "mohan": "te-IN-MohanNeural",

    # Malayalam Voices
    "sobhana": "ml-IN-SobhanaNeural",
    "midhun": "ml-IN-MidhunNeural",

    # Kannada Voices
    "sapna": "kn-IN-SapnaNeural",
    "gagan": "kn-IN-GaganNeural"
}


def resolve_voice_identifier(voice_query: Optional[str], lang: str) -> str:
    """Resolves short voice names or aliases to verified Edge-TTS full voice tags."""
    if not voice_query:
        return get_default_voice(lang)
    q = voice_query.strip().lower()
    if q in VOICE_ALIASES:
        return VOICE_ALIASES[q]
    for alias, full_v in VOICE_ALIASES.items():
        if alias in q:
            return full_v
    # If already a full Edge-TTS neural tag
    if "neural" in q:
        return voice_query.strip()
    return voice_query.strip()


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
    output_target: Optional[str] = None,
    lang: Optional[str] = None,
    output_dir: Optional[str] = None,
    custom_voice: Optional[str] = None,
    voice: Optional[str] = None,
    rate: str = "+0%",
    pitch: str = "+0Hz"
) -> Dict[str, Any]:
    """
    Main entry point for voiceover generation.
    Supports directory or file output targets, voice/custom_voice, and automatic language detection.
    """
    import re
    import tempfile
    # Determine language
    default_tmp = tempfile.gettempdir()
    if output_target in ["en", "ta", "hi", "te", "ml", "kn"]:
        lang = output_target
        dest = output_dir or default_tmp
    else:
        dest = output_target or output_dir or default_tmp

    if not lang:
        lang = "ta" if re.search(r'[\u0B80-\u0BFF]', text) else "en"

    # Resolve audio file path
    if dest.endswith((".mp3", ".wav", ".m4a", ".aac")):
        audio_path = dest
        os.makedirs(os.path.dirname(audio_path) or ".", exist_ok=True)
    else:
        os.makedirs(dest, exist_ok=True)
        audio_path = os.path.join(dest, "voiceover.mp3")

    effective_voice_arg = voice or custom_voice
    resolved_voice = resolve_voice_identifier(effective_voice_arg, lang)

    # Automatically enhance pacing and inflection for Tamil
    eff_rate = rate
    eff_pitch = pitch
    if lang == "ta" and (rate == "+0%" or not rate):
        eff_rate = "+8%"
        eff_pitch = "+1Hz"

    # 1. Try Edge-TTS with millisecond word boundary capture
    success, boundaries = asyncio.run(
        try_edge_tts_with_boundaries(text, resolved_voice, audio_path, rate=eff_rate, pitch=eff_pitch)
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


def preview_voiceover(text: str, voice: str = "jarvis"):
    """Plays voiceover narration through studio audio for previewing before video render."""
    import shutil
    import tempfile
    from pathlib import Path

    if shutil.which("iram-voice"):
        voice_slug = voice
        for k, v in VOICE_ALIASES.items():
            if v == voice or k == voice:
                voice_slug = k
                break
        print(f"🔊 Playing preview via IRAM Voice Studio ({voice_slug})...")
        subprocess.run(["iram-voice", "speak", text, "--voice", voice_slug])
        return

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        generate_voiceover(text, tmp_path, voice=voice)
        if shutil.which("pw-play"):
            subprocess.run(["pw-play", tmp_path])
        elif shutil.which("ffplay"):
            subprocess.run(["ffplay", "-nodisp", "-autoexit", tmp_path])
        elif shutil.which("mpv"):
            subprocess.run(["mpv", "--no-video", tmp_path])
        else:
            print(f"🔊 [Voice Preview] Audio generated at: {tmp_path} (install ffplay or mpv to listen directly)")
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


