# AGENTS.md - Developer & AI Agent Operations Manual for `shorts-creator` 🤖

This document is the definitive operational guide for autonomous AI coding agents (Antigravity, Claude, Cursor, OpenAI Codex, OpenHands) operating within this repository.

---

## 🎯 1. System Overview & Core Philosophy

**ShortsCreator AI 2.1 (Universal Video Engine & Film Studio)**
> Autonomous AI YouTube Shorts, Codebase Showcases, and Multi-Scene Animated Film Generator for Tamil (தமிழ்) and English. Zero mandatory API keys, powered by Microsoft Edge Neural TTS, Hardware Acceleration (NVENC, VAAPI, VideoToolbox), FastMCP AI Agent Server, Multi-Model Generative AI Hub (Google Veo, Wan 2.1, HunyuanVideo), Shotcraft Cinematic Recipes, Developer Codebase 'Brag' Mode, High-CTR Thumbnail Studio, and Studio EBU R128 audio mastering. 1. ⚡ Hardware-Accelerated Video Compositing (--encoder):

### Key Architectural Capabilities
- **⚡ Hardware-Accelerated Video Compositing (`--encoder`)**: 
- `h264_nvenc`: NVIDIA GeForce / RTX GPU acceleration with NVENC.
- `h264_vaapi`: Intel / AMD hardware acceleration on Linux.
- `h264_videotoolbox`: Apple Silicon (M1/M2/M3/M4) hardware encoding on macOS.
- `h264_qsv`: Intel QuickSync Video.
- `libx264`: High-quality CPU fallback.

---

## 🏗️ 2. Repository Structure & Directory Map

| Path | Role & Architectural Responsibility |
| :--- | :--- |
| `.github/` | Subsystem directory (.github) |
| `Dockerfile` | Container build specification |
| `assets/` | Static media assets, fonts, icons, soundscapes |
| `pyproject.toml` | Python package configuration, dependencies, and tool settings |
| `shorts_creator/` | Main Python application package |
| `shorts_creator.egg-info/` | Subsystem directory (shorts_creator.egg-info) |
| `tests/` | Automated test suite (unit, integration, regression) |

---

## ⚙️ 3. Executable Verification Pipeline

Before marking any task complete, an AI agent **must** run the following verification steps sequentially:

### Tier 1: Syntax & Bytecode Compilation Check (< 2 seconds)
Ensures all modified Python files parse cleanly with zero syntax or indentation errors:
```bash
python3 -m py_compile $(find . -maxdepth 3 -name '*.py' -not -path '*/.*' -not -path '*/venv/*')
```

### Tier 2: Static Analysis & Linting
```bash
ruff check . || flake8 . || python3 -m py_compile **/*.py
```

### Tier 3: Automated Test Suite (Fast Offline / Mocked)
Verifies functional regressions across all unit tests:
```bash
pytest -v
```

### Tier 4: Smoke Test / CLI Verification
Run a non-destructive dry-run or help check to confirm executable health:
```bash
pip install -e .
pip install -e ".[all]"
```

---

## 🛡️ 4. Architectural Invariants & Non-Negotiable Rules

### Strict Invariants ("Never Do" List):
1. **Never Introduce Silent Mock Fallbacks:** If an external LLM, API, or system binary fails, raise an explicit, descriptive exception. Never return mock strings that mask runtime failures.
2. **Strict Type Annotations:** All new function signatures must include Python type annotations (`typing`, `pydantic`, or native dataclasses).
3. **Zero Hardcoded Secrets or Paths:** Never embed API keys, bearer tokens, or absolute paths (e.g., `/home/apravint`). Use `os.environ` or XDG specification paths.

### Security & Environment Variables:
- All API keys and secrets must be loaded strictly from environment variables.
- Never commit `.env`, `.pem`, token files, or private credentials.

---

## 🤖 5. Autonomous Agent Operational Protocol

When dispatched to resolve an issue, implement a feature, or refactor code in this repo:

1. **Phase 1 — Explore & Plan:**
   - Read this `AGENTS.md` and relevant source files.
   - Check existing tests to establish the baseline.
2. **Phase 2 — Act (Surgical Implementation):**
   - Implement changes with minimal blast radius.
   - Adhere to the established code style and existing conventions.
3. **Phase 3 — Verify:**
   - Run the Tier 1, 2, and 3 verification commands listed above.
   - Ensure all existing and new tests pass cleanly.
4. **Phase 4 — Reflect:**
   - Review `git diff` to confirm zero unintended whitespace or collateral changes.
   - Confirm no untracked scratch files remain.

---
*Maintained by Ayyappa Pravin • Engineered for Antigravity, Claude, Cursor & Modern Autonomous AI Agents.*
