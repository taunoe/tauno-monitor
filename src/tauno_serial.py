# tauno_serial.py
# Tauno Erik
# 28.07.2024

import serial
import serial.tools.list_ports
from gi.repository import Adw, Gtk, Gio, GObject, GLib, Gdk

class TaunoSerial():

    def __init__(self, window_reference):
        self.window_reference = window_reference
        self.is_open = False
        self.myserial = serial.Serial()


    def open(self, port, baud):
        """ Open to serial port """
        # Close if already open
        if self.myserial.is_open:
            print("open sulgeb")
            self.close()
        else:
            # Open Serial port
            print("Open: " + port + " " + baud)
            self.myserial.baudrate = baud
            self.myserial.port = port
            self.myserial.open()

            if self.myserial.is_open:
                self.is_open = True
                print("Opened Serial Port successfully")
            else:
                print("Unable to open: " + port + " " + baud)


    def close(self):
        """ Close serial port """
        print("Close(): " + str(self.myserial.port) + " " + str(self.myserial.baudrate) )
        self.myserial.close()
        if self.myserial.is_open is False:
            self.is_open = False
            print("Closed Serial Port successfully")
        else:
            print("Unable to open: " + str(self.myserial.port) + " " + str(self.myserial.baudrate) )


    def read(self):
        """ Read while serial port is open """
        while self.is_open:
            try:
                data_in = self.myserial.read()  # read a byte
                GLib.idle_add(self.window_reference.add_to_text_view, data_in)
            except Exception as ex:
                print("Serial read error: ", ex)
                # Close serial port
                if self.myserial.is_open:
                    self.window_reference.reconnect_serial(self.myserial.port, self.myserial.baudrate)
                return


    def write(self, data):
        """ Write to serial port """
        print(f"Serial Port Write: {data}")

        if self.myserial.is_open:
            self.myserial.write(data.encode('utf-8'))

