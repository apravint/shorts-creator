"""Tests for the TTS and voice resolution engine."""

import unittest
from unittest.mock import patch
from shorts_creator.tts_engine import (
    resolve_voice_identifier,
    get_default_voice,
    get_audio_duration,
    VOICE_MAP,
    VOICE_ALIASES
)


class TestTTSEngine(unittest.TestCase):
    def test_get_default_voice(self):
        ta_voice = get_default_voice("ta")
        self.assertIn("ta-", ta_voice)

        en_voice = get_default_voice("en")
        self.assertIn("en-", en_voice)

    def test_resolve_voice_identifier_aliases(self):
        # Test known aliases
        self.assertEqual(resolve_voice_identifier("jarvis", "en"), "en-US-ChristopherNeural")
        self.assertEqual(resolve_voice_identifier("samantha", "en"), "en-US-JennyNeural")
        self.assertEqual(resolve_voice_identifier("pallavi", "ta"), "ta-IN-PallaviNeural")
        self.assertEqual(resolve_voice_identifier("valluvar", "ta"), "ta-IN-ValluvarNeural")

    def test_resolve_voice_identifier_full_tag(self):
        full_tag = "en-US-AvaMultilingualNeural"
        self.assertEqual(resolve_voice_identifier(full_tag, "en"), full_tag)

    def test_resolve_voice_identifier_none_fallback(self):
        res = resolve_voice_identifier(None, "ta")
        self.assertEqual(res, get_default_voice("ta"))

    @patch("subprocess.run")
    def test_get_audio_duration_success(self, mock_run):
        mock_run.return_value.stdout = "24.500\n"
        dur = get_audio_duration("dummy.mp3")
        self.assertAlmostEqual(dur, 24.5)

    @patch("subprocess.run", side_effect=Exception("ffprobe missing"))
    def test_get_audio_duration_fallback(self, mock_run):
        dur = get_audio_duration("non_existent.mp3")
        self.assertEqual(dur, 30.0)


if __name__ == "__main__":
    unittest.main()
