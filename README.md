# ⚡ ShortsCreator AI 2.1 (Universal Video Engine & Film Studio)

> **Autonomous AI YouTube Shorts, Codebase Showcases, and Multi-Scene Animated Film Generator for Tamil (தமிழ்) and English.**
> Zero mandatory API keys, powered by Microsoft Edge Neural TTS, Hardware Acceleration (NVENC, VAAPI, VideoToolbox), FastMCP AI Agent Server, Multi-Model Generative AI Hub (Google Veo, Wan 2.1, HunyuanVideo), Shotcraft Cinematic Recipes, Developer Codebase 'Brag' Mode, High-CTR Thumbnail Studio, and Studio EBU R128 audio mastering.

---

## 🌟 Superpowers & Architecture (v2.1 Upgrade)

1. **⚡ Hardware-Accelerated Video Compositing (`--encoder`)**:
   - Zero-hang non-interactive probe-based detection of GPU hardware encoders:
     - `h264_nvenc`: NVIDIA GeForce / RTX GPU acceleration with NVENC.
     - `h264_vaapi`: Intel / AMD hardware acceleration on Linux.
     - `h264_videotoolbox`: Apple Silicon (M1/M2/M3/M4) hardware encoding on macOS.
     - `h264_qsv`: Intel QuickSync Video.
     - `libx264`: High-quality CPU fallback.
   - 3-5x faster rendering on supported hardware.

2. **✨ Subtitles 2.0 (Kinetic Word-Glow & Sliding Window)**:
   - **Hormozi Pop**: Active word scales up with bold stroke outline.
   - **Neon Glow Aura (`neon_glow`)**: Multi-layered blurred neon halo surrounding the active word.
   - **Dual-Line Sliding Window (`sliding`)**: Displays 2-line context where previous words gently dim down, giving viewers natural reading rhythm.
   - **Custom Highlight Colors (`--highlight-color`)**: Hex picker or ASS format (`#00FFFF`, `#05FFA1`, `#FFD700`, `#FF00FF`, `#FF4500`).
   - Semantic auto-emoji insertion (🚀, 🧠, ⚡, 💡, 🔥, 🏆, etc.).

3. **🎙️ Auto-Caption Existing Videos (`shorts caption`)**:
   - Transcribe raw or pre-recorded MP4/MOV videos with Whisper / fallback alignment.
   - Burn kinetic animated ASS subtitles into any existing video with hardware acceleration in one simple command.

4. **🔌 FastMCP Server for AI Agents (`shorts mcp` / `shorts-mcp`)**:
   - Native Model Context Protocol (MCP) server over standard JSON-RPC stdio.
   - Exposes tools to AI assistants (Claude, Cursor, Antigravity, OpenClaw):
     - `create_short`: Generate complete YouTube Short video.
     - `caption_video`: Auto-caption existing video.
     - `brag_codebase`: Generate developer launch trailer from repository.
     - `render_cad_animation`: 3D CAD exploded-view schematic animation.
     - `list_voices`: List neural TTS voices.
     - `generate_script`: AI viral script generation.

5. **💻 Project-to-Video 'Brag' Mode (`shorts brag`)**:
   - Inspects any codebase or Git repository: commit logs, README markdown, tech stack markers (Rust, Go, Python, TypeScript, Docker).
   - Generates high-energy 30-45s developer launch trailer shorts with syntax terminal scans, architecture highlights, and viral hook variants.

6. **🎥 Shotcraft Cinematic Recipe Cards (`--recipe`)**:
   - 12 production-ready cinematic shot recipes with real lens physics and adaptive optical grading:
     - `hero_reveal`: Slow dramatic steady push-in with volumetric rim lighting.
     - `speed_ramp`: Smooth dolly movement decelerating into slow-motion focus.
     - `macro_orbit`: Ultra close-up smooth focal drift with shallow depth of field.
     - `terminal_glitch_scan`: Developer terminal code scan with crisp typography.
     - `isometric_exploded`: 3D technical isometric architecture and wireframes.
     - `dutch_angle_tension`: Chiaroscuro high-contrast psychological tension.
     - `split_comparison`: Balanced side-by-side split comparison.
     - `broll_whip_pan`: Smooth cinematic camera transition.

7. **🤖 Multi-Model Generative AI Video Hub (`--generator`)**:
   - **Google Veo 3.1 / 2.0**: Native generative video synthesis with cinematic lighting via Gemini API.
   - **Alibaba Wan 2.2 / 2.1**: Diffusion Transformer video generation via Fal.ai or Replicate.
   - **Tencent HunyuanVideo**: 13B open video DiT with cinema-grade motion fluidity.
   - **Open-Source Video Harvester**: Cascading retrieval from Mixkit, Wikimedia Commons Video API, Pexels, and Pixabay with bilingual Tamil-to-English entity translation.

