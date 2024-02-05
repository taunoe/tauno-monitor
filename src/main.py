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

import gettext
import locale
from os import path

locale.bindtextdomain('tauno-monitor', path.join(path.dirname(__file__).split('tauno-monitor')[0],'locale'))
locale.textdomain('tauno-monitor')

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





    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        self.win = self.props.active_window
        if not self.win:
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
                                version='0.1.10',
                                developers=['Tauno Erik'],
                                copyright='© 2023-204 Tauno Erik')
        about.present()


    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        preferences = Adw.PreferencesWindow(transient_for=self.props.active_window)

        # Title
        settings_page = Adw.PreferencesPage(title="Preferences")
        settings_page.set_icon_name("applications-system-symbolic")
        preferences.add(settings_page)

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

        ### Dark Mode
        dark_mode_row = Adw.ActionRow(title="Dark Mode")
        ui_group.add(dark_mode_row)
        dark_mode_switch = Gtk.Switch(valign = Gtk.Align.CENTER,)
        dark_mode_row.add_suffix(dark_mode_switch)
        ### Current mode: True is Dark
        dark_mode_switch.set_active(self.settings.get_boolean("dark-mode"))

        ### Notifications
        notifications_row = Adw.ActionRow(title="Notifications")
        ui_group.add(notifications_row)
        notifications_switch = Gtk.Switch(valign = Gtk.Align.CENTER,)
        notifications_row.add_suffix(notifications_switch)
        # Get saved state:
        notifications_switch.set_active(self.settings.get_boolean("notifications"))

        ## Data group
        data_group = Adw.PreferencesGroup(title="Data")
        settings_page.add(data_group)
        rx_row = Adw.ActionRow(title="RX data format")
        data_group.add(rx_row)
        rx_format = Gtk.DropDown.new_from_strings(strings=self.data_formats)
        rx_format.set_valign(Gtk.Align.CENTER)
        # get saved index
        index = self.data_formats.index(self.win.rx_format_saved)
        rx_format.set_selected(position=index)
        rx_row.add_suffix(rx_format)
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
        preferences.present()

        # Connects
        font_spin_button.connect("value-changed", self.text_size_action)
        dark_mode_switch.connect("state-set", self.dark_mode_switch_action)
        notifications_switch.connect("state-set", self.notifications_switch_action)
        rx_format.connect("notify::selected-item", self.rx_data_format_action)

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


    def text_size_action(self, action):
        new_size = action.get_value_as_int()
        self.win.change_font_size(new_size)
        # Save settings
        self.settings.set_int("font-size", new_size)


def main(version):
    app = TaunoMonitorApplication()
    return app.run(sys.argv)

