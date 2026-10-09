import unittest

from src.text_format import encode_tx_data, strip_ansi_escape_codes, tx_line_ending


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
            3: ";",
            4: "",
        }

        for index, line_ending in expected.items():
            with self.subTest(index=index):
                self.assertEqual(tx_line_ending(index), line_ending)


class EncodeTxDataTests(unittest.TestCase):
    def test_encodes_supported_transmit_formats(self):
        examples = (
            ("ASCII", "Hello", b"Hello"),
            ("ASCII", "café", "café".encode("utf-8")),
            ("HEX", "48 65 6c 6c 6f", b"Hello"),
            ("HEX", "0x48,0x69", b"Hi"),
            ("BIN", "01001000 01101001", b"Hi"),
            ("BIN", "0100100001101001", b"Hi"),
            ("DEC", "72, 105", b"Hi"),
            ("OCT", "110 151", b"Hi"),
            ("HEX", "", b""),
        )

        for data_format, data, expected in examples:
            with self.subTest(data_format=data_format, data=data):
                self.assertEqual(encode_tx_data(data, data_format), expected)

    def test_rejects_invalid_or_out_of_range_transmit_values(self):
        examples = (
            ("HEX", "1"),
            ("HEX", "gg"),
            ("BIN", "0100000"),
            ("BIN", "0100000x"),
            ("DEC", "256"),
            ("DEC", "-1"),
            ("OCT", "400"),
            ("OCT", "8"),
            ("UNKNOWN", "1"),
        )

        for data_format, data in examples:
            with self.subTest(data_format=data_format, data=data):
                with self.assertRaises(ValueError):
                    encode_tx_data(data, data_format)


if __name__ == "__main__":
    unittest.main()
