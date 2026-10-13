"""
End-to-End AI Animated Film Pipeline for ShortsCreator AI.
Orchestrates:
1. Multi-scene cinematic screenplay generation (Tamil & English)
2. Neural character/narrator voice synthesis with speech timing
3. Generative video model hub (Google Veo, Fal Wan 2.1, Replicate Hunyuan, Open Stock, Anime AI)
4. 2.5D dynamic camera animation per scene (zooms, pans, sweeps)
5. Multi-scene seamless movie stitching & studio audio mastering
6. Automatic high-CTR cinematic thumbnail generation
"""

import os
import re
import time
from typing import Dict, Any, Optional, Callable
from rich.console import Console

from shorts_creator.film_generator.screenplay import get_screenplay, ANIMATION_STYLES
from shorts_creator.film_generator.art_generator import generate_scene_image
from shorts_creator.film_generator.animator import animate_scene_shot
from shorts_creator.film_generator.movie_compositor import assemble_animated_movie
from shorts_creator.tts_engine import generate_voiceover
from shorts_creator.bgm_manager import prepare_bgm_track
from shorts_creator.cli import get_default_output_dir
from shorts_creator.video_fetcher import get_open_source_video
from shorts_creator.ai_video import AIVideoHub
from shorts_creator.thumbnail import generate_thumbnail

console = Console()


