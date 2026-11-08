# AGENTS.md - Developer & AI Agent Guide for shorts-creator 🤖

## 🎯 Repository Overview
**shorts-creator**: > **Autonomous AI YouTube Shorts, Codebase Showcases, and Multi-Scene Animated Film Generator for Tamil (தமிழ்) and English.** > Zero mandatory API keys, powered by Microsoft Edge Neural TTS, Hardware Acceleration (NVENC, VAAPI, VideoToolbox), FastMCP AI Agent Server, Multi-Model Generative AI Hub (Google Veo, Wan 2.1, HunyuanVideo), Shotcraft Cinematic Recipes, Developer Codebase 'Brag' Mode, High-CTR Thumbnail Studio, and Studio EBU R128 audio mastering. 1. **⚡ Hardware-Accelerated Video Compositing (`--encoder`)**:

---

## 🏗️ Repository Architecture
Key directories and files: `.github/, Dockerfile, LICENSE, README.md, assets/, docker-compose.yml, output/, pyproject.toml, requirements.txt, setup.py, shorts_creator/, shorts_creator.egg-info/`.

### Tech Stack & Runtime
- **Language:** Python 3.10+ (type-annotated, modern packaging)
- **Package / Build:** `pyproject.toml` / `pip install -e .`

## ⚙️ Executable Verification Commands

Before marking any agent task as complete, run verification:

### 1. Syntax & Compilation Check
```bash
python3 -m py_compile $(find . -maxdepth 3 -name '*.py' -not -path '*/.*' -not -path '*/venv/*')
```

### 2. Linting & Formatting
```bash
ruff check . || flake8 . || python3 -m py_compile **/*.py
```

### 3. Test Suite Execution
```bash
pytest
```

---

## 🛡️ Coding & Safety Guidelines for Autonomous Agents

1. **Documentation Integrity:** Preserve all existing docstrings, header comments, and licensing banners. Never delete context unless specifically instructed.
2. **Zero Hardcoded Secrets:** Never embed API keys, OAuth tokens, personal access tokens, or sensitive credentials in committed files. Read credentials exclusively from environment variables or secure credential paths.
3. **Git Hygiene:**
   - Do not force-push (`git push --force`) or run destructive commands.
   - Never modify root git configurations or harness infrastructure outside task scope.
   - Keep git diffs atomic, focused, and verified before committing.
4. **Agent Workflow Protocol:**
   - **Plan:** Inspect codebase architecture and dependencies before editing.
   - **Act:** Make minimal, clean, high-precision changes.
   - **Verify:** Run the appropriate verification commands listed above.
   - **Reflect:** Confirm zero regressions and review `git diff`.

---
*Maintained by Ayyappa Pravin • Built for Antigravity, Claude, Cursor & Autonomous AI Agents.*
