# window.py
#
# Copyright 2023-2024 Tauno Erik
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

from gi.repository import Adw, Gtk, Gio, GObject, GLib, Gdk
import os
import serial
import serial.tools.list_ports
import threading
import time
import codecs

import gettext
import locale
from os import path
from os.path import abspath, dirname, join, realpath

locale.bindtextdomain('tauno-monitor', path.join(path.dirname(__file__).split('tauno-monitor')[0],'locale'))
locale.textdomain('tauno-monitor')

@Gtk.Template(resource_path='/art/taunoerik/tauno-monitor/window.ui')

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
    toast_overlay = Gtk.Template.Child()  # notifications
    banner_no_ports = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings(schema_id="art.taunoerik.tauno-monitor")

        # Get saved settings from gschema.xml
        self.settings.bind("window-width", self, "default-width",
                            Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-height", self, "default-height",
                            Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-maximized", self, "maximized",
                            Gio.SettingsBindFlags.DEFAULT)

        baud_index_saved = self.settings.get_int("baud-index")
        self.baud_drop_down.set_selected(baud_index_saved)

        self.ports_str_list = []
        self.load_saved_port()

        # Saved RX data format
        self.rx_format_saved = self.settings.get_string("rx-data-format")

        # font size
        self.font_size_saved = self.settings.get_int("font-size")
        self.change_font_size(self.font_size_saved)

        # Button Update available ports list
        update_ports_action = Gio.SimpleAction(name="update")
        update_ports_action.connect("activate", self.btn_update_ports)
        self.add_action(update_ports_action)

        # Button Open action
        open_action = Gio.SimpleAction(name="open")
        open_action.connect("activate", self.btn_open)
        self.add_action(open_action)

        # Entry
        self.send_cmd.connect('activate', self.on_key_enter_pressed)

        # Button Send
        send_action = Gio.SimpleAction(name="send")
        send_action.connect("activate", self.btn_send)
        self.add_action(send_action)

        # Button Guide
        guide_action = Gio.SimpleAction(name="guide")
        guide_action.connect("activate", self.btn_guide)
        self.add_action(guide_action)

        # Get Serial instance, open later
        self.tauno_serial = TaunoSerial(window_reference=self)

        # TextView Buffer
        self.text_buffer = self.input_text_view.get_buffer()
        self.text_iter_end = self.text_buffer.get_end_iter()
        self.text_mark_end = self.text_buffer.create_mark("", self.text_iter_end, False)


    def load_saved_port(self):
        """ Load saved port from saved settings """

        port_str = self.settings.get_string("port-str")

        self.scan_serial_ports()
        # set selection
        if port_str in self.ports_str_list:
            port_index = self.ports_str_list.index(port_str)
            self.port_drop_down.set_selected(port_index)


    def change_font_size(self, new_size):
        """ Changes the css file"""
        css_provider = Gtk.CssProvider()
        css_provider.load_from_string('textview { font-size: ' + str(new_size) + 'pt; }')
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


    def scan_serial_ports(self):
        """ Scans available serial ports and adds them to drop down list"""
        old_size = len(self.port_drop_down_list)

        try:
            ports = list(serial.tools.list_ports.comports())

            if len(ports) == 0:
                # TODO: Kui päriselt on 0 porti aga kõik töötab?
                self.banner_no_ports.set_revealed(revealed=True)

            self.ports_str_list.clear()
            for port in ports:
                self.ports_str_list.append(str(port[0]))

            self.port_drop_down_list.splice(0, old_size, self.ports_str_list)
        except Exception as e:
            print("Scan serial ports error: ",e)
            return


    def btn_guide(self, action, _):
        """ Button Guide action """
        self.banner_no_ports.set_revealed(revealed=False)

        guide = Gtk.Window.new()
        guide.set_modal(modal=True)
        guide.set_transient_for(self)
        guide.set_default_size(width=600, height=300)
        guide.set_size_request(width=600, height=300)
        guide.set_titlebar(Gtk.HeaderBar())
        guide.set_title(title='Guide')

        vbox = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.set_margin_top(margin=12)
        vbox.set_margin_end(margin=12)
        vbox.set_margin_bottom(margin=12)
        vbox.set_margin_start(margin=12)
        guide.set_child(child=vbox)


        txt1 = "To make serial ports visible to the app add the user to 'dialout' group. Please open Terminal and type:"
        label1 = Gtk.Label.new(txt1)
        label1.props.xalign = False
        vbox.append(child=label1)

        code_window = Gtk.ScrolledWindow.new()
        vbox.append(child=code_window)

        code = Gtk.TextView.new()
        code_buffer = code.get_buffer()
        code_buffer.set_text("sudo usermod -a -G dialout $USER\n\
sudo usermod -a -G plugdev $USER")
        code.set_cursor_visible(True)
        code.set_editable(False)
        code_window.set_child(code)

        txt2 = "You will need to log out and log back in again (or reboot) for the user group changes to take effect."
        label2 = Gtk.Label.new(txt2)
        label2.props.xalign = False
        vbox.append(child=label2)

        txt3 = "Ubuntu users also must enable \"Access USB hardware directly\" in the Ubuntu Store Software store."
        label3 = Gtk.Label.new(txt3)
        label3.props.xalign = False
        vbox.append(child=label3)

        lnbtn = Gtk.LinkButton.new_with_label('https://github.com/taunoe/tauno-monitor', 'More information on the project\'s GitHub page')
        vbox.append(child=lnbtn)

        guide.present()



    def btn_update_ports(self, action, _):
        """ Button Update ports list action """
        self.scan_serial_ports()


    def btn_open(self, action, _):
        """ Button Open action """
        #self.banner_no_ports.set_revealed(revealed=True) # for testing
        # Selected Port
        try:
            port_obj = self.port_drop_down.get_selected_item()
            selected_port = port_obj.get_string()
        except Exception as ex:
            print("Open error:", ex)
            selected_port = 'not avaible' # not avaible
        # save port to settings
        self.settings.set_string("port-str", selected_port)

        # selected Baud Rate
        baud_obj = self.baud_drop_down.get_selected_item()
        selected_baud_rate = baud_obj.get_string()
        # save baud settings to settings
        baud_index_new = self.baud_drop_down.get_selected()
        self.settings.set_int("baud-index", baud_index_new)
        # Open Serial Port
        self.tauno_serial.open(selected_port, selected_baud_rate)

        # Change button label and title
        if self.tauno_serial.is_open:
            self.open_button.set_label("Close")
            self.set_title(str(selected_port)+":"+str(selected_baud_rate))

        else:
            self.open_button.set_label("Open")
            self.set_title("Tauno Monitor")

        display_notifications = self.settings.get_boolean("notifications")
        if self.tauno_serial.is_open:
            if display_notifications:
                self.toast_overlay.add_toast(Adw.Toast(title=f"{selected_port} {selected_baud_rate} connected"))
            # THREAD version
            # https://pygobject.readthedocs.io/en/latest/guide/threading.html
            thread = threading.Thread(target=self.tauno_serial.read)
            thread.daemon = True
            thread.start()
        else:
            if display_notifications:
                self.toast_overlay.add_toast(Adw.Toast(title=f"{selected_port} {selected_baud_rate} closed"))


    def update(self, data):
        """ Update Text View """
        try:
            self.text_buffer = self.input_text_view.get_buffer()
            self.text_iter_end = self.text_buffer.get_end_iter()
            #print("byte:", data)
            #print(repr(data.decode()))

            if self.rx_format_saved == 'HEX':
                # 0x0a == \n
                # 0x0d == \r
                self.text_buffer.insert(self.text_iter_end, data.hex())
                self.text_buffer.insert(self.text_iter_end, ' ')
            else: # ASCII
                if data.decode() != '\r': # ignore \r - is it good idea??
                    self.text_buffer.insert(self.text_iter_end, data.decode())

            self.input_text_view.scroll_to_mark(self.text_mark_end, 0, False, 0, 0)
        except Exception as ex:
            print("update error:", ex)
            return


    def btn_send(self, action, _):
        """ Button Send action """
        buffer = self.send_cmd.get_buffer()
        text = buffer.get_text()
        print(f"Entry: {text}")
        self.tauno_serial.write(text)
        buffer.delete_text(0, len(text))


    def on_key_enter_pressed(self, entry):
        #print(f'(activate) Value entered in entry: {entry.get_text()}')
        if self.tauno_serial.is_open:
            buffer = self.send_cmd.get_buffer()
            text = buffer.get_text()
            print(f"Entry: {text}")
            self.tauno_serial.write(text)
            buffer.delete_text(0, len(text))


