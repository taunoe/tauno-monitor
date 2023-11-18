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

from gi.repository import Adw, Gtk, Gio, GObject, GLib
import os
import serial
import serial.tools.list_ports
import threading
import time

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
    update_ports = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings(schema_id="art.taunoerik.TaunoMonitor")

        #resource = Gio.resource_load(os.path.join('@PKGDATA_DIR@', 'resources.gresource.xml'))
        #Gio.Resource._register(resource)

        # get saved ui width etc.
        self.settings.bind("window-width", self, "default-width",
                            Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-height", self, "default-height",
                            Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-maximized", self, "maximized",
                            Gio.SettingsBindFlags.DEFAULT)

        # Get saved baud index:
        baud_index = self.settings.get_int("baud-index")
        self.baud_drop_down.set_selected(baud_index)

        # Get saved port string
        port_str = self.settings.get_string("port-str")
        print(port_str)
        self.ports_str_list = []
        self.scan_serial_ports()
        # set selection
        if port_str in self.ports_str_list:
            port_index = self.ports_str_list.index(port_str)
            self.port_drop_down.set_selected(port_index)


        # Update available ports list
        update_ports_action = Gio.SimpleAction(name="update")
        update_ports_action.connect("activate", self.btn_update_ports)
        self.add_action(update_ports_action)

        # Button Open action
        open_action = Gio.SimpleAction(name="open")
        open_action.connect("activate", self.btn_open)
        self.add_action(open_action)

        # Button Send
        send_action = Gio.SimpleAction(name="send")
        send_action.connect("activate", self.btn_send)
        self.add_action(send_action)

        # Get Serial instance, open later
        self.tauno_serial = TaunoSerial(window_reference=self)

        # Buffer
        self.text_buffer = self.input_text_view.get_buffer()
        self.text_iter_end = self.text_buffer.get_end_iter()
        self.text_mark_end = self.text_buffer.create_mark("", self.text_iter_end, False)


    def scan_serial_ports(self):
        """ Scans available serial ports and adds them to drop down list"""
        old_size = len(self.port_drop_down_list)

        ports = list(serial.tools.list_ports.comports())

        self.ports_str_list.clear()
        for port in ports:
            self.ports_str_list.append(str(port[0]))

        self.port_drop_down_list.splice(0, old_size, self.ports_str_list)


    def btn_update_ports(self, action, _):
        print("Btn Update")
        self.scan_serial_ports()


    def btn_open(self, action, _):
        print("Btn Open")

        # Selected Port
        port_obj = self.port_drop_down.get_selected_item()
        selected_port = port_obj.get_string()
        # save port to settings
        self.settings.set_string("port-str", selected_port)

        # selected Baud Rate
        baud_obj = self.baud_drop_down.get_selected_item()
        selected_baud_rate = baud_obj.get_string()
        # save baud settings to settings
        baud_index = self.baud_drop_down.get_selected()
        self.settings.set_int("baud-index", baud_index)
        # Open Serial Port
        self.tauno_serial.open(selected_port, selected_baud_rate)

        if self.tauno_serial.is_open:
            self.open_button.set_label("Close")
        else:
            self.open_button.set_label("Open")

        if self.tauno_serial.is_open:
            # THREAD version
            # https://pygobject.readthedocs.io/en/latest/guide/threading.html
            thread = threading.Thread(target=self.tauno_serial.read)
            thread.daemon = True
            thread.start()


    def update(self, data):
        """ Update Text View """
        try:
            self.text_buffer = self.input_text_view.get_buffer()
            self.text_iter_end = self.text_buffer.get_end_iter()
            self.text_buffer.insert(self.text_iter_end, data.decode('utf-8'))

            self.input_text_view.scroll_to_mark(self.text_mark_end, 0, False, 0, 0)
        except Exception as ex:
            print(ex)


    def btn_send(self, action, _):
        print("Btn Send")

        buffer = self.send_cmd.get_buffer()
        text = buffer.get_text()
        print(f"Entry: {text}")

        self.tauno_serial.write(text)

        buffer.delete_text(0, len(text))


class TaunoSerial():

    def __init__(self, window_reference):
        self.window_reference = window_reference
        #print("Tauno Serial Init")
        self.is_open = False
        self.myserial = serial.Serial()

    def open(self, port, baud):
        print("Tauno Serial Open()")

        # Close if already open
        if self.myserial.is_open:
            self.close()
        else:
            # Open Serial import
            self.myserial.baudrate = baud
            self.myserial.port = port
            self.myserial.open()

            if self.myserial.is_open:
                self.is_open = True
                print("Serial is open")


    def close(self):
        print("Tauno Serial Close()")
        self.myserial.close()
        if self.myserial.is_open is False:
            self.is_open = False
            print("Serial is closed")


    def read(self):
        """ Read while serial is open """
        print("Tauno Serial Read()")
        while self.is_open:
            try:
                data_in = self.myserial.readline()#.decode('utf8')
                GLib.idle_add(self.window_reference.update, data_in)
            except Exception as ex:
                print(ex)


    def write(self, data):
        print("Tauno Serial Write()")

        print(f"Write: {data}")

        if self.myserial.is_open:
            self.myserial.write(data.encode('utf-8'))


