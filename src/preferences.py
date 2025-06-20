# File:        preferences.py
# Started:     03.08.2024
# Edited:      21.06.2025
# Author:      Tauno Erik
# Description: Displays Preferences window

from gi.repository import Adw, Gtk, Gio, GObject, GLib, Gdk

#@Gtk.Template(resource_path='/art/taunoerik/tauno-monitor/preferences.ui')#not ready
class TaunoPreferencesWindow(Adw.PreferencesWindow):
    __gtype_name__ = 'TaunoPreferencesWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def on_guide_action(self, widget, _):
        self.preferences = Adw.PreferencesWindow(transient_for=self.props.active_window)
        self.preferences.set_default_size(width=500, height=650)
        self.preferences.set_size_request(width=500, height=650)

        # Title
        settings_page = Adw.PreferencesPage(title="Preferences")
        settings_page.set_icon_name("applications-system-symbolic")
        self.preferences.add(settings_page)

        ################################################################
        ## UI group
        ################################################################
        ui_group = Adw.PreferencesGroup(title="Appearance")
        settings_page.add(ui_group)


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

        #####################################################################
        ## Data group
        #####################################################################
        data_group = Adw.PreferencesGroup(title="Data view")
        settings_page.add(data_group)

        ### Data Format
        rx_row = Adw.ActionRow(title="Format")
        data_group.add(rx_row)
        self.rx_format = Gtk.DropDown.new_from_strings(strings=self.serial_data_formats)
        self.rx_format.set_valign(Gtk.Align.CENTER)
        # Get saved index from windows.py
        index = self.serial_data_formats.index(self.win.get_rx_format_saved)
        self.rx_format.set_selected(position=index)
        rx_row.add_suffix(self.rx_format)
        # Connect function from main.py
        self.rx_format.connect("notify::selected-item", self.rx_data_format_action)

        reset_data_format_button = Gtk.Button(label="Reset")
        reset_data_format_button.set_icon_name("arrow-circular-small-top-left-symbolic")
        reset_data_format_button.set_valign(Gtk.Align.CENTER)
        reset_data_format_button.set_has_frame(False)
        reset_data_format_button.set_tooltip_text("Reset")
        rx_row.add_suffix(reset_data_format_button)
        # Connect function from main.py to reset
        reset_data_format_button.connect("clicked", self.reset_data_format_button_action)

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
        out_color_row = Adw.ActionRow(title="Transmitted (TX) data Color")
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
        in_color_row = Adw.ActionRow(title="Received (RX) data Color")
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


        ### Show line endings
        show_line_end_row = Adw.ActionRow(title="Show line endings")
        data_group.add(show_line_end_row)
        show_line_end_switch = Gtk.Switch(valign = Gtk.Align.CENTER,)
        show_line_end_row.add_suffix(show_line_end_switch)
        # Get saved state: show-line-end
        show_line_end_switch.set_active(self.settings.get_boolean("show-line-end"))
        # Connect function from main.py to save
        show_line_end_switch.connect("state-set", self.show_line_end_switch_action)

        ### Show Line ending color
        show_line_end_color_row = Adw.ActionRow(title="Line end color")
        # Color Dialog
        data_group.add(show_line_end_color_row)
        self.show_line_end_color_dialog_button = Gtk.ColorDialogButton.new(dialog=self.color_dialog)
        show_line_end_color = Gdk.RGBA()
        #
        show_line_end_color.parse(self.settings.get_string("saved-show-line-end-color"))
        #
        self.show_line_end_color_dialog_button.set_rgba(show_line_end_color)
        self.show_line_end_color_dialog_button.set_valign(Gtk.Align.CENTER)
        show_line_end_color_row.add_suffix(self.show_line_end_color_dialog_button)
        #
        self.show_line_end_color_dialog_button.connect('notify::rgba', self.on_show_line_end_color_selected)

        #TODO: reset
        reset_line_end_color_button = Gtk.Button(label="Reset")
        reset_line_end_color_button.set_icon_name("arrow-circular-small-top-left-symbolic")
        reset_line_end_color_button.set_valign(Gtk.Align.CENTER)
        reset_line_end_color_button.set_has_frame(False)  # flat
        reset_line_end_color_button.set_tooltip_text("Reset")
        show_line_end_color_row.add_suffix(reset_line_end_color_button)
        reset_line_end_color_button.connect("clicked", self.reset_line_end_color_button_action)


        ####################################################################
        ## Logging group
        ####################################################################
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


        #TODO
        #####################################################################
        ## Serial group
        #####################################################################
        serial_group = Adw.PreferencesGroup(title="Serial")
        settings_page.add(serial_group)

        #####################################################################
        ### Data bits row
        ### 5, 6, 7, 8
        data_bits_row = Adw.ActionRow(title="Data bits")
        serial_group.add(data_bits_row)
        self.data_bits_drop_down = Gtk.DropDown.new_from_strings(strings=self.serial_data_bits)
        self.data_bits_drop_down.set_valign(Gtk.Align.CENTER)
        # Get saved index from windows.py
        data_bit_index = self.win.get_data_bit_saved
        self.data_bits_drop_down.set_selected(position=data_bit_index)
        data_bits_row.add_suffix(self.data_bits_drop_down)
        # Connect function from main.py to save
        self.data_bits_drop_down.connect('notify::selected-item', self.serial_data_bits_action)

        reset_data_bits_button = Gtk.Button(label="Reset")
        reset_data_bits_button.set_icon_name("arrow-circular-small-top-left-symbolic")
        reset_data_bits_button.set_valign(Gtk.Align.CENTER)
        reset_data_bits_button.set_has_frame(False)  # flat
        reset_data_bits_button.set_tooltip_text("Reset")
        data_bits_row.add_suffix(reset_data_bits_button)
        # Connect function from main.py to reset
        reset_data_bits_button.connect("clicked", self.reset_data_bits_button_action)

        ####################################################################
        ### Parities row
        ### N (none)
        ### E (even)
        ### O (odd)
        ### M (mark)
        ### S (space)
        parity_row = Adw.ActionRow(title="Parity")
        serial_group.add(parity_row)
        self.parity_drop_down = Gtk.DropDown.new_from_strings(strings=self.serial_parities)
        self.parity_drop_down.set_valign(Gtk.Align.CENTER)
        # Get saved index from windows.py
        parity_index = self.win.get_parity_saved
        self.parity_drop_down.set_selected(position=parity_index)
        parity_row.add_suffix(self.parity_drop_down)
        # Connect function from main.py to save
        self.parity_drop_down.connect('notify::selected-item', self.serial_parity_action)

        reset_parity_button = Gtk.Button(label="Reset")
        reset_parity_button.set_icon_name("arrow-circular-small-top-left-symbolic")
        reset_parity_button.set_valign(Gtk.Align.CENTER)
        reset_parity_button.set_has_frame(False)  # flat
        reset_parity_button.set_tooltip_text("Reset")
        parity_row.add_suffix(reset_parity_button)
        # Connect function from main.py to reset
        reset_parity_button.connect("clicked", self.reset_parity_button_action)

        #####################################################################
        ### Stop bits row
        ### 1, 1.5, 2
        stop_bits_row = Adw.ActionRow(title="Stop Bits")
        serial_group.add(stop_bits_row)
        self.stop_bits_drop_down = Gtk.DropDown.new_from_strings(strings=self.serial_stop_bits)
        self.stop_bits_drop_down.set_valign(Gtk.Align.CENTER)
        # Get saved index from windows.py
        stop_bit_index = self.win.get_stop_bit_saved
        self.stop_bits_drop_down.set_selected(position=stop_bit_index)
        stop_bits_row.add_suffix(self.stop_bits_drop_down)
        # Connect function from main.py to save
        self.stop_bits_drop_down.connect('notify::selected-item', self.serial_stop_bits_action)

        reset_stop_bits_button = Gtk.Button(label="Reset")
        reset_stop_bits_button.set_icon_name("arrow-circular-small-top-left-symbolic")
        reset_stop_bits_button.set_valign(Gtk.Align.CENTER)
        reset_stop_bits_button.set_has_frame(False)  # flat
        reset_stop_bits_button.set_tooltip_text("Reset")
        stop_bits_row.add_suffix(reset_stop_bits_button)
        # Connect function from main.py to reset
        reset_stop_bits_button.connect("clicked", self.reset_stop_bits_button_action)

        ###################################################################
        ### TX transmitted data, Enter sends:
        ### \n, \r, \r\n or nothing
        TX_line_end_row = Adw.ActionRow(title="End of line of transmitted (TX) data")
        serial_group.add(TX_line_end_row)
        self.TX_line_end_drop_down = Gtk.DropDown.new_from_strings(strings=self.serial_tx_line_endings)
        self.TX_line_end_drop_down.set_valign(Gtk.Align.CENTER)
        # Get saved index from windows.py
        line_end_index = self.win.get_TX_line_end_saved
        self.TX_line_end_drop_down.set_selected(position=line_end_index)
        TX_line_end_row.add_suffix(self.TX_line_end_drop_down)
        # Connect function from main.py to save
        self.TX_line_end_drop_down.connect('notify::selected-item', self.serial_TX_line_end_action)

        reset_TX_line_end_button = Gtk.Button(label="Reset")
        reset_TX_line_end_button.set_icon_name("arrow-circular-small-top-left-symbolic")
        reset_TX_line_end_button.set_valign(Gtk.Align.CENTER)
        reset_TX_line_end_button.set_has_frame(False)  # flat
        reset_TX_line_end_button.set_tooltip_text("Reset")
        TX_line_end_row.add_suffix(reset_TX_line_end_button)
        # Connect function from main.py to reset
        reset_TX_line_end_button.connect("clicked", self.reset_TX_line_end_button_action)

        ###################################################################
        ### RX Received data:
        RX_line_end_row = Adw.ActionRow(title="End of line of received (RX) data")
        serial_group.add(RX_line_end_row)
        self.RX_line_end_drop_down = Gtk.DropDown.new_from_strings(strings=self.serial_rx_line_endings)
        self.RX_line_end_drop_down.set_valign(Gtk.Align.CENTER)
        # Get saved index from windows.py
        line_end_index = self.win.get_RX_line_end_saved
        self.RX_line_end_drop_down.set_selected(position=line_end_index)
        RX_line_end_row.add_suffix(self.RX_line_end_drop_down)
        # Connect function from main.py to save
        self.RX_line_end_drop_down.connect('notify::selected-item', self.serial_RX_line_end_action)

        reset_RX_line_end_button = Gtk.Button(label="Reset")
        reset_RX_line_end_button.set_icon_name("arrow-circular-small-top-left-symbolic")
        reset_RX_line_end_button.set_valign(Gtk.Align.CENTER)
        reset_RX_line_end_button.set_has_frame(False)  # flat
        reset_RX_line_end_button.set_tooltip_text("Reset")
        RX_line_end_row.add_suffix(reset_RX_line_end_button)
        # Connect function from main.py to reset
        reset_RX_line_end_button.connect("clicked", self.reset_RX_line_end_button_action)
        ### TODO: Timeout

        ### TODO: Custom baud rate

        ##################################################################
        # Display all
        ##################################################################
        self.preferences.present()


