"""
CLI Interface for YouTube Shorts Creator & AI Film Engine.
Features rich terminal UI, interactive wizard mode, codebase 'brag' showcase,
generative video models, Shotcraft recipes, digital talking avatar PiP, and Studio-grade mastering.
"""

import os
import sys
import re
import argparse
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

from shorts_creator.script_gen import prepare_script, detect_language
from shorts_creator.tts_engine import generate_voiceover, VOICE_MAP
from shorts_creator.subtitle_gen import generate_ass_subtitles
from shorts_creator.bgm_manager import prepare_bgm_track
from shorts_creator.video_engine import assemble_shorts_video
from shorts_creator.thumbnail import generate_thumbnail
from shorts_creator.brag import BragHarvester

console = Console()


def print_banner():
    banner = """[bold cyan]⚡ SHORTS CREATOR AI 2.0 ⚡[/bold cyan]
[dim]Autonomous Video Engine • Multi-Model Generative AI • தமிழ் (Tamil) & English[/dim]"""
    console.print(Panel(banner, border_style="cyan", expand=False))


def get_default_output_dir() -> str:
    """Find the best destination directory, prioritizing Android's shared Download folder."""
    candidates = [
        "/storage/emulated/0/Download/Shorts",
        "/sdcard/Download/Shorts",
        os.path.expanduser("~/storage/downloads/Shorts"),
        os.path.join(os.getcwd(), "output")
    ]
    for d in candidates:
        try:
            os.makedirs(d, exist_ok=True)
            test_file = os.path.join(d, ".write_test")
            with open(test_file, "w") as f:
                f.write("1")
            os.remove(test_file)
            return d
        except Exception:
            continue
    return os.path.join(os.getcwd(), "output")


def list_voices():
    print_banner()
    table = Table(title="🎙️ Verified Working Neural Voices (Tamil, English & Regional)", border_style="cyan")
    table.add_column("Language", style="bold green")
    table.add_column("Gender", style="yellow")
    table.add_column("Alias (-v)", style="bold magenta")
    table.add_column("Voice ID (Edge-TTS)", style="cyan")
    table.add_column("Accent & Tone Description", style="white")

    # Tamil Voices
    table.add_row("Tamil (தமிழ்)", "Female", "pallavi", "ta-IN-PallaviNeural", "India (Natural & Expressive ⭐)")
    table.add_row("Tamil (தமிழ்)", "Female", "venba", "ta-SG-VenbaNeural", "Singapore (Articulate & Modern)")
    table.add_row("Tamil (தமிழ்)", "Female", "saranya", "ta-LK-SaranyaNeural", "Sri Lanka (Gentle & Storytelling)")
    table.add_row("Tamil (தமிழ்)", "Female", "kani", "ta-MY-KaniNeural", "Malaysia (Vibrant & Energetic)")
    table.add_row("Tamil (தமிழ்)", "Male", "valluvar", "ta-IN-ValluvarNeural", "India (Authoritative & Deep)")
    table.add_row("Tamil (தமிழ்)", "Male", "anbu", "ta-SG-AnbuNeural", "Singapore (Crisp & Fast)")
    table.add_row("Tamil (தமிழ்)", "Male", "surya", "ta-MY-SuryaNeural", "Malaysia (Clear Narrative)")
    table.add_row("Tamil (தமிழ்)", "Male", "kumar", "ta-LK-KumarNeural", "Sri Lanka (Calm Cadence)")

    # English Female Voices
    table.add_row("English", "Female", "ava", "en-US-AvaMultilingualNeural", "US Copilot (Warm, Expressive ⭐)")
    table.add_row("English", "Female", "emma", "en-US-EmmaMultilingualNeural", "US Copilot (Cheerful & Clear)")
    table.add_row("English", "Female", "jenny", "en-US-JennyNeural", "US (Friendly Creator Standard ⭐)")
    table.add_row("English", "Female", "aria", "en-US-AriaNeural", "US (Confident, News & Audiobooks)")
    table.add_row("English", "Female", "ana", "en-US-AnaNeural", "US (Cute & Animated Storyteller)")
    table.add_row("English", "Female", "neerja", "en-IN-NeerjaExpressiveNeural", "India (Clear Indian English)")
    table.add_row("English", "Female", "sonia", "en-GB-SoniaNeural", "UK (British Documentary)")
    table.add_row("English", "Female", "natasha", "en-AU-NatashaNeural", "Australia (Friendly Accent)")

    # English Male Voices
    table.add_row("English", "Male", "andrew", "en-US-AndrewMultilingualNeural", "US Copilot (Warm & Authentic ⭐)")
    table.add_row("English", "Male", "brian", "en-US-BrianMultilingualNeural", "US Copilot (Approachable, Casual)")
    table.add_row("English", "Male", "christopher", "en-US-ChristopherNeural", "US (Deep Viral Hook Authority)")
    table.add_row("English", "Male", "guy", "en-US-GuyNeural", "US (Passionate & Dynamic)")
    table.add_row("English", "Male", "prabhat", "en-IN-PrabhatNeural", "India (Clear Indian English)")
    table.add_row("English", "Male", "ryan", "en-GB-RyanNeural", "UK (Modern British Accent)")

    # Regional Indian Voices
    table.add_row("Hindi (हिंदी)", "Female", "swara", "hi-IN-SwaraNeural", "India (Warm Hindi)")
    table.add_row("Hindi (हिंदी)", "Male", "madhur", "hi-IN-MadhurNeural", "India (Clear Hindi)")
    table.add_row("Telugu (తెలుగు)", "Female", "shruti", "te-IN-ShrutiNeural", "India (Clear Telugu)")
    table.add_row("Malayalam (മലയാളം)", "Female", "sobhana", "ml-IN-SobhanaNeural", "India (Clear Malayalam)")
    table.add_row("Kannada (ಕನ್ನಡ)", "Female", "sapna", "kn-IN-SapnaNeural", "India (Clear Kannada)")

    console.print(table)


