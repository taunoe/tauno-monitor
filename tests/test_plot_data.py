import unittest

from src.plot_data import SerialPlotData


class SerialPlotDataTests(unittest.TestCase):
    def setUp(self):
        self.plot = SerialPlotData()

    def test_parses_supported_reading_formats_and_separators(self):
        updated = self.plot.feed(
            b"temperature: 21.5,pressure=1.02\nvoltage 3.3;offset: -2\r"
        )

        self.assertTrue(updated)
        self.assertEqual(list(self.plot.series["temperature"]), [21.5])
        self.assertEqual(list(self.plot.series["pressure"]), [1.02])
        self.assertEqual(list(self.plot.series["voltage"]), [3.3])
        self.assertEqual(list(self.plot.series["offset"]), [-2.0])

    def test_reading_can_span_multiple_input_chunks(self):
        self.assertFalse(self.plot.feed(b"temperature: 2"))
        self.assertTrue(self.plot.feed(b"1.5\n"))

        self.assertEqual(list(self.plot.series["temperature"]), [21.5])

    def test_ignores_invalid_and_non_finite_readings(self):
        updated = self.plot.feed(
            b"missing-value:,invalid: nope,nan: NaN,infinity: inf,"
            b"bad-utf8: \xff,valid: 4\n"
        )

        self.assertTrue(updated)
        self.assertEqual(list(self.plot.series), ["valid"])
        self.assertEqual(list(self.plot.series["valid"]), [4.0])

    def test_discards_overlong_readings_until_separator(self):
        self.plot.feed(b"x" * (self.plot.MAX_LINE_BYTES + 1) + b": 1,good: 2\n")

        self.assertEqual(list(self.plot.series), ["good"])
        self.assertEqual(list(self.plot.series["good"]), [2.0])

    def test_limits_series_count_and_retains_only_recent_samples(self):
        for index in range(self.plot.MAX_SERIES):
            self.plot.feed(f"series{index}: 0\n".encode())
        self.plot.feed(b"overflow: 1\n")

        self.assertNotIn("overflow", self.plot.series)
        for sample in range(self.plot.MAX_SAMPLES + 3):
            self.plot.feed(f"series0: {sample}\n".encode())

        self.assertEqual(len(self.plot.series["series0"]), self.plot.MAX_SAMPLES)
        self.assertEqual(
            self.plot.series["series0"][0],
            3,
        )
        self.assertEqual(self.plot.series["series0"][-1], self.plot.MAX_SAMPLES + 2)

    def test_clear_removes_series_and_partial_input(self):
        self.plot.feed(b"temperature: 2")
        self.plot.clear()

        self.assertFalse(self.plot.series)
        self.assertFalse(self.plot.feed(b"1.5\n"))
        self.assertFalse(self.plot.series)


if __name__ == "__main__":
    unittest.main()
