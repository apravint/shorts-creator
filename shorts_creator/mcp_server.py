"""
FastMCP Server for ShortsCreator AI.
Allows AI coding agents (Claude, Antigravity, Cursor, OpenClaw) to autonomously create,
script, voice, and render YouTube Shorts, 3D CAD animations, and codebase brag trailers.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional

from shorts_creator.tts_engine import VOICE_MAP, VOICE_ALIASES, resolve_voice_identifier
from shorts_creator.script_gen import prepare_script
from shorts_creator.shotcraft import SHOT_RECIPES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("shorts-mcp")


TOOLS_SPEC = [
    {
        "name": "create_short",
        "description": "Create an autonomous AI YouTube Short or Cinema Trailer with voiceover, B-roll, captions, and soundscapes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Topic or headline for the short (e.g. 'Why Python 3.14 GIL Removal Matters', 'விண்வெளியின் மர்மங்கள்')"},
                "lang": {"type": "string", "enum": ["en", "ta", "hi", "te", "ml", "kn"], "default": "en", "description": "Language (en, ta, hi, te, etc.)"},
                "recipe": {"type": "string", "enum": list(SHOT_RECIPES.keys()), "default": "hero_reveal", "description": "Cinematic shotcraft camera recipe"},
                "style": {"type": "string", "enum": ["hormozi", "neon_glow", "sliding", "neon-cyan", "fire-red"], "default": "hormozi", "description": "Animated caption style"},
                "bg_type": {"type": "string", "enum": ["cosmic", "tech", "cyber", "emerald", "gold", "fire"], "default": "tech", "description": "Background aesthetic"}
            },
            "required": ["topic"]
        }
    },
    {
        "name": "brag_codebase",
        "description": "Inspect a Git repository or directory and generate an explosive 30-45s developer launch trailer with terminal scans.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {"type": "string", "default": ".", "description": "Path to local codebase repository"},
                "lang": {"type": "string", "enum": ["en", "ta"], "default": "en"},
                "recipe": {"type": "string", "default": "terminal_glitch_scan"}
            }
        }
    },
    {
        "name": "render_cad_animation",
        "description": "Generate an autonomous 3D CAD exploded-view animation with mechanical Foley sound design (Sundar Pichai / Gemini Argon style).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "preset": {"type": "string", "enum": ["pixel_tensor", "quantum_chip", "gpu_arch", "neural_engine"], "default": "pixel_tensor"},
                "title": {"type": "string", "description": "Custom headline for the hardware architecture"}
            }
        }
    },
    {
        "name": "caption_video",
        "description": "Transcribe an existing MP4/MOV video and burn animated Hormozi/Neon Glow subtitles into it.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "video_path": {"type": "string", "description": "Path to input video file"},
                "style": {"type": "string", "enum": ["hormozi", "neon_glow", "sliding"], "default": "hormozi"},
                "lang": {"type": "string", "description": "Language code (optional, e.g. en, ta)"}
            },
            "required": ["video_path"]
        }
    },
    {
        "name": "list_voices",
        "description": "List verified neural speech voices for Tamil, English, and regional languages.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "lang": {"type": "string", "enum": ["en", "ta", "hi", "te", "ml", "kn"], "default": "en"}
            }
        }
    },
    {
        "name": "generate_script",
        "description": "Generate a high-retention viral YouTube Shorts script with hook, body, and call-to-action.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Topic to write about"},
                "lang": {"type": "string", "enum": ["en", "ta", "hi"], "default": "en"},
                "style": {"type": "string", "default": "viral"}
            },
            "required": ["topic"]
        }
    }
]


def handle_tool_call(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute requested tool and return standardized JSON result."""
    try:
        if name == "create_short":
            from shorts_creator.cli import run_create_pipeline
            topic = args.get("topic", "ShortsCreator AI Demo")
            lang = args.get("lang", "en")
            recipe = args.get("recipe", "hero_reveal")
            bg_type = args.get("bg_type", "tech")
            style = args.get("style", "hormozi")

            res = run_create_pipeline(
                topic=topic,
                lang=lang,
                recipe=recipe,
                bg_type=bg_type,
                style=style
            )
            return {"status": "success", "result": res}

        elif name == "brag_codebase":
            from shorts_creator.brag import inspect_codebase, generate_brag_script
            repo_path = os.path.abspath(args.get("repo_path", "."))
            info = inspect_codebase(repo_path)
            lang = args.get("lang", "en")
            script = generate_brag_script(info, lang=lang)
            return {
                "status": "success",
                "repo_name": info.get("name"),
                "tech_stack": info.get("stack", []),
                "script": script
            }

        elif name == "render_cad_animation":
            from shorts_creator.exploded_engine import ExplodedCADVideoEngine
            preset = args.get("preset", "pixel_tensor")
            title = args.get("title")
            engine = ExplodedCADVideoEngine()
            out_file = engine.generate_hardware_video(preset_name=preset, custom_title=title)
            return {"status": "success", "video_path": out_file}

        elif name == "caption_video":
            from shorts_creator.caption_engine import auto_caption_video
            vid = args.get("video_path")
            style = args.get("style", "hormozi")
            lang = args.get("lang")
            out = auto_caption_video(vid, style=style, lang=lang)
            return {"status": "success", "captioned_video": out}

        elif name == "list_voices":
            lang = args.get("lang", "en")
            voices = VOICE_MAP.get(lang, VOICE_MAP["en"])
            return {"status": "success", "language": lang, "voices": voices, "aliases": VOICE_ALIASES}

        elif name == "generate_script":
            topic = args.get("topic")
            lang = args.get("lang", "en")
            script_data = prepare_script(topic, lang=lang)
            return {"status": "success", "script": script_data}

        else:
            return {"status": "error", "message": f"Unknown tool: {name}"}

    except Exception as e:
        logger.error(f"Error executing {name}: {e}")
        return {"status": "error", "error": str(e)}


def run_stdio_server():
    """Standard Model Context Protocol JSON-RPC Stdio Server."""
    logger.info("ShortsCreator MCP Server online (stdio transport)")
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "initialize":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {
                            "name": "shorts-creator-mcp",
                            "version": "2.1.0"
                        },
                        "capabilities": {
                            "tools": {}
                        }
                    }
                }
            elif method == "tools/list":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": TOOLS_SPEC
                    }
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                call_res = handle_tool_call(tool_name, tool_args)
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(call_res, indent=2)}
                        ]
                    }
                }
            elif method == "notifications/initialized":
                continue
            else:
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }

            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        except Exception as e:
            logger.error(f"MCP protocol error: {e}")


def main():
    run_stdio_server()


if __name__ == "__main__":
    main()
