"""
Web Studio Server for ShortsCreator AI.
Runs a zero-dependency, high-performance local web server (mobile & desktop friendly)
allowing script generation, voice auditions, live 9:16 simulator previews, and one-click video rendering.
"""

import os
import sys
import json
import uuid
import time
import shutil
import threading
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

from shorts_creator.script_gen import prepare_script, get_procedural_template
from shorts_creator.templates import VIRAL_TEMPLATES
from shorts_creator.tts_engine import generate_voiceover, get_default_voice
from shorts_creator.subtitle_gen import generate_ass_subtitles
from shorts_creator.bgm_manager import prepare_bgm_track
from shorts_creator.video_engine import assemble_shorts_video
from shorts_creator.cli import get_default_output_dir

STATIC_DIR = os.path.join(os.path.dirname(__file__), "web_static")
JOB_REGISTRY: Dict[str, Dict[str, Any]] = {}


class ShortsWebHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Clean console logging
        pass

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        # 1. Main UI
        if path in ("/", "/index.html"):
            index_file = os.path.join(STATIC_DIR, "index.html")
            if os.path.exists(index_file):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(index_file, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "index.html not found")
            return

        # 2. Template API
        if path == "/api/template":
            cat = params.get("cat", ["space"])[0]
            lang = params.get("lang", ["en"])[0]
            tmpl = VIRAL_TEMPLATES.get(cat, VIRAL_TEMPLATES["space"]).get(lang, {})
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(tmpl).encode("utf-8"))
            return

        # 3. Voice Preview API
        if path == "/api/preview-voice":
            voice = params.get("voice", ["en-US-ChristopherNeural"])[0]
            lang = params.get("lang", ["en"])[0]
            sample_text = "Hello, this is a studio voiceover test for YouTube Shorts."
            if lang == "ta":
                sample_text = "வணக்கம், இது யூடியூப் ஷார்ட்ஸ் தமிழ் குரல் சோதனை."

            temp_dir = os.path.join(os.getcwd(), "output", "temp_voice_preview")
            try:
                tts = generate_voiceover(
                    text=sample_text,
                    lang=lang,
                    output_dir=temp_dir,
                    custom_voice=voice
                )
                audio_file = tts["audio_path"]
                if os.path.isfile(audio_file):
                    self.send_response(200)
                    self.send_header("Content-Type", "audio/mpeg")
                    self.send_header("Content-Length", str(os.path.getsize(audio_file)))
                    self.end_headers()
                    with open(audio_file, "rb") as f:
                        self.wfile.write(f.read())
                    return
            except Exception as e:
                self.send_error(500, f"Voice preview error: {e}")
                return

        # 4. Job Status API
        if path == "/api/status":
            job_id = params.get("job_id", [""])[0]
            job = JOB_REGISTRY.get(job_id)
            if not job:
                self.send_error(404, "Job not found")
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(job).encode("utf-8"))
            return

        # 5. Video Stream API
        if path == "/api/video-stream":
            video_path = params.get("path", [""])[0]
            if os.path.isfile(video_path):
                self.serve_file(video_path, "video/mp4")
            else:
                self.send_error(404, "Video file not found")
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len > 0 else b"{}"
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            payload = {}

        # 1. Script Generator API
        if path == "/api/generate-script":
            topic = payload.get("topic", "")
            lang = payload.get("lang", "en")
            try:
                data = prepare_script(topic=topic, lang=lang)
                resp = {
                    "success": True,
                    "title": data.get("title", topic),
                    "hook": data.get("sentences", [""])[0] if data.get("sentences") else "",
                    "points": data.get("sentences", [])[1:-1] if len(data.get("sentences", [])) > 2 else [],
                    "cta": data.get("sentences", [])[-1] if len(data.get("sentences", [])) > 1 else "",
                    "tags": data.get("tags", [])
                }
            except Exception as e:
                resp = {"success": False, "error": str(e)}

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        # 2. Render Pipeline Job API
        if path == "/api/render":
            job_id = str(uuid.uuid4())[:8]
            JOB_REGISTRY[job_id] = {
                "id": job_id,
                "status": "queued",
                "logs": ["Job initialized in studio queue..."],
                "video_path": None,
                "video_url": None
            }

            # Spawn rendering thread
            threading.Thread(
                target=execute_render_job,
                args=(job_id, payload),
                daemon=True
            ).start()

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"job_id": job_id}).encode("utf-8"))
            return

        # 3. Film Screenplay Generator API
        if path == "/api/generate-screenplay":
            from shorts_creator.film_generator.screenplay import get_screenplay
            prompt = payload.get("prompt", "")
            lang = payload.get("lang", "en")
            style = payload.get("style", "anime_shinkai")
            num_scenes = int(payload.get("num_scenes", 4))
            try:
                screenplay = get_screenplay(prompt, lang=lang, style_key=style, num_scenes=num_scenes)
                resp = {"success": True, "screenplay": screenplay}
            except Exception as e:
                resp = {"success": False, "error": str(e)}

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        # 4. Animated Film Render Pipeline Job API
        if path == "/api/render-film":
            job_id = str(uuid.uuid4())[:8]
            JOB_REGISTRY[job_id] = {
                "id": job_id,
                "status": "queued",
                "logs": ["Film rendering job queued in studio..."],
                "video_path": None,
                "video_url": None
            }

            threading.Thread(
                target=execute_film_render_job,
                args=(job_id, payload),
                daemon=True
            ).start()

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"job_id": job_id}).encode("utf-8"))
            return

        self.send_error(404, "Not Found")

    def serve_file(self, file_path: str, content_type: str):
        file_size = os.path.getsize(file_path)
        range_header = self.headers.get("Range")

        if range_header:
            # Parse Range header for video seeking
            range_match = range_header.replace("bytes=", "").split("-")
            start = int(range_match[0])
            end = int(range_match[1]) if range_match[1] else file_size - 1
            length = (end - start) + 1

            self.send_response(206)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Content-Length", str(length))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()

            with open(file_path, "rb") as f:
                f.seek(start)
                self.wfile.write(f.read(length))
        else:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
            with open(file_path, "rb") as f:
                shutil.copyfileobj(f, self.wfile)


