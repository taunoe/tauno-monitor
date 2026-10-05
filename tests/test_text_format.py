import unittest

from src.text_format import strip_ansi_escape_codes, tx_line_ending


class StripAnsiEscapeCodesTests(unittest.TestCase):
    def test_removes_sgr_color_and_style_codes(self):
        text = "\x1b[31merror\x1b[1;4m!\x1b[0m"

        self.assertEqual(strip_ansi_escape_codes(text), "error!")

    def test_preserves_plain_text_and_non_sgr_escape_sequences(self):
        text = "plain \x1b[2J screen clear"

        self.assertEqual(strip_ansi_escape_codes(text), text)

    def test_transmit_line_ending_options(self):
        expected = {
            0: "\n",
            1: "\r",
            2: "\r\n",
            3: "",
        }

        for index, line_ending in expected.items():
            with self.subTest(index=index):
                self.assertEqual(tx_line_ending(index), line_ending)


if __name__ == "__main__":
    unittest.main()
