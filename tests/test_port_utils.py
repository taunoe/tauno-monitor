import unittest
from types import SimpleNamespace

from src.port_utils import format_port_label


class FormatPortLabelTests(unittest.TestCase):
    def test_includes_device_and_product_without_manufacturer(self):
        port = SimpleNamespace(
            device="/dev/ttyACM0",
            manufacturer="Arduino LLC",
            product="Arduino Uno",
            description="Arduino Uno",
        )

        self.assertEqual(
            format_port_label(port),
            "/dev/ttyACM0\nArduino Uno",
        )

    def test_uses_description_when_usb_identity_is_missing(self):
        port = SimpleNamespace(
            device="/dev/ttyUSB0",
            manufacturer=None,
            product=None,
            description="USB Serial",
        )

        self.assertEqual(format_port_label(port), "/dev/ttyUSB0\nUSB Serial")

    def test_falls_back_to_device_when_no_identity_is_available(self):
        port = SimpleNamespace(
            device="/dev/ttyUSB0",
            manufacturer=None,
            product=None,
            description="/dev/ttyUSB0",
        )

        self.assertEqual(format_port_label(port), "/dev/ttyUSB0")

    def test_does_not_include_manufacturer_when_product_is_available(self):
        port = SimpleNamespace(
            device="/dev/ttyACM0",
            manufacturer="Arduino",
            product="Arduino",
            description="Arduino",
        )

        self.assertEqual(format_port_label(port), "/dev/ttyACM0\nArduino")


if __name__ == "__main__":
    unittest.main()
