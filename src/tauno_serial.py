# tauno_serial.py
# Tauno Erik
# 18.06.2025

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
            print("Open Port: " + port)
            self.tauno_serial.baudrate = baud
            print(f"Open Baud: {baud}")
            self.tauno_serial.port = port

            # Data Bit (index: main.py)
            bytesize_index = self.window_reference.get_data_bit_saved
            if bytesize_index == 0:
                self.tauno_serial.bytesize = serial.FIVEBITS
            elif bytesize_index == 1:
                self.tauno_serial.bytesize = serial.SIXBITS
            elif bytesize_index == 2:
                self.tauno_serial.bytesize = serial.SEVENBITS
            elif bytesize_index == 3:
                self.tauno_serial.bytesize = serial.EIGHTBITS

            # Parity
            parity_index = self.window_reference.get_parity_saved

            if parity_index == 0:
                self.tauno_serial.parity = serial.PARITY_NONE
            elif parity_index == 1:
                self.tauno_serial.parity = serial.PARITY_EVEN
            elif parity_index == 2:
                self.tauno_serial.parity = serial.PARITY_ODD
            elif parity_index == 3:
                self.tauno_serial.parity = serial.PARITY_MARK
            elif parity_index == 5:
                self.tauno_serial.parity = serial.PARITY_SPACE

            # Stopbit
            stopbit_index = self.window_reference.get_stop_bit_saved

            if stopbit_index == 0:
                self.tauno_serial.stopbits = serial.STOPBITS_ONE
            elif stopbit_index == 1:
                self.tauno_serial.stopbits = serial.STOPBITS_ONE_POINT_FIVE
            elif stopbit_index == 2:
                self.tauno_serial.stopbits = serial.STOPBITS_TWO

            # TODO:
            #self.tauno_serial.timeout = 1

            self.tauno_serial.open()
            self.tauno_serial.flushInput() # Clear any old data in the buffer

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

    """
    Read byte while serial port is open
    """
    def read(self):
        while self.is_open:
            # bytes(HEX) or line?
            #print("serial read")
            type = self.window_reference.get_rx_format_saved
            #print(f"type={type}")

            end_index = self.window_reference.get_RX_line_end_saved
            if end_index == 0:
                end = b'\n'
            elif end_index == 1:
                end = b'\r'
            elif end_index == 2:
                end = b'\r\n'
            elif end_index == 3:
                end = b';'

            try:
                if type == 'HEX':
                    # read a byte
                    #print("try=HEX")
                    data_in = self.tauno_serial.read()
                else:
                    #print("try=ASCII")
                    # Read a line until selected end
                    data_in = self.tauno_serial.read_until(expected=end)
                GLib.idle_add(self.window_reference.add_to_text_view, data_in)
            except Exception as ex:
                print("Serial read error: ", ex)
                # Close serial port
                if self.tauno_serial.is_open:
                    self.window_reference.reconnect_serial(self.tauno_serial.port, self.tauno_serial.baudrate)
                return


    """
    Read line while serial port is open
    """




    def write(self, data):
        """ Write to serial port """
        print(f"Serial Port Write: {data}")
        if self.tauno_serial.is_open:
            self.tauno_serial.write(data.encode('utf-8'))

