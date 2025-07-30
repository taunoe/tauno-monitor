# File:    tauno_logging.py
# Author:  Tauno Erik
# Started: 29.07.2024
# Edited:  19.07.2025

from datetime import datetime

class TaunoLogging():

    def __init__(self, window_reference):
        self.window_reference = window_reference
        self.log_file_path = ''
        self.file_handle = None
        self.hex_counter = 0


    def create_file(self, file_path):
        """ Creates log file. Returns True if successful. """
        print("log:create_file()")

        self.log_file_path = file_path

        try:
            open(self.log_file_path, "x")
            print(f"logfile:{self.log_file_path}")
            return True
        except Exception as e:
            print(f"Error creating file: {e}")
            return False


    def write_data(self, data):
        """ Writes data to log file. Adds start time. """
        #print("log:write_data()")
        if self.window_reference.write_logs:
            # Open the file the first time the method is called
            if self.file_handle is None:
                try:
                    self.file_handle = open(self.log_file_path, 'a')
                    # Write start time
                    current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                    self.write_data("Tauno-Monitor log started: " + current_datetime + "\n")
                except Exception as e:
                    print(f"Error writing data: {e}")
            else:
                print("else:self.file_handle is None")

            # Write data to the file
            self.file_handle.write(data)
            print(f"log write data: {data}")
        else:
            pass
            #print("else:self.window_reference.write_logs")


    def write_hex_data(self, data):
        """ Write HEX data in a nice format """

        print("log:write_hex_data()")

        if self.window_reference.write_logs:
            # Open the file the first time the method is called
            if self.file_handle is None:
                self.file_handle = open(self.log_file_path, 'a')
                # Write start time
                current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                self.write_data("Tauno-Monitor log started: " + current_datetime + "\n")
            # Write data to the file
            self.file_handle.write(data)
            self.file_handle.write(' ')
            self.hex_counter += 1
            if self.hex_counter == 16:
                self.file_handle.write('\n')
                self.hex_counter = 0

    def close_file(self):
        """ Closes log file. Adds end time, """

        print("log:close_file()")

        # Write end time
        current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.write_data("\nTauno-Monitor log ended: " + current_datetime + "\n\n")
        # Close file
        if self.file_handle is not None:
            self.file_handle.close()
            self.file_handle = None