def execute_render_job(job_id: str, payload: Dict[str, Any]):
    job = JOB_REGISTRY[job_id]
    job["status"] = "running"
    
    def log(msg: str):
        job["logs"].append(f"[{time.strftime('%H:%M:%S')}] {msg}")

    try:
        topic = payload.get("topic", "Short")
        script = payload.get("script", "")
        lang = payload.get("lang", "en")
        voice = payload.get("voice")
        style = payload.get("style", "hormozi")
        bg_type = payload.get("bg_type", "space")
        bgm_vibe = payload.get("bgm_vibe", "ambient")
        progress_bar = payload.get("progress_bar", True)

        log("Step 1: Preparing script structure...")
        script_data = prepare_script(topic=topic, custom_script=script, lang=lang)
        detected_lang = script_data["language"]

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        workspace_dir = os.path.join(os.getcwd(), "output", f"session_web_{timestamp}")
        os.makedirs(workspace_dir, exist_ok=True)

        log(f"Step 2: Synthesizing studio {detected_lang.upper()} voiceover via neural TTS...")
        tts_data = generate_voiceover(
            text=script_data["full_text"],
            lang=detected_lang,
            output_dir=workspace_dir,
            custom_voice=voice
        )
        duration = tts_data["duration"]
        log(f"Voiceover completed ({duration:.1f}s) with exact speech timestamps.")

        log("Step 3: Generating word-by-word animated subtitles with HarfBuzz shaping...")
        ass_path = os.path.join(workspace_dir, "subtitles.ass")
        generate_ass_subtitles(
            sentences=script_data["sentences"],
            total_duration=duration,
            output_ass_path=ass_path,
            lang=detected_lang,
            style=style,
            boundaries=tts_data.get("boundaries", [])
        )

        final_bgm = None
        if bgm_vibe != "none":
            log(f"Step 4: Synthesizing {bgm_vibe} background music & audio ducking...")
            final_bgm = prepare_bgm_track(workspace_dir, duration, vibe=bgm_vibe)

        # Output path
        default_dir = get_default_output_dir()
        slug = f"short_{timestamp}"
        out_mp4 = os.path.join(default_dir, f"{slug}.mp4")

        log("Step 5: FFmpeg 1080x1920 vertical compositing & EBU R128 mastering...")
        assemble_shorts_video(
            voiceover_path=tts_data["audio_path"],
            subtitle_ass_path=ass_path,
            duration=duration,
            output_path=out_mp4,
            topic=topic,
            bg_type=bg_type,
            bgm_path=final_bgm,
            progress_bar=progress_bar
        )

        log(f"Rendering complete! Saved to {out_mp4}")
        job["status"] = "completed"
        job["video_path"] = out_mp4
        job["video_url"] = f"/api/video-stream?path={urllib.parse.quote(out_mp4)}"

    except Exception as e:
        log(f"ERROR: {str(e)}")
        job["status"] = "failed"


def execute_film_render_job(job_id: str, payload: Dict[str, Any]):
    from shorts_creator.film_generator import generate_animated_film
    job = JOB_REGISTRY[job_id]
    job["status"] = "running"

    def log_cb(msg: str, pct: float):
        job["logs"].append(f"[{time.strftime('%H:%M:%S')}] {msg}")

    try:
        prompt = payload.get("prompt", "")
        lang = payload.get("lang", "en")
        style = payload.get("style", "anime_shinkai")
        aspect = payload.get("aspect_ratio", "16:9")
        num_scenes = int(payload.get("num_scenes", 4))
        voice = payload.get("voice")
        bgm_vibe = payload.get("bgm_vibe", "ambient")

        res = generate_animated_film(
            prompt=prompt,
            lang=lang,
            style=style,
            aspect_ratio=aspect,
            num_scenes=num_scenes,
            voice=voice,
            bgm_vibe=bgm_vibe,
            progress_callback=log_cb
        )

        film_path = res["film_path"]
        job["logs"].append(f"[{time.strftime('%H:%M:%S')}] Film saved to {film_path}")
        job["status"] = "completed"
        job["video_path"] = film_path
        job["video_url"] = f"/api/video-stream?path={urllib.parse.quote(film_path)}"
    except Exception as e:
        job["logs"].append(f"[{time.strftime('%H:%M:%S')}] ERROR: {str(e)}")
        job["status"] = "failed"



def start_web_server(port: int = 8080, host: str = "0.0.0.0"):
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, ShortsWebHandler)
    url = f"http://localhost:{port}"
    print(f"\n🚀 ShortsCreator Web Studio is running live!")
    print(f"👉 Local Browser: {url}")
    print(f"👉 Mobile / Local Network: http://<your-device-ip>:{port}\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down ShortsCreator Web Studio.")
        httpd.server_close()


if __name__ == "__main__":
    start_web_server()
