import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import serial

from src import tauno_serial
from src.tauno_serial import TaunoSerial


class TaunoSerialTests(unittest.TestCase):
    def setUp(self):
        self.window = SimpleNamespace(
            get_data_bit_saved=3,
            get_parity_saved=0,
            get_stop_bit_saved=0,
            get_rx_format_saved="ASCII",
            get_RX_line_end_saved=0,
        )
        self.device = Mock()
        self.device.is_open = False
        self.device.open.side_effect = self.mark_open
        self.device.close.side_effect = self.mark_closed
        self.serial_patch = patch.object(tauno_serial.serial, "Serial", return_value=self.device)
        self.serial_patch.start()
        self.addCleanup(self.serial_patch.stop)
        self.connection = TaunoSerial(self.window)

    def mark_open(self):
        self.device.is_open = True

    def mark_closed(self):
        self.device.is_open = False

    def test_open_applies_serial_settings_and_resets_input(self):
        self.window.get_data_bit_saved = 2
        self.window.get_parity_saved = 2
        self.window.get_stop_bit_saved = 1

        self.connection.open("/dev/fake", 115200)

        self.assertEqual(self.device.port, "/dev/fake")
        self.assertEqual(self.device.baudrate, 115200)
        self.assertEqual(self.device.bytesize, serial.SEVENBITS)
        self.assertEqual(self.device.parity, serial.PARITY_ODD)
        self.assertEqual(self.device.stopbits, serial.STOPBITS_ONE_POINT_FIVE)
        self.device.reset_input_buffer.assert_called_once_with()
        self.assertTrue(self.connection.is_open)

    def test_open_maps_all_supported_line_configurations(self):
        byte_sizes = (
            serial.FIVEBITS,
            serial.SIXBITS,
            serial.SEVENBITS,
            serial.EIGHTBITS,
        )
        parities = (
            serial.PARITY_NONE,
            serial.PARITY_EVEN,
            serial.PARITY_ODD,
            serial.PARITY_MARK,
            serial.PARITY_SPACE,
        )
        stop_bits = (
            serial.STOPBITS_ONE,
            serial.STOPBITS_ONE_POINT_FIVE,
            serial.STOPBITS_TWO,
        )

        for index, expected in enumerate(byte_sizes):
            with self.subTest(setting="bytesize", index=index):
                self.window.get_data_bit_saved = index
                self.connection.open("/dev/fake", 9600)
                self.assertEqual(self.device.bytesize, expected)
                self.connection.close()
        for index, expected in enumerate(parities):
            with self.subTest(setting="parity", index=index):
                self.window.get_parity_saved = index
                self.connection.open("/dev/fake", 9600)
                self.assertEqual(self.device.parity, expected)
                self.connection.close()
        for index, expected in enumerate(stop_bits):
            with self.subTest(setting="stopbits", index=index):
                self.window.get_stop_bit_saved = index
                self.connection.open("/dev/fake", 9600)
                self.assertEqual(self.device.stopbits, expected)
                self.connection.close()

    def test_close_updates_connection_state(self):
        self.connection.open("/dev/fake", 9600)

        self.connection.close()

        self.assertFalse(self.connection.is_open)
        self.device.close.assert_called_once_with()

    def test_write_filters_controls_and_caps_payload_length(self):
        self.connection.open("/dev/fake", 9600)

        self.connection.write("hello\x00\nworld")
        self.device.write.assert_called_once_with(b"hello\nworld")
        self.device.flush.assert_called_once_with()

        self.device.write.reset_mock()
        self.connection.write("x" * 1025)
        self.assertEqual(self.device.write.call_args.args[0], b"x" * 1024)

    def test_write_does_nothing_when_port_is_closed(self):
        self.connection.write("hello")

        self.device.write.assert_not_called()
        self.device.flush.assert_not_called()

    def test_read_uses_selected_line_ending_and_dispatches_data(self):
        callback = Mock()
        self.window.add_to_text_view = callback

        def read_until(expected):
            self.assertEqual(expected, b"\r\n")
            self.connection.is_open = False
            return b"data\r\n"

        self.device.is_open = True
        self.connection.is_open = True
        self.device.read_until.side_effect = read_until

        with patch.object(tauno_serial.GLib, "idle_add", return_value=0) as idle_add:
            self.window.get_RX_line_end_saved = 2
            self.connection.read()

        idle_add.assert_called_once_with(callback, b"data\r\n")

    def test_hex_read_reads_one_byte_without_line_terminator(self):
        self.window.get_rx_format_saved = "HEX"
        self.device.is_open = True
        self.connection.is_open = True
        self.device.read.side_effect = lambda: self.stop_after_read(b"\xff")
        self.window.add_to_text_view = Mock()

        with patch.object(tauno_serial.GLib, "idle_add", return_value=0) as idle_add:
            self.connection.read()

        self.device.read.assert_called_once_with()
        self.device.read_until.assert_not_called()
        idle_add.assert_called_once_with(self.window.add_to_text_view, b"\xff")

    def stop_after_read(self, data):
        self.connection.is_open = False
        return data


if __name__ == "__main__":
    unittest.main()
