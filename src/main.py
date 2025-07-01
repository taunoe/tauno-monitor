# main.py
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

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Adw, Gtk, Gio, GLib, Gdk
from .window import TaunoMonitorWindow
from .preferences import TaunoPreferencesWindow
import os
import gettext, locale

APP_VERSION = '0.2.5'

class TaunoMonitorApplication(Adw.Application):
    """The main application singleton class."""

    # Serial byte sizes
    serial_data_bits = ['5 Bits', '6 Bits', '7 Bits', '8 Bits']
    # Serial data formats
    serial_data_formats = ['ASCII', 'HEX', 'BIN', 'DEC', 'OCT']
    # Serial parities
    serial_parities = ['None', 'Even', 'Odd', 'Mark', 'Space']
    serial_stop_bits = ['1', '1.5', '2']

     # Also in: window.py insert_line_end_to_text_view()!!!
    serial_tx_line_endings = ['\\n', '\\r', '\\r\\n', 'None']
    serial_rx_line_endings = ['\\n', '\\r', '\\r\\n', ';']


    def __init__(self, version):
        super().__init__(application_id='art.taunoerik.tauno-monitor',
                         #flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
                         #flags=Gio.ApplicationFlags.NON_UNIQUE
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         )

        self.version = version

        self.settings = Gio.Settings(schema_id="art.taunoerik.tauno-monitor")

        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

        # Add the "new-window" action
        new_window_action = Gio.SimpleAction.new("new-window", None)
        new_window_action.connect("activate", self.on_new_window)
        self.add_action(new_window_action)

        # Shortcuts
        self.set_accels_for_action('win.open', ['<Ctrl>o'])

        # Get saved Color Mode
        self.dark_mode_saved = self.settings.get_boolean("dark-mode")
        style_manager = Adw.StyleManager.get_default()

        if self.dark_mode_saved: # is True
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)

        # Folder dialog
        self.filedialog = Gtk.FileDialog()
        # Get saved log folder
        self.log_folder_path = self.settings.get_string("log-folder")
        # If default get user home
        if self.log_folder_path == '~':
            self.log_folder_path = os.path.expanduser("~")

        # Color dialog
        self.color_dialog = Gtk.ColorDialog.new()
        self.color_dialog.set_modal(modal=True)
        self.color_dialog.set_title(title='Select a color.')

        # Language
        localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
        locale.setlocale(locale.LC_ALL, '')
        gettext.bindtextdomain('art.taunoerik.tauno-monitor', localedir)
        gettext.textdomain('art.taunoerik.tauno-monitor')
        _ = gettext.gettext

    """
    Called when the application is activated.
    We raise the application's main window, creating it if necessary.
    """
    def do_activate(self):
        #self.win = self.props.active_window
        #self.win = TaunoMonitorWindow(application=self)
        #self.win.present()
        # TODO: Every activation creates a new, independent window?
        #win = self.props.active_window
        self.win = TaunoMonitorWindow(application=self)
        self.win.present()

    def on_new_window(self):
        # This function is called when the "new-window" action is triggered
        self.do_activate()


    def do_command_line(self, command_line: None):
        """
        options = command_line.get_arguments()[1:]
        if "--new-window" in options:
            self.on_new_window()
        else:
            self.do_activate()
        return 0
        """

        args = command_line.get_arguments()[1:] # Skip the program name
        if "--new-window" in args:
            self.on_new_window()
        else:
            self.do_activate()
        return 0



    #def do_startup(self):
        #Gtk.Application.do_startup(self)
        # Any other startup logic...


    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.
        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


    def on_guide_action(self, widget, _):
        """Callback for the app.guide action."""
        guide = Adw.tWindow(transient_for=self.props.active_window)
        guide.present()


    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(transient_for=self.props.active_window,
                                application_name='Tauno Monitor',
                                application_icon='art.taunoerik.tauno-monitor',
                                website='https://github.com/taunoe/tauno-monitor',
                                developer_name='Tauno Erik',
                                version=APP_VERSION,
                                developers=['Tauno Erik'],
                                copyright='© 2023-2025 Tauno Erik')
        about.present()


    def on_preferences_action(self, widget, _):
        """ Dispplay Preferences Window """
        #preferences_window = TaunoPreferencesWindow(transient_for=self.props.active_window)
        #preferences_window.present()
        TaunoPreferencesWindow.on_guide_action(self, widget, _)


    def on_time_color_selected(self, color_dialog_button, g_param_boxed):
        """ Get and save time tag color """
        gdk_rgba = color_dialog_button.get_rgba()
        print("New Time color " + gdk_rgba.to_string())
        # Save color settings
        self.settings.set_string("saved-time-color", gdk_rgba.to_string())
        # Update tag
        self.win.update_time_tag()

    def reset_time_color_button_action(self, widget):
        """ Reset time color to default one """
        default_color = Gdk.RGBA()
        default_color.parse(self.settings.get_string("default-time-color"))
        self.settings.set_string("saved-time-color", default_color.to_string())
        self.time_color_dialog_button.set_rgba(default_color)

    def on_arrow_color_selected(self, color_dialog_button, g_param_boxed):
        """ Get and save Arrow tag color """
        gdk_rgba = color_dialog_button.get_rgba()
        print("New Arrow color " + gdk_rgba.to_string())
        # Save color settings
        self.settings.set_string("saved-arrow-color", gdk_rgba.to_string())
        # Update tag
        self.win.update_arrow_tag()

    def reset_arrow_color_button_action(self, widget):
        print("Reset arrow color")
        default_color = Gdk.RGBA()
        default_color.parse(self.settings.get_string("default-arrow-color"))
        self.settings.set_string("saved-arrow-color", default_color.to_string())
        self.arrow_color_dialog_button.set_rgba(default_color)

    def on_out_color_selected(self, color_dialog_button, g_param_boxed):
        """ Get and save Out tag color """
        gdk_rgba = color_dialog_button.get_rgba()
        print("New TX color " + gdk_rgba.to_string())
        # Save color settings
        self.settings.set_string("saved-out-color", gdk_rgba.to_string())
        # Update tag
        self.win.update_out_tag()

    def reset_out_color_button_action(self, widget):
        #print("Reset TX color")
        default_color = Gdk.RGBA()
        default_color.parse(self.settings.get_string("default-out-color"))
        self.settings.set_string("saved-out-color", default_color.to_string())
        self.out_color_dialog_button.set_rgba(default_color)

    """
    Get and save line end tag color
    """
    def on_show_line_end_color_selected(self, color_dialog_button, g_param_boxed):
        gdk_rgba = color_dialog_button.get_rgba()
        print("Line End color " + gdk_rgba.to_string())
        # Save color settings
        self.settings.set_string("saved-show-line-end-color", gdk_rgba.to_string())
        # Update tag
        self.win.update_line_end_tag()

    """
    """
    def reset_line_end_color_button_action(self, widget):
        print("reset_line_end_color_button_action")
        default_color = Gdk.RGBA()
        default_color.parse(self.settings.get_string("default-show-line-end-color"))
        self.settings.set_string("saved-show-line-end-color", default_color.to_string())
        self.show_line_end_color_dialog_button.set_rgba(default_color)


    def on_in_color_selected(self, color_dialog_button, g_param_boxed):
        """ Get and save In tag color """
        gdk_rgba = color_dialog_button.get_rgba()
        print("New RX color " + gdk_rgba.to_string())
        # Save color settings
        self.settings.set_string("saved-in-color", gdk_rgba.to_string())
        # Update tag
        self.win.update_in_tag()

    def reset_in_color_button_action(self, widget):
        #print("Reset RX color")
        default_color = Gdk.RGBA()
        default_color.parse(self.settings.get_string("default-in-color"))
        self.settings.set_string("saved-in-color", default_color.to_string())
        self.in_color_dialog_button.set_rgba(default_color)

    # ajutine!
    def on_color_selected(self, color_dialog_button, g_param_boxed):
        gdk_rgba = color_dialog_button.get_rgba()
        print(f'Color RGB = {gdk_rgba.to_string()}')
        print(f'Alpha = {gdk_rgba.alpha}')
        print(f'Red = {gdk_rgba.red}')
        print(f'Green = {gdk_rgba.green}')
        print(f'Blue = {gdk_rgba.blue}')

    def select_log_folder_button_action(self, widget):
        """ Button to select logging folder action """
        self.filedialog.select_folder(
            self.preferences, cancellable=None,
            callback=self.on_filedialog_select_folder)


    def on_filedialog_select_folder(self, filedialog, task):
        """ Dialog to select logging folder """
        try:
            # Folder selection dialog
            folder = filedialog.select_folder_finish(task)
        except GLib.GError:
            return

        if folder is not None:
            self.log_folder_path = folder.get_path()

            # If not a folder
            if (os.path.exists(self.log_folder_path) == False):
                self.win.toast_overlay.add_toast(Adw.Toast(title=f"{self.log_folder_path} is not a folder!"))

            # Is it writeable?
            test_file_path = self.log_folder_path+'/tauno_monitor_test.txt'
            # We create test file and then will remove it
            try:
                with open(test_file_path, 'w') as file:
                    file.write('Hello!')
                    file.close()
                    os.remove(test_file_path)
            except IOError as error:
                self.win.toast_overlay.add_toast(Adw.Toast(title=f"No write permission on this directory!"))

            # Update label on preferences
            self.entry_buffer.set_text(self.log_folder_path, len(self.log_folder_path))
            # Update saved settings
            self.settings.set_string("log-folder", self.log_folder_path)

    """
    Function called when Serial RX data format is changed in App preferences
    """
    def rx_data_format_action(self, drop_down, g_param_object):
        string_object = drop_down.get_selected_item()
        index = drop_down.get_selected()
        new_format = string_object.get_string()
        #print(f'Position: {index} - value: {string_object.get_string()}')
        # save settings
        self.settings.set_string("saved-serial-rx-data-format", new_format)
        # update pos
        self.win.get_rx_format_saved = self.settings.get_string("saved-serial-rx-data-format")

        # End the HEX data block with a newline when starting ASCII
        if self.win.get_rx_format_saved != 'HEX':
            #print("HEX --> ASCII")
            data = '\n'
            self.win.insert_data_to_text_view(data.encode(), 'ASCII')
            self.win.logging.hex_counter = 0;
            self.win.logging.write_data('')


    """
    """
    def reset_data_format_button_action(self, widget):
        print("Reset data format")
        # Get deffault
        default = self.settings.get_string("default-serial-rx-data-format")
        # Save setting
        self.settings.set_string("saved-serial-rx-data-format", default)
        # Reload UI
        index = self.serial_data_formats.index(default)
        self.rx_format.set_selected(position=index)


    """
    Function called when Serial Data Bits selection is changed in App preferences
    """
    def serial_data_bits_action(self, drop_down, g_param_object):
        # Get selected index
        string_object = drop_down.get_selected_item()
        index = drop_down.get_selected()
        print(f'Selected Data Bit Pos: {index} val: {string_object.get_string()}')
        # Save index
        if self.win.get_data_bit_saved != index:
            print("Saving Serial Data Bit index")
            self.settings.set_int("saved-serial-data-bit-index", index)
            # Reload setting
            self.win.get_data_bit_saved = self.settings.get_int("saved-serial-data-bit-index")


    """
    Function to reset Serial Data Bit to default value
    """
    def reset_data_bits_button_action(self, widget):
        defalut_value = self.settings.get_int("default-serial-data-bit-index")
        print(f"Reset Data Bit index to: {defalut_value}")
        # save setting
        self.settings.set_int("saved-serial-data-bit-index", defalut_value)
        # reload setting
        self.win.get_data_bit_saved = self.settings.get_int("saved-serial-data-bit-index")
        # reload UI from preferences.py
        self.data_bits_drop_down.set_selected(position=defalut_value)


    """
    Function called when Serial Parity selection is changed in App preferences
    """
    def serial_parity_action(self, drop_down, g_param_object):
        # Get selected index
        string_object = drop_down.get_selected_item()
        index = drop_down.get_selected()
        print(f'Selected Parity Pos: {index} val: {string_object.get_string()}')
        # Save index
        if self.win.get_parity_saved != index:
            print("Saving Serial Parity index")
            self.settings.set_int("saved-serial-parity-index", index)
            # Reload setting
            self.win.get_parity_saved = self.settings.get_int("saved-serial-parity-index")


    """
    Function to reset Serial Parity to default value
    """
    def reset_parity_button_action(self, widget):
        defalut_value = self.settings.get_int("default-serial-parity-index")
        print(f"Reset Parity index to: {defalut_value}")
        # Save setting
        self.settings.set_int("saved-serial-parity-index", defalut_value)
        # reload setting
        self.win.get_parity_saved = self.settings.get_int("saved-serial-parity-index")
        # reload UI from preferences.py
        self.parity_drop_down.set_selected(position=defalut_value)


    """
    Function called when Serial Stop Bits selection is changed in App preferences
    """
    def serial_stop_bits_action(self, drop_down, g_param_object):
        # Get selected index
        string_object = drop_down.get_selected_item()
        index = drop_down.get_selected()
        print(f'Selected Stop Bit Pos: {index} val: {string_object.get_string()}')
        # Save index
        if self.win.get_stop_bit_saved != index:
            print("Saving Serial Stop Bit index")
            self.settings.set_int("saved-serial-stop-bit-index", index)
            # Reload setting
            self.win.get_stop_bit_saved = self.settings.get_int("saved-serial-stop-bit-index")


    """
    Function to reset Serial Stop Bit to default value
    """
    def reset_stop_bits_button_action(self, widget):
        defalut_value = self.settings.get_int("default-serial-stop-bit-index")
        print(f"Reset Stop Bit index to: {defalut_value}")
        # save setting
        self.settings.set_int("saved-serial-stop-bit-index", defalut_value)
        # reload setting
        self.win.get_stop_bit_saved = self.settings.get_int("saved-serial-stop-bit-index")
        # reload UI from preferences.py
        self.stop_bits_drop_down.set_selected(position=defalut_value)


    """
    Function called when Serial Line End selection is changed in App preferences
    """
    def serial_TX_line_end_action(self, drop_down, g_param_object):
        # Get selected index
        string_object = drop_down.get_selected_item()
        index = drop_down.get_selected()
        print(f'Selected Line End Pos: {index} val: {string_object.get_string()}')
        # Save index
        if self.win.get_TX_line_end_saved != index:
            print("Saving Serial Line End index")
            self.settings.set_int("saved-serial-tx-line-end-index", index)
            # Reload setting
            self.win.get_TX_line_end_saved = self.settings.get_int("saved-serial-tx-line-end-index")


    """
    Function to reset Serial Line End to default value
    """
    def reset_TX_line_end_button_action(self, widget):
        defalut_value = self.settings.get_int("default-serial-tx-line-end-index")
        print(f"Reset Line End index to: {defalut_value}")
        # save setting
        self.settings.set_int("saved-serial-tx-line-end-index", defalut_value)
        # reload setting
        self.win.get_TX_line_end_saved = self.settings.get_int("saved-serial-tx-line-end-index")
        # reload UI from preferences.py
        self.TX_line_end_drop_down.set_selected(position=defalut_value)


    """
    Function called when Serial Line End selection is changed in App preferences
    RX
    """
    def serial_RX_line_end_action(self, drop_down, g_param_object):
        # Get selected index
        string_object = drop_down.get_selected_item()
        index = drop_down.get_selected()
        print(f'Selected Line End Pos: {index} val: {string_object.get_string()}')
        # Save index
        if self.win.get_RX_line_end_saved != index:
            print("Saving Serial Line End index")
            self.settings.set_int("saved-serial-rx-line-end-index", index)
            # Reload setting
            self.win.get_RX_line_end_saved = self.settings.get_int("saved-serial-rx-line-end-index")


    """
    Function to reset Serial Line End to default value
    RX
    """
    def reset_RX_line_end_button_action(self, widget):
        defalut_value = self.settings.get_int("default-serial-rx-line-end-index")
        print(f"Reset Line End index to: {defalut_value}")
        # save setting
        self.settings.set_int("saved-serial-rx-line-end-index", defalut_value)
        # reload setting
        self.win.get_RX_line_end_saved = self.settings.get_int("saved-serial-rx-line-end-index")
        # reload UI from preferences.py
        self.RX_line_end_drop_down.set_selected(position=defalut_value)


    """
    """
    def dark_mode_switch_action(self, widget, state):
        dark_mode = state

        style_manager = Adw.StyleManager.get_default()

        if dark_mode: # is True
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        self.settings.set_boolean("dark-mode", dark_mode)


    """
    Get notifications settings change and save
    """
    def notifications_switch_action(self, widget, state):
        notifications_state = state
        # Save settings
        self.settings.set_boolean("notifications", notifications_state)


    """
    Get timestamp settings change and save
    """
    def timestamp_switch_action(self, widget, state):
        timestamp_state = state
        # Save settings
        self.settings.set_boolean("timestamp", timestamp_state)


    """
    Get show line endings settings change and save
    """
    def show_line_end_switch_action(self, widget, state):
        show_line_end_state = state
        # Save settings
        self.settings.set_boolean("show-line-end", show_line_end_state)


    def text_size_action(self, action):
        new_size = action.get_value_as_int()
        self.win.change_font_size(new_size)
        # Save settings
        self.settings.set_int("font-size", new_size)


    def on_font_selected(self, font_dialog_button, g_param_boxed):
        font_selected = font_dialog_button.get_font_desc()
        print(f'Font name: {font_selected.get_family()}')

        new_size = int(font_selected.get_size() / 1024)
        print(f'Font size: {new_size}')
        self.win.change_font_size(new_size)
        # Save settings
        self.settings.set_int("font-size", new_size)

        print(f'Font style: {font_selected.get_style()}')
        print(f'Font weight: {font_selected.get_weight()}')


def main(version):
    app = TaunoMonitorApplication(version)
    return app.run(sys.argv)


