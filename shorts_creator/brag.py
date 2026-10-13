"""
Project-to-Video 'Brag' & Developer Launch Showcase Engine for ShortsCreator AI.
Inspects any codebase, Git repository, or project folder to extract key metrics,
features, and tech stack markers, generating high-CTR launch shorts & viral hooks.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional


class BragHarvester:
    """Inspects a software repository and extracts high-CTR launch story metrics."""

    @staticmethod
    def inspect_repository(repo_path: Path) -> Dict[str, Any]:
        repo_path = Path(repo_path).resolve()
        info: Dict[str, Any] = {
            "name": repo_path.name.replace("-", " ").title(),
            "description": "",
            "features": [],
            "tech_stack": [],
            "cli_command": repo_path.name.lower(),
            "git_stats": {}
        }

        # 1. Inspect README
        readme_candidates = list(repo_path.glob("README*")) + list(repo_path.glob("readme*"))
        if readme_candidates:
            try:
                with open(readme_candidates[0], "r", encoding="utf-8", errors="ignore") as rf:
                    text = rf.read(64000)
                # Extract title
                m_title = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
                if m_title:
                    info["name"] = m_title.group(1).strip()
                # Extract first descriptive paragraph
                paragraphs = [p.strip() for p in text.split("\n\n") if p.strip() and not p.startswith("#")]
                if paragraphs:
                    info["description"] = paragraphs[0][:220].replace("\n", " ")
                # Extract feature bullet points
                bullets = re.findall(r"^[\*\-]\s+\*\*([^\*]+)\*\*:\s*(.+)$", text, re.MULTILINE)
                if not bullets:
                    bullets = re.findall(r"^[\*\-]\s+(.+)$", text, re.MULTILINE)
                for b in bullets[:6]:
                    feat_str = f"{b[0]}: {b[1]}" if isinstance(b, tuple) else str(b)
                    info["features"].append(feat_str[:90])
            except Exception:
                pass

        # 2. Inspect Tech Stack Markers
        if (repo_path / "Cargo.toml").exists() or any(repo_path.glob("**/*.rs")):
            info["tech_stack"].append("Rust")
        if (repo_path / "go.mod").exists() or any(repo_path.glob("**/*.go")):
            info["tech_stack"].append("Go")
        if (repo_path / "package.json").exists() or any(repo_path.glob("**/*.ts")):
            info["tech_stack"].append("TypeScript / React")
        if (repo_path / "pyproject.toml").exists() or (repo_path / "requirements.txt").exists() or (repo_path / "setup.py").exists() or any(repo_path.glob("**/*.py")):
            info["tech_stack"].append("Python")
        if (repo_path / "Dockerfile").exists():
            info["tech_stack"].append("Docker")

        # 3. Inspect Git Log
        try:
            commits = subprocess.check_output(
                ["git", "log", "-n", "10", "--oneline"],
                cwd=str(repo_path),
                text=True,
                stderr=subprocess.DEVNULL
            ).strip().splitlines()
            info["git_stats"]["recent_commits"] = len(commits)
            info["git_stats"]["latest_commit"] = commits[0] if commits else ""
        except Exception:
            pass

        return info

    @staticmethod
    def craft_launch_script(info: Dict[str, Any], lang: str = "en") -> Dict[str, Any]:
        """Crafts a high-energy 30-45s developer launch showcase script."""
        name = info.get("name", "New Project")
        desc = info.get("description", "A game-changing software release.")
        stack = ", ".join(info.get("tech_stack", ["Modern High-Performance Stack"]))
        feats = info.get("features", [])
        feat1 = feats[0] if len(feats) > 0 else "Blazing-fast execution and zero friction"
        feat2 = feats[1] if len(feats) > 1 else "Next-generation autonomous automation"
        cmd = info.get("cli_command", "run")

        if lang == "ta":
            title = f"{name} - புதிய டெவலப்பர் மென்பொருள் வெளியீடு"
            script = (
                f"டெவலப்பர்களுக்கான ஒரு புரட்சிகரமான புதிய கருவி தான் {name}! "
                f"இது {stack} கொண்டு மிகத் துல்லியமாக உருவாக்கப்பட்டுள்ளது. "
                f"முதல் முக்கிய அம்சம்: {feat1}. "
                f"அடுத்ததாக: {feat2}. "
                f"இனி நேரத்தை வீணடிக்காமல் ஒரே கமாண்டில் '{cmd}' இயக்கி உடனடியாக உங்கள் வேலைகளை பலமடங்கு வேகப்படுத்துங்கள்! "
                f"முழுமையான விவரங்கள் மற்றும் சோர்ஸ் கோட் கீழே உள்ள லிங்கில் உள்ளது."
            )
        else:
            title = f"Meet {name} — The Developer Tool That Changes Everything"
            script = (
                f"Stop doing things the old way. Meet {name}! "
                f"Built with {stack}, it solves your biggest development headache in seconds. "
                f"Number one: {feat1}. "
                f"Number two: {feat2}. "
                f"All it takes is one simple terminal command: '{cmd}'. "
                f"Check out the open source repo today and star the project on GitHub!"
            )

        return {
            "title": title,
            "script": script,
            "info": info
        }


class ViralHookGenerator:
    """Generates 3 distinct viral opening hooks for A/B testing."""

    @staticmethod
    def generate_hooks(topic: str, lang: str = "en") -> List[Dict[str, str]]:
        if lang == "ta":
            return [
                {"type": "Contrarian", "hook": f"நீங்கள் நினைப்பது தவறு! {topic} பற்றி யாருக்கும் தெரியாத உண்மை."},
                {"type": "Curiosity", "hook": f"இதை மட்டும் நீங்கள் தெரிந்துகொண்டால் உங்கள் வாழ்க்கையே மாறும்: {topic}."},
                {"type": "Direct Urgency", "hook": f"இப்போது கவனியுங்கள்! {topic} குறித்து அடுத்த 60 வினாடிகளில் தெரிந்து கொள்ளுங்கள்."}
            ]
        return [
            {"type": "Contrarian", "hook": f"Everything you’ve been told about {topic} is completely backwards."},
            {"type": "Curiosity", "hook": f"Almost nobody knows this secret about {topic}, but it changes everything."},
            {"type": "Direct Urgency", "hook": f"Stop scrolling. Here is what you actually need to know about {topic} in 45 seconds."}
        ]
