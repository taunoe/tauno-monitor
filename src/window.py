# window.py
#
# Copyright 2023-2025 Tauno Erik
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

# https://pygobject.gnome.org/tutorials/gtk4/textview.html

from gi.repository import Adw, Gtk, Gio, GObject, GLib, Gdk
import serial
import serial.tools.list_ports
import threading
from datetime import datetime
import codecs
import time
from .tauno_serial import TaunoSerial
from .tauno_logging import TaunoLogging
from .guide import TaunoGuideWindow
import gettext, locale, os, random, string


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

        # https://github.com/natorsc/python-gtk-pygobject/blob/ac01a136a480ee18b55d5062f986336373a26d9b/src/gtk-widgets/translator-gettext/MainWindow.py
        # # The default language of the operating system will be used.
        localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
        locale.setlocale(locale.LC_ALL, '')
        gettext.bindtextdomain('art.taunoerik.tauno-monitor', localedir)
        gettext.textdomain('art.taunoerik.tauno-monitor')
        _ = gettext.gettext


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

        # Get saved Serial RX data format
        self.get_rx_format_saved = self.settings.get_string("saved-serial-rx-data-format")
        #
        self.get_data_bit_saved = self.settings.get_int("saved-serial-data-bit-index")
        self.get_parity_saved = self.settings.get_int("saved-serial-parity-index")
        self.get_stop_bit_saved = self.settings.get_int("saved-serial-stop-bit-index")
        self.get_send_line_end_saved = self.settings.get_int("saved-serial-send-line-end-index")

        # font size
        self.font_size_saved = self.settings.get_int("font-size")
        self.change_font_size(self.font_size_saved)

        # Button Update available ports list
        self.create_action('update', self.btn_update_ports)

        # Button Open action
        self.create_action('open', self.btn_open)

        # Button Send
        self.create_action('send', self.btn_send)

        # Button Guide
        self.create_action('guide', self.btn_guide)

        # Button clear textview
        self.create_action('clear', self.btn_clear_textview)

        # Switch log
        self.create_action('log', self.btn_log)

        # Entry
        self.send_cmd.connect('activate', self.on_key_enter_pressed)

        self.write_logs = False
        self.log_file_exist = False #

        # Get Serial instance, open later
        self.tauno_serial = TaunoSerial(window_reference=self)

        self.logging = TaunoLogging(window_reference=self)

        # TextView Buffer
        self.text_buffer = self.input_text_view.get_buffer()
        self.text_iter_end = self.text_buffer.get_end_iter()
        self.text_mark_end = self.text_buffer.create_mark("", self.text_iter_end, False)

        # Tags
        # https://pygobject.gnome.org/tutorials/gtk4/textview.html
        # https://stackoverflow.com/questions/24619467/pygobject-hex-color-to-gdk-rgba

        time_color = self.settings.get_string("saved-time-color")
        self.tag_time = self.text_buffer.create_tag('time', foreground=time_color)

        arrow_color = self.settings.get_string("saved-arrow-color")
        self.tag_arrow = self.text_buffer.create_tag('arrow', foreground=arrow_color)

        out_color = self.settings.get_string("saved-out-color")
        self.tag_out = self.text_buffer.create_tag('out', foreground=out_color)

        in_color = self.settings.get_string("saved-in-color")
        self.tag_in = self.text_buffer.create_tag('in', foreground=in_color)

        line_end_color = self.settings.get_string("saved-show-line-end-color")
        self.tag_line_end = self.text_buffer.create_tag('line_end', foreground=in_color)

        self.prev_char = '\n'  # store prev char

        # Reconnect
        self.reconnecting_serial = False

        # https://realpython.com/python-sleep/
        self.event = threading.Event()

    def create_action(self, name, function, shortcuts=None):
        """ Add an application action.
        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", function)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


    def generate_random_string(self, length):
        """ Useful for creating a unique name """
        # Create a pool of characters containing lowercase, uppercase letters and digits
        characters = string.ascii_letters + string.digits
        # Generate a random string of the specified length
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string


    def update_time_tag(self):
        """ Creates new tag with a new color """
        # TODO How to change already existing tag color?
        #print("update_time_tag")
        self.text_buffer = self.input_text_view.get_buffer()
        color = self.settings.get_string("saved-time-color")
        self.table = self.text_buffer.get_tag_table()
        new_tag_name = 'time' + self.generate_random_string(10)
        self.tag_time = self.text_buffer.create_tag(new_tag_name, foreground=color)

    def update_arrow_tag(self):
        """ Creates new tag with a new color """
        #print("update_arrow_tag")
        self.text_buffer = self.input_text_view.get_buffer()
        color = self.settings.get_string("saved-arrow-color")
        self.table = self.text_buffer.get_tag_table()
        new_tag_name = 'arrow' + self.generate_random_string(10)
        self.tag_arrow = self.text_buffer.create_tag(new_tag_name, foreground=color)


    def update_out_tag(self):
        """ Creates new tag with a new color """
        #print("update_out_tag")
        self.text_buffer = self.input_text_view.get_buffer()
        color = self.settings.get_string("saved-out-color")
        self.table = self.text_buffer.get_tag_table()
        new_tag_name = 'out' + self.generate_random_string(10)
        self.tag_out = self.text_buffer.create_tag(new_tag_name, foreground=color)


    def update_in_tag(self):
        """ Creates new tag with a new color """
        #print("update_in_tag")
        self.text_buffer = self.input_text_view.get_buffer()
        color = self.settings.get_string("saved-in-color")
        self.table = self.text_buffer.get_tag_table()
        new_tag_name = 'in' + self.generate_random_string(10)
        self.tag_in = self.text_buffer.create_tag(new_tag_name, foreground=color)


    def update_line_end_tag(self):
        """ Creates new tag with a new color """
        #print("update_line_end_tag")
        self.text_buffer = self.input_text_view.get_buffer()
        color = self.settings.get_string("saved-show-line-end-color")
        self.table = self.text_buffer.get_tag_table()
        new_tag_name = 'lineend' + self.generate_random_string(10)
        self.tag_line_end = self.text_buffer.create_tag(new_tag_name, foreground=color)


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
        if self.log_switch.props.active:
            print("log switch active")
            self.write_logs = True
            # Does log file exists?
            if self.log_file_exist == False:
                folder = self.settings.get_string("log-folder")
                current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                log_file_path = folder + "/tauno-monitor_log-" + current_datetime + ".txt"
                # Create log file
                self.log_file_exist = self.logging.create_file(log_file_path)
        else:
            print("log switch deactivate")
            self.logging.close_file()
            self.write_logs = False


    def btn_guide(self, action, _):
        """ Dispplay Guide Window """
        guide_window = TaunoGuideWindow(transient_for=self)
        guide_window.present()


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
        # TODO: korrastada ja lihtsustada!
        # rescan ports
        self.scan_serial_ports()

        # Selected Port
        try:
            port_obj = self.port_drop_down.get_selected_item()
            selected_port = port_obj.get_string()
        except Exception as ex:
            print("BTN Open error:", ex)
            selected_port = 'not available'
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
            title = str(selected_port)+":"+str(selected_baud_rate)
            self.set_title(title) # port
            self.logging.write_data("Opened " + title + "\n")
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
        print("Auto reconnecting serial ")
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

            i = 0
            while self.tauno_serial.is_open == False and self.reconnecting_serial == True:
                self.event.wait(0.5)
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
                self.tauno_serial.close()
                self.set_title('Tauno Monitor')


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


    def add_to_text_view(self, data):
        """ Update Text View """
        try:
            # HEX
            if self.get_rx_format_saved == 'HEX':
                self.insert_data_to_text_view(data, 'HEX')
            # ASCII
            else:
                if self.prev_char == '\n':
                    # Timestamp
                    self.insert_time_to_text_view()
                    # Arrow
                    self.insert_arrow_to_text_view('RX')
                if data.decode() != '\r':  # ignore \r - is it good idea??
                    self.insert_data_to_text_view(data, 'ASCII')
            # Scroll text view
            self.input_text_view.scroll_to_mark(self.text_mark_end, 0, False, 0, 0)
        except Exception as ex:
            print("add_to_text_view error:", ex)
            return


    def insert_data_to_text_view(self, data, type):
        """ Types 'HEX', 'ASCII', 'TX' """
        self.text_buffer = self.input_text_view.get_buffer()
        self.text_iter_end = self.text_buffer.get_end_iter()
        start_mark = self.text_buffer.create_mark('start_mark', self.text_buffer.get_end_iter(), True)

        if type == 'HEX':
            self.text_buffer.insert(self.text_iter_end, data.hex())
            self.text_buffer.insert(self.text_iter_end, ' ')
            self.logging.write_hex_data(data.hex())
            tag = self.tag_in
        elif type == 'ASCII':
            self.prev_char = data.decode()  # Store char
            self.text_buffer.insert(self.text_iter_end, data.decode())
            self.logging.write_data(data.decode())
            tag = self.tag_in
        elif type == 'TX':
            self.text_buffer.insert(self.text_iter_end, data)
            self.logging.write_data(data)
            tag = self.tag_out
        else:
            print("Wrong data type!")

        end_mark = self.text_buffer.create_mark('end_mark', self.text_buffer.get_end_iter(), True)
        self.text_buffer.apply_tag(tag, self.text_buffer.get_iter_at_mark(start_mark), self.text_buffer.get_iter_at_mark(end_mark))



    def insert_arrow_to_text_view(self, type):
        """" Display a arrow RX or TX"""
        if type == 'TX':
            arrow = '<-- '  # TX
        else:
            arrow = '--> '  # RX

        self.text_buffer = self.input_text_view.get_buffer()
        # start
        arrow_start_mark = self.text_buffer.create_mark('arrow_start_mark', self.text_buffer.get_end_iter(), True)
        # arrow
        self.text_buffer.insert(self.text_iter_end, arrow)
        # end
        arrow_end_mark = self.text_buffer.create_mark('arrow_end_mark', self.text_buffer.get_end_iter(), True)
        # tag
        self.text_buffer.apply_tag(self.tag_arrow, self.text_buffer.get_iter_at_mark(arrow_start_mark), self.text_buffer.get_iter_at_mark(arrow_end_mark))
        # Log arrow
        self.logging.write_data(arrow)


    def insert_time_to_text_view(self):
        """ Add timestamp if needed """
        is_timestamp = self.settings.get_boolean("timestamp")

        if is_timestamp:
            # Get time
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S.%f ")
            # Buffer
            self.text_buffer = self.input_text_view.get_buffer()
            # Start
            time_start_mark = self.text_buffer.create_mark('time_start_mark', self.text_buffer.get_end_iter(), True)
            # Time
            self.text_buffer.insert(self.text_iter_end, current_time)
            # End
            time_end_mark = self.text_buffer.create_mark('time_end_mark', self.text_buffer.get_end_iter(), True)
            # Tag
            self.text_buffer.apply_tag(self.tag_time, self.text_buffer.get_iter_at_mark(time_start_mark), self.text_buffer.get_iter_at_mark(time_end_mark))
            # Log
            self.logging.write_data(current_time)


    def btn_send(self, action, _):
        """ Button Send action """
        cmd_buffer = self.send_cmd.get_buffer()
        data = cmd_buffer.get_text()
        self.send_to_serial(data)
        cmd_buffer.delete_text(0, len(data))


    def on_key_enter_pressed(self, entry):
        """ Send cmd Enter key pressed """
        cmd_buffer = self.send_cmd.get_buffer()
        data = cmd_buffer.get_text()
        self.send_to_serial(data)
        cmd_buffer.delete_text(0, len(data))


    def send_to_serial(self, data):
        """ Write data to Serial port """
        if self.tauno_serial.is_open:
            self.tauno_serial.write(data)
        else:
            print("Send cmd: Serial is not Open")

        data =  data + '\n'

        self.insert_time_to_text_view()
        self.insert_arrow_to_text_view('TX')
        self.insert_data_to_text_view(data, 'TX')


