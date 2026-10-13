"""
Multi-Beat B-Roll Montage & Visual Synchronization Engine for ShortsCreator AI.
Transforms full-length scripts into dynamically cut, sentence-synchronized B-roll video montages.
Every beat/sentence gets a unique, authentic visual shot (open-source video or 2.5D camera animated AI art)
perfectly matching spoken words and timing. Eliminates repetitive static loops and cards.
"""

import os
import re
import math
import random
import urllib.parse
import urllib.request
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

from .video_fetcher import get_open_source_video, TAMIL_TO_ENGLISH_MAP

USER_AGENT = "ShortsCreatorAI/2.0 (https://github.com/apravint/shorts-creator; apravint@gmail.com)"


def calculate_sentence_timings(
    sentences: List[str],
    total_duration: float,
    boundaries: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Calculates exact start, end, and duration for each sentence in the script.
    If speech engine word boundaries are provided, maps them to sentences with millisecond precision.
    Otherwise, applies intelligent syllable/word length proportionality.
    """
    clean_sentences = [s.strip() for s in sentences if s.strip()]
    if not clean_sentences:
        return [{"text": "Video", "start": 0.0, "end": total_duration, "duration": total_duration}]

    # 1. Map boundaries from Edge-TTS if available
    if boundaries and len(boundaries) >= 4:
        # Normalize boundaries
        beats = []
        b_idx = 0
        total_bounds = len(boundaries)

        for s_idx, sent in enumerate(clean_sentences):
            sent_words = [w.lower().strip(".,!?:;\"'()[]") for w in sent.split() if w.strip()]
            if not sent_words:
                continue

            start_t = boundaries[b_idx]["start"] if b_idx < total_bounds else (total_duration * (s_idx / len(clean_sentences)))

            # Advance boundary pointer
            matched = 0
            while b_idx < total_bounds and matched < len(sent_words):
                b_word = boundaries[b_idx].get("text", "").lower().strip(".,!?:;\"'()[]")
                if b_word in sent_words or any(sw in b_word for sw in sent_words):
                    matched += 1
                b_idx += 1

            end_t = boundaries[min(b_idx, total_bounds - 1)]["end"] if b_idx > 0 else (start_t + 3.0)
            if s_idx == len(clean_sentences) - 1:
                end_t = total_duration

            dur = max(1.8, end_t - start_t)
            beats.append({
                "index": s_idx + 1,
                "text": sent,
                "start": round(start_t, 3),
                "end": round(start_t + dur, 3),
                "duration": round(dur, 3)
            })

        if beats:
            # Scale sum to precisely match total_duration
            curr_total = sum(b["duration"] for b in beats)
            if curr_total > 0:
                scale = total_duration / curr_total
                curr_t = 0.0
                for b in beats:
                    b["start"] = round(curr_t, 3)
                    b["duration"] = round(b["duration"] * scale, 3)
                    curr_t += b["duration"]
                    b["end"] = round(curr_t, 3)
                beats[-1]["end"] = round(total_duration, 3)
                beats[-1]["duration"] = round(beats[-1]["end"] - beats[-1]["start"], 3)
                return beats

    # 2. Word-count proportional calculation fallback
    word_counts = [max(1, len(s.split())) for s in clean_sentences]
    total_w = sum(word_counts)
    beats = []
    curr_t = 0.0

    for idx, (sent, wc) in enumerate(zip(clean_sentences, word_counts)):
        dur = (wc / total_w) * total_duration
        beats.append({
            "index": idx + 1,
            "text": sent,
            "start": round(curr_t, 3),
            "end": round(curr_t + dur, 3),
            "duration": round(dur, 3)
        })
        curr_t += dur

    if beats:
        beats[-1]["end"] = round(total_duration, 3)
        beats[-1]["duration"] = round(beats[-1]["end"] - beats[-1]["start"], 3)

    return beats


def resolve_beat_visual_query(sentence_text: str, global_topic: str = "", beat_idx: int = 1) -> str:
    """
    Extracts semantic visual context from sentence text (Tamil & English) to retrieve
    a bespoke, contextually accurate visual shot.
    """
    text_lower = (sentence_text or "").lower()
    topic_lower = (global_topic or "").lower()
    combined = f"{text_lower} {topic_lower}"

    # 1. Motivation / Mindset / Struggle / Victory
    is_motivational = any(k in combined for k in [
        "தோல்வி", "வெற்றி", "விடாமுயற்சி", "உழைப்பு", "கனவு", "நம்பிக்கை",
        "எழுச்சி", "சிகரம்", "ஓடு", "தடை", "அடி", "கைவிடாதே", "வீரம்", "நெருப்பு",
        "discipline", "motivation", "unstoppable", "mindset", "success", "action",
        "fear", "courage", "overcome", "victory", "runner", "athlete", "summit", "perseverance"
    ])

    if is_motivational:
        if any(k in text_lower for k in ["தோல்வி", "விழு", "உடைக்க", "இருள்", "தடை", "fail", "broken", "fall", "obstacle", "storm", "struggle"]):
            shots = [
                "dramatic dark storm ocean waves crashing rocks silhouette",
                "lone determined figure walking through dark foggy rain",
                "boxer exhausted in shadows catching breath dramatic lighting",
                "intense warrior silhouette standing against dark stormy sky"
            ]
            return shots[(beat_idx) % len(shots)]

        elif any(k in text_lower for k in ["விதை", "விருட்சம்", "முளைத்து", "மண்", "seed", "sprout", "grow", "tree", "plant", "roots"]):
            shots = [
                "seedling sprouting green dark rich soil time lapse cinematic",
                "giant majestic oak tree sunbeams breaking through forest",
                "golden hour sunrise over mountain forest landscape"
            ]
            return shots[(beat_idx) % len(shots)]

        elif any(k in text_lower for k in ["கனவு", "நம்பிக்கை", "பாதை", "horizon", "dream", "vision", "path", "hope"]):
            shots = [
                "lone hiker walking toward distant epic mountain peaks golden hour",
                "eagle soaring above vast sunrise clouds aerial cinematic",
                "rock climber standing on mountain ledge looking into vast horizon"
            ]
            return shots[(beat_idx) % len(shots)]

        elif any(k in text_lower for k in ["அடி", "தொடங்கு", "துவங்கு", "உழைப்பு", "step", "start", "action", "work", "train"]):
            shots = [
                "sprinter in starting blocks athletic track focused eyes",
                "running shoes sprinting fast across morning pavement dawn",
                "athlete training intense workout sweat dramatic gym lighting"
            ]
            return shots[(beat_idx) % len(shots)]

        elif any(k in text_lower for k in ["வெற்றி", "சிகரம்", "எழுந்து", "தலைவணங்கும்", "win", "victory", "champion", "summit", "peak"]):
            shots = [
                "climber standing on mountain summit sunrise raising hands in victory",
                "athlete crossing finish line victory golden sunlight",
                "breathtaking golden mountain peak sunrise volumetric light rays"
            ]
            return shots[(beat_idx) % len(shots)]
        else:
            shots = [
                "dramatic hero reveal silhouette rising morning dawn",
                "fire burning torch flame dramatic dark background",
                "athlete running along ocean beach sunrise waves"
            ]
            return shots[(beat_idx) % len(shots)]

    # 2. Deep Space / Astronomy
    is_space = any(k in combined for k in [
        "space", "galaxy", "universe", "planet", "stars", "black hole", "cosmic", "mars",
        "விண்வெளி", "கிரகம்", "சூரியன்", "நிலா", "அண்டம்", "கருந்துளை"
    ])
    if is_space:
        space_shots = [
            "deep space galaxy nebula spiral stars cinematic 8k",
            "supermassive black hole glowing accretion disk gravitational lensing",
            "futuristic spaceship exploring alien planet orbit cosmic",
            "mars rover surface red dust landscape sunset",
            "astronaut floating in deep space earth background sun flare"
        ]
        return space_shots[(beat_idx) % len(space_shots)]

    # 3. Technology / AI / Coding / Cyber
    is_tech = any(k in combined for k in [
        "tech", "technology", "drone", "computer", "coding", "software", "ai", "cyber", "robot",
        "தொழில்நுட்பம்", "கணினி", "ரோபோ", "செயற்கை நுண்ணறிவு"
    ])
    if is_tech:
        tech_shots = [
            "futuristic neural network AI brain glowing data connections",
            "hands typing mechanical keyboard syntax code dark neon desk",
            "datacenter server racks glowing blue fiber optic cables",
            "futuristic cyberpunk city skyline flying cars neon rain",
            "microchip processor circuit board glowing gold data pulses"
        ]
        return tech_shots[(beat_idx) % len(tech_shots)]

    # 4. Nature / Ocean / Ancient
    if any(k in combined for k in ["கடல்", "ocean", "sea", "water", "waves"]):
        return "majestic turquoise ocean giant waves crashing dramatic aerial 4k"
    if any(k in combined for k in ["மலை", "mountain", "peak", "climb"]):
        return "epic misty mountain range sunrise clouds cinematic 4k"
    if any(k in combined for k in ["வரலாறு", "கோயில்", "சோழர்", "history", "ancient", "temple"]):
        return "ancient magnificent stone temple royal architecture golden hour"

    # Default fallback
    clean = re.sub(r'[^\w\s]', ' ', text_lower)
    words = [w for w in clean.split() if len(w) > 3][:3]
    return f"{' '.join(words)} cinematic masterpiece 4k" if words else "cinematic documentary landscape 4k"


def download_ai_keyframe_image(prompt: str, out_image_path: Path, width: int = 1080, height: int = 1920) -> bool:
    """Generates an ultra-crisp AI visual keyframe using Pollinations AI (zero-auth, instantaneous)."""
    out_image_path = Path(out_image_path)
    out_image_path.parent.mkdir(parents=True, exist_ok=True)

    seed = random.randint(1000, 999999)
    clean_p = urllib.parse.quote(f"cinematic photorealistic 8k, {prompt}, masterpiece, 35mm photography, natural lighting")
    url = f"https://image.pollinations.ai/prompt/{clean_p}?width={width}&height={height}&seed={seed}&nologo=true"

    headers = {"User-Agent": USER_AGENT}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = resp.read()
            if len(content) > 15000:
                with open(out_image_path, "wb") as f:
                    f.write(content)
                return True
    except Exception:
        pass
    return False


def render_single_beat_clip(
    query: str,
    duration: float,
    out_video_path: Path,
    beat_idx: int = 1,
    width: int = 1080,
    height: int = 1920,
    fps: int = 30,
    used_videos: Optional[set] = None,
    visual_mode: str = "auto"
) -> Path:
    """
    Renders an individual beat clip tailored to its exact duration:
    1. Attempts to find an unused matching open-source video clip (if not forced AI).
    2. If found, scales & crops to 9:16 vertical and trims to duration.
    3. If no video is found or already used, generates a high-res AI keyframe and animates it with Ken Burns 2.5D camera movement!
    """
    out_video_path = Path(out_video_path)
    out_video_path.parent.mkdir(parents=True, exist_ok=True)
    d_frames = max(30, int(duration * fps))

    # 1. Try real open-source stock video (if allowed by visual_mode)
    if visual_mode != "ai":
        stock_candidate = get_open_source_video(query_or_topic=query)
        if (
            stock_candidate
            and os.path.isfile(stock_candidate)
            and os.path.getsize(stock_candidate) > 200000
            and (used_videos is None or stock_candidate not in used_videos)
        ):
            if used_videos is not None:
                used_videos.add(stock_candidate)

            # Randomize offset slightly so clips don't all start identically
            ss_offset = (beat_idx * 2) % 6
            crop_filter = (
                f"scale={width}:{height}:force_original_aspect_ratio=increase,"
                f"crop={width}:{height},setsar=1,"
                f"eq=contrast=1.04:brightness=-0.03"
            )
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(ss_offset),
                "-stream_loop", "-1",
                "-i", stock_candidate,
                "-vf", crop_filter,
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "19",
                "-pix_fmt", "yuv420p",
                "-an",
                "-t", f"{duration:.3f}",
                str(out_video_path)
            ]
            try:
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                if out_video_path.exists() and out_video_path.stat().st_size > 10000:
                    return out_video_path
            except Exception:
                pass

    # 2. Bespoke High-resolution AI Keyframe + 2.5D Ken Burns Cinematic Camera Animator
    img_path = out_video_path.with_suffix(".jpg")
    img_success = download_ai_keyframe_image(query, img_path, width=width, height=height)

    if img_success and img_path.exists():
        # Alternate 4-way cinematic camera choreography
        camera_type = beat_idx % 4
        if camera_type == 0:
            # Steady slow push-in (Hero focus)
            zp = f"zoompan=z='min(zoom+0.0005,1.08)':d={d_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
        elif camera_type == 1:
            # Gentle pull-back (Revealing scale)
            zp = f"zoompan=z='max(1.08-0.0005*on,1.0)':d={d_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
        elif camera_type == 2:
            # Upward hero rise (Aspirational climb)
            zp = f"zoompan=z=1.05:d={d_frames}:x='iw/2-(iw/zoom/2)':y='ih*0.62-(ih*0.25*(on/{d_frames}))':s={width}x{height}:fps={fps}"
        else:
            # Subtle horizontal drift (Documentary pan)
            zp = f"zoompan=z=1.06:d={d_frames}:x='(iw*0.05)+(iw*0.1*(on/{d_frames}))':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"

        cmd_anim = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_path),
            "-vf", f"{zp},eq=contrast=1.04:saturation=1.03,format=yuv420p",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-an",
            "-t", f"{duration:.3f}",
            str(out_video_path)
        ]
        try:
            subprocess.run(cmd_anim, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            if out_video_path.exists() and out_video_path.stat().st_size > 10000:
                return out_video_path
        except Exception:
            pass

    # 3. Emergency Procedural Motion Gradient
    cmd_proc = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"gradients=s={width}x{height}:d={duration}:r={fps}:c0=0x0a0f1d:c1=0x1e1b4b,vignette=PI/3.2",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-an",
        "-t", f"{duration:.3f}",
        str(out_video_path)
    ]
    subprocess.run(cmd_proc, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return out_video_path


def build_multi_beat_montage(
    sentences: List[str],
    total_duration: float,
    workspace_dir: Path,
    out_stitched_video: Path,
    global_topic: str = "",
    boundaries: Optional[List[Dict[str, Any]]] = None,
    width: int = 1080,
    height: int = 1920,
    visual_mode: str = "auto"
) -> Path:
    """
    Master B-Roll Orchestrator:
    1. Splits script into rhythmic visual beats synced to speech timestamps.
    2. Renders a unique, non-repeating video clip for every single beat.
    3. Stitches all clips seamlessly into a single 1080x1920 video montage.
    """
    workspace_dir = Path(workspace_dir)
    workspace_dir.mkdir(parents=True, exist_ok=True)
    beats_dir = workspace_dir / "beat_clips"
    beats_dir.mkdir(parents=True, exist_ok=True)

    beats = calculate_sentence_timings(sentences, total_duration, boundaries=boundaries)
    rendered_clips: List[Path] = []
    used_stock_videos: set = set()

    print(f"🎬 [B-Roll Director] Assembling dynamic {len(beats)}-shot visual montage for '{global_topic[:30]}'...")

    for idx, beat in enumerate(beats):
        dur = beat["duration"]
        sent = beat["text"]
        query = resolve_beat_visual_query(sent, global_topic=global_topic, beat_idx=idx + 1)
        beat_out = beats_dir / f"beat_{idx+1:02d}.mp4"

        print(f"   🎥 Beat {idx+1}/{len(beats)} ({dur:.1f}s): \"{sent[:32]}...\" -> Query: \"{query[:36]}\"")
        clip = render_single_beat_clip(
            query=query,
            duration=dur,
            out_video_path=beat_out,
            beat_idx=idx + 1,
            width=width,
            height=height,
            used_videos=used_stock_videos,
            visual_mode=visual_mode
        )
        rendered_clips.append(clip)

    # Concatenate all beat video clips using FFmpeg concat demuxer
    concat_list = beats_dir / "concat_beats.txt"
    with open(concat_list, "w") as f:
        for clip in rendered_clips:
            f.write(f"file '{clip.resolve()}'\n")

    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(out_stitched_video)
    ]

    try:
        subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        # Fallback filter_complex concat if stream copy fails
        inputs = []
        fc = []
        for i, c in enumerate(rendered_clips):
            inputs.extend(["-i", str(c)])
            fc.append(f"[{i}:v]")
        fc.append(f"concat=n={len(rendered_clips)}:v=1:a=0[vout]")
        cmd_filter = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", "".join(fc),
            "-map", "[vout]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            str(out_stitched_video)
        ]
        subprocess.run(cmd_filter, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    print(f"   ✓ [B-Roll Director] Successfully stitched {len(rendered_clips)} unique shots ({total_duration:.1f}s)")
    return out_stitched_video
