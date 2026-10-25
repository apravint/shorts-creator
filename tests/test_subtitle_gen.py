"""Tests for viral ASS subtitle generation and semantic emojis."""

import os
import tempfile
import unittest
from shorts_creator.subtitle_gen import (
    format_ass_time,
    split_into_bursts,
    get_word_emoji,
    get_palette_color,
    generate_ass_subtitles
)


class TestSubtitleGen(unittest.TestCase):
    def test_format_ass_time(self):
        self.assertEqual(format_ass_time(0.0), "0:00:00.00")
        self.assertEqual(format_ass_time(65.45), "0:01:05.45")
        self.assertEqual(format_ass_time(3661.12), "1:01:01.12")
        self.assertEqual(format_ass_time(-5.0), "0:00:00.00")

    def test_split_into_bursts(self):
        text = "Why Python GIL Removal Changes Everything In 2026"
        bursts = split_into_bursts(text, max_words=2)
        self.assertEqual(len(bursts), 4)
        self.assertEqual(bursts[0], ["Why", "Python"])
        self.assertEqual(bursts[1], ["GIL", "Removal"])

    def test_get_word_emoji(self):
        # English
        self.assertEqual(get_word_emoji("rocket"), "🚀")
        self.assertEqual(get_word_emoji("fire!"), "🔥")
        self.assertEqual(get_word_emoji("brain"), "🧠")
        # Tamil
        self.assertEqual(get_word_emoji("வெற்றி"), "🏆")
        self.assertEqual(get_word_emoji("நெருப்பு"), "🔥")
        # Unmatched
        self.assertEqual(get_word_emoji("regularword"), "")

    def test_get_palette_color(self):
        self.assertEqual(get_palette_color("hormozi"), "&H00FFFF&")
        self.assertEqual(get_palette_color("neon-green"), "&H00FF00&")
        self.assertEqual(get_palette_color("&HFF0000&"), "&HFF0000&")
        self.assertEqual(get_palette_color("#FF8800"), "&H0088FF&")

    def test_generate_ass_subtitles_file_creation(self):
        sentences = [
            "Welcome to the autonomous future.",
            "ShortsCreator AI is fully operational."
        ]
        with tempfile.NamedTemporaryFile(suffix=".ass", delete=False) as f:
            temp_path = f.name

        try:
            out_file = generate_ass_subtitles(
                sentences=sentences,
                total_duration=10.0,
                output_ass_path=temp_path,
                lang="en",
                style="neon_glow"
            )
            self.assertTrue(os.path.exists(out_file))
            with open(out_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("[Script Info]", content)
            self.assertIn("[V4+ Styles]", content)
            self.assertIn("Dialogue:", content)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
