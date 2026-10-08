import unittest

from canlog_stats import analyze_frames, parse_asc_lines


SAMPLE = """\
0.000000 1 123 Rx d 8 00 00 00 00 00 00 00 00
0.500000 1 123 Rx d 8 01 00 00 00 00 00 00 00
1.000000 1 123 Rx d 8 00 00 00 00 00 00 00 00
1.250000 1 123 Rx d 8 01 00 00 00 00 00 00 00
2.000000 1 123 Rx d 8 00 00 00 00 00 00 00 00
2.500000 1 123 Rx d 8 01 00 00 00 00 00 00 00
"""


class CanLogStatsTests(unittest.TestCase):
    def test_detects_timing_anomalies(self):
        frames = parse_asc_lines(SAMPLE.splitlines())
        result = analyze_frames(frames)
        self.assertEqual(result["frame_count"], 6)
        message = result["messages"][0]
        self.assertEqual(message["can_id"], "0x123")
        self.assertEqual(message["cycle"]["median_s"], 0.5)
        intervals = [entry["interval_s"] for entry in message["cycle"]["anomalies"]]
        self.assertEqual(intervals, [0.25, 0.75])


if __name__ == "__main__":
    unittest.main()
