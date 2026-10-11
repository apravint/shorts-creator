# ⚡ ShortsCreator & FilmEngine AI (Shorts & Animated Film Generator)

> **Automated AI YouTube Shorts & Multi-Scene Animated Film / Movie Generator for Tamil (தமிழ்) and English.**
> Zero mandatory API keys, powered by Microsoft Edge Neural TTS, Pollinations AI neural visual art, 2.5D Ken Burns camera animation, ASS animated subtitles, and FFmpeg 1080p compositing (16:9 Cinema & 9:16 Reels).

---

## 🌟 Key Features

* **🎬 Multi-Scene Animated Film Generator (`shorts film`)**:
  * **Always Fresh AI Visuals**: Every movie scene generates unique neural anime/cinematic artwork tailored to the scene script (no repeating stock loops).
  * **6 Visual Anime & Film Styles**:
    * `anime_shinkai`: Makoto Shinkai aesthetic (breathtaking skies, volumetric lighting)
    * `studio_ghibli`: Hand-painted Hayao Miyazaki watercolor fantasy
    * `cyberpunk`: Neo-Tokyo futuristic cyberpunk with neon rain
    * `pixar_3d`: 3D animated feature film render
    * `dark_fantasy`: Elden Ring / Berserk dark fantasy anime
    * `tamil_epic`: Historical Chola & Pandya royal naval grandeur (Baahubali / Ponniyin Selvan aesthetic)
  * **2.5D Cinematic Camera Choreography**: Dynamic Ken Burns sweeps, dramatic push-ins, pull-backs, and pan shots with atmospheric grading.
  * **Dual Aspect Ratios**: **16:9 Widescreen Cinema (1920x1080)** with letterbox bars or **9:16 Vertical Reel (1080x1920)** for short films.
* **🌐 Web Studio Dashboard (`shorts web`)**:
  * Dual-mode studio: Toggle between **Viral Shorts Creator** and **Animated Movie Studio**.
  * Multi-scene interactive storyboard editor with camera movement tags and dialogue previews.
  * Dynamic simulator: Switches between a **9:16 Mobile Smartphone** and a **16:9 Cinema Theater**.
  * Instant voice audition tester and live rendering log console.
* **🇮🇳 Full Bilingual Engine (Tamil & English)**:
  * **Tamil (தமிழ்)**: Native pronunciation with `ta-IN-PallaviNeural` and `ta-SG-AnbuNeural`. Full Tamil Unicode font rendering using `Mukta Malar` with HarfBuzz complex ligature shaping.
  * **English**: Studio-grade delivery with `en-US-ChristopherNeural` and `en-IN-PrabhatNeural`.
* **🎯 True Millisecond Word-by-Word Subtitle Sync**:
  * Streams Edge-TTS `WordBoundary` timestamps for 100% millisecond-accurate caption highlighting.
  * Micro-bounce pop animations (`\fscx`, `\fscy`) on active spoken words.
* **📈 Dynamic Retention Progress Bar**:
  * Glowing progress indicator along the bottom of the video for YouTube Shorts / Reels.
* **🎵 Procedural Atmospheric BGM & Audio Ducking**:
  * Vibes: `ambient` (lush drone), `suspense` (dark tension), and `cyber` (synthwave pulse).
  * Studio vocal mastering: EBU R128 loudness normalization (-16 LUFS) with 48,000Hz 320kbps output.

---

## 🚀 Installation

Install the CLI tool locally on your Linux / Termux machine:

```bash
cd ~/shorts-creator
pip install -e .
```

This registers the global commands `shorts` and `shorts-creator`.

---

## 📖 Usage Examples

### 1. Launch the Browser Web Studio
```bash
shorts web
# Opens on http://localhost:8080 (accessible from mobile browser or PC on local Wi-Fi)
```

### 2. Generate an AI Animated Film (16:9 Cinema Movie)
Create a 4-scene Makoto Shinkai anime movie in English:
```bash
shorts film \
  --prompt "A lone cyber detective searching for a lost human soul in Neo Tokyo" \
  --style anime_shinkai \
  --aspect 16:9 \
  --scenes 4 \
  --bgm-vibe ambient
```

Create a Tamil Historical Animated Film (தமிழ்):
```bash
shorts film \
  --prompt "புலிக்கொடி ஏந்திய சோழர் கடற்படையின் கடல் வெற்றி" \
  --lang ta \
  --style tamil_epic \
  --aspect 16:9 \
  --scenes 4 \
  --bgm-vibe suspense
```

Create a Studio Ghibli Fantasy Vertical Short Film (9:16):
```bash
shorts film \
  --prompt "A young girl discovering a glowing star spirit inside an ancient mossy forest" \
  --style studio_ghibli \
  --aspect 9:16 \
  --scenes 4
```

### 3. Create a Viral YouTube Short (9:16)
```bash
shorts create --topic "Dark Psychology Facts" --lang en --style gold --bgm-vibe suspense
```

### 4. Interactive Step-by-Step Wizard
```bash
shorts wizard
```

---

## ⚙️ Options & Arguments

### Film Mode (`shorts film`)
| Flag | Short | Description |
| :--- | :--- | :--- |
| `--prompt` | `-p` | Story concept / film idea |
| `--lang` | `-l` | Language (`en` for English, `ta` for Tamil) |
| `--style` | `-s` | `anime_shinkai`, `studio_ghibli`, `cyberpunk`, `pixar_3d`, `dark_fantasy`, `tamil_epic` |
| `--aspect` | `-a` | Aspect ratio: `16:9` (Cinema) or `9:16` (Vertical Reel) |
| `--scenes` | `-n` | Number of animated scenes (default: 4) |
| `--voice` | `-v` | Voice identifier |
| `--bgm-vibe` | | Soundtrack mood: `ambient`, `suspense`, `cyber`, `none` |
| `--out` | `-o` | Output file path |

### Shorts Mode (`shorts create`)
| Flag | Short | Description |
| :--- | :--- | :--- |
| `--topic` | `-t` | Topic for viral short |
| `--style` | | `hormozi`, `neon-cyan`, `neon-green`, `fire-red`, `gold`, `purple-neon`, `white-classic` |
| `--bg-video` | | Custom background video file |
| `--bg-type` | | `space`, `tech`, `cosmic`, `cyber`, `fire`, `emerald` |
| `--no-progress-bar` | | Disable retention progress bar |

---

## 📄 License
MIT License - Created for Creators & Developers.
