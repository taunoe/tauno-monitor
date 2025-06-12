# tauno_serial.py
# Tauno Erik
# 12.06.2025

import serial
import serial.tools.list_ports
from gi.repository import Adw, Gtk, Gio, GObject, GLib, Gdk

class TaunoSerial():

    def __init__(self, window_reference):
        self.window_reference = window_reference
        self.is_open = False
        self.tauno_serial = serial.Serial()


    def open(self, port, baud):
        """ Open to serial port """
        # Close if already open
        if self.tauno_serial.is_open:
            print("Already open: Close()")
            self.close()
        else:
            # Open Serial port
            print("Open: " + port + " " + baud)
            self.tauno_serial.baudrate = baud
            self.tauno_serial.port = port
            self.tauno_serial.open()

            if self.tauno_serial.is_open:
                self.is_open = True
                print("Opened Serial Port successfully")
            else:
                print("Unable to open: " + port + " " + baud)


    def close(self):
        """ Close serial port """
        print("Close(): " + str(self.tauno_serial.port) + " " + str(self.tauno_serial.baudrate) )
        self.tauno_serial.close()
        if self.tauno_serial.is_open is False:
            self.is_open = False
            print("Closed Serial Port successfully")
        else:
            print("Unable to open: " + str(self.tauno_serial.port) + " " + str(self.tauno_serial.baudrate) )


    def read(self):
        """ Read while serial port is open """
        while self.is_open:
            try:
                data_in = self.tauno_serial.read()  # read a byte
                GLib.idle_add(self.window_reference.add_to_text_view, data_in)
            except Exception as ex:
                print("Serial read error: ", ex)
                # Close serial port
                if self.tauno_serial.is_open:
                    self.window_reference.reconnect_serial(self.tauno_serial.port, self.tauno_serial.baudrate)
                return



    def write(self, data):
        """ Write to serial port """
        print(f"Serial Port Write: {data}")
        if self.tauno_serial.is_open:
            self.tauno_serial.write(data.encode('utf-8'))

