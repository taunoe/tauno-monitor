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

APP_VERSION = '0.2.11'

class TaunoMonitorApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self, version):
        super().__init__(application_id='art.taunoerik.tauno-monitor',
                         #flags=Gio.ApplicationFlags.NON_UNIQUE,
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         )

        self.version = version

        self.settings = Gio.Settings(schema_id="art.taunoerik.tauno-monitor")

        # menu actions
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)
        self.create_action('newwindow', self.on_newwindow)

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


    def do_activate(self):
        """
        Called when the application is activated.
        We raise the application's main window, creating it if necessary.
        """
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

    def on_newwindow(self, widget, param):
        """App Menu New Window action """
        print("New Window")
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

    def on_tool_baud_action(self, widget, _):
        """Callback for the app.tool_baud action."""
        tool_baud = Adw.tWindow(transient_for=self.props.active_window)
        tool_baud.present()


    def on_about_action(self, widget, param):
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


    def on_preferences_action(self, widget, param):
        """
        Presents the preferences window.
        """
        active_window = self.get_active_window()

        if not active_window:
            return

        preferences_window = TaunoPreferencesWindow(main_window=active_window, settings=self.settings, transient_for=self)
        preferences_window.present()

    # ajutine!
    def on_color_selected(self, color_dialog_button, g_param_boxed):
        gdk_rgba = color_dialog_button.get_rgba()
        print(f'Color RGB = {gdk_rgba.to_string()}')
        print(f'Alpha = {gdk_rgba.alpha}')
        print(f'Red = {gdk_rgba.red}')
        print(f'Green = {gdk_rgba.green}')
        print(f'Blue = {gdk_rgba.blue}')


def main(version):
    app = TaunoMonitorApplication(version)
    return app.run(sys.argv)


