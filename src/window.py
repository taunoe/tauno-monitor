# window.py
#
# Copyright 2023 Tauno Erik
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk, Gio
import serial
import serial.tools.list_ports

@Gtk.Template(resource_path='/art/taunoerik/TaunoMonitor/window.ui')

class TaunoMonitorWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'TaunoMonitorWindow'

    input_text_view = Gtk.Template.Child()
    open_button = Gtk.Template.Child()
    send_button = Gtk.Template.Child()
    send_cmd = Gtk.Template.Child()
    port_drop_down = Gtk.Template.Child()
    port_drop_down_list = Gtk.Template.Child()
    baud_drop_down = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings(schema_id="art.taunoerik.TaunoMonitor")

        self.settings.bind("window-width", self, "default-width",
                            Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-height", self, "default-height",
                            Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-maximized", self, "maximized",
                            Gio.SettingsBindFlags.DEFAULT)


        # Button Open action
        open_action = Gio.SimpleAction(name="open")
        open_action.connect("activate", self.open_serial_port)
        self.add_action(open_action)

        # Button Send
        send_action = Gio.SimpleAction(name="send")
        send_action.connect("activate", self.send_to_serial_port)
        self.add_action(send_action)

        # list available serial ports
        self.scan_serial_ports()
        # Get Serial instance, open laiter
        self.myserial = serial.Serial()


    def scan_serial_ports(self):
        self.port_drop_down_list.remove(0) # Removes: not available

        serial.tools.list_ports.comports()

        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            self.port_drop_down_list.append(str(port[0]))
            #print(port[1])  # info


    def open_serial_port(self, action, _):
        print("Btn Open")

        if self.myserial.is_open:
            self.myserial.close()
            if self.myserial.is_open is False:
                print("Serial is closed")
                self.open_button.set_label("Open")
        else:
            # Selected Port
            port_obj = self.port_drop_down.get_selected_item()
            selected_port = port_obj.get_string()
            print(selected_port)
            # selected Baud Rate
            baud_obj = self.baud_drop_down.get_selected_item()
            selected_baud_rate = baud_obj.get_string()
            print(selected_baud_rate)
            # Open Serial import
            self.myserial.baudrate = selected_baud_rate
            self.myserial.port = selected_port
            self.myserial.open()

            if self.myserial.is_open:
                print("Serial is open")
                self.open_button.set_label("Close")



    def send_to_serial_port(self, action, _):
        print("Btn Send")
        buffer = self.send_cmd.get_buffer()
        text = buffer.get_text()
        print(f"Enter CMD: {text}")

        if self.myserial.is_open:
            self.myserial.write(text.encode('utf-8'))

        buffer.delete_text(0, len(text))


    def add_serial_output_to_text_view(self, data):
        try:
            text = data.decode('utf-8')
        except Exception:
            print(Exception)
            return

        buffer = self.input_text_view.get_buffer()



