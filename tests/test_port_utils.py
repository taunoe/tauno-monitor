import unittest
from types import SimpleNamespace

from src.port_utils import (
    describe_open_error,
    format_port_label,
    lookup_usb_names,
)


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


class LookupUsbNamesTests(unittest.TestCase):
    DB = {
        "1a86": {
            "name": " QinHeng Electronics",
            "products": {"7523": " CH340 serial converter"},
        },
    }

    def test_lookup_is_case_insensitive_and_strips_names(self):
        self.assertEqual(
            lookup_usb_names("1A86", "7523", self.DB),
            ("QinHeng Electronics", "CH340 serial converter"),
        )

    def test_unknown_product_and_vendor_return_none(self):
        self.assertEqual(
            lookup_usb_names("1a86", "FFFF", self.DB),
            ("QinHeng Electronics", None),
        )
        self.assertEqual(lookup_usb_names("FFFF", "0001", self.DB), (None, None))


class DescribeOpenErrorTests(unittest.TestCase):
    def test_known_errno_values_get_short_messages(self):
        self.assertIn(
            "No permission",
            describe_open_error("/dev/ttyUSB0", PermissionError(13, "denied")),
        )
        self.assertIn(
            "not found",
            describe_open_error("/dev/ttyUSB0", FileNotFoundError(2, "missing")),
        )
        self.assertIn(
            "in use",
            describe_open_error("/dev/ttyUSB0", OSError(16, "busy")),
        )

    def test_other_errors_keep_their_text(self):
        self.assertEqual(
            describe_open_error("/dev/ttyUSB0", ValueError("bad baud")),
            "Could not open /dev/ttyUSB0: bad baud",
        )


if __name__ == "__main__":
    unittest.main()
