# File:    tool_baud.py
# Author:  Tauno Erik
# Started: 16.07.2025
# Edited:  17.07.2025
# Find the baud rate

from gi.repository import Adw, Gtk, Gio, GObject, GLib, Gdk
import serial
import time

@Gtk.Template(resource_path='/art/taunoerik/tauno-monitor/tool_baud.ui')
class TaunoToolBaudWindow(Adw.Window):
    __gtype_name__ = 'TaunoToolBaudWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.port = '/dev/ttyACM0'

        self.COMMON_BAUD_RATES = [50, 75, 110, 134, 150, 200, 300, 600, 750,
            1200, 1800, 2400, 4800, 7200, 9600, 14400, 19200, 28800, 31250,
            38400, 56000, 57600, 74880, 76800, 115200, 115600, 128000, 230400,
            250000, 256000, 460800, 500000, 576000, 921600, 1000000, 1152000,
            1500000, 2000000, 2500000, 3000000, 3500000, 4000000]

    @Gtk.Template.Callback()
    def on_button_close_clicked(self, button):
        self.destroy()

    @Gtk.Template.Callback()
    def on_find_baud_rate(self, button):
        scores = []

        # Scan Baud Rates
        for baud in self.COMMON_BAUD_RATES:
            score, example_lines = self.try_baud_rate(self.port, baud)
            scores.append((score, baud, example_lines))

        # Find best
        best = max(scores, key=lambda x: x[0])
        score, baud, lines = best
        print("\nBest match:")
        print(f"{baud} with {score} valid lines")
        # Print valid lines
        for line in lines:
            print(f"  {line.decode('utf-8', errors='ignore').strip()}")

        return baud


    def try_baud_rate(self, port, baudrate, timeout=2.0):
        print(f"Trying {baudrate} baud...")

        try:
            with serial.Serial(port, baudrate, timeout=timeout) as ser:
                time.sleep(1.5)  # wait for Arduino reset
                buffer = b""
                good_lines = []
                start_time = time.time()
                score = 0

                while time.time() - start_time < timeout:
                    chunk = ser.read(180)  # read small chunk
                    if chunk:
                        buffer += chunk
                        while b'\n' in buffer:
                            line, buffer = buffer.split(b'\n', 1)
                            print(f"line: {line}")
                            line = line.strip(b'\r')
                            if line:
                                if line.isascii():
                                    score += 1
                                good_lines.append(line + b'\n')  # re-add newline
                    else:
                        time.sleep(0.01)  # avoid busy loop

                return score, good_lines[:5]  # return a few examples too
        except Exception as e:
            print(f"Error at {baudrate} baud: {e}")
            return 0, []



    @Gtk.Template.Callback()
    def on_set_baud_rate(self, buttom):
        print("on_set_baud_rate")

