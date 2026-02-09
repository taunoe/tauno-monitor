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
from .tool_baud import TaunoToolBaudWindow
import gettext, locale, os, random, string
import re
from .usb_db import usb_db

APP_NAME = "Tauno Monitor"
APP_ID = "art.taunoerik.tauno-monitor"

@Gtk.Template(resource_path='/art/taunoerik/tauno-monitor/window.ui')
class TaunoMonitorWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'TaunoMonitorWindow'

    input_text_view = Gtk.Template.Child()
    open_button = Gtk.Template.Child()
    send_button = Gtk.Template.Child()
    clear_button = Gtk.Template.Child()
    log_switch = Gtk.Template.Child()
    send_cmd_entry = Gtk.Template.Child()
    rx_line_end_label_drop_down = Gtk.Template.Child()
    rx_line_end_label_drop_down_list = Gtk.Template.Child()
    ui_tx_end = Gtk.Template.Child()
    ui_tx_end_list = Gtk.Template.Child()
    port_drop_down = Gtk.Template.Child()
    port_drop_down_list = Gtk.Template.Child()
    baud_drop_down = Gtk.Template.Child()
    update_ports = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()  # notifications
    banner_no_ports = Gtk.Template.Child()
    # Sidebar
    show_sidebar_button = Gtk.Template.Child()
    info_port_value = Gtk.Template.Child()
    info_baud_value = Gtk.Template.Child()
    info_Name = Gtk.Template.Child()
    info_Description = Gtk.Template.Child()
    info_VID = Gtk.Template.Child()
    info_VID_Vendor = Gtk.Template.Child()
    info_PID = Gtk.Template.Child()
    info_PID_Product = Gtk.Template.Child()
    info_Serial_Number = Gtk.Template.Child()
    info_Location = Gtk.Template.Child()
    info_Manufacturer = Gtk.Template.Child()
    info_Product = Gtk.Template.Child()
    info_Interface = Gtk.Template.Child()

    split_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # https://github.com/natorsc/python-gtk-pygobject/blob/ac01a136a480ee18b55d5062f986336373a26d9b/src/gtk-widgets/translator-gettext/MainWindow.py
        # # The default language of the operating system will be used.
        localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
        locale.setlocale(locale.LC_ALL, '')
        gettext.bindtextdomain(APP_ID, localedir)
        gettext.textdomain(APP_ID)
        _ = gettext.gettext

        self.connect("close-request", self.on_close_request)

        self.settings = Gio.Settings(schema_id=APP_ID)

        # Get saved settings from gschema.xml
        self.settings.bind("window-width", self, "default-width",
                            Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-height", self, "default-height",
                            Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-maximized", self, "maximized",
                            Gio.SettingsBindFlags.DEFAULT)

        self.COMMON_BAUD_RATES = [50, 75, 110, 134, 150, 200, 300, 600, 750,
            1200, 1800, 2400, 4800, 7200, 9600, 14400, 19200, 28800, 31250,
            38400, 56000, 57600, 74880, 76800, 115200, 115600, 128000, 230400,
            250000, 256000, 460800, 500000, 576000, 921600, 1000000, 1152000,
            1500000, 2000000, 2500000, 3000000, 3500000, 4000000]
        self.str_COMMON_BAUD_RATES = [str(i) for i in self.COMMON_BAUD_RATES]

        baud_model = Gtk.StringList.new(self.str_COMMON_BAUD_RATES)
        self.baud_drop_down.set_model(baud_model)

        baud_index_saved = self.settings.get_int("baud-index")
        self.baud_drop_down.set_selected(baud_index_saved)
        # Add to Info Sidebar:
        selected_str = self.baud_drop_down.get_selected_item().get_string()
        self.info_baud_value.set_label(selected_str)
        self.baud_drop_down.connect("notify::selected-item", self.on_baud_drop_down_changed)

        self.ports_str_list = []
        self.load_saved_port()
        self.port_drop_down.connect("notify::selected-item", self.on_port_drop_down_changed)


        self.serial_tx_line_endings = ['\\n', '\\r', '\\r\\n', 'None']
        self.serial_rx_line_endings = ['\\n', '\\r', '\\r\\n', ';', 'None']
        ####
        tx_end_model = Gtk.StringList.new(self.serial_tx_line_endings)
        self.ui_tx_end.set_model(tx_end_model)

        rx_end_model = Gtk.StringList.new(self.serial_rx_line_endings)
        self.rx_line_end_label_drop_down.set_model(rx_end_model)

        # Get saved Serial RX data format
        self.get_rx_format_saved = self.settings.get_string("saved-serial-rx-data-format")



        # Get saved data bit index
        self.get_data_bit_saved = self.settings.get_int("saved-serial-data-bit-index")

        # Get saved parity index
        self.get_parity_saved = self.settings.get_int("saved-serial-parity-index")

        # Get Stop Bit index
        self.get_stop_bit_saved = self.settings.get_int("saved-serial-stop-bit-index")

        # Get TX line end index
        self.get_TX_line_end_saved = self.settings.get_int("saved-serial-tx-line-end-index")

        self.ui_tx_end.set_selected(self.get_TX_line_end_saved)
        self.ui_tx_end.connect("notify::selected-item", self.on_ui_tx_end_changed)

        # Get RX line end index
        self.get_RX_line_end_saved = self.settings.get_int("saved-serial-rx-line-end-index")

        self.rx_line_end_label_drop_down.set_selected(self.get_RX_line_end_saved)
        self.rx_line_end_label_drop_down.connect("notify::selected-item", self.on_ui_rx_end_changed)

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

        # Menu Button Tool Baud
        self.create_action('tool_baud', self.btn_tool_baud)

        # Button clear textview
        self.create_action('clear', self.btn_clear_textview)

        # Switch log
        self.create_action('log', self.btn_log)

        # Entry
        self.send_cmd_entry.connect('activate', self.on_key_enter_pressed)

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
        self.tag_line_end = self.text_buffer.create_tag('line_end', foreground=line_end_color)

        self.prev_char = '\n'  # store prev char


        # Reconnect
        self.reconnecting_serial = False

        # https://realpython.com/python-sleep/
        self.event = threading.Event()

        # TX command history
        self.send_cmd_history = []
        self.send_cmd_history_index = -1
        self.send_cmd_current = ""
        self.send_cmd_history_max_size = 50
        # Arrow key up
        # Connect key press event using event controller
        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.add_controller(key_controller)


    def on_key_pressed(self, controller, keyval, keycode, state):
        """
        Detect key presses
        UP and DOWN arrow keys for TX history
        """
        if keyval == Gdk.KEY_Up:
            print("up")
            self.navigate_cmd_history(-1)
            return True
        elif keyval == Gdk.KEY_Down:
            print("down")
            self.navigate_cmd_history(1)
            return True
        return False


    def navigate_cmd_history(self, direction):
        """
        Navigate in TX command history
        UP and DOWN arrow keyes
        """
        if not self.send_cmd_history:
            return

        # Save current text if we're at the end of history
        if self.send_cmd_history_index == len(self.send_cmd_history):
            current = self.send_cmd_entry.get_buffer()#self.get_text()
            if type(current) == str:
                self.send_cmd_current = current

        # Update index
        self.send_cmd_history_index += direction

        # Boundary checks
        if self.send_cmd_history_index < 0:
            self.send_cmd_history_index = 0
        elif self.send_cmd_history_index > len(self.send_cmd_history):
            self.send_cmd_history_index = len(self.send_cmd_history)

        # Set text based on history position
        if self.send_cmd_history_index == len(self.send_cmd_history):
            self.send_cmd_entry.set_text(self.send_cmd_current)
        else:
            self.send_cmd_entry.set_text(self.send_cmd_history[self.send_cmd_history_index])

        # Move cursor to end of text
        self.send_cmd_entry.set_position(-1)


    def on_close_request(self, window):
        print("Window is being closed")
        if self.log_file_exist:
                self.logging.close_file()
        return False  # allow closing


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
            # Add to Info Sidebar:
            self.info_port_value.set_label(port_str)
            self.get_port_info(port_str)


    def change_font_size(self, new_size):
        """ Changes the css file"""
        css_provider = Gtk.CssProvider()
        css_provider.load_from_string('textview { font-size: ' + str(new_size) + 'pt; }')
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


    def scan_serial_ports(self):
        """ Scans available serial ports and adds them to drop down list"""
        old_size = len(self.port_drop_down_list)

        try:
            all_ports = list(serial.tools.list_ports.comports())
            ports = []

            for port in all_ports:
                # Does port have vid/pid number?
                # If not, then it not useful for us
                if port.vid != None:
                    ports.append(port)

            if len(ports) == 0:
                self.banner_no_ports.set_revealed(revealed=True)
            else:
                self.banner_no_ports.set_revealed(revealed=False)

            self.ports_str_list.clear()
            for port in ports:
                self.ports_str_list.append(str(port[0]))

            self.port_drop_down_list.splice(0, old_size, self.ports_str_list)
        except Exception as e:
            print("Scan serial ports error: ", e)
            return


    def btn_log(self, switch, _gparam):
        """ Logging switch action """
        if self.log_switch.props.active:
            print("log switch active")
            self.write_logs = True
            # Does log file exists?
            if self.log_file_exist == False:
                folder = self.settings.get_string("log-folder")
                # Directory write premission
                if os.access(folder, os.W_OK):
                    current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                    log_file_path = folder + "/tauno-monitor_log-" + current_datetime + ".txt"
                    # Create log file
                    self.log_file_exist = self.logging.create_file(log_file_path)
                else:
                    print(f"No write permission in log directory:{folder}")
                    # Notification
                    self.notify(f"No write permission in log directory:{folder}")
                    # Turn switch off
                    GLib.idle_add(self.log_switch.set_active, False)
        else:
            print("log switch deactivate")
            if self.log_file_exist:
                self.logging.close_file()
            self.write_logs = False


    def btn_guide(self, action, _):
        """ Dispplay Guide Window """
        guide_window = TaunoGuideWindow(transient_for=self)
        guide_window.present()


    def btn_tool_baud(self, action, _):
        """ Dispplay Tool Baud Window """
        tool_baud_window = TaunoToolBaudWindow(transient_for=self, window_reference=self)
        tool_baud_window.present()


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

        """
        # selected Baud Rate
        baud_obj = self.baud_drop_down.get_selected_item()

        selected_baud_rate = baud_obj.get_string()

        # save baud settings to settings
        baud_index_new = self.baud_drop_down.get_selected()

        self.settings.set_int("baud-index", baud_index_new)
        """

        # If we a middle of reconnection
        if self.reconnecting_serial:
            self.tauno_serial.close()
            self.reconnecting_serial = False
            #self.open_button.set_label("Open")
            self.open_button.set_icon_name("play-large-symbolic")
            self.set_title(APP_NAME)
        else:
            # Get saved
            selected_port = self.settings.get_string("port-str")
            selected_baud_index = self.settings.get_int("baud-index")
            selected_baud_rate = self.baud_drop_down.get_selected_item().get_string()
            # Open Serial Port
            self.tauno_serial.open(selected_port, selected_baud_rate)

        # Change button label and title
        if self.tauno_serial.is_open:
            #self.open_button.set_label("Close")
            self.open_button.set_icon_name("stop-large-symbolic")
            title = str(selected_port)+":"+str(selected_baud_rate)
            self.set_title(title) # port
            self.logging.write_data("Opened " + title + "\n")
        else:
            #self.open_button.set_label("Open")
            self.open_button.set_icon_name("play-large-symbolic")
            self.set_title(APP_NAME)

        if self.tauno_serial.is_open:
            self.notify(f"{selected_port} {selected_baud_rate} connected")
            self.thread_read_serial()
        else:
            self.notify(f"{selected_port} {selected_baud_rate} closed")


    def thread_read_serial(self):
        """ Thread to read serial port"""
        # THREAD version
        # https://pygobject.readthedocs.io/en/latest/guide/threading.html
        thread = threading.Thread(target=self.tauno_serial.read)
        thread.daemon = True
        thread.start()


    def reconnect_serial(self, selected_port, selected_baudrate):
        """
        Tries to reconnect the serial connection. Using the latest settings.
        """
        print("Auto reconnecting serial ")
        self.tauno_serial.close()

        # Display notification
        self.notify(f"{selected_port} {selected_baudrate} lost")

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
                self.set_title(APP_NAME)


    def reconnecting_msg(self, i):
        """
        Title animation
        """
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
        """
        Update Text View
        """
        try:
            # Show data as HEX
            if self.get_rx_format_saved == 'HEX':
                self.insert_data_to_text_view(data, 'HEX')
            elif self.get_rx_format_saved == 'DEC':
                self.insert_data_to_text_view(data, 'DEC')
            elif self.get_rx_format_saved == 'OCT':
                self.insert_data_to_text_view(data, 'OCT')
            # Show data as binary
            elif self.get_rx_format_saved == 'BIN':
                # Timestamp
                self.insert_time_to_text_view()
                # Arrow
                self.insert_arrow_to_text_view('RX')
                # Binary
                self.insert_data_to_text_view(data, 'BIN')
                # Line end
                self.insert_line_end_to_text_view('RX')
            # Show data as ASCII chars == Plain text
            else:
                # Timestamp
                self.insert_time_to_text_view()
                # Arrow
                self.insert_arrow_to_text_view('RX')
                # data
                self.insert_data_to_text_view(data, 'ASCII')
                self.insert_line_end_to_text_view('RX')

            # Scroll text view
            self.input_text_view.scroll_to_mark(self.text_mark_end, 0, False, 0, 0)
        except Exception as ex:
            print("add_to_text_view error:", ex)
            return


    def insert_data_to_text_view(self, data, type):
        """
        Insert data to text view
        Types 'HEX', 'ASCII', 'TX'
        """
        self.text_buffer = self.input_text_view.get_buffer()
        self.text_iter_end = self.text_buffer.get_end_iter()
        start_mark = self.text_buffer.create_mark('start_mark', self.text_buffer.get_end_iter(), True)

        if type == 'HEX':
            self.text_buffer.insert(self.text_iter_end, data.hex())
            self.text_buffer.insert(self.text_iter_end, ' ')
            self.logging.write_hex_data(data.hex())
            tag = self.tag_in
        elif type == 'BIN':
            for byte in data:
                # Pad with leading zeros to show the full byte
                binary_8 = format(byte, '08b')
                self.text_buffer.insert(self.text_iter_end, binary_8)
                self.logging.write_data(binary_8)
            tag = self.tag_in
        elif type == 'OCT':
            for byte in data:
                octal_str = format(byte, '03o')
                self.text_buffer.insert(self.text_iter_end, octal_str)
                self.text_buffer.insert(self.text_iter_end, ' ')
                self.logging.write_hex_data(octal_str)
            tag = self.tag_in
        elif type == 'DEC':
            for byte in data:
                octal_str = format(byte, '03d')
                self.text_buffer.insert(self.text_iter_end, octal_str)
                self.text_buffer.insert(self.text_iter_end, ' ')
                self.logging.write_hex_data(octal_str)
            tag = self.tag_in
        elif type == 'ASCII':
            line = data.decode('utf-8').strip()
            print("line " + line)
            self.text_buffer.insert(self.text_iter_end, line)
            self.logging.write_data(line)
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
        """"
        Display a arrow RX or TX
        """
        is_arrow = self.settings.get_boolean("arrow")

        if type == 'TX':
            arrow = '<-- '  # TX
        else:
            arrow = '--> '  # RX

        if is_arrow:
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
        """
        Add timestamp if needed
        """
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


    def insert_line_end_to_text_view(self, direction):
        """
        Add line end for text-view and real
        """
        show_line_end = self.settings.get_boolean("show-line-end")

        if direction == 'TX':
            index = self.settings.get_int("saved-serial-tx-line-end-index")
            show_end = self.serial_tx_line_endings[index]
        if direction == 'RX':
            index = self.settings.get_int("saved-serial-rx-line-end-index")
            print(index)
            if index == 4: #None
                show_end = ''
            else:
                show_end = self.serial_rx_line_endings[index]

        # Add line end for show
        if show_line_end:

            # Buffer
            self.text_buffer = self.input_text_view.get_buffer()

            # Start mark
            line_end_start_mark = self.text_buffer.create_mark('line_end_start_mark', self.text_buffer.get_end_iter(), True)

            # Insert line end
            self.text_buffer.insert(self.text_iter_end, show_end)

            # End mark
            line_end_end_mark = self.text_buffer.create_mark('line_end_end_mark', self.text_buffer.get_end_iter(), True)

            # Tag
            self.text_buffer.apply_tag(self.tag_line_end, self.text_buffer.get_iter_at_mark(line_end_start_mark), self.text_buffer.get_iter_at_mark(line_end_end_mark))

            # Log
            self.logging.write_data(show_end)
        # Add real line end
        if index == 1:
            self.text_buffer.insert(self.text_iter_end, '\r')
            # Log
            self.logging.write_data('\r')
        elif index == 2:
            self.text_buffer.insert(self.text_iter_end, '\r\n')
            # Log
            self.logging.write_data('\r\n')
        elif index == 3:
            self.text_buffer.insert(self.text_iter_end, ';')
            # Log
            self.logging.write_data(';')
        elif index == 4: #none
            self.text_buffer.insert(self.text_iter_end, '')
            # Log
            self.logging.write_data('')
        else:
            self.text_buffer.insert(self.text_iter_end, '\n')
            # Log
            self.logging.write_data('\n')


    def btn_send(self, action, _):
        """
        Button Send action
        """
        cmd_buffer = self.send_cmd_entry.get_buffer()
        data = cmd_buffer.get_text()
        self.send_to_serial(data)
        cmd_buffer.delete_text(0, len(data))


    def on_key_enter_pressed(self, entry):
        """
        Send cmd or Enter key pressed
        """
        cmd_buffer = self.send_cmd_entry.get_buffer()
        data = cmd_buffer.get_text()
        self.send_to_serial(data)

        # Ad to history
        cmd = data.strip()
        if cmd: # Don't store empty commands
            self.send_cmd_history.append(cmd)

            # Enforce maximum history size
            if len(self.send_cmd_history) > self.send_cmd_history_max_size:
                # Remove the oldest command
                self.send_cmd_history.pop(0)

            self.send_cmd_history_index = len(self.send_cmd_history)
            self.send_cmd_current = ""
        # Kustuta puhver
        cmd_buffer.delete_text(0, len(data))


    def send_to_serial(self, data):
        """
        Write data to Serial port
        """
        end = ''
        index = self.get_TX_line_end_saved

        if index == 0:
            text_view_end = '\\n'
            end = '\n'
        elif index == 1:
            end = '\r'
        elif index == 2:
            end = '\r\n'

        data = data + end
        if self.tauno_serial.is_open:
            self.tauno_serial.write(data)
        else:
            print("Send cmd: Serial is not Open")

        self.insert_time_to_text_view()
        self.insert_arrow_to_text_view('TX')
        self.insert_data_to_text_view(data, 'TX')
        self.insert_line_end_to_text_view('TX')


    def notify(self, message):
        """ """
        display_notifications = self.settings.get_boolean("notifications")

        if display_notifications:
            self.toast_overlay.add_toast(Adw.Toast(title=message))


    def on_port_drop_down_changed(self, widget, param):
        """ When user selects new port """
        try:
            selected_item = widget.get_selected_item()
            selected_str = selected_item.get_string()
            print(f"Selected port: {selected_str}")
            # Add to Info Sidebar:
            self.info_port_value.set_label(selected_str)
            # save port to settings
            self.settings.set_string("port-str", selected_str)
            # Get info
            self.get_port_info(selected_str)
        except Exception as ex:
            print("Ports are not available!")
            #print("Port selection error:", ex)


    def on_baud_drop_down_changed(self, widget, param):
        """ When user selects new baud rate """
        selected_item = widget.get_selected_item()

        selected_str = selected_item.get_string()
        print(f"Selected baud: {selected_str}")
        # Add to Info Sidebar:
        self.info_baud_value.set_label(selected_str)
        # save baud settings to settings
        baud_index_new = widget.get_selected()
        baud_index_new = int(baud_index_new)
        print(f"Baud index: {baud_index_new}")
        self.settings.set_int("baud-index", baud_index_new)


    def get_port_info(self, port_name):
        """ Get connected Device Info from serial port """
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if port.device == port_name:
                #print(f"Port          : {port.device}")

                print(f"Name          : {port.name}")
                if port.name == None:
                    self.info_Name.set_label("None")
                else:
                    self.info_Name.set_label(port.name)

                print(f"Description   : {port.description}")
                if port.description == None:
                    self.info_Description.set_label("None")
                else:
                    self.info_Description.set_label(port.description)

                print(f"HWID          : {port.hwid}")#raw hex
                self.parse_hwid(port.hwid)

                print(f"VID           : {port.vid}")
                #self.info_VID.set_label(str(port.vid))#int

                print(f"PID           : {port.pid}")
                #self.info_PID.set_label(str(port.pid))#int

                print(f"Serial Number : {port.serial_number}")
                if port.serial_number == None:
                    self.info_Serial_Number.set_label("None")
                else:
                    self.info_Serial_Number.set_label(str(port.serial_number))

                print(f"Location      : {port.location}")
                if port.location == None:
                    self.info_Location.set_label("None")
                else:
                    self.info_Location.set_label(port.location)

                print(f"Manufacturer  : {port.manufacturer}")
                if port.manufacturer == None:
                    self.info_Manufacturer.set_label("None")
                else:
                    self.info_Manufacturer.set_label(port.manufacturer)

                print(f"Product       : {port.product}")
                if port.product == None:
                    self.info_Product.set_label("None")
                else:
                    self.info_Product.set_label(port.product)

                print(f"Interface     : {port.interface}")
                if port.interface == None:
                    self.info_Interface.set_label("None")
                else:
                    self.info_Interface.set_label(port.interface)
                break # Exit loop

                # Try to open and query serial settings
                """
                try:
                    with serial.Serial(port.device, timeout=1) as ser:
                        print("Opened successfully.")
                        print(f"Baudrate      : {ser.baudrate}")
                        print(f"Bytesize      : {ser.bytesize}")
                        print(f"Parity        : {ser.parity}")
                        print(f"Stopbits      : {ser.stopbits}")
                        print(f"Timeout       : {ser.timeout}")
                except Exception as e:
                    print(f"Could not open port: {e}")
                break
                """

    def parse_hwid(self, hwid_str):
        """
        Split HWID
        http://www.linux-usb.org/usb.ids
        """
        result = {}
        # Match VID and PID
        vid_pid_match = re.search(r'VID:PID=([0-9A-Fa-f]+):([0-9A-Fa-f]+)', hwid_str)
        if vid_pid_match:
            result['VID'] = vid_pid_match.group(1)
            result['PID'] = vid_pid_match.group(2)
            self.info_VID.set_label(str(result['VID']))#hex
            self.info_PID.set_label(str(result['PID']))#hex

            vendor = usb_db.get(result['VID'], {})
            vendor_name = vendor.get("name")
            product = vendor.get("products", {}).get(result['PID'])
            # Add to Sidebar
            if vendor_name == None:
                self.info_VID_Vendor.set_label("None")
            else:
                self.info_VID_Vendor.set_label(vendor_name.strip())
            if product == None:
                self.info_PID_Product.set_label("None")
            else:
                self.info_PID_Product.set_label(product.strip())


        # Match Serial Number
        ser_match = re.search(r'SER=([\w\d]+)', hwid_str)
        if ser_match:
            result['Serial'] = ser_match.group(1)

        # Match Location
        loc_match = re.search(r'LOCATION=([\d\-\.]+)', hwid_str)
        if loc_match:
            result['Location'] = loc_match.group(1)

    def on_ui_tx_end_changed(self, drop_down, g_param_object):
        """
        Function called when Serial Line End selection is changed in App preferences
        """
        # Get selected index
        string_object = drop_down.get_selected_item()
        index = drop_down.get_selected()
        print(f'Selected TX Line End Pos: {index} val: {string_object.get_string()}')
        # Save index
        if self.get_TX_line_end_saved != index:
            print("Saving TX Line End index")
            self.settings.set_int("saved-serial-tx-line-end-index", index)
            # Reload setting
            self.get_TX_line_end_saved = self.settings.get_int("saved-serial-tx-line-end-index")


    def on_ui_rx_end_changed(self, drop_down, g_param_object):
        """
        Function called when Serial Line End selection is changed in App preferences
        """
        # Get selected index
        string_object = drop_down.get_selected_item()
        index = drop_down.get_selected()
        print(f'Selected RX Line End Pos: {index} val: {string_object.get_string()}')
        # Save index
        if self.get_RX_line_end_saved != index:
            print("Saving RX Line End index")
            self.settings.set_int("saved-serial-rx-line-end-index", index)
            # Reload setting
            self.get_RX_line_end_saved = self.settings.get_int("saved-serial-rx-line-end-index")