def generate_animated_film(
    prompt: Optional[str] = None,
    lang: str = "en",
    style: str = "anime_shinkai",
    aspect_ratio: str = "16:9",
    num_scenes: int = 4,
    voice: Optional[str] = None,
    bgm_vibe: str = "ambient",
    video_source: str = "auto",
    recipe: Optional[str] = None,
    output_path: Optional[str] = None,
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> Dict[str, Any]:
    """
    Generate a complete multi-scene animated movie from a prompt or concept.
    video_source: 'auto', 'veo', 'wan2.1', 'hunyuan', 'stock', 'anime_ai'.
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    workspace = os.path.join(os.getcwd(), "output", f"film_session_{timestamp}")
    os.makedirs(workspace, exist_ok=True)

    def notify(msg: str, pct: float = 0.0):
        if progress_callback:
            progress_callback(msg, pct)

    notify("Step 1: Writing cinematic screenplay...", 0.1)

    # 1. Screenplay
    screenplay = get_screenplay(prompt, lang=lang, style_key=style, num_scenes=num_scenes)
    movie_title = screenplay.get("title", "Animated Film")
    scenes = screenplay.get("scenes", [])
    if not scenes:
        raise ValueError("Screenplay generation produced no scenes.")

    # 2. Voiceover & Audio Timing for each scene
    scene_audios = []
    scene_durations = []
    scene_timings = []
    current_time = 0.2

    notify("Step 2: Synthesizing character voiceovers...", 0.25)
    for idx, sc in enumerate(scenes):
        scene_dir = os.path.join(workspace, f"scene_{idx+1}")
        os.makedirs(scene_dir, exist_ok=True)
        text = sc.get("narration", "").strip()

        tts = generate_voiceover(
            text=text,
            lang=lang,
            output_dir=scene_dir,
            custom_voice=voice
        )
        audio_path = tts["audio_path"]
        dur = max(2.5, tts["duration"] + 0.4)

        scene_audios.append(audio_path)
        scene_durations.append(dur)
        scene_timings.append({
            "start": current_time,
            "end": current_time + dur - 0.2,
            "text": text
        })
        current_time += dur

    total_duration = current_time

    # 3. Generate Scene Videos
    scene_videos = []
    width, height = (1920, 1080) if aspect_ratio == "16:9" else (1080, 1920)

    for idx, sc in enumerate(scenes):
        pct = 0.35 + (0.45 * (idx / len(scenes)))
        notify(f"Rendering Scene {idx+1}/{len(scenes)}: {sc.get('setting', '')[:30]}...", pct)

        scene_dir = os.path.join(workspace, f"scene_{idx+1}")
        shot_video_path = os.path.join(scene_dir, "shot.mp4")
        dur = scene_durations[idx]
        visual_prompt = sc.get("visual_prompt", sc.get("setting", prompt or ""))

        # Check generative video models (Google Veo, Fal Wan, Replicate Hunyuan)
        gen_backend = video_source.lower().strip()
        if gen_backend in ("veo", "wan", "wan2.1", "wan2.2", "hunyuan"):
            gen_out = os.path.join(scene_dir, f"ai_gen_{idx+1}.mp4")
            AIVideoHub.get_or_synthesize_video(
                prompt_or_query=visual_prompt,
                out_path=gen_out,
                duration=dur,
                is_shorts=(aspect_ratio == "9:16"),
                generator_backend=gen_backend
            )
            if os.path.isfile(gen_out) and os.path.getsize(gen_out) > 50000:
                scene_videos.append(gen_out)
                continue

        # Open-source stock video download
        stock_vid = None
        if gen_backend in ("auto", "stock"):
            search_term = sc.get("setting", "") + " " + visual_prompt
            stock_vid = get_open_source_video(query_or_topic=search_term)

        if stock_vid and os.path.isfile(stock_vid) and os.path.getsize(stock_vid) > 200000:
            crop_filter = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1,eq=contrast=1.05:brightness=-0.02"
            cmd_clip = [
                "ffmpeg", "-y",
                "-stream_loop", "-1",
                "-i", stock_vid,
                "-vf", crop_filter,
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "19",
                "-pix_fmt", "yuv420p",
                "-t", str(dur),
                shot_video_path
            ]
            try:
                import subprocess
                subprocess.run(cmd_clip, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                scene_videos.append(shot_video_path)
                continue
            except Exception:
                pass

        # Fallback to AI Keyframe Art + 2.5D Camera Animator
        art_path = os.path.join(scene_dir, "frame.jpg")
        generate_scene_image(
            prompt=visual_prompt,
            output_path=art_path,
            style_key=style,
            aspect_ratio=aspect_ratio,
            seed=None
        )
        camera = sc.get("camera", "zoom_in")
        animate_scene_shot(
            image_path=art_path,
            duration=dur,
            output_video_path=shot_video_path,
            camera=camera,
            aspect_ratio=aspect_ratio
        )
        scene_videos.append(shot_video_path)

    # 4. Cinematic Background Music
    notify("Mastering continuous cinematic music score...", 0.85)
    bgm_path = None
    if bgm_vibe != "none":
        bgm_path = prepare_bgm_track(workspace, total_duration, vibe=bgm_vibe)

    # 5. Final Compositing & Subtitles
    notify("Finalizing film assembly & color grading...", 0.92)
    if not output_path:
        default_dir = get_default_output_dir()
        clean_slug = re.sub(r'[^\w\u0B80-\u0BFF]+', '_', movie_title[:24]).strip('_') or "animated_film"
        output_path = os.path.join(default_dir, f"{clean_slug}_{timestamp}.mp4")

    final_film = assemble_animated_movie(
        scene_video_paths=scene_videos,
        scene_audio_paths=scene_audios,
        scene_timings=scene_timings,
        output_movie_path=output_path,
        total_duration=total_duration,
        bgm_path=bgm_path,
        aspect_ratio=aspect_ratio
    )

    # 6. Generate High-CTR Thumbnail
    thumb_path = output_path.rsplit(".", 1)[0] + "_thumbnail.png"
    bullets = [sc.get("setting", "Scene")[:30] for sc in scenes[:3]]
    try:
        generate_thumbnail(
            title=movie_title,
            output_path=thumb_path,
            bullets=bullets,
            is_shorts=(aspect_ratio == "9:16"),
            badge="★ CINEMATIC MOVIE"
        )
    except Exception:
        thumb_path = None

    notify("Animated movie creation complete! 🎉", 1.0)

    return {
        "title": movie_title,
        "film_path": final_film,
        "thumbnail_path": thumb_path,
        "duration": total_duration,
        "scenes_count": len(scenes),
        "style": ANIMATION_STYLES.get(style, {}).get("name", style),
        "aspect_ratio": aspect_ratio,
        "lang": lang,
        "screenplay": screenplay
    }
