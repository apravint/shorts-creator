"""
Multi-Beat B-Roll Montage & Visual Synchronization Engine for ShortsCreator AI.
Transforms full-length scripts into dynamically cut, sentence-synchronized B-roll video montages.
Every beat/sentence gets a unique, authentic visual shot (open-source video or 2.5D camera animated AI art)
perfectly matching spoken words and timing. Eliminates repetitive static loops and cards.
"""

import os
import re
import io
import json
import math
import random
import urllib.parse
import urllib.request
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

from PIL import Image

from .text_match import has_term
from .video_fetcher import get_open_source_video, reset_download_budget, NEGATIVE_NOISE_TERMS, TAMIL_TO_ENGLISH_MAP

USER_AGENT = "ShortsCreatorAI/2.0 (https://github.com/apravint/shorts-creator; apravint@gmail.com)"

# Longest a single shot may hold before the montage cuts away
MAX_SHOT_SECONDS = 3.0
# Licenses that allow reuse in a monetized video without on-screen attribution
NO_ATTRIBUTION_LICENSES = ("public domain", "cc0", "pd")


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
        # TTS tokenization differs slightly from str.split(), so locate each sentence by its share of the words
        word_counts = [max(1, len(s.split())) for s in clean_sentences]
        total_words = sum(word_counts)
        total_bounds = len(boundaries)
        starts = []
        words_before = 0
        for wc in word_counts:
            b_idx = min(total_bounds - 1, round(words_before / total_words * total_bounds))
            starts.append(boundaries[b_idx]["start"])
            words_before += wc
        starts[0] = 0.0

        beats = []
        for s_idx, sent in enumerate(clean_sentences):
            start_t = starts[s_idx]
            end_t = starts[s_idx + 1] if s_idx + 1 < len(starts) else total_duration
            beats.append({
                "index": s_idx + 1,
                "text": sent,
                "start": round(start_t, 3),
                "end": round(end_t, 3),
                "duration": round(end_t - start_t, 3)
            })
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
    is_motivational = has_term(combined, [
        "தோல்வி", "வெற்றி", "விடாமுயற்சி", "உழைப்பு", "கனவு", "நம்பிக்கை",
        "எழுச்சி", "சிகரம்", "ஓடு", "தடை", "அடி", "கைவிடாதே", "வீரம்", "நெருப்பு",
        "discipline", "motivation", "unstoppable", "mindset", "success", "action",
        "fear", "courage", "overcome", "victory", "runner", "athlete", "summit", "perseverance"
    ])

    if is_motivational:
        if any(k in text_lower for k in ["தோல்வி", "பயப்படாதீங்க", "பயப்படாதீர்கள்", "பயம்", "விழு", "உடைக்க", "இருட்டு", "இருள்", "தடை", "fail", "broken", "fall", "obstacle", "storm", "struggle"]):
            shots = [
                "lone determined figure walking through dark foggy rain, dramatic volumetric lighting, cinematic 8k vertical",
                "intense warrior silhouette standing against dark stormy sky lightning, epic cinematic vertical",
                "boxer exhausted in shadows catching breath dramatic rim lighting, vertical composition",
                "dramatic storm ocean waves crashing on dark rocks silhouette, 8k vertical"
            ]
            return shots[(beat_idx) % len(shots)]

        elif any(k in text_lower for k in ["விதை", "விருட்சம்", "மரம்", "முளைத்து", "மண்", "விஸ்வரூப", "seed", "sprout", "grow", "tree", "plant", "roots"]):
            shots = [
                "glowing green seedling sprouting from dark rich soil into giant tree, golden sunbeams, cinematic vertical 8k",
                "giant majestic ancient oak tree sunbeams breaking through forest canopy, fantasy nature photography, vertical",
                "lush emerald green mountain forest landscape golden hour sunlight, 8k vertical"
            ]
            return shots[(beat_idx) % len(shots)]

        elif any(k in text_lower for k in ["கனவு", "கனவுகள்", "நம்பிக்கை", "பாதை", "வானம்", "horizon", "dream", "vision", "path", "hope"]):
            shots = [
                "majestic eagle soaring high above golden sunrise clouds and mountain peaks, aerial cinematic 8k vertical",
                "lone hiker standing on mountain cliff looking into vast infinite golden horizon, cinematic 8k vertical",
                "rock climber looking up at soaring granite peak in morning light, epic vertical"
            ]
            return shots[(beat_idx) % len(shots)]

        elif any(k in text_lower for k in ["அடி", "முன்னாடி", "முன்னேறி", "தொடங்கு", "துவங்கு", "உழைப்பு", "போராடு", "step", "start", "action", "work", "train"]):
            shots = [
                "running shoes sprinting fast across morning track, golden hour dust kicking up, dynamic dynamic vertical 8k",
                "athlete focused runner starting blocks sunrise stadium, intense determination, cinematic vertical",
                "intense workout warrior training in moody gym dramatic lighting, sweat glistening, vertical"
            ]
            return shots[(beat_idx) % len(shots)]

        elif any(k in text_lower for k in ["வெற்றி", "சிகரம்", "எழுந்து", "தலைவணங்கும்", "win", "victory", "champion", "summit", "peak"]):
            shots = [
                "triumphant climber standing on snowy mountain summit sunrise raising hands in victory, golden sunlight, cinematic 8k vertical",
                "champion athlete crossing finish line golden hour stadium, roaring crowd, heroic vertical",
                "breathtaking majestic mountain peak summit touched by golden first light, volumetric rays, 8k vertical"
            ]
            return shots[(beat_idx) % len(shots)]
        else:
            shots = [
                "heroic silhouette rising toward brilliant morning dawn, cinematic vertical",
                "athlete running along ocean beach sunrise waves, dynamic action vertical",
                "boxer throwing powerful punch training in gym with dramatic rim light, vertical",
                "burning golden torch flame in dark cinematic atmosphere, 8k vertical",
                "modern focused athlete walking confidently through bustling city street morning sun, vertical",
                "intense warrior silhouette standing on mountain summit against dramatic sky, 8k vertical"
            ]
            return shots[(beat_idx) % len(shots)]

    # 2. Deep Space / Astronomy
    is_space = has_term(combined, [
        "space", "galaxy", "universe", "planet", "stars", "black hole", "cosmic", "mars",
        "விண்வெளி", "கிரகம்", "சூரியன்", "நிலா", "அண்டம்", "கருந்துளை"
    ])
    if is_space:
        space_shots = [
            "deep space galaxy nebula spiral stars cinematic 8k vertical",
            "supermassive black hole glowing accretion disk gravitational lensing vertical",
            "futuristic spaceship exploring alien planet orbit cosmic vertical",
            "mars rover surface red dust landscape sunset vertical",
            "astronaut floating in deep space earth background sun flare vertical"
        ]
        return space_shots[(beat_idx) % len(space_shots)]

    # 3. Technology / AI / Coding / Cyber
    is_tech = has_term(combined, [
        "tech", "technology", "drone", "computer", "coding", "software", "ai", "cyber", "robot",
        "தொழில்நுட்பம்", "கணினி", "ரோபோ", "செயற்கை நுண்ணறிவு"
    ])
    if is_tech:
        tech_shots = [
            "futuristic neural network AI brain glowing data connections vertical",
            "hands typing mechanical keyboard syntax code dark neon desk vertical",
            "datacenter server racks glowing blue fiber optic cables vertical",
            "futuristic cyberpunk city skyline flying cars neon rain vertical",
            "microchip processor circuit board glowing gold data pulses vertical"
        ]
        return tech_shots[(beat_idx) % len(tech_shots)]

    # 4. Nature / Ocean / Ancient
    if has_term(combined, ["கடல்", "ocean", "sea", "water", "waves"]):
        return "majestic turquoise ocean giant waves crashing dramatic aerial 4k vertical"
    if has_term(combined, ["மலை", "mountain", "peak", "climb"]):
        return "epic misty mountain range sunrise clouds cinematic 4k vertical"
    if has_term(combined, ["வரலாறு", "கோயில்", "சோழர்", "history", "ancient", "temple"]):
        return "ancient magnificent stone temple royal architecture golden hour vertical"

    # 5. Night / Sleep / Bedtime / Peace / Cozy
    is_night = has_term(combined, [
        "night", "sleep", "sleeping", "dream", "dreams", "bed", "rest", "calm", "moon", "moonlight",
        "starry", "stars", "good night", "peaceful", "quiet", "breathe", "இரவு", "தூக்கம்", "நிலவு"
    ])
    if is_night:
        night_shots = [
            "serene starry night sky milky way glowing over quiet mountain lake, peaceful vertical 8k",
            "cozy aesthetic warm bedroom window soft ambient lamp gentle rain outside, warm glow vertical",
            "gentle luminous full moon glowing through soft clouds silver reflection, serene 8k vertical",
            "warm glowing fireplace embers cozy cabin quiet relaxing night, peaceful vertical",
            "misty quiet pine forest illuminated by soft silver moonlight, ethereal serene vertical 8k",
            "calm dark ocean waves gently lapping beach under starlight, peaceful night vertical"
        ]
        return night_shots[(beat_idx) % len(night_shots)]

    # Default fallback
    clean = re.sub(r'[^\w\s]', ' ', text_lower)
    words = [w for w in clean.split() if len(w) > 3][:3]
    return f"{' '.join(words)} cinematic masterpiece 4k vertical" if words else "cinematic documentary landscape 4k vertical"


