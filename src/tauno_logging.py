# tauno_logging.py
# Tauno Erik
# 28.07.2024

from datetime import datetime

class TaunoLogging():

    def __init__(self, window_reference):
        self.window_reference = window_reference
        self.file_path = ''
        self.file_handle = None


    def write_data(self, data):
        if self.file_handle is None:
            # Open the file the first time the method is called
            self.file_handle = open(self.file_path, 'a')

        # Write data to the file
        self.file_handle.write(data + '\n')


    def close_file(self):
        if self.file_handle is not None:
            self.file_handle.close()
            self.file_handle = None

