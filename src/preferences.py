# File:    preferences.py
# Started: 03.08.2024
# Author:  Tauno Erik
# Displays Preferences window

from gi.repository import Adw, Gtk, Gio, GObject, GLib, Gdk

#@Gtk.Template(resource_path='/art/taunoerik/tauno-monitor/preferences.ui')
class TaunoPreferencesWindow(Adw.PreferencesWindow):
    __gtype_name__ = 'TaunoPreferencesWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)



    def on_guide_action(self, widget, _):
        self.preferences = Adw.PreferencesWindow(transient_for=self.props.active_window)
        self.preferences.set_default_size(width=500, height=800)
        self.preferences.set_size_request(width=500, height=800)

        # Title
        settings_page = Adw.PreferencesPage(title="Preferences")
        settings_page.set_icon_name("applications-system-symbolic")
        self.preferences.add(settings_page)

        ## UI group
        ui_group = Adw.PreferencesGroup(title="Appearance")
        settings_page.add(ui_group)


        # TODO font selection
        #font_dialog = Gtk.FontDialog.new()
        #font_dialog.set_modal(modal=True)
        #font_dialog.set_title(title='Select a font.')
        #font_dialog_row = Adw.ActionRow(title="Font")
        #ui_group.add(font_dialog_row)
        #font_dialog_button = Gtk.FontDialogButton.new(dialog=font_dialog)
        #font_dialog_button.set_valign(Gtk.Align.CENTER)
        #font_dialog_row.add_suffix(font_dialog_button)
        #font_dialog_button.connect('notify::font-desc', self.on_font_selected)

        ### Text size
        font_size_row = Adw.ActionRow(title="Text size")
        ui_group.add(font_size_row)
        spin_adjustment = Gtk.Adjustment(value=self.win.font_size_saved,
                                 lower=2,
                                 upper=100,
                                 step_increment=1)
        font_spin_button = Gtk.SpinButton(valign = Gtk.Align.CENTER,
                                    adjustment=spin_adjustment,
                                    climb_rate=1,
                                    digits=0)
        font_size_row.add_suffix(font_spin_button)
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
        data_group = Adw.PreferencesGroup(title="Data view")
        settings_page.add(data_group)

        ### Data Format
        rx_row = Adw.ActionRow(title="Format")
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

        # https://github.com/natorsc/python-gtk-pygobject?tab=readme-ov-file#gtkcolordialogbutton

        # Timestamp color
        time_color_row = Adw.ActionRow(title="Timestamp Color")
        # Color Dialog
        data_group.add(time_color_row)
        self.time_color_dialog_button = Gtk.ColorDialogButton.new(dialog=self.color_dialog)
        time_color = Gdk.RGBA()
        time_color.parse(self.settings.get_string("saved-time-color"))
        self.time_color_dialog_button.set_rgba(time_color)
        self.time_color_dialog_button.set_valign(Gtk.Align.CENTER)
        time_color_row.add_suffix(self.time_color_dialog_button)
        self.time_color_dialog_button.connect('notify::rgba', self.on_time_color_selected)
        # Reset color btn
        reset_time_color_button = Gtk.Button(label="Reset")
        reset_time_color_button.set_icon_name("arrow-circular-small-top-left-symbolic")
        reset_time_color_button.set_valign(Gtk.Align.CENTER)
        reset_time_color_button.set_has_frame(False)  # flat
        reset_time_color_button.set_tooltip_text("Reset")
        time_color_row.add_suffix(reset_time_color_button)
        reset_time_color_button.connect("clicked", self.reset_time_color_button_action)

        # Arrow color
        arrow_color_row = Adw.ActionRow(title="Arrow Color")
        # Color Dialog
        data_group.add(arrow_color_row)
        self.arrow_color_dialog_button = Gtk.ColorDialogButton.new(dialog=self.color_dialog)
        arrow_color = Gdk.RGBA()
        arrow_color.parse(self.settings.get_string("saved-arrow-color"))
        self.arrow_color_dialog_button.set_rgba(arrow_color)
        self.arrow_color_dialog_button.set_valign(Gtk.Align.CENTER)
        arrow_color_row.add_suffix(self.arrow_color_dialog_button)
        self.arrow_color_dialog_button.connect('notify::rgba', self.on_arrow_color_selected)
        # Reset color btn
        reset_arrow_color_button = Gtk.Button(label="Reset")
        reset_arrow_color_button.set_icon_name("arrow-circular-small-top-left-symbolic")
        reset_arrow_color_button.set_valign(Gtk.Align.CENTER)
        reset_arrow_color_button.set_has_frame(False)  # flat
        reset_arrow_color_button.set_tooltip_text("Reset")
        arrow_color_row.add_suffix(reset_arrow_color_button)
        reset_arrow_color_button.connect("clicked", self.reset_arrow_color_button_action)

        # Transmitted outgoing data color
        out_color_row = Adw.ActionRow(title="TX Color")
        # Color Dialog
        data_group.add(out_color_row)
        self.out_color_dialog_button = Gtk.ColorDialogButton.new(dialog=self.color_dialog)
        out_color = Gdk.RGBA()
        out_color.parse(self.settings.get_string("saved-out-color"))
        self.out_color_dialog_button.set_rgba(out_color)
        self.out_color_dialog_button.set_valign(Gtk.Align.CENTER)
        out_color_row.add_suffix(self.out_color_dialog_button)
        self.out_color_dialog_button.connect('notify::rgba', self.on_out_color_selected)
        # Reset color btn
        reset_out_color_button = Gtk.Button(label="Reset")
        reset_out_color_button.set_icon_name("arrow-circular-small-top-left-symbolic")
        reset_out_color_button.set_valign(Gtk.Align.CENTER)
        reset_out_color_button.set_has_frame(False)  # flat
        reset_out_color_button.set_tooltip_text("Reset")
        out_color_row.add_suffix(reset_out_color_button)
        reset_out_color_button.connect("clicked", self.reset_out_color_button_action)

        # Received incoming data color
        in_color_row = Adw.ActionRow(title="RX Color")
        # Color Dialog
        data_group.add(in_color_row)
        self.in_color_dialog_button = Gtk.ColorDialogButton.new(dialog=self.color_dialog)
        in_color = Gdk.RGBA()
        in_color.parse(self.settings.get_string("saved-in-color"))
        self.in_color_dialog_button.set_rgba(in_color)
        self.in_color_dialog_button.set_valign(Gtk.Align.CENTER)
        in_color_row.add_suffix(self.in_color_dialog_button)
        self.in_color_dialog_button.connect('notify::rgba', self.on_in_color_selected)
        # Reset color btn
        reset_in_color_button = Gtk.Button(label="Reset")
        reset_in_color_button.set_icon_name("arrow-circular-small-top-left-symbolic")
        reset_in_color_button.set_valign(Gtk.Align.CENTER)
        reset_in_color_button.set_has_frame(False)  # flat
        reset_in_color_button.set_tooltip_text("Reset")
        in_color_row.add_suffix(reset_in_color_button)
        reset_in_color_button.connect("clicked", self.reset_in_color_button_action)

        ## Logging group
        logging_group = Adw.PreferencesGroup(title="Logging")
        settings_page.add(logging_group)
        log_folder_row = Adw.ActionRow(title="Folder")
        logging_group.add(log_folder_row)
        # Entry
        log_folder_entry = Gtk.Entry.new()
        log_folder_entry.set_valign(Gtk.Align.CENTER)
        log_folder_entry.set_hexpand(True)
        log_folder_row.add_suffix(log_folder_entry)
        self.entry_buffer = log_folder_entry.get_buffer()
        self.entry_buffer.set_text(self.log_folder_path, len(self.log_folder_path))
        # Select Folder Button
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
        # Display all
        self.preferences.present()



    #@Gtk.Template.Callback()
    #def on_button_close_clicked(self, button):
    #    self.destroy()

