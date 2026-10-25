"""Tests for the B-roll sentence timing and montage synchronization engine."""

import unittest
from shorts_creator.b_roll_engine import calculate_sentence_timings


class TestBRollEngine(unittest.TestCase):
    def test_calculate_sentence_timings_empty(self):
        timings = calculate_sentence_timings([], 15.0)
        self.assertEqual(len(timings), 1)
        self.assertEqual(timings[0]["duration"], 15.0)

    def test_calculate_sentence_timings_proportional(self):
        sentences = [
            "This is the first sentence.",
            "This is the second longer sentence that takes more time.",
            "Short final call to action."
        ]
        total_duration = 18.0
        timings = calculate_sentence_timings(sentences, total_duration)

        self.assertEqual(len(timings), len(sentences))
        # Total sum should cover the video duration
        self.assertAlmostEqual(timings[-1]["end"], total_duration, places=1)
        # Ensure sequential order
        for i in range(len(timings) - 1):
            self.assertLessEqual(timings[i]["start"], timings[i]["end"])
            self.assertLessEqual(timings[i]["end"], timings[i + 1]["start"] + 0.1)


if __name__ == "__main__":
    unittest.main()
