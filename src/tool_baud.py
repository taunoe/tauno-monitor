# File:    tool_baud.py
# Author:  Tauno Erik
# Started: 16.07.2025
# Edited:  18.07.2025
# Find the baud rate

from gi.repository import Adw, Gtk, Gio, GObject, GLib, Gdk
import threading
import serial
import time
import gettext
_ = gettext.gettext
import locale
import os

@Gtk.Template(resource_path='/art/taunoerik/tauno-monitor/tool_baud.ui')
class TaunoToolBaudWindow(Adw.Window):
    __gtype_name__ = 'TaunoToolBaudWindow'

    message_label = Gtk.Template.Child()
    scan_button = Gtk.Template.Child()
    use_button = Gtk.Template.Child()
    progress_bar = Gtk.Template.Child()

    def __init__(self, window_reference, **kwargs):
        super().__init__(**kwargs)

        self.window_reference = window_reference

        self.port = self.window_reference.settings.get_string("port-str")
        print(f"todo {self.port}")

        self.event = threading.Event()

        self.scores = []
        self.best_baud = None

    """
    @Gtk.Template.Callback()
    def on_button_close_clicked(self, button):
        self.destroy()
    """

    @Gtk.Template.Callback()
    def on_find_baud_rate(self, button):
        # Disable Scan button
        self.scan_button.set_sensitive(False)
        thread = threading.Thread(target=self.find_baud_rate)
        thread.daemon = True
        thread.start()

    def find_baud_rate(self):
        self.scores.clear()
        total = len(self.window_reference.COMMON_BAUD_RATES)

        # Scan Baud Rates
        for index, baud in enumerate(self.window_reference.COMMON_BAUD_RATES):
           self.try_baud_rate(self.port, baud)

           # Update progress bar
           fraction = (index + 1) / total
           GLib.idle_add(self.progress_bar.set_fraction, fraction)
           GLib.idle_add(self.progress_bar.set_show_text, True)
           GLib.idle_add(self.progress_bar.set_text, f"{int(fraction * 100)}%")
        # Done
        GLib.idle_add(self.progress_bar.set_text, _("Done"))
        GLib.idle_add(self.progress_bar.set_fraction, 1.0)

        # Find best
        best = max(self.scores, key=lambda x: x[0])
        score, baud, lines = best
        self.message_label.set_label(_(f"Best match: {baud} baud"))
        print("\nBest match:")
        print(f"{baud} with {score} valid lines")
        # Print valid lines
        for line in lines:
            print(f"  {line.decode('utf-8', errors='ignore').strip()}")

        self.best_baud = baud
        #Enable Scan button
        self.scan_button.set_sensitive(True)
        self.scan_button.remove_css_class("suggested-action")
        self.use_button.set_sensitive(True)
        self.use_button.add_css_class("suggested-action")
        return


    def try_baud_rate(self, port, baudrate, timeout=2.0):
        GLib.idle_add(self.message_label.set_label, _(f"Trying {baudrate} baud..."))
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

                #return score, good_lines[:5]  # return a few examples too
                self.scores.append((score, baudrate, good_lines[:5]))
        except Exception as e:
            print(f"Error at {baudrate} baud: {e}")
            self.message_label.set_label(_(f"Connect the device to the port!"))
            #return 0, []
            self.scores.append((0, baudrate, []))



    @Gtk.Template.Callback()
    def on_set_baud_rate(self, buttom):
        print("on_set_baud_rate")

        if self.best_baud in self.window_reference.COMMON_BAUD_RATES:
            pos = self.window_reference.COMMON_BAUD_RATES.index(self.best_baud)
            self.window_reference.baud_drop_down.set_selected(pos)
        # Close window
        self.destroy()