def run_pipeline(
    topic: str = None,
    custom_script: str = None,
    script_file: str = None,
    lang: str = "en",
    voice: str = None,
    style: str = "hormozi",
    bg_video: str = None,
    bg_type: str = "cosmic",
    bgm_path: str = None,
    no_bgm: bool = False,
    bgm_vibe: str = "ambient",
    progress_bar: bool = True,
    recipe: str = None,
    avatar: str = None,
    cinema: bool = False,
    ambient: str = None,
    sfx: str = None,
    thumb: bool = True,
    generator: str = "auto",
    rate: str = None,
    output_path: str = None,
    harness: bool = False
):
    print_banner()

    # Create temporary session workspace
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    workspace_dir = os.path.join(os.getcwd(), "output", f"session_{timestamp}")
    os.makedirs(workspace_dir, exist_ok=True)

    # Determine default output directory
    if not output_path:
        default_dir = get_default_output_dir()
        slug = re.sub(r'[^\w\u0B80-\u0BFF]+', '_', (topic or custom_script or "short")[:25]).strip('_')
        if not slug:
            slug = "viral_short"
        output_path = os.path.join(default_dir, f"{slug}_{timestamp}.mp4")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        # Step 1: Script Preparation
        task_script = progress.add_task("[cyan]✍️ Generating viral script & hook...", total=1)
        script_data = prepare_script(
            topic=topic,
            custom_script=custom_script,
            script_file=script_file,
            lang=lang
        )
        detected_lang = script_data["language"]
        progress.update(task_script, completed=1)

        # Step 2: High-Quality Voiceover Synthesis
        eff_rate = rate or ("+8%" if detected_lang == "ta" else "+0%")
        task_tts = progress.add_task(f"[green]🎙️ Synthesizing {detected_lang.upper()} voiceover ({eff_rate})...", total=1)
        tts_data = generate_voiceover(
            text=script_data["full_text"],
            lang=detected_lang,
            output_dir=workspace_dir,
            custom_voice=voice,
            rate=eff_rate
        )
        duration = tts_data["duration"]
        progress.update(task_tts, completed=1)

        # Step 3: Subtitle Generation
        task_sub = progress.add_task("[yellow]📝 Generating word-by-word animated captions...", total=1)
        ass_path = os.path.join(workspace_dir, "subtitles.ass")
        generate_ass_subtitles(
            sentences=script_data["sentences"],
            total_duration=duration,
            output_ass_path=ass_path,
            lang=detected_lang,
            style=style,
            boundaries=tts_data.get("boundaries", [])
        )
        progress.update(task_sub, completed=1)

        # Step 4: High-Quality BGM Synthesizer
        final_bgm = None
        if not no_bgm:
            task_bgm = progress.add_task(f"[magenta]🎵 Mastering BGM score ({bgm_vibe})...", total=1)
            final_bgm = prepare_bgm_track(workspace_dir, duration, custom_bgm=bgm_path, vibe=bgm_vibe)
            progress.update(task_bgm, completed=1)

        # Step 5: FFmpeg Video Compositing & Studio Audio Mastering
        task_video = progress.add_task(f"[bold red]🎬 Rendering Video ({duration:.1f}s)...", total=1)
        final_video = assemble_shorts_video(
            voiceover_path=tts_data["audio_path"],
            subtitle_ass_path=ass_path,
            duration=duration,
            output_path=output_path,
            topic=script_data.get("title") or topic,
            sentences=script_data.get("sentences", []),
            boundaries=tts_data.get("boundaries", []),
            bg_video_path=bg_video,
            bg_type=bg_type,
            bgm_path=final_bgm,
            progress_bar=progress_bar,
            recipe=recipe,
            avatar_img=avatar,
            is_cinema=cinema,
            ambient_vibe=ambient,
            sfx_cue=sfx,
            visual_mode=generator
        )
        progress.update(task_video, completed=1)

    # Step 6: Generate High-CTR Thumbnail
    thumb_path = None
    if thumb:
        thumb_path = output_path.rsplit(".", 1)[0] + "_thumbnail.png"
        try:
            generate_thumbnail(
                title=script_data["title"],
                output_path=thumb_path,
                bullets=script_data.get("tags", [])[:3] or ["Key Takeaway", "Pro Tip"],
                is_shorts=(not cinema),
                theme=bg_type
            )
        except Exception:
            thumb_path = None

    # Success Summary Card
    console.print()
    summary_text = f"""[bold green]✅ Video Created Successfully![/bold green]

[bold]Video File:[/bold] [underline cyan]{final_video}[/underline cyan]
[bold]Thumbnail:[/bold] [underline yellow]{thumb_path or 'N/A'}[/underline yellow]
[bold]Title:[/bold] {script_data['title']}
[bold]Language:[/bold] {'தமிழ் (Tamil)' if detected_lang == 'ta' else 'English'}
[bold]Duration:[/bold] {duration:.1f} seconds
[bold]Voice Engine:[/bold] {tts_data['voice']}
[bold]Audio Mastering:[/bold] [bold magenta]EBU R128 (-16 LUFS) with Sidechain Ducking[/bold magenta]
[bold]Shotcraft Recipe:[/bold] {recipe or 'Standard Flow'}
[bold]📱 Android Downloads / Gallery:[/bold] [bold yellow]{final_video}[/bold yellow]
[bold]Hashtags:[/bold] [dim]{' '.join(script_data['tags'])}[/dim]
"""
    console.print(Panel(summary_text, border_style="green", expand=False))

    # Optional Post-Render Harness² Cyclic Verification & Healing
    if harness:
        from shorts_creator.harness_verifier import VideoHarnessVerifier
        console.print("[bold cyan]🧠 [HARNESS²] Dispatching post-render cyclic verification loop (Plan -> Act -> Verify -> Reflect)...[/bold cyan]")
        verifier = VideoHarnessVerifier(output_dir=Path(final_video).parent / ".harness")
        verifier.plan_stage(title=script_data["title"], expected_scenes=1, target_aspect="16:9" if cinema else "9:16")
        report = verifier.verify_stage(Path(final_video))
        healed = verifier.reflect_and_heal(Path(final_video), report)
        if healed != Path(final_video) and healed.exists():
            final_video = str(healed)
            console.print(f"[bold green]🏆 [HARNESS²] Certified release candidate: {final_video}[/bold green]")

    return final_video


