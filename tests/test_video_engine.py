"""Tests for video compositing and hardware-accelerated encoder detection."""

import unittest
from shorts_creator.video_engine import (
    detect_optimal_video_encoder,
    probe_hardware_encoder,
    build_procedural_background_filter
)


class TestVideoEngine(unittest.TestCase):
    def test_probe_hardware_encoder_invalid(self):
        # A nonexistent encoder must return False cleanly without throwing
        res = probe_hardware_encoder("nonexistent_fake_encoder_xyz")
        self.assertFalse(res)

    def test_detect_optimal_video_encoder_cpu_fallback(self):
        enc_name, enc_flags = detect_optimal_video_encoder("cpu")
        self.assertEqual(enc_name, "libx264")
        self.assertIn("-c:v", enc_flags)
        self.assertIn("libx264", enc_flags)

    def test_detect_optimal_video_encoder_auto(self):
        enc_name, enc_flags = detect_optimal_video_encoder("auto")
        self.assertIsInstance(enc_name, str)
        self.assertIsInstance(enc_flags, list)
        self.assertIn("-c:v", enc_flags)

    def test_build_procedural_background_filter(self):
        f_cyber = build_procedural_background_filter("cyber", 10.0, 1080, 1920)
        self.assertIn("gradients=", f_cyber)
        self.assertIn("vignette=", f_cyber)
        self.assertIn("s=1080x1920", f_cyber)

        f_fire = build_procedural_background_filter("fire", 5.0, 1080, 1920)
        self.assertIn("d=5.0", f_fire)


if __name__ == "__main__":
    unittest.main()
