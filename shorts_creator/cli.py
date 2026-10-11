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
            task_bgm = progress.add_task("[magenta]🎵 Mastering 320kbps BGM & audio ducking...", total=1)
            final_bgm = prepare_bgm_track(workspace_dir, duration, custom_bgm=bgm_path)
            progress.update(task_bgm, completed=1)

        # Step 5: FFmpeg Video Compositing & Studio Audio Mastering
        task_video = progress.add_task(f"[bold red]🎬 Rendering 1080x1920 Short ({duration:.1f}s)...", total=1)
        final_video = assemble_shorts_video(
            voiceover_path=tts_data["audio_path"],
            subtitle_ass_path=ass_path,
            duration=duration,
            output_path=output_path,
            bg_video_path=bg_video,
            bg_type=bg_type,
            bgm_path=final_bgm
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
        choices=["hormozi", "neon-cyan", "neon-green", "fire-red"],
        default="hormozi"
    )

    # 5. Background Motion Theme
    bg_type = Prompt.ask(
        "Motion Background Theme",
        choices=["cosmic", "cyber", "fire", "emerald"],
        default="cosmic"
    )

    run_pipeline(
        topic=topic,
        custom_script=custom_script,
        lang=lang_choice,
        voice=voice,
        style=style,
        bg_type=bg_type
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
    create_p.add_argument("--style", choices=["hormozi", "neon-cyan", "neon-green", "fire-red"], default="hormozi", help="Subtitle highlight style")
    create_p.add_argument("--bg-video", help="Path to background video file (auto-crops to 9:16)")
    create_p.add_argument("--bg-type", choices=["cosmic", "cyber", "fire", "emerald"], default="cosmic", help="Procedural background theme")
    create_p.add_argument("--bgm", help="Path to custom BGM track")
    create_p.add_argument("--no-bgm", action="store_true", help="Disable background music")
    create_p.add_argument("-o", "--out", help="Output MP4 file path (defaults to Android Download/Shorts folder)")

    # Command: wizard
    subparsers.add_parser("wizard", help="Interactive step-by-step creation wizard")
    subparsers.add_parser("interactive", help="Alias for wizard")

    # Command: voices
    subparsers.add_parser("voices", help="List verified working Tamil and English voices")

    args = parser.parse_args()

    if args.command in ("wizard", "interactive"):
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
