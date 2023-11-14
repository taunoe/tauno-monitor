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

@Gtk.Template(resource_path='/art/taunoerik/TaunoMonitor/window.ui')

class TaunoMonitorWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'TaunoMonitorWindow'

    input_text_view = Gtk.Template.Child()
    open_button = Gtk.Template.Child()
    send_button = Gtk.Template.Child()
    send_cmd = Gtk.Template.Child()
    port_drop_down_list = Gtk.Template.Child()
    baud_drop_down_list = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings(schema_id="art.taunoerik.TaunoMonitor")

        self.settings.bind("window-width", self, "default-width",
                            Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-height", self, "default-height",
                            Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-maximized", self, "maximized",
                            Gio.SettingsBindFlags.DEFAULT)

        # Set Baud Rate
        baud_action = Gio.SimpleAction(name="baud")
        baud_action.connect("activate", self.set_baud_rate)

        # Button Open
        open_action = Gio.SimpleAction(name="open")
        open_action.connect("activate", self.open_serial_port)
        self.add_action(open_action)

        # CMD Entry
        self.send_cmd.set_placeholder_text("Enter cmd")


        # Button Send
        send_action = Gio.SimpleAction(name="send")
        send_action.connect("activate", self.send_to_serial_port)
        self.add_action(send_action)


    def set_baud_rate(self, action, _):
        pass

    def open_serial_port(self, action, _):
        print("Btn Open")

    def send_to_serial_port(self, action, _):
        print("Btn Send")
        #text = self.send_cmd.get_buffer()
        buffer = self.send_cmd.get_buffer()
        text = buffer.get_text()
        print(f"Entry text changed: {text}")
        buffer.delete_text(0, len(text))


    def add_serial_output_to_text_view(self, data):
        try:
            text = data.decode('utf-8')
        except Exception:
            print(Exception)
            return

        buffer = self.input_text_view.get_buffer()