8. **🎵 Multi-Layer Semantic Soundscapes & Foley SFX (`--ambient`, `--sfx`)**:
   - **Acoustic Atmospheres**: `rain` (droplets & storm), `keyboard` (mechanical typing), `server` (datacenter hum), `wind` (atmospheric room tone).
   - **Hollywood Foley SFX**: `impact` (sub-bass drop), `whoosh` (camera sweep), `telemetry` (futuristic HUD beeps), `riser` (tension build-up).
   - **Studio Audio Mastering**: EBU R128 loudness normalization (-16 LUFS), 80Hz rumble filter, 3.2kHz vocal presence boost, and dynamic audio sidechain ducking.

9. **🖼️ High-CTR YouTube Thumbnail Studio**:
   - Automatically generates attention-grabbing 1080x1920 (Vertical Shorts) and 1280x720 (Cinema) thumbnails with category badge pills, bold typography, bullet points, and glowing gradient borders.

10. **👤 Digital Human Talking Presenter PiP (`--avatar`)**:
    - Transforms any portrait photo into an audio-driven talking digital presenter with lip viseme synchronization and subtle head movement, composited in a Picture-in-Picture circle.

11. **🎬 Multi-Scene Animated Film Studio (`shorts film`)**:
    - Generate multi-scene cinematic films in 6 visual anime styles (`anime_shinkai`, `studio_ghibli`, `cyberpunk`, `pixar_3d`, `dark_fantasy`, `tamil_epic`) in 16:9 Cinema or 9:16 Vertical Reel.

12. **🇮🇳 Native Tamil (தமிழ்) & English Support**:
    - Bundled `Mukta Malar` typography with HarfBuzz complex shaping (`shaping=1`) ensuring 100% accurate Tamil ligatures (`க்ஷ`, `ஸ்ரீ`).
    - Neural voices: `ta-IN-PallaviNeural`, `ta-IN-ValluvarNeural`, `ta-SG-AnbuNeural`, `en-US-ChristopherNeural`, `en-IN-PrabhatNeural`.

---

## 🚀 Installation

```bash
cd ~/shorts-creator
pip install -e .

# Or install with optional AI & captioning extras:
pip install -e ".[all]"
```

### Docker Deployment

```bash
# Run Web Studio on port 8080:
docker compose up shorts-web

# Or run headless MCP server:
docker compose up shorts-mcp
```

---

## 📖 CLI Usage & Quick Start

### 1. Auto-Caption Any Existing Video (`shorts caption`)
```bash
# Burn Neon Glow animated captions into a video:
shorts caption my_raw_video.mp4 --style neon_glow --highlight-color "#00FFFF"

# Dual-Line Sliding Window subtitles with GPU acceleration:
shorts caption input.mp4 --style sliding --encoder nvenc -o captioned_output.mp4
```

### 2. Developer Project Launch Showcase (`shorts brag`)
```bash
# Ingest local repo and build a 30s developer launch video:
shorts brag . --lang en

# Tamil Developer Showcase:
shorts brag . --lang ta --recipe terminal_glitch_scan
```

### 3. Viral YouTube Short with Shotcraft Recipe, Hardware Encoder & Soundscape
```bash
# English Short with Hero Reveal recipe, NVENC GPU acceleration, and ambient datacenter hum:
shorts create -t "Why Python 3.14 GIL Removal Matters" \
  --recipe hero_reveal \
  --encoder auto \
  --style neon_glow \
  --highlight-color "#05FFA1" \
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

### 4. Hollywood Cinema Scope Trailer (`--cinema`)
```bash
shorts create -t "The Quantum Horizon" \
  --cinema \
  --recipe dutch_angle_tension \
  --bgm-vibe suspense
```

### 5. Multi-Scene AI Animated Film (`shorts film`)
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

### 6. Connect to AI Agents via MCP (`shorts mcp`)
Add to your Claude Code or Cursor MCP config:
```json
{
  "mcpServers": {
    "shorts-creator": {
      "command": "python3",
      "args": ["-m", "shorts_creator.mcp_server"]
    }
  }
}
```

### 7. Launch the Browser Web Studio
```bash
shorts web
# Open http://localhost:8080 in any browser or on your phone via local Wi-Fi
```

---

## 🧪 Testing

```bash
python3 -m pytest tests/ -v
```

---

## 📄 License
MIT License.
