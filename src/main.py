# main.py
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

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw, GLib
from .window import TaunoMonitorWindow
import os

#import gettext
#import locale
#from os import path


# Set up translation for the application
#locale.setlocale(locale.LC_ALL, '')
#locale.bindtextdomain('tauno-monitor', os.path.join(os.path.dirname(__file__), 'locales'))
#gettext.bindtextdomain('tauno-monitor', os.path.join(os.path.dirname(__file__), 'locales'))
#gettext.textdomain('tauno-monitor')
#_ = gettext.gettext


class TaunoMonitorApplication(Adw.Application):
    """The main application singleton class."""

    byte_sizes = ['FIVEBITS', 'SIXBITS', 'SEVENBITS', 'EIGHTBITS']  # serial
    data_formats = ['ASCII', 'HEX']


    def __init__(self):
        super().__init__(application_id='art.taunoerik.tauno-monitor',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

        self.settings = Gio.Settings(schema_id="art.taunoerik.tauno-monitor")

        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)


        # shortcut
        self.set_accels_for_action('win.open', ['<Ctrl>o'])

        # Get saved Color Mode
        self.dark_mode_saved = self.settings.get_boolean("dark-mode")
        style_manager = Adw.StyleManager.get_default()

        if self.dark_mode_saved: # is True
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)

        # Select log folder
        self.filedialog = Gtk.FileDialog()
        # Get saved log folder
        self.log_folder_path = self.settings.get_string("log-folder")
        # If default get user home
        if self.log_folder_path == '~':
            self.log_folder_path = os.path.expanduser("~")



    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        """
        self.win = self.props.active_window
        if not self.win:
            self.win = TaunoMonitorWindow(application=self)
        self.win.present()
        """
        self.win = self.props.active_window
        self.win = TaunoMonitorWindow(application=self)
        self.win.present()


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
                                version='0.1.16',
                                developers=['Tauno Erik'],
                                copyright='© 2023-2024 Tauno Erik')
        about.present()



    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        self.preferences = Adw.PreferencesWindow(transient_for=self.props.active_window)

        # Title
        settings_page = Adw.PreferencesPage(title="Preferences")
        settings_page.set_icon_name("applications-system-symbolic")
        self.preferences.add(settings_page)

        ## UI group
        ui_group = Adw.PreferencesGroup(title="Appearance")
        settings_page.add(ui_group)

        ### Text size
        font_row = Adw.ActionRow(title="Text size")
        ui_group.add(font_row)
        spin_adjustment = Gtk.Adjustment(value=self.win.font_size_saved,
                                 lower=2,
                                 upper=100,
                                 step_increment=1)
        font_spin_button = Gtk.SpinButton(valign = Gtk.Align.CENTER,
                                    adjustment=spin_adjustment,
                                    climb_rate=1,
                                    digits=0)
        font_row.add_suffix(font_spin_button)
        font_spin_button.connect("value-changed", self.text_size_action)

        ### Dark Mode
        dark_mode_row = Adw.ActionRow(title="Dark Mode")
        ui_group.add(dark_mode_row)
        dark_mode_switch = Gtk.Switch(valign = Gtk.Align.CENTER,)
        dark_mode_row.add_suffix(dark_mode_switch)
        # Current mode: True is Dark
        dark_mode_switch.set_active(self.settings.get_boolean("dark-mode"))
        dark_mode_switch.connect("state-set", self.dark_mode_switch_action)

        ### Notifications
        notifications_row = Adw.ActionRow(title="Notifications")
        ui_group.add(notifications_row)
        notifications_switch = Gtk.Switch(valign = Gtk.Align.CENTER,)
        notifications_row.add_suffix(notifications_switch)
        # Get saved state:
        notifications_switch.set_active(self.settings.get_boolean("notifications"))
        notifications_switch.connect("state-set", self.notifications_switch_action)

        ## Data group
        data_group = Adw.PreferencesGroup(title="Data")
        settings_page.add(data_group)

        ### Data Format
        rx_row = Adw.ActionRow(title="RX data format")
        data_group.add(rx_row)
        rx_format = Gtk.DropDown.new_from_strings(strings=self.data_formats)
        rx_format.set_valign(Gtk.Align.CENTER)
        # get saved index
        index = self.data_formats.index(self.win.rx_format_saved)
        rx_format.set_selected(position=index)
        rx_row.add_suffix(rx_format)
        rx_format.connect("notify::selected-item", self.rx_data_format_action)

        ### Timestamp
        timestamp_row = Adw.ActionRow(title="Timestamp")
        data_group.add(timestamp_row)
        timestamp_switch = Gtk.Switch(valign = Gtk.Align.CENTER,)
        timestamp_row.add_suffix(timestamp_switch)
        # Get saved state:
        timestamp_switch.set_active(self.settings.get_boolean("timestamp"))
        timestamp_switch.connect("state-set", self.timestamp_switch_action)

        ## Logging group
        logging_group = Adw.PreferencesGroup(title="Logging")
        settings_page.add(logging_group)
        log_folder_row = Adw.ActionRow(title="Folder")
        logging_group.add(log_folder_row)
        #entry
        log_folder_entry = Gtk.Entry.new()
        log_folder_entry.set_valign(Gtk.Align.CENTER)
        log_folder_entry.set_hexpand(True)
        log_folder_row.add_suffix(log_folder_entry)
        self.entry_buffer = log_folder_entry.get_buffer()
        self.entry_buffer.set_text(self.log_folder_path, len(self.log_folder_path))
        #button
        select_log_folder_button = Gtk.Button(label="Select Folder")
        select_log_folder_button.set_icon_name("search-folder-symbolic")
        select_log_folder_button.set_valign(Gtk.Align.CENTER)
        log_folder_row.add_suffix(select_log_folder_button)
        select_log_folder_button.connect("clicked", self.select_log_folder_button_action)

        """
        TODO
        ## Serial group
        serial_group = Adw.PreferencesGroup(title="Serial")
        settings_page.add(serial_group)
        ### Byte-size row
        bytesize_row = Adw.ActionRow(title="Byte-size")
        serial_group.add(bytesize_row)
        bytesize_drop_down = Gtk.DropDown.new_from_strings(strings=self.byte_sizes)
        bytesize_drop_down.set_valign(Gtk.Align.CENTER)

        bytesize_drop_down.set_selected(position=3)
        bytesize_row.add_suffix(bytesize_drop_down)
        #bytesize_drop_down.connect('notify::selected-item', self.on_selected_item)
        """
        #
        self.preferences.present()


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
                    file.write('hello!')
                    file.close()
                    os.remove(test_file_path)
            except IOError as error:
                self.win.toast_overlay.add_toast(Adw.Toast(title=f"No write permission on this directory!"))

            # Update label on preferences
            self.entry_buffer.set_text(self.log_folder_path, len(self.log_folder_path))
            # Update saved settings
            self.settings.set_string("log-folder", self.log_folder_path)


    def rx_data_format_action(self, drop_down, g_param_object):
        string_object = drop_down.get_selected_item()
        index = drop_down.get_selected()
        new_format = string_object.get_string()
        #print(f'Position: {index} - value: {string_object.get_string()}')
        # save settings
        self.settings.set_string("rx-data-format", new_format)
        # update pos
        self.win.rx_format_saved = self.settings.get_string("rx-data-format")


    def dark_mode_switch_action(self, widget, state):
        dark_mode = state

        style_manager = Adw.StyleManager.get_default()

        if dark_mode: # is True
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        self.settings.set_boolean("dark-mode", dark_mode)


    def notifications_switch_action(self, widget, state):
        """ Get notifications settings change and save """
        notifications_state = state

        # Save settings
        self.settings.set_boolean("notifications", notifications_state)

    def timestamp_switch_action(self, widget, state):
        """ Get timestamp settings change and save """
        timestamp_state = state

        # Save settings
        self.settings.set_boolean("timestamp", timestamp_state)


    def text_size_action(self, action):
        new_size = action.get_value_as_int()
        self.win.change_font_size(new_size)
        # Save settings
        self.settings.set_int("font-size", new_size)


def main(version):
    app = TaunoMonitorApplication()
    return app.run(sys.argv)