def search_wikimedia_highres_image(query: str, used_urls: Optional[set] = None) -> Optional[str]:
    """Search Wikimedia Commons for high-res photography that needs no attribution (public domain / CC0)."""
    # Strip modifier keywords to form clean natural search query
    clean_words = [
        w for w in re.sub(r'[^\w\s]', ' ', query).split()
        if len(w) > 2 and w.lower() not in [
            "vertical", "cinematic", "photorealistic", "volumetric", "lighting",
            "masterpiece", "still", "video", "composition", "8k", "4k", "detailed"
        ]
    ]
    search_term = " ".join(clean_words[:4]) or "mountain sunrise landscape"
    clean_q = urllib.parse.quote(search_term)
    api_url = (
        f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&"
        f"gsrsearch={clean_q}&gsrnamespace=6&prop=imageinfo&iiprop=url|mime|size|width|height|extmetadata&gsrlimit=20"
    )
    headers = {"User-Agent": USER_AGENT}
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for _, page in pages.items():
                if any(noise in page.get("title", "").lower() for noise in NEGATIVE_NOISE_TERMS):
                    continue
                for ii in page.get("imageinfo", []):
                    license_name = ii.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "").lower()
                    if not license_name.startswith(NO_ATTRIBUTION_LICENSES):
                        continue
                    mime = ii.get("mime", "")
                    if mime.startswith("image/jpeg") or mime.startswith("image/png"):
                        if ii.get("width", 0) >= 800:
                            u = ii.get("url", "")
                            if u and (used_urls is None or u not in used_urls):
                                if used_urls is not None:
                                    used_urls.add(u)
                                return u
    except Exception:
        pass
    return None