class TaunoSerial():

    def __init__(self, window_reference):
        self.window_reference = window_reference
        self.is_open = False
        self.myserial = serial.Serial()

    def open(self, port, baud):
        """ Open to serial port """
        # Close if already open
        if self.myserial.is_open:
            self.close()
        else:
            # Open Serial port
            print("Open: " + port + " " + baud)
            self.myserial.baudrate = baud
            self.myserial.port = port
            self.myserial.open()

            if self.myserial.is_open:
                self.is_open = True
                print("Opened successfully")
            else:
                print("Unable to open: " + port + " " + baud)


    def close(self):
        """ Close serial port """
        print("Close: " + str(self.myserial.port) + " " + str(self.myserial.baudrate) )
        self.myserial.close()
        if self.myserial.is_open is False:
            self.is_open = False
            print("Closed successfully")
        else:
            print("Unable to open: " + str(self.myserial.port) + " " + str(self.myserial.baudrate) )


    def read(self):
        """ Read while serial port is open """
        while self.is_open:
            try:
                data_in = self.myserial.read()  # read a byte
                GLib.idle_add(self.window_reference.update, data_in)
            except Exception as ex:
                print("Serial read error: ", ex)
                # Close serial port
                # It happens when some other program uses the same port
                self.window_reference.btn_open("open", _)
                return


    def write(self, data):
        """ Write to serial port """
        print(f"Write: {data}")

        if self.myserial.is_open:
            self.myserial.write(data.encode('utf-8'))

