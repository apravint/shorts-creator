# ⚡ ShortsCreator AI (YouTube Shorts Video Creator)

> **Automated AI YouTube Shorts & Reels Video Creator for Tamil (தமிழ்) and English.**
> 100% Offline-capable, zero mandatory API keys, powered by Microsoft Edge Neural TTS, ASS animated subtitles, and FFmpeg 9:16 vertical video compositing.

---

## 🌟 Key Features

* **🇮🇳 Full Bilingual Engine (Tamil & English)**:
  * **Tamil (தமிழ்)**: Native pronunciation with `ta-IN-PallaviNeural` (Female) and `ta-SG-AnbuNeural` (Male). Full Tamil Unicode font rendering using `Noto Sans Tamil`.
  * **English**: Studio-grade delivery with `en-US-ChristopherNeural` (US Male) and `en-IN-PrabhatNeural` (Indian English Male).
* **✍️ AI Viral Script & Hook Generator**:
  * Powered by Google Gemini API (if `GEMINI_API_KEY` is present) or built-in procedural viral scripts across **Space, Psychology, History, Technology, Wealth, and Science**.
  * Custom script support directly via `--script` or `--script-file`.
* **🔥 Dynamic Word-by-Word Animated Subtitles (Hormozi Style)**:
  * Neon Yellow, Cyan Glow, Emerald Green, and Fire Red glowing highlights on current spoken words.
  * Thick black stroke and drop shadow, perfectly aligned to avoid mobile YouTube UI overlays.
* **🎬 Automated 9:16 Vertical Video Compositor (1080x1920)**:
  * Automatically crops or loops any background video file.
  * **Zero-Asset Procedural Mode**: Generates animated gradient motion graphics (Cosmic, Cyber, Fire, Emerald) if no video is provided.
* **🎵 BGM & Automatic Audio Ducking**:
  * Voiceover is held crisp at 100% volume while atmospheric background music sits at 15% volume with smooth fade-in and fade-out.

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

### 1. Interactive Step-by-Step Wizard
Launch the guided interactive walkthrough:
```bash
shorts wizard
# or simply:
shorts
```

### 2. Create a Tamil Short (தமிழ்)
Generate a high-retention Tamil short about Space Mysteries:
```bash
shorts create --topic "விண்வெளியின் மர்மங்கள்" --lang ta --style hormozi
```

With custom script text in Tamil:
```bash
shorts create --script "சூரிய குடும்பத்தின் மிகப்பெரிய கோள் வியாழன் ஆகும். இதில் பூமி போல் ஆயிரம் கோள்களை அடக்க முடியும்!" --lang ta
```

### 3. Create an English Short
Generate an English short about dark psychology:
```bash
shorts create --topic "Dark Psychology Facts" --lang en --style neon-cyan --bg-type cyber
```

### 4. Use Custom Background Video and Music
```bash
shorts create \
  --topic "Black Hole Secrets" \
  --lang en \
  --bg-video ~/Videos/gameplay.mp4 \
  --bgm ~/Music/chill_lofi.mp3 \
  --out ~/Videos/black_holes_short.mp4
```

### 5. Check Working Neural Voices
```bash
shorts voices
```

---

## ⚙️ Options & Arguments

| Flag | Short | Description |
| :--- | :--- | :--- |
| `--topic` | `-t` | Topic for AI script generation |
| `--lang` | `-l` | Language (`ta` for Tamil, `en` for English - auto-detected if omitted) |
| `--voice` | `-v` | Voice ID (e.g. `ta-IN-PallaviNeural`, `en-US-ChristopherNeural`) |
| `--script` | `-s` | Custom script text |
| `--script-file` | | Path to `.txt` file containing the script |
| `--style` | | Subtitle highlight style: `hormozi`, `neon-cyan`, `neon-green`, `fire-red` |
| `--bg-video` | | Path to background video file (auto-crops and loops to 9:16) |
| `--bg-type` | | Procedural motion background: `cosmic`, `cyber`, `fire`, `emerald` |
| `--bgm` | | Custom background music path |
| `--no-bgm` | | Disable background music |
| `--out` | `-o` | Output file path (defaults to `output/short_<timestamp>.mp4`) |

---

## 📄 License
MIT License - Created for Creators & Developers.
