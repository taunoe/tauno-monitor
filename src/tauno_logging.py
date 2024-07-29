# tauno_logging.py
# Tauno Erik
# 29.07.2024

from datetime import datetime

class TaunoLogging():

    def __init__(self, window_reference):
        self.window_reference = window_reference
        self.file_path = ''
        self.file_handle = None


    def create_file(self, file_path):
        """ Creates log file. Returns True if successful. """
        self.file_path = file_path
        try:
            open(self.log_file_path, "x")
            # self.write_data('')
            return True
        except:
            return False


    def write_data(self, data):
        """ Writes data to log file. Adds start time. """
        if self.window_reference.write_logs:
            # Open the file the first time the method is called
            if self.file_handle is None:
                self.file_handle = open(self.file_path, 'a')
                # Write start time
                current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                self.write_data("Tauno-Monitor log started: " + current_datetime + "\n")

            # Write data to the file
            self.file_handle.write(data)


    def close_file(self):
        """ Closes log file. Adds end time, """
        # Write end time
        current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.write_data("Tauno-Monitor log ended: " + current_datetime + "\n\n")
        # Close file
        if self.file_handle is not None:
            self.file_handle.close()
            self.file_handle = None

