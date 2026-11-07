"""Regression tests for defects that silently degraded rendered shorts."""

import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from shorts_creator.b_roll_engine import calculate_sentence_timings, split_beats_into_shots
from shorts_creator.script_gen import is_valid_script, get_procedural_template
from shorts_creator.soundscape import SoundscapeEngine
from shorts_creator.subtitle_gen import clean_caption_word, get_word_emoji, build_hook_event
from shorts_creator.text_match import has_term
from shorts_creator.tts_engine import try_edge_tts_with_boundaries
from shorts_creator.video_engine import build_progress_bar_graph
from shorts_creator.video_fetcher import extract_search_category
from shorts_creator.web import is_servable_video


def _tone(path, freq, seconds=3):
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"sine=frequency={freq}:duration={seconds}", path],
        check=True
    )


class TestAudioMix(unittest.TestCase):
    def test_music_and_sfx_survive_the_mix(self):
        # Wrong input indexes used to fail the mix and silently ship a narration-only track
        with tempfile.TemporaryDirectory() as d:
            voice, music, out = [os.path.join(d, n) for n in ("v.mp3", "m.mp3", "out.aac")]
            _tone(voice, 440)
            _tone(music, 200)
            with patch("builtins.print") as printed:
                SoundscapeEngine.mix_master_soundscape(
                    voice, music, out, duration=3.0, ambient_vibe="wind", cut_timestamps=[1.5], work_dir=d
                )
            self.assertFalse(any("Audio mix failed" in str(c) for c in printed.call_args_list))
            codec = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name", "-of", "csv=p=0", out],
                capture_output=True, text=True, check=True
            ).stdout.strip()
            self.assertEqual(codec, "aac")


class TestLoudness(unittest.TestCase):
    def test_master_reaches_shorts_target(self):
        with tempfile.TemporaryDirectory() as d:
            quiet, out = os.path.join(d, "quiet.wav"), os.path.join(d, "out.aac")
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=300:duration=6",
                 "-af", "volume=0.05", quiet],
                check=True
            )
            SoundscapeEngine.master_loudness(quiet, out)
            report = subprocess.run(
                ["ffmpeg", "-i", out, "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                capture_output=True, text=True
            ).stderr
            integrated = float(report.rsplit("I:", 1)[1].split("LUFS")[0])
            self.assertAlmostEqual(integrated, -14.0, delta=1.0)


class TestWordBoundaries(unittest.IsolatedAsyncioTestCase):
    async def test_word_boundaries_are_requested_from_edge_tts(self):
        # edge-tts 7.x defaults to SentenceBoundary, which discarded the neural voice for gTTS
        with patch("shorts_creator.tts_engine.edge_tts.Communicate", side_effect=RuntimeError("stop")) as comm:
            with tempfile.TemporaryDirectory() as d, patch("builtins.print"):
                await try_edge_tts_with_boundaries("hello there", "en-US-GuyNeural", os.path.join(d, "a.mp3"))
        self.assertEqual(comm.call_args.kwargs.get("boundary"), "WordBoundary")


class TestEdgeRetry(unittest.TestCase):
    def test_transient_edge_failure_is_retried_before_gtts(self):
        attempts = []

        async def flaky(text, voice, path, rate="+0%", pitch="+0Hz"):
            attempts.append(1)
            if len(attempts) == 1:
                return False, []
            with open(path, "wb") as f:
                f.write(b"0" * 9000)
            return True, [{"word": "hi", "start": 0.0, "end": 0.5}]

        with tempfile.TemporaryDirectory() as d, \
                patch("shorts_creator.tts_engine.try_edge_tts_with_boundaries", side_effect=flaky), \
                patch("shorts_creator.tts_engine.synthesize_with_gtts") as gtts, \
                patch("shorts_creator.tts_engine.get_audio_duration", return_value=1.0), \
                patch("shorts_creator.tts_engine.time.sleep"):
            from shorts_creator.tts_engine import generate_voiceover
            result = generate_voiceover("hi", lang="en", output_dir=d)
        self.assertEqual(len(attempts), 2)
        gtts.assert_not_called()
        self.assertIn("Edge-TTS", result["voice"])


class TestMontageTiming(unittest.TestCase):
    def test_timings_follow_speech_boundaries(self):
        sentences = ["one two", "three four five six"]
        boundaries = [
            {"word": w, "start": float(i * 2), "end": float(i * 2 + 1)}
            for i, w in enumerate("one two three four five six".split())
        ]
        beats = calculate_sentence_timings(sentences, 12.0, boundaries=boundaries)
        self.assertEqual(beats[0]["start"], 0.0)
        self.assertEqual(beats[1]["start"], 4.0)
        self.assertEqual(beats[1]["end"], 12.0)

    def test_long_beats_split_into_short_shots(self):
        shots = split_beats_into_shots([{"index": 1, "text": "a", "duration": 7.0}], max_shot=3.0)
        self.assertEqual(len(shots), 3)
        self.assertLessEqual(max(s["duration"] for s in shots), 3.0)
        self.assertEqual([s["starts_beat"] for s in shots], [True, False, False])


class TestProgressBar(unittest.TestCase):
    def test_bar_grows_over_time(self):
        # drawbox cannot animate: the old bar was full from the first frame
        graph = build_progress_bar_graph("null", 2.0, "0xFF0000", 10, 64, thickness=8)
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "f_%d.rgb")
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "color=black:s=64x64:d=2:r=10",
                 "-vf", graph, "-pix_fmt", "rgb24", "-f", "image2", "-vcodec", "rawvideo", out],
                check=True
            )

            def lit(frame):
                with open(os.path.join(d, f"f_{frame}.rgb"), "rb") as f:
                    row = f.read()[63 * 64 * 3:]
                return sum(1 for i in range(0, len(row), 3) if row[i] > 128)

            self.assertLess(lit(2), lit(18))
            self.assertLess(lit(2), 16)


