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
import serial
import serial.tools.list_ports
import threading
from datetime import datetime
import codecs
import time
from .tauno_serial import TaunoSerial
from .tauno_logging import TaunoLogging

@Gtk.Template(resource_path='/art/taunoerik/tauno-monitor/window.ui')

class TaunoMonitorWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'TaunoMonitorWindow'

    input_text_view = Gtk.Template.Child()
    open_button = Gtk.Template.Child()
    send_button = Gtk.Template.Child()
    clear_button = Gtk.Template.Child()
    log_switch = Gtk.Template.Child()
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

        # Button clear textview
        clear_textview_action = Gio.SimpleAction(name="clear")
        clear_textview_action.connect("activate", self.btn_clear_textview)
        self.add_action(clear_textview_action)

        # Switch log
        log_action = Gio.SimpleAction(name="log")
        log_action.connect("activate", self.btn_log)
        self.add_action(log_action)
        self.write_logs = False
        self.log_file_exist = False
        self.log_file_path = ""
        self.file_handle = None  # opened log file

        # Get Serial instance, open later
        self.tauno_serial = TaunoSerial(window_reference=self)

        self.tauno_logging = TaunoLogging(window_reference=self)

        # TextView Buffer
        self.text_buffer = self.input_text_view.get_buffer()
        self.text_iter_end = self.text_buffer.get_end_iter()
        self.text_mark_end = self.text_buffer.create_mark("", self.text_iter_end, False)

        self.prev_char = '\n'

        # Reconnect
        self.reconnecting_serial = False

        # https://realpython.com/python-sleep/
        self.event = threading.Event()


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


    def btn_log(self, switch, _gparam):
        """ Logging switch action """
        current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        if self.log_switch.props.active:
            print("log switch active")
            self.write_logs = True
            # Does log file exists?
            if self.log_file_exist == False:
                folder = self.settings.get_string("log-folder")
                self.log_file_path = folder + "/tauno-monitor_log-" + current_datetime + ".txt"
                # Create log file
                f = open(self.log_file_path, "x")
                self.log_file_exist = True

            self.write_data_to_log("\nTauno-Monitor log started: " + current_datetime + "\n")
        else:
            print("log switch deactive")
            self.write_data_to_log("Tauno-Monitor log ended: " + current_datetime + "\n")
            self.write_logs = False
            self.close_log_file()


    def write_data_to_log(self, data):  # data == char
        """ Write data to log file """
        if self.write_logs == True:
            if self.file_handle is None:
                # Open the file the first time the method is called
                self.file_handle = open(self.log_file_path, 'a')
            # Write data to the file
            self.file_handle.write(data)  # + '\n'


    def close_log_file(self):
        """ Close the log file """
        if self.file_handle is not None:
            self.file_handle.close()
            self.file_handle = None


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

    def btn_clear_textview(self, action, _):
        """ Clear textview buffer: data printed by serial """
        # print("btn_clear_textview")
        self.text_buffer = self.input_text_view.get_buffer()
        self.text_iter_start = self.text_buffer.get_start_iter()
        self.text_iter_end = self.text_buffer.get_end_iter()
        self.text_buffer.delete(self.text_iter_start, self.text_iter_end)


    def btn_open(self, action, _):
        """ Button Open action """
        # rescan ports
        self.scan_serial_ports()

        # Selected Port
        try:
            port_obj = self.port_drop_down.get_selected_item()
            selected_port = port_obj.get_string()
        except Exception as ex:
            print("Open error:", ex)
            selected_port = 'not available' # not available
        # save port to settings
        self.settings.set_string("port-str", selected_port)

        # selected Baud Rate
        baud_obj = self.baud_drop_down.get_selected_item()
        selected_baud_rate = baud_obj.get_string()
        # save baud settings to settings
        baud_index_new = self.baud_drop_down.get_selected()
        self.settings.set_int("baud-index", baud_index_new)

        # If we a middle of reconnection
        if self.reconnecting_serial:
            self.tauno_serial.close()
            self.reconnecting_serial = False
            self.open_button.set_label("Open")
            self.set_title("Tauno Monitor")
        else:
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
            self.thread_read_serial()
        else:
            if display_notifications:
                self.toast_overlay.add_toast(Adw.Toast(title=f"{selected_port} {selected_baud_rate} closed"))


    def thread_read_serial(self):
        """ Thread to read serial port"""
        # THREAD version
        # https://pygobject.readthedocs.io/en/latest/guide/threading.html
        thread = threading.Thread(target=self.tauno_serial.read)
        thread.daemon = True
        thread.start()


    def reconnect_serial(self, selected_port, selected_baudrate):
        """ Tries to reconnect the serial connection. Using the latest settings. """
        print("Auto reconnect_serial")
        self.tauno_serial.close()

        # Display notification
        display_notifications = self.settings.get_boolean("notifications")
        if display_notifications:
                self.toast_overlay.add_toast(Adw.Toast(title=f"{selected_port} {selected_baudrate} lost"))

        self.reconnecting_serial = True

        if self.reconnecting_serial:
            self.set_title("Reconnecting")
            port_obj = self.port_drop_down.get_selected_item()
            last_port = port_obj.get_string()

            baud_obj = self.baud_drop_down.get_selected_item()
            last_baud = baud_obj.get_string()

            print("reconnecting ")
            i = 0
            while self.tauno_serial.is_open == False and self.reconnecting_serial == True:
                self.event.wait(0.75)
                try:
                    self.tauno_serial.open(last_port, last_baud)
                except:
                    self.reconnecting_msg(i)  # Title animation
                    i = i+1
                    if i > 3:
                        i = 0

            self.thread_read_serial()  # Start reading
            self.reconnecting_serial = False

            if self.tauno_serial.is_open:
                self.set_title(str(last_port)+":"+str(last_baud))
                print(" reconnected!")
            else: # Close button is pressed
                pass


    def reconnecting_msg(self, i):
        """ Title animation """
        print(".")
        if i == 1:
            self.set_title("Reconnecting .")
        elif i == 2:
            self.set_title("Reconnecting ..")
        elif i == 3:
            self.set_title("Reconnecting ...")
        else:
             self.set_title("Reconnecting ")


    def update(self, data):
        """ Update Text View """
        try:
            self.text_buffer = self.input_text_view.get_buffer()
            self.text_iter_end = self.text_buffer.get_end_iter()
            #print("byte:", data)
            #print(repr(data.decode()))

            # get time
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S.%f ")
            arrow = '--> '

            if self.rx_format_saved == 'HEX':
                # 0x0a == \n
                # 0x0d == \r
                self.text_buffer.insert(self.text_iter_end, data.hex())
                self.text_buffer.insert(self.text_iter_end, ' ')
            else: # ASCII
                add_timestamp = self.settings.get_boolean("timestamp")
                if add_timestamp:
                    # add time when prev char was newline
                    if self.prev_char == '\n':
                        self.text_buffer.insert(self.text_iter_end, current_time)
                        self.write_data_to_log(current_time)
                        self.text_buffer.insert(self.text_iter_end, arrow)
                        self.write_data_to_log(arrow)
                else:
                    if self.prev_char == '\n':
                        self.text_buffer.insert(self.text_iter_end, arrow)
                        self.write_data_to_log(arrow)

                if data.decode() != '\r': # ignore \r - is it good idea??
                    # Store char
                    self.prev_char = data.decode()
                    self.text_buffer.insert(self.text_iter_end, data.decode())
                    self.write_data_to_log(data.decode())


            self.input_text_view.scroll_to_mark(self.text_mark_end, 0, False, 0, 0)
        except Exception as ex:
            print("update error:", ex)
            return





    def btn_send(self, action, _):
        """ Button Send action """
        buffer = self.send_cmd.get_buffer()
        text = buffer.get_text()
        print(f"Entry send: {text}")
        self.tauno_serial.write(text)

        text = '<-- ' + text + '\n'

        self.text_buffer = self.input_text_view.get_buffer()
        self.text_iter_end = self.text_buffer.get_end_iter()
        add_timestamp = self.settings.get_boolean("timestamp")
        if add_timestamp:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S.%f ")
            self.text_buffer.insert(self.text_iter_end, current_time)
            self.write_data_to_log(current_time)

        self.write_data_to_log(text)
        self.text_buffer.insert(self.text_iter_end, text)

        buffer.delete_text(0, len(text))


    def on_key_enter_pressed(self, entry):
        #print(f'(activate) Value entered in entry: {entry.get_text()}')

        if self.tauno_serial.is_open:
            buffer = self.send_cmd.get_buffer()
            text = buffer.get_text()
            print(f"Entry enter: {text}")
            self.tauno_serial.write(text)

            text = '<-- ' + text + '\n'

            self.text_buffer = self.input_text_view.get_buffer()
            self.text_iter_end = self.text_buffer.get_end_iter()
            add_timestamp = self.settings.get_boolean("timestamp")
            if add_timestamp:
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S.%f ")
                self.text_buffer.insert(self.text_iter_end, current_time)
                self.write_data_to_log(current_time)

            self.write_data_to_log(text)
            self.text_buffer.insert(self.text_iter_end, text)

            buffer.delete_text(0, len(text))


