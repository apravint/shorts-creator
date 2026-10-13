# ⚡ ShortsCreator AI 2.0 (Universal Video Engine & Film Studio)

> **Autonomous AI YouTube Shorts, Codebase Showcases, and Multi-Scene Animated Film Generator for Tamil (தமிழ்) and English.**
> Zero mandatory API keys, powered by Microsoft Edge Neural TTS, Multi-Model Generative AI Hub (Google Veo, Wan 2.1, HunyuanVideo), Shotcraft Cinematic Recipes, Developer Codebase 'Brag' Mode, High-CTR Thumbnail Studio, and Studio EBU R128 audio mastering.

---

## 🌟 Superpowers & Architecture (v2.0 Upgrade)

1. **💻 Project-to-Video 'Brag' Mode (`shorts brag`)**:
   - Inspects any codebase or Git repository: commit logs, README markdown, tech stack markers (Rust, Go, Python, TypeScript, Docker).
   - Generates high-energy 30-45s developer launch trailer shorts with syntax terminal scans, architecture highlights, and viral hook variants.
2. **🎥 Shotcraft Cinematic Recipe Cards (`--recipe`)**:
   - 12 production-ready cinematic shot recipes with real lens physics and adaptive optical grading:
     - `hero_reveal`: Slow dramatic steady push-in with volumetric rim lighting.
     - `speed_ramp`: Smooth dolly movement decelerating into slow-motion focus.
     - `macro_orbit`: Ultra close-up smooth focal drift with shallow depth of field.
     - `terminal_glitch_scan`: Developer terminal code scan with crisp typography.
     - `isometric_exploded`: 3D technical isometric architecture and wireframes.
     - `dutch_angle_tension`: Chiaroscuro high-contrast psychological tension.
     - `split_comparison`: Balanced side-by-side split comparison.
     - `broll_whip_pan`: Smooth cinematic camera transition.
3. **🤖 Multi-Model Generative AI Video Hub (`--generator`)**:
   - **Google Veo 3.1 / 2.0**: Native generative video synthesis with cinematic lighting via Gemini API.
   - **Alibaba Wan 2.2 / 2.1**: Diffusion Transformer video generation via Fal.ai or Replicate.
   - **Tencent HunyuanVideo**: 13B open video DiT with cinema-grade motion fluidity.
   - **Open-Source Video Harvester**: Cascading retrieval from Mixkit, Wikimedia Commons Video API, Pexels, and Pixabay with bilingual Tamil-to-English entity translation.
4. **🎵 Multi-Layer Semantic Soundscapes & Foley SFX (`--ambient`, `--sfx`)**:
   - **Acoustic Atmospheres**: `rain` (droplets & storm), `keyboard` (mechanical typing), `server` (datacenter hum), `wind` (atmospheric room tone).
   - **Hollywood Foley SFX**: `impact` (sub-bass drop), `whoosh` (camera sweep), `telemetry` (futuristic HUD beeps), `riser` (tension build-up).
   - **Studio Audio Mastering**: EBU R128 loudness normalization (-16 LUFS), 80Hz rumble filter, 3.2kHz vocal presence boost, and dynamic audio sidechain ducking.
5. **🖼️ High-CTR YouTube Thumbnail Studio**:
   - Automatically generates attention-grabbing 1080x1920 (Vertical Shorts) and 1280x720 (Cinema) thumbnails with category badge pills, bold typography, bullet points, and glowing gradient borders.
6. **👤 Digital Human Talking Presenter PiP (`--avatar`)**:
   - Transforms any portrait photo into an audio-driven talking digital presenter with lip viseme synchronization and subtle head movement, composited in a Picture-in-Picture circle.
7. **🎬 Multi-Scene Animated Film Studio (`shorts film`)**:
   - Generate multi-scene cinematic films in 6 visual anime styles (`anime_shinkai`, `studio_ghibli`, `cyberpunk`, `pixar_3d`, `dark_fantasy`, `tamil_epic`) in 16:9 Cinema or 9:16 Vertical Reel.
8. **🇮🇳 Native Tamil (தமிழ்) & English Support**:
   - Bundled `Mukta Malar` typography with HarfBuzz complex shaping (`shaping=1`) ensuring 100% accurate Tamil ligatures (`க்ஷ`, `ஸ்ரீ`).
   - Neural voices: `ta-IN-PallaviNeural`, `ta-IN-ValluvarNeural`, `ta-SG-AnbuNeural`, `en-US-ChristopherNeural`, `en-IN-PrabhatNeural`.

---

## 🚀 Installation

```bash
cd ~/shorts-creator
pip install -e .
```

---

## 📖 CLI Usage & Quick Start

### 1. Developer Project Launch Showcase (`shorts brag`)
```bash
# Ingest local repo and build a 30s developer launch video:
shorts brag . --lang en

# Tamil Developer Showcase:
shorts brag . --lang ta --recipe terminal_glitch_scan
```

### 2. Viral YouTube Short with Shotcraft Recipe & Soundscape
```bash
# English Short with Hero Reveal recipe and ambient datacenter hum:
shorts create -t "Why Python 3.14 GIL Removal Matters" \
  --recipe hero_reveal \
  --ambient server \
  --sfx telemetry \
  --bg-type tech

# Tamil Motivation Short with cinematic impact:
shorts create -t "விண்வெளியின் மர்மங்கள்" \
  --lang ta \
  --recipe hero_reveal \
  --ambient wind \
  --sfx impact \
  --style hormozi
```

### 3. Hollywood Cinema Scope Trailer (`--cinema`)
```bash
shorts create -t "The Quantum Horizon" \
  --cinema \
  --recipe dutch_angle_tension \
  --bgm-vibe suspense
```

### 4. Multi-Scene AI Animated Film (`shorts film`)
```bash
# 4-Scene Makoto Shinkai Anime Film (16:9 Widescreen):
shorts film \
  --prompt "A lone cyber detective searching for a lost human soul in Neo Tokyo" \
  --style anime_shinkai \
  --aspect 16:9 \
  --scenes 4 \
  --bgm-vibe ambient

# Tamil Epic Historical Short Film:
shorts film \
  --prompt "புலிக்கொடி ஏந்திய சோழர் கடற்படையின் கடல் வெற்றி" \
  --lang ta \
  --style tamil_epic \
  --aspect 16:9 \
  --scenes 4
```

### 5. Launch the Browser Web Studio
```bash
shorts web
# Open http://localhost:8080 in any browser or on your phone via local Wi-Fi
```

---

## 📄 License
MIT License.
