import os
import tempfile
import unittest

from src.tauno_logging import TaunoLogging


class WindowReference:
    write_logs = True


class TaunoLoggingTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.window = WindowReference()
        self.logger = TaunoLogging(self.window)
        self.addCleanup(self.logger.cleanup)

    def create_log_file(self, name="monitor.log"):
        path = os.path.join(self.temp_dir.name, name)
        self.assertTrue(self.logger.create_file(path))
        return path

    def test_create_file_is_exclusive(self):
        path = self.create_log_file()

        self.assertFalse(self.logger.create_file(path))
        self.assertTrue(os.path.isfile(path))

    def test_allows_log_file_in_user_selected_folder_outside_home(self):
        selected_folder = os.path.join(self.temp_dir.name, "selected-folder")
        os.mkdir(selected_folder)
        path = os.path.join(selected_folder, "monitor.log")

        self.assertTrue(self.logger.create_file(path))
        self.assertTrue(os.path.isfile(path))

    def test_write_data_adds_start_and_end_markers(self):
        path = self.create_log_file()

        self.logger.write_data("received data\n")
        self.logger.close_file()

        with open(path, encoding="utf-8") as log_file:
            contents = log_file.read()
        self.assertIn("Tauno-Monitor log started: ", contents)
        self.assertIn("received data\n", contents)
        self.assertIn("Tauno-Monitor log ended: ", contents)
        self.assertIsNone(self.logger.file_handle)

    def test_hex_data_wraps_after_sixteen_bytes(self):
        path = self.create_log_file()

        for value in range(16):
            self.logger.write_hex_data(f"{value:02x}")
        self.logger.close_file()

        with open(path, encoding="utf-8") as log_file:
            contents = log_file.read()
        hex_data = contents.split("started: ", 1)[1].split("\n", 1)[1]
        self.assertIn("0e 0f \n", hex_data)
        self.assertEqual(self.logger.hex_counter, 0)

    def test_disabled_logging_does_not_open_or_write(self):
        path = self.create_log_file()
        self.window.write_logs = False

        self.logger.write_data("ignored")
        self.logger.write_hex_data("ff")

        self.assertIsNone(self.logger.file_handle)
        with open(path, encoding="utf-8") as log_file:
            self.assertEqual(log_file.read(), "")


if __name__ == "__main__":
    unittest.main()
