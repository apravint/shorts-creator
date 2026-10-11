"""
CLI Interface for YouTube Shorts Creator.
Features rich terminal UI, interactive wizard mode, and one-line automated short generation.
Outputs directly to Android's Download folder with Studio-grade 320kbps 48kHz audio mastering.
"""

import os
import sys
import re
import argparse
from datetime import datetime
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

console = Console()


def print_banner():
    banner = """[bold cyan]⚡ SHORTS CREATOR AI ⚡[/bold cyan]
[dim]Automated Viral YouTube Shorts Pipeline • தமிழ் (Tamil) & English[/dim]"""
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
    table = Table(title="🎙️ Verified Working Neural Voices", border_style="cyan")
    table.add_column("Language", style="bold green")
    table.add_column("Gender", style="yellow")
    table.add_column("Voice ID (Edge-TTS)", style="cyan")
    table.add_column("Accent / Dialect", style="white")

    table.add_row("Tamil (தமிழ்)", "Female", "ta-IN-PallaviNeural", "India (Natural & Expressive)")
    table.add_row("Tamil (தமிழ்)", "Male", "ta-SG-AnbuNeural", "Singapore (Crisp & Clear)")
    table.add_row("English", "Male", "en-US-ChristopherNeural", "US (Deep Broadcast / Viral)")
    table.add_row("English", "Indian Male", "en-IN-PrabhatNeural", "India (Clear English)")

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
    output_path: str = None
):
    print_banner()

    # Create temporary session workspace
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    workspace_dir = os.path.join(os.getcwd(), "output", f"session_{timestamp}")
    os.makedirs(workspace_dir, exist_ok=True)

    # Determine default output directory (Android Download folder prioritized)
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
        task_tts = progress.add_task(f"[green]🎙️ Synthesizing {detected_lang.upper()} voiceover...", total=1)
        tts_data = generate_voiceover(
            text=script_data["full_text"],
            lang=detected_lang,
            output_dir=workspace_dir,
            custom_voice=voice
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
            task_bgm = progress.add_task(f"[magenta]🎵 Mastering 320kbps BGM ({bgm_vibe}) & audio ducking...", total=1)
            final_bgm = prepare_bgm_track(workspace_dir, duration, custom_bgm=bgm_path, vibe=bgm_vibe)
            progress.update(task_bgm, completed=1)

        # Step 5: FFmpeg Video Compositing & Studio Audio Mastering
        task_video = progress.add_task(f"[bold red]🎬 Rendering 1080x1920 Short ({duration:.1f}s)...", total=1)
        final_video = assemble_shorts_video(
            voiceover_path=tts_data["audio_path"],
            subtitle_ass_path=ass_path,
            duration=duration,
            output_path=output_path,
            topic=script_data.get("title") or topic,
            bg_video_path=bg_video,
            bg_type=bg_type,
            bgm_path=final_bgm,
            progress_bar=progress_bar
        )
        progress.update(task_video, completed=1)

    # Success Summary Card
    console.print()
    summary_text = f"""[bold green]✅ YouTube Short Created Successfully![/bold green]

[bold]Video File:[/bold] [underline cyan]{final_video}[/underline cyan]
[bold]Title:[/bold] {script_data['title']}
[bold]Language:[/bold] {'தமிழ் (Tamil)' if detected_lang == 'ta' else 'English'}
[bold]Duration:[/bold] {duration:.1f} seconds
[bold]Voice Engine:[/bold] {tts_data['voice']}
[bold]Typography:[/bold] Mukta Malar (HarfBuzz Complex Ligature Shaping)
[bold]Background:[/bold] High-Definition 1080x1920 Vertical Video Loop
[bold]Audio Mastering:[/bold] [bold magenta]320kbps 48,000Hz (EBU R128 Normalized)[/bold magenta]
[bold]📱 Android Downloads / Gallery:[/bold] [bold yellow]{final_video}[/bold yellow]
[bold]Hashtags:[/bold] [dim]{' '.join(script_data['tags'])}[/dim]
"""
    console.print(Panel(summary_text, border_style="green", expand=False))
    return final_video


def interactive_wizard():
    print_banner()
    console.print("[bold yellow]🚀 Welcome to the YouTube Shorts Creator Wizard![/bold yellow]\n")

    # 1. Language
    lang_choice = Prompt.ask(
        "Select Language",
        choices=["en", "ta"],
        default="en"
    )

    # 2. Topic / Script Mode
    mode = Prompt.ask(
        "Script Source",
        choices=["ai_topic", "custom_text"],
        default="ai_topic"
    )

    topic = None
    custom_script = None
    if mode == "ai_topic":
        if lang_choice == "ta":
            topic = Prompt.ask("Enter Topic (e.g. விண்வெளி மர்மங்கள், உளவியல் ரகசியங்கள், வரலாறு)", default="விண்வெளியின் மர்மங்கள்")
        else:
            topic = Prompt.ask("Enter Topic (e.g. Mind-blowing space facts, Dark psychology, Wealth habits)", default="3 Terrifying Space Facts")
    else:
        custom_script = Prompt.ask("Enter custom script text")

    # 3. Voice
    if lang_choice == "ta":
        voice = Prompt.ask(
            "Select Voice",
            choices=["ta-IN-PallaviNeural (Female)", "ta-SG-AnbuNeural (Male)"],
            default="ta-IN-PallaviNeural (Female)"
        ).split()[0]
    else:
        voice = Prompt.ask(
            "Select Voice",
            choices=["en-US-ChristopherNeural (US Male)", "en-IN-PrabhatNeural (Indian Male)"],
            default="en-US-ChristopherNeural (US Male)"
        ).split()[0]

    # 4. Caption Style
    style = Prompt.ask(
        "Subtitle Color Style",
        choices=["hormozi", "neon-cyan", "neon-green", "fire-red", "gold", "purple-neon", "white-classic"],
        default="hormozi"
    )

    # 5. Background Video Theme
    bg_type = Prompt.ask(
        "Background Video Theme",
        choices=["space", "tech", "cosmic", "cyber", "fire", "emerald"],
        default="space"
    )

    # 6. Audio Vibe
    bgm_vibe = Prompt.ask(
        "Background Music Vibe",
        choices=["ambient", "suspense", "cyber"],
        default="ambient"
    )

    run_pipeline(
        topic=topic,
        custom_script=custom_script,
        lang=lang_choice,
        voice=voice,
        style=style,
        bg_type=bg_type,
        bgm_vibe=bgm_vibe
    )


def main():
    parser = argparse.ArgumentParser(
        description="ShortsCreator - Automated AI YouTube Shorts Video Creator (Tamil & English)"
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
    create_p.add_argument("--bg-video", help="Path to background video file (auto-crops to 9:16)")
    create_p.add_argument("--bg-type", choices=["space", "tech", "cosmic", "cyber", "fire", "emerald"], default="space", help="Background video theme")
    create_p.add_argument("--bgm", help="Path to custom BGM track")
    create_p.add_argument("--bgm-vibe", choices=["ambient", "suspense", "cyber"], default="ambient", help="Procedural background music vibe")
    create_p.add_argument("--no-bgm", action="store_true", help="Disable background music")
    create_p.add_argument("--no-progress-bar", action="store_true", help="Disable bottom retention progress bar")
    create_p.add_argument("-o", "--out", help="Output MP4 file path (defaults to Android Download/Shorts folder)")

    # Command: film
    film_p = subparsers.add_parser("film", help="Generate a multi-scene AI animated film / cinematic movie")
    film_p.add_argument("-p", "--prompt", help="Story concept / film prompt")
    film_p.add_argument("-l", "--lang", choices=["en", "ta"], default=None, help="Language (en=English, ta=Tamil)")
    film_p.add_argument("-s", "--style", choices=["anime_shinkai", "studio_ghibli", "cyberpunk", "pixar_3d", "dark_fantasy", "tamil_epic"], default="anime_shinkai", help="Animation visual style")
    film_p.add_argument("-a", "--aspect", choices=["16:9", "9:16"], default="16:9", help="Aspect ratio (16:9 Cinema or 9:16 Vertical Reel)")
    film_p.add_argument("-n", "--scenes", type=int, default=4, help="Number of animated scenes (default: 4)")
    film_p.add_argument("-v", "--voice", help="Neural voice identifier")
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

    args = parser.parse_args()

    if args.command == "film":
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
            output_path=args.out
        )
        console.print()
        card = f"""[bold green]🎉 Animated Film Created Successfully![/bold green]

[bold]Movie Title:[/bold] {res['title']}
[bold]Video File:[/bold] [underline cyan]{res['film_path']}[/underline cyan]
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
        # Auto-detect language from topic/script if not given
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
            output_path=args.out
        )
    else:
        # Default behavior with no arguments: show help or launch wizard
        if len(sys.argv) == 1:
            interactive_wizard()
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
