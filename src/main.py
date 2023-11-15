# main.py
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

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw, GLib
from .window import TaunoMonitorWindow


class TaunoMonitorApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='art.taunoerik.TaunoMonitor',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

        self.settings = Gio.Settings(schema_id="art.taunoerik.TaunoMonitor")

        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

        # shortcut
        self.set_accels_for_action('win.open', ['<Ctrl>o'])

        # Dark Mode
        dark_mode = self.settings.get_boolean("dark-mode")
        style_manager = Adw.StyleManager.get_default()

        if dark_mode:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            #style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)

        dark_mode_action = Gio.SimpleAction(name="dark-mode",
                                            state=GLib.Variant.new_boolean(dark_mode))
        dark_mode_action.connect("activate", self.toggle_dark_mode)
        dark_mode_action.connect("change-state", self.change_color_scheme)
        self.add_action(dark_mode_action)


    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = TaunoMonitorWindow(application=self)
        win.present()


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


    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(transient_for=self.props.active_window,
                                application_name='Tauno Monitor',
                                application_icon='art.taunoerik.TaunoMonitor',
                                website='https://github.com/taunoe/tauno-monitor',
                                developer_name='Tauno Erik',
                                version='0.1.0',
                                developers=['Tauno Erik'],
                                copyright='© 2023 Tauno Erik')
        about.present()

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print('app.preferences action activated')

    def toggle_dark_mode(self, action, _):
        """
        this callback toggles the state of the dark-mode action between “true” and “false”
        """
        state = action.get_state()
        old_state = state.get_boolean()
        new_state = not old_state
        action.change_state(GLib.Variant.new_boolean(new_state))

    def change_color_scheme(self, action, new_state):
        """
        this callback is responsible for switching the application’s color scheme using the AdwStyleManager API
        """
        dark_mode = new_state.get_boolean()
        style_manager = Adw.StyleManager.get_default()
        if dark_mode:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        action.set_state(new_state)
        self.settings.set_boolean("dark-mode", dark_mode)


def main(version):
    """The application's entry point."""
    app = TaunoMonitorApplication()
    return app.run(sys.argv)