def _save_valid_image(url: str, out_image_path: Path, timeout: int) -> bool:
    """Download url and keep it only if it decodes as a real image."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
        if len(content) <= 15000:
            return False
        Image.open(io.BytesIO(content)).verify()
        with open(out_image_path, "wb") as f:
            f.write(content)
        return True
    except Exception:
        return False


def download_ai_keyframe_image(prompt: str, out_image_path: Path, width: int = 1080, height: int = 1920, used_urls: Optional[set] = None) -> bool:
    """
    Downloads a visual keyframe that matches the beat:
    1. Pollinations AI generation, which follows the prompt most closely.
    2. Wikimedia Commons photography that needs no attribution.
    Returns False rather than substituting an unrelated random photo.
    """
    out_image_path = Path(out_image_path)
    out_image_path.parent.mkdir(parents=True, exist_ok=True)
    seed = random.randint(1000, 999999)

    safe_words = [w for w in prompt.split() if w.lower() not in ["sprouting", "seedling", "soil", "glowing", "rich", "darkness"]]
    clean_prompt = " ".join(safe_words[:12]) or "mountain sunrise dawn"
    clean_p = urllib.parse.quote(f"cinematic photorealistic 8k, {clean_prompt}, natural lighting, masterpiece")
    poll_url = f"https://image.pollinations.ai/prompt/{clean_p}?width={width}&height={height}&seed={seed}&nologo=true"
    if _save_valid_image(poll_url, out_image_path, timeout=45):
        return True

    wiki_url = search_wikimedia_highres_image(prompt, used_urls=used_urls)
    return bool(wiki_url and _save_valid_image(wiki_url, out_image_path, timeout=15))


def probe_duration(path: str) -> float:
    """Clip length in seconds, or 0.0 if it cannot be read."""
    try:
        res = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True
        )
        return float(res.stdout.strip())
    except Exception:
        return 0.0


def split_beats_into_shots(beats: List[Dict[str, Any]], max_shot: float = MAX_SHOT_SECONDS) -> List[Dict[str, Any]]:
    """Divide each sentence beat into equal shots of at most max_shot seconds, marking the first of each beat."""
    shots = []
    for beat in beats:
        count = max(1, math.ceil(beat["duration"] / max_shot))
        for i in range(count):
            shots.append({
                "text": beat["text"],
                "beat_index": beat.get("index", 1) - 1,
                "duration": round(beat["duration"] / count, 3),
                "starts_beat": i == 0
            })
    return shots


def render_single_beat_clip(
    query: str,
    duration: float,
    out_video_path: Path,
    beat_idx: int = 1,
    width: int = 1080,
    height: int = 1920,
    fps: int = 30,
    used_videos: Optional[set] = None,
    used_images: Optional[set] = None,
    visual_mode: str = "auto"
) -> Path:
    """
    Renders an individual beat clip tailored to its exact duration:
    1. If visual_mode is 'stock', attempts to find a matching open-source video clip.
    2. Default: Generates a 100% brand-new, customized AI visual keyframe and animates it with Ken Burns 2.5D camera movement!
    """
    out_video_path = Path(out_video_path)
    out_video_path.parent.mkdir(parents=True, exist_ok=True)
    d_frames = max(30, int(duration * fps))

    # 1. Try real open-source stock video for 'stock' and 'auto' modes
    if visual_mode in ("stock", "auto"):
        stock_candidate = get_open_source_video(query_or_topic=query, exclude_paths=used_videos)
        if (
            stock_candidate
            and os.path.isfile(stock_candidate)
            and os.path.getsize(stock_candidate) > 200000
        ):
            if used_videos is not None:
                used_videos.add(stock_candidate)

            # Random in-point so a clip that must repeat still shows different footage
            clip_len = probe_duration(stock_candidate)
            ss_offset = round(random.uniform(0, max(0.0, clip_len - duration - 0.5)), 2)
            # Oversize slightly, then drift the crop so no shot sits perfectly still
            over_w, over_h = int(width * 1.12) // 2 * 2, int(height * 1.12) // 2 * 2
            direction = 1 if beat_idx % 2 else -1
            crop_filter = (
                f"scale={over_w}:{over_h}:force_original_aspect_ratio=increase,"
                f"crop={width}:{height}:x='(iw-ow)/2+{direction}*50*(t/{duration:.3f}-0.5)':y='(ih-oh)/2',setsar=1,fps={fps},"
                f"eq=contrast=1.03:brightness=-0.01"
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
    img_success = download_ai_keyframe_image(query, img_path, width=width, height=height, used_urls=used_images)

    if img_success and img_path.exists():
        # Alternate 4-way cinematic camera choreography
        camera_type = beat_idx % 4
        if camera_type == 0:
            # Steady slow push-in (Hero focus)
            zp = f"zoompan=z='min(1.0+0.08*(on/{d_frames}),1.08)':d={d_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
        elif camera_type == 1:
            # Gentle pull-back (Revealing scale)
            zp = f"zoompan=z='max(1.08-0.08*(on/{d_frames}),1.0)':d={d_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
        elif camera_type == 2:
            # Upward hero rise (Aspirational climb)
            zp = f"zoompan=z=1.08:d={d_frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-on/{d_frames})':s={width}x{height}:fps={fps}"
        else:
            # Subtle horizontal drift (Documentary pan)
            zp = f"zoompan=z=1.08:d={d_frames}:x='(iw-iw/zoom)*(on/{d_frames})':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"

        cmd_anim = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_path),
            "-vf", (
                # Fill 9:16 without squashing, oversampled so zoompan does not jitter
                f"scale={width * 2}:{height * 2}:force_original_aspect_ratio=increase,"
                f"crop={width * 2}:{height * 2},setsar=1,"
                f"{zp},eq=contrast=1.04:saturation=1.03,format=yuv420p"
            ),
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
    visual_mode: str = "auto",
    visual_queries: Optional[List[str]] = None
) -> Any:
    """
    Master B-Roll Orchestrator:
    1. Splits script into rhythmic visual beats synced to speech timestamps, then into shots of at most MAX_SHOT_SECONDS.
    2. Renders a separate video clip for every shot, using visual_queries[beat] when the script supplies them.
    3. Stitches all clips with FFmpeg xfade micro-transitions and unified color grading.
    4. Returns (out_stitched_video, cut_timestamps), where cut_timestamps are the sentence changes that get a whoosh.
    """
    workspace_dir = Path(workspace_dir)
    workspace_dir.mkdir(parents=True, exist_ok=True)
    beats_dir = workspace_dir / "beat_clips"
    beats_dir.mkdir(parents=True, exist_ok=True)

    reset_download_budget()
    beats = calculate_sentence_timings(sentences, total_duration, boundaries=boundaries)
    rendered_clips: List[Path] = []
    used_stock_videos: set = set()
    used_image_urls: set = set()

    # Pre-calculate cut timestamps and transition overlap
    trans_dur = 0.15
    shots = split_beats_into_shots(beats)
    shot_cuts: List[float] = []
    cut_timestamps: List[float] = []
    accum = 0.0
    for idx, shot in enumerate(shots[:-1]):
        accum += shot["duration"]
        shot_cuts.append(round(accum, 3))
        if shots[idx + 1]["starts_beat"]:
            cut_timestamps.append(round(accum, 3))

    num_shots = len(shots)
    print(f"🎬 [B-Roll Director] Assembling dynamic {num_shots}-shot visual montage for '{global_topic[:30]}'...")

    for idx, shot in enumerate(shots):
        base_dur = shot["duration"]
        # Extend duration by transition duration for all clips except the last for smooth xfade
        render_dur = base_dur + trans_dur if idx < num_shots - 1 else base_dur
        sent = shot["text"]
        beat_index = shot["beat_index"]
        supplied = visual_queries[beat_index] if visual_queries and beat_index < len(visual_queries) else None
        query = supplied or resolve_beat_visual_query(sent, global_topic=global_topic, beat_idx=idx + 1)
        beat_out = beats_dir / f"beat_{idx+1:02d}.mp4"

        print(f"   🎥 Shot {idx+1}/{num_shots} ({render_dur:.1f}s): \"{sent[:32]}...\" -> Query: \"{query[:36]}\"")
        clip = render_single_beat_clip(
            query=query,
            duration=render_dur,
            out_video_path=beat_out,
            beat_idx=idx + 1,
            width=width,
            height=height,
            used_videos=used_stock_videos,
            used_images=used_image_urls,
            visual_mode=visual_mode
        )
        rendered_clips.append(clip)

    # 1. Attempt smooth xfade transition stitching with cinematic color grading
    xfade_done = False
    if len(rendered_clips) >= 2 and all(shot["duration"] > trans_dur for shot in shots):
        try:
            inputs = []
            for c in rendered_clips:
                inputs.extend(["-i", str(c)])

            fc = []
            prev_stream = "[0:v]"
            for i in range(len(rendered_clips) - 1):
                next_in = f"[{i+1}:v]"
                out_stream = f"[vx_{i+1}]" if i < len(rendered_clips) - 2 else "[vx_last]"
                offset = shot_cuts[i]
                # A vertical move marks a new sentence; cuts inside a sentence stay quick and invisible
                transition = "smoothup" if shots[i + 1]["starts_beat"] else "fadefast"
                fc.append(f"{prev_stream}{next_in}xfade=transition={transition}:duration={trans_dur}:offset={offset}{out_stream}")
                prev_stream = out_stream

            # Unified subtle cinematic optical grading (contrast 1.04, saturation 1.05)
            fc.append("[vx_last]eq=contrast=1.04:saturation=1.05[vout]")

            cmd_xfade = [
                "ffmpeg", "-y",
                *inputs,
                "-filter_complex", ";".join(fc),
                "-map", "[vout]",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-t", f"{total_duration:.3f}",
                str(out_stitched_video)
            ]
            subprocess.run(cmd_xfade, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            if out_stitched_video.exists() and out_stitched_video.stat().st_size > 10000:
                xfade_done = True
                print(f"   ✨ Applied smooth xfade micro-transitions across {len(shot_cuts)} cuts")
        except Exception as e:
            xfade_done = False

    # 2. Resilient fallback to concat if xfade is unsuitable
    if not xfade_done:
        concat_list = beats_dir / "concat_beats.txt"
        with open(concat_list, "w") as f:
            for clip in rendered_clips:
                f.write(f"file '{clip.resolve()}'\n")

        cmd_concat = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list),
            "-vf", "eq=contrast=1.04:saturation=1.05",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-t", f"{total_duration:.3f}",
            str(out_stitched_video)
        ]
        try:
            subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except Exception:
            # Fallback filter_complex concat
            inputs = []
            fc = []
            for i, c in enumerate(rendered_clips):
                inputs.extend(["-i", str(c)])
                fc.append(f"[{i}:v]")
            fc.append(f"concat=n={len(rendered_clips)}:v=1:a=0,eq=contrast=1.04:saturation=1.05[vout]")
            cmd_filter = [
                "ffmpeg", "-y",
                *inputs,
                "-filter_complex", "".join(fc),
                "-map", "[vout]",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-t", f"{total_duration:.3f}",
                str(out_stitched_video)
            ]
            subprocess.run(cmd_filter, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    print(f"   ✓ [B-Roll Director] Successfully stitched {len(rendered_clips)} unique shots ({total_duration:.1f}s)")
    return out_stitched_video, cut_timestamps
