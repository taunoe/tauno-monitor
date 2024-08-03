# File:    guide.py
# Started: 03.08.2024
# Author:  Tauno Erik
# Displays Guide window

from gi.repository import Adw, Gtk, Gio, GObject, GLib, Gdk

GUIDE_TEXT = """sudo usermod -a -G dialout $USER\n\
sudo usermod -a -G plugdev $USER"""

@Gtk.Template(resource_path='/art/taunoerik/tauno-monitor/guide.ui')
class TaunoGuideWindow(Adw.Window):
    __gtype_name__ = 'TaunoGuideWindow'

    text_buffer = Gtk.Template.Child('text_buffer')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Adding rendered text to Gtk.TextView.
        text_buffer_iter = self.text_buffer.get_end_iter()
        self.text_buffer.insert_markup(
            iter=text_buffer_iter,
            markup=GUIDE_TEXT,
            len=-1,
        )

    @Gtk.Template.Callback()
    def on_button_close_clicked(self, button):
        self.destroy()