def interactive_wizard():
    print_banner()
    console.print("[bold yellow]🚀 Welcome to the ShortsCreator AI Wizard![/bold yellow]\n")

    # 1. Mode Selection
    mode = Prompt.ask(
        "Choose Mode",
        choices=["create_short", "brag_repo", "ai_film"],
        default="create_short"
    )

    if mode == "brag_repo":
        repo_dir = Prompt.ask("Enter Path to Codebase / Repository", default=os.getcwd())
        lang = Prompt.ask("Language", choices=["en", "ta"], default="en")
        recipe = Prompt.ask("Shotcraft Recipe", choices=["terminal_glitch_scan", "isometric_exploded", "speed_ramp"], default="terminal_glitch_scan")
        info = BragHarvester.inspect_repository(Path(repo_dir))
        brag_script = BragHarvester.craft_launch_script(info, lang=lang)
        run_pipeline(
            custom_script=brag_script["script"],
            topic=brag_script["title"],
            lang=lang,
            bg_type="tech",
            bgm_vibe="cyber",
            recipe=recipe,
            ambient="keyboard"
        )
        return

    # 2. Language
    lang_choice = Prompt.ask(
        "Select Language",
        choices=["en", "ta"],
        default="en"
    )

    # 3. Topic / Script Mode
    script_mode = Prompt.ask(
        "Script Source",
        choices=["ai_topic", "custom_text"],
        default="ai_topic"
    )

    topic = None
    custom_script = None
    if script_mode == "ai_topic":
        if lang_choice == "ta":
            topic = Prompt.ask("Enter Topic (e.g. விண்வெளி மர்மங்கள், தமிழ் வரலாறு)", default="விண்வெளியின் மர்மங்கள்")
        else:
            topic = Prompt.ask("Enter Topic (e.g. 3 Mind-blowing space facts, Dark psychology)", default="3 Terrifying Space Facts")
    else:
        custom_script = Prompt.ask("Enter custom script text")

    # 4. Voice
    if lang_choice == "ta":
        voice = Prompt.ask(
            "Select Voice",
            choices=["ta-IN-PallaviNeural (Female)", "ta-IN-ValluvarNeural (Male)"],
            default="ta-IN-PallaviNeural (Female)"
        ).split()[0]
    else:
        voice = Prompt.ask(
            "Select Voice",
            choices=["en-US-ChristopherNeural (US Male)", "en-IN-PrabhatNeural (Indian Male)"],
            default="en-US-ChristopherNeural (US Male)"
        ).split()[0]

    # 5. Caption Style
    style = Prompt.ask(
        "Subtitle Color Style",
        choices=["hormozi", "neon-cyan", "neon-green", "fire-red", "gold", "purple-neon", "white-classic"],
        default="hormozi"
    )

    # 6. Background Video Theme
    bg_type = Prompt.ask(
        "Background Video Theme",
        choices=["space", "tech", "cosmic", "cyber", "fire", "emerald", "ancient", "ocean"],
        default="space"
    )

    # 7. Shotcraft Recipe
    recipe = Prompt.ask(
        "Shotcraft Recipe",
        choices=["none", "hero_reveal", "speed_ramp", "macro_orbit", "terminal_glitch_scan", "dutch_angle_tension"],
        default="none"
    )
    if recipe == "none":
        recipe = None

    run_pipeline(
        topic=topic,
        custom_script=custom_script,
        lang=lang_choice,
        voice=voice,
        style=style,
        bg_type=bg_type,
        bgm_vibe="ambient",
        recipe=recipe
    )