class TestTextRules(unittest.TestCase):
    def test_terms_match_whole_latin_words(self):
        self.assertFalse(has_term("heavy rain on the mountain", ["ai"]))
        self.assertTrue(has_term("how ai works", ["ai"]))
        self.assertTrue(has_term("தமிழ்நாட்டில்", ["தமிழ்"]))

    def test_category_follows_the_strongest_match(self):
        self.assertEqual(extract_search_category("dark rogue planet drifting in space"), "space")
        self.assertEqual(extract_search_category("milky way galaxy from earth night sky"), "space")

    def test_template_choice_ignores_substrings(self):
        self.assertEqual(
            get_procedural_template("mountain rain", "en"),
            get_procedural_template("anything else", "en")
        )

    def test_emoji_ignores_english_substrings(self):
        self.assertEqual(get_word_emoji("thinking"), "")
        self.assertEqual(get_word_emoji("start"), "")

    def test_caption_words_are_safe_and_clean(self):
        self.assertEqual(clean_caption_word("galaxy,"), "GALAXY")
        self.assertEqual(clean_caption_word("{\\b1}why?"), "B1WHY?")

    def test_hook_event_has_two_lines(self):
        event = build_hook_event("Space is not silent", "&H00FFFF&")
        self.assertIn("SPACE IS\\N", event)
        self.assertEqual(build_hook_event("  ", "&H00FFFF&"), "")

    def test_incomplete_model_response_is_rejected(self):
        self.assertFalse(is_valid_script({"hook": "x", "cta": "y"}))
        self.assertFalse(is_valid_script({"hook": "x", "cta": "y", "points": []}))
        self.assertTrue(is_valid_script({"hook": "x", "cta": "y", "points": ["z"]}))


class TestWebStreaming(unittest.TestCase):
    def test_only_generated_videos_are_served(self):
        self.assertFalse(is_servable_video("/etc/passwd"))
        with tempfile.NamedTemporaryFile(suffix=".mp4") as outside:
            self.assertFalse(is_servable_video(outside.name))
        with tempfile.TemporaryDirectory() as d, patch("shorts_creator.web.os.getcwd", return_value=d):
            os.makedirs(os.path.join(d, "output"))
            video = os.path.join(d, "output", "a.mp4")
            open(video, "wb").close()
            self.assertTrue(is_servable_video(video))
            self.assertFalse(is_servable_video(os.path.join(d, "output", "..", "output", "a.txt")))


if __name__ == "__main__":
    unittest.main()