def main():
    parser = argparse.ArgumentParser(
        description="ShortsCreator AI - Universal AI Video & Film Engine (English & தமிழ்)"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Command: create
    create_p = subparsers.add_parser("create", help="Create a YouTube Short video")
    create_p.add_argument("-t", "--topic", help="Topic for AI script generation")
    create_p.add_argument("-l", "--lang", choices=["en", "ta"], default=None, help="Language (en=English, ta=Tamil)")
    create_p.add_argument("-v", "--voice", help="Edge-TTS voice identifier")
    create_p.add_argument("-s", "--script", help="Custom script text directly")
    create_p.add_argument("--script-file", help="Path to text file containing script")
    create_p.add_argument("--style", choices=["hormozi", "neon-cyan", "neon-green", "fire-red", "gold", "purple-neon", "white-classic"], default="hormozi", help="Subtitle highlight style")
    create_p.add_argument("--recipe", choices=["hero_reveal", "macro_orbit", "speed_ramp", "isometric_exploded", "dutch_angle_tension", "terminal_glitch_scan", "split_comparison", "broll_whip_pan"], default=None, help="Shotcraft cinematic recipe card")
    create_p.add_argument("--avatar", help="Path to portrait image for digital human talking presenter PiP")
    create_p.add_argument("--cinema", action="store_true", help="Compile as 2.39:1 Hollywood Scope letterbox")
    create_p.add_argument("--ambient", choices=["rain", "keyboard", "server", "wind", "room_tone"], default=None, help="Procedural ambient acoustic texture")
    create_p.add_argument("--sfx", choices=["impact", "whoosh", "telemetry", "riser"], default=None, help="Procedural Hollywood Foley sound cue")
    create_p.add_argument("--generator", default="auto", help="Generative video model (auto, veo, wan2.1, hunyuan, stock)")
    create_p.add_argument("--bg-video", help="Path to background video file (auto-crops to 9:16)")
    create_p.add_argument("--bg-type", choices=["space", "tech", "cosmic", "cyber", "fire", "emerald", "ancient", "ocean"], default="space", help="Background video theme")
    create_p.add_argument("--bgm", help="Path to custom BGM track")
    create_p.add_argument("--bgm-vibe", choices=["ambient", "suspense", "cyber", "none"], default="ambient", help="Procedural background music vibe")
    create_p.add_argument("--no-bgm", action="store_true", help="Disable background music")
    create_p.add_argument("--no-progress-bar", action="store_true", help="Disable bottom retention progress bar")
    create_p.add_argument("--rate", default=None, help="Speech rate / pacing (e.g. +8%%, +12%%)")
    create_p.add_argument("--no-thumb", action="store_true", help="Disable high-CTR thumbnail generation")
    create_p.add_argument("--harness", action="store_true", help="Run with Harness² cyclic verification loop (Plan -> Act -> Verify -> Reflect)")
    create_p.add_argument("-o", "--out", help="Output MP4 file path")

    # Command: brag
    brag_p = subparsers.add_parser("brag", help="Inspect a codebase/repo and generate an explosive developer launch trailer")
    brag_p.add_argument("repo_path", nargs="?", default=".", help="Path to code repository (default: current directory)")
    brag_p.add_argument("-l", "--lang", choices=["en", "ta"], default="en", help="Language")
    brag_p.add_argument("--recipe", default="terminal_glitch_scan", help="Shotcraft recipe (default: terminal_glitch_scan)")
    brag_p.add_argument("-o", "--out", help="Output MP4 file path")

    # Command: film
    film_p = subparsers.add_parser("film", help="Generate a multi-scene AI animated film / cinematic movie")
    film_p.add_argument("-p", "--prompt", help="Story concept / film prompt")
    film_p.add_argument("-l", "--lang", choices=["en", "ta"], default=None, help="Language (en=English, ta=Tamil)")
    film_p.add_argument("-s", "--style", choices=["anime_shinkai", "studio_ghibli", "cyberpunk", "pixar_3d", "dark_fantasy", "tamil_epic"], default="anime_shinkai", help="Animation visual style")
    film_p.add_argument("-a", "--aspect", choices=["16:9", "9:16"], default="16:9", help="Aspect ratio (16:9 Cinema or 9:16 Vertical Reel)")
    film_p.add_argument("-n", "--scenes", type=int, default=4, help="Number of animated scenes (default: 4)")
    film_p.add_argument("-v", "--voice", help="Neural voice identifier")
    film_p.add_argument("--generator", default="auto", help="Generative video model (auto, veo, wan2.1, hunyuan, stock, anime_ai)")
    film_p.add_argument("--bgm-vibe", choices=["ambient", "suspense", "cyber", "none"], default="ambient", help="Cinematic soundtrack vibe")
    film_p.add_argument("-o", "--out", help="Output MP4 file path")

    # Command: web
    web_p = subparsers.add_parser("web", help="Launch ShortsCreator Web Studio on browser")
    web_p.add_argument("-p", "--port", type=int, default=8080, help="Web server port (default: 8080)")
    web_p.add_argument("--host", default="0.0.0.0", help="Web server host (default: 0.0.0.0)")

    # Command: wizard
    subparsers.add_parser("wizard", help="Interactive step-by-step creation wizard")
    subparsers.add_parser("interactive", help="Alias for wizard")

    # Command: voices
    subparsers.add_parser("voices", help="List verified working Tamil and English voices")

    # Command: exploded
    exploded_p = subparsers.add_parser(
        "exploded",
        help="Generate autonomous 3D CAD exploded-view animation with mechanical Foley sound design (Sundar Pichai / Gemini Argon style)"
    )
    exploded_p.add_argument("-p", "--preset", choices=["pixel", "tensor", "quantum", "gpu"], default="pixel", help="Hardware CAD architecture preset")
    exploded_p.add_argument("-d", "--duration", type=float, default=18.0, help="Animation duration in seconds (default: 18.0)")
    exploded_p.add_argument("-a", "--aspect", choices=["16:9", "9:16"], default="16:9", help="Aspect ratio (16:9 Cinema or 9:16 Vertical Reel)")
    exploded_p.add_argument("-s", "--script", help="Optional voiceover narration script text")
    exploded_p.add_argument("-l", "--lang", choices=["en", "ta"], default="en", help="Narration language")
    exploded_p.add_argument("-v", "--voice", help="Neural voice identifier")
    exploded_p.add_argument("--fps", type=int, default=30, help="Render frame rate (default: 30)")
    exploded_p.add_argument("-o", "--out", help="Output MP4 file path")

    # Command: threejs
    threejs_p = subparsers.add_parser("threejs", help="Launch Three.js 3D WebGL motion graphics & kinetic titles studio")
    threejs_p.add_argument("--export", dest="export_3d", help="Export a standalone Three.js 3D WebGL motion title scene to specified HTML file")
    threejs_p.add_argument("-t", "--title", default="SHORTS CREATOR 3D ENGINE", help="Title text for 3D kinetic scene")
    threejs_p.add_argument("-s", "--subtitle", default="Hardware-Accelerated Autonomous Multimedia Engine", help="Subtitle text")
    threejs_p.add_argument("-p", "--palette", choices=["tokyo_storm", "cyberpunk_neon", "catppuccin", "matrix_green"], default="tokyo_storm", help="Color theme palette")
    threejs_p.add_argument("-a", "--aspect", choices=["16:9", "9:16"], default="16:9", help="Aspect ratio")

    # Command: harness
    harness_p = subparsers.add_parser("harness", help="Run Harness² cyclic verification audit on an existing MP4 video (Plan -> Act -> Verify -> Reflect)")
    harness_p.add_argument("video_path", help="Path to MP4 video file to verify and certify")

    # Command: preview-voice
    pv_p = subparsers.add_parser("preview-voice", help="Preview speech synthesis directly through studio audio")
    pv_p.add_argument("text", nargs="?", default="Welcome to ShortsCreator AI Studio.", help="Text to speak")
    pv_p.add_argument("-v", "--voice", default="jarvis", help="Voice identifier or persona")

    # Top-Level Flags for convenience
    parser.add_argument("--threejs", "--3d", dest="threejs", action="store_true", help="Launch Three.js 3D WebGL motion graphics & kinetic titles studio")
    parser.add_argument("--export-3d", dest="export_3d", default=None, help="Export a standalone Three.js 3D WebGL motion title scene to specified HTML file")
    parser.add_argument("--harness", action="store_true", help="Run with Harness² cyclic verification loop (Plan -> Act -> Verify -> Reflect)")
    parser.add_argument("--verify-video", dest="verify_video", default=None, help="Run Harness² cyclic verification audit on an existing MP4 video")
    parser.add_argument("--preview-voice", dest="preview_voice", action="store_true", help="Preview speech synthesis directly through studio audio")

    args = parser.parse_args()

    # Direct top-level handlers
    if getattr(args, "threejs", False):
        from shorts_creator.threejs_engine import launch_3d_studio
        print("🪐 [THREE.JS] Launching Three.js 3D Motion Graphics Studio...")
        launch_3d_studio()
        return

    if getattr(args, "export_3d", None):
        from shorts_creator.threejs_engine import export_3d_title_scene
        title = getattr(args, "topic", None) or "SHORTS CREATOR 3D ENGINE"
        export_3d_title_scene(args.export_3d, title, aspect_ratio="9:16")
        return

    if getattr(args, "verify_video", None):
        from shorts_creator.harness_verifier import run_harness_audit
        run_harness_audit(args.verify_video)
        return

    if getattr(args, "preview_voice", False):
        from shorts_creator.tts_engine import preview_voiceover
        text = getattr(args, "topic", None) or getattr(args, "script", None) or "Welcome to ShortsCreator AI Studio."
        voice = getattr(args, "voice", None) or "jarvis"
        preview_voiceover(text, voice)
        return

    if args.command == "threejs":
        from shorts_creator.threejs_engine import export_3d_title_scene, launch_3d_studio
        if getattr(args, "export_3d", None):
            export_3d_title_scene(args.export_3d, args.title, args.subtitle, palette=args.palette, aspect_ratio=args.aspect)
        else:
            launch_3d_studio()
        return
    elif args.command == "harness":
        from shorts_creator.harness_verifier import run_harness_audit
        run_harness_audit(args.video_path)
        return
    elif args.command == "preview-voice":
        from shorts_creator.tts_engine import preview_voiceover
        preview_voiceover(args.text, args.voice)
        return

    if args.command == "brag":
        repo_path = Path(args.repo_path).resolve()
        info = BragHarvester.inspect_repository(repo_path)
        brag_script = BragHarvester.craft_launch_script(info, lang=args.lang)
        console.print(f"[bold cyan]🚀 Crafting Developer Launch Video for '{info['name']}'...[/bold cyan]\n")
        run_pipeline(
            custom_script=brag_script["script"],
            topic=brag_script["title"],
            lang=args.lang,
            bg_type="tech",
            bgm_vibe="cyber",
            recipe=args.recipe,
            ambient="keyboard",
            output_path=args.out
        )
    elif args.command == "film":
        from shorts_creator.film_generator import generate_animated_film
        target_lang = args.lang or detect_language(args.prompt or "")
        print_banner()
        console.print(f"[bold cyan]🎬 Generating AI Animated Film in {target_lang.upper()}...[/bold cyan]\n")
        res = generate_animated_film(
            prompt=args.prompt,
            lang=target_lang,
            style=args.style,
            aspect_ratio=args.aspect,
            num_scenes=args.scenes,
            voice=args.voice,
            bgm_vibe=args.bgm_vibe,
            video_source=getattr(args, "generator", "auto"),
            output_path=args.out
        )
        console.print()
        card = f"""[bold green]🎉 Animated Film Created Successfully![/bold green]

[bold]Movie Title:[/bold] {res['title']}
[bold]Video File:[/bold] [underline cyan]{res['film_path']}[/underline cyan]
[bold]Thumbnail:[/bold] [underline yellow]{res.get('thumbnail_path', 'N/A')}[/underline yellow]
[bold]Style:[/bold] {res['style']}
[bold]Format:[/bold] {res['aspect_ratio']} Cinema ({res['duration']:.1f}s, {res['scenes_count']} Scenes)
[bold]Language:[/bold] {'தமிழ் (Tamil)' if res['lang'] == 'ta' else 'English'}
"""
        console.print(Panel(card, border_style="green", expand=False))
    elif args.command == "web":
        from shorts_creator.web import start_web_server
        start_web_server(port=args.port, host=args.host)
    elif args.command in ("wizard", "interactive"):
        interactive_wizard()
    elif args.command == "voices":
        list_voices()
    elif args.command == "create":
        target_lang = args.lang
        if not target_lang:
            target_lang = detect_language(args.topic or args.script or "")
        
        run_pipeline(
            topic=args.topic,
            custom_script=args.script,
            script_file=args.script_file,
            lang=target_lang,
            voice=args.voice,
            style=args.style,
            bg_video=args.bg_video,
            bg_type=args.bg_type,
            bgm_path=args.bgm,
            no_bgm=args.no_bgm,
            bgm_vibe=args.bgm_vibe,
            progress_bar=not args.no_progress_bar,
            recipe=args.recipe,
            avatar=args.avatar,
            cinema=args.cinema,
            ambient=args.ambient,
            sfx=args.sfx,
            thumb=not args.no_thumb,
            generator=args.generator,
            rate=args.rate,
            output_path=args.out,
            harness=getattr(args, "harness", False)
        )
    elif args.command == "exploded":
        from shorts_creator.exploded_engine import ExplodedCADVideoEngine, PIXEL_TENSOR_HARDWARE_PRESET
        print_banner()
        console.print("[bold cyan]🔬 Synthesizing Autonomous 3D CAD Exploded-View Video (Gemini Argon Workflow)...[/bold cyan]\n")

        w, h = (1920, 1080) if args.aspect == "16:9" else (1080, 1920)
        engine = ExplodedCADVideoEngine(width=w, height=h, fps=args.fps)

        out_dest = args.out
        if not out_dest:
            default_dir = get_default_output_dir()
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_dest = os.path.join(default_dir, f"{args.preset}_exploded_cad_{ts}.mp4")

        res = engine.generate_exploded_video(
            output_video_path=out_dest,
            duration=args.duration,
            preset=PIXEL_TENSOR_HARDWARE_PRESET,
            script_text=args.script,
            voice=args.voice,
            lang=args.lang
        )

        console.print()
        card = f"""[bold green]✨ CAD Exploded-View Video Created Successfully![/bold green]

[bold]Video File:[/bold] [underline cyan]{res['video_path']}[/underline cyan]
[bold]Companion Blender Script:[/bold] [underline yellow]{res['blender_script']}[/underline yellow]
[bold]Resolution:[/bold] {res['resolution']} @ {res['fps']}fps ({res['duration']:.1f}s)
[bold]Hardware Preset:[/bold] {res['preset']}
[bold]Audio Track:[/bold] Procedural Mechanical Foley (Pneumatics, Stepper Servos, Magnetic Latches, Sub-Bass)
"""
        console.print(Panel(card, border_style="cyan", expand=False))
    else:
        if len(sys.argv) == 1:
            interactive_wizard()
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
