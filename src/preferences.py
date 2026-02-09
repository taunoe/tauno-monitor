# File:        preferences.py
# Started:     03.08.2024
# Edited:      09.02.2026
# Author:      Tauno Erik
# Description: Displays Preferences window

from gi.repository import Adw, Gtk, Gio, GObject, GLib, Gdk
import os

@Gtk.Template(resource_path='/art/taunoerik/tauno-monitor/preferences.ui')
class TaunoPreferencesWindow(Adw.PreferencesWindow):
    __gtype_name__ = 'TaunoPreferencesWindow'

    # --- UI Template Widget Bindings ---
    # These lines bind the widgets from the .ui file to class instance variables.
    # The name of the variable must match the 'id' of the widget in the .ui file.

    # Appearance
    font_spin_button = Gtk.Template.Child()
    dark_mode_switch = Gtk.Template.Child()
    notifications_switch = Gtk.Template.Child()

    # Data View
    rx_format_dropdown = Gtk.Template.Child()
    reset_data_format_button = Gtk.Template.Child()
    timestamp_switch = Gtk.Template.Child()
    time_color_button = Gtk.Template.Child()
    reset_time_color_button = Gtk.Template.Child()
    arrow_switch = Gtk.Template.Child()
    arrow_color_button = Gtk.Template.Child()
    reset_arrow_color_button = Gtk.Template.Child()
    out_color_button = Gtk.Template.Child()
    reset_out_color_button = Gtk.Template.Child()
    in_color_button = Gtk.Template.Child()
    reset_in_color_button = Gtk.Template.Child()
    show_line_end_switch = Gtk.Template.Child()
    show_line_end_color_button = Gtk.Template.Child()
    reset_line_end_color_button = Gtk.Template.Child()

    # Logging
    log_folder_entry = Gtk.Template.Child()
    select_log_folder_button = Gtk.Template.Child()

    # Serial
    data_bits_dropdown = Gtk.Template.Child()
    reset_data_bits_button = Gtk.Template.Child()
    parity_dropdown = Gtk.Template.Child()
    reset_parity_button = Gtk.Template.Child()
    stop_bits_dropdown = Gtk.Template.Child()
    reset_stop_bits_button = Gtk.Template.Child()
    #tx_line_end_dropdown = Gtk.Template.Child()
    #reset_tx_line_end_button = Gtk.Template.Child()
    #rx_line_end_dropdown = Gtk.Template.Child()
    #reset_rx_line_end_button = Gtk.Template.Child()


    def __init__(self, main_window, settings, **kwargs):
        """
        Initializes the Preferences Window.

        Args:
            main_window: A reference to the main application window (must be a Gtk.Window).
            settings: The application's GSettings object.
            **kwargs: Additional arguments.
        """
        kwargs.pop('transient_for', None)
        super().__init__(transient_for=main_window, **kwargs)
        self.init_template()
        self.win = main_window
        self.settings = settings
        # Folder dialog
        self.filedialog = Gtk.FileDialog()
        self.color_dialog = Gtk.ColorDialog()
        self.setup_widgets()
        self.connect_signals()


    def setup_widgets(self):
        """ Sets the initial state of widgets based on saved settings."""
        # --- Appearance ---
        adj = self.font_spin_button.get_adjustment()
        adj.set_value(self.win.font_size_saved)
        self.dark_mode_switch.set_active(self.settings.get_boolean("dark-mode"))
        self.notifications_switch.set_active(self.settings.get_boolean("notifications"))

        # --- Data View ---
        # Serial data formats
        self.serial_data_formats = ['ASCII', 'HEX', 'BIN', 'DEC', 'OCT']
        self.rx_format_dropdown.set_model(Gtk.StringList.new(self.serial_data_formats))
        self.rx_format_dropdown.set_selected(0)

        self.timestamp_switch.set_active(self.settings.get_boolean("timestamp"))
        self.arrow_switch.set_active(self.settings.get_boolean("arrow"))

        # Setup Color Buttons
        self.setup_color_button(self.time_color_button, "saved-time-color")
        self.setup_color_button(self.arrow_color_button, "saved-arrow-color")
        self.setup_color_button(self.out_color_button, "saved-out-color")
        self.setup_color_button(self.in_color_button, "saved-in-color")
        self.setup_color_button(self.show_line_end_color_button, "saved-show-line-end-color")

        self.show_line_end_switch.set_active(self.settings.get_boolean("show-line-end"))

        # --- Logging ---
        # Get saved log folder
        self.log_folder_path = self.settings.get_string("log-folder")
        log_buffer = self.log_folder_entry.get_buffer()
        log_buffer.set_text(self.log_folder_path, -1)

        # --- Serial ---
        # Serial byte sizes
        self.serial_data_bits = ['5 Bits', '6 Bits', '7 Bits', '8 Bits']
         # Get saved data bit index
        self.get_data_bit_saved_index = self.settings.get_int("saved-serial-data-bit-index")
        self.data_bits_dropdown.set_model(Gtk.StringList.new(self.serial_data_bits))
        self.data_bits_dropdown.set_selected(self.get_data_bit_saved_index)

        # Serial parities
        self.serial_parities = ['None', 'Even', 'Odd', 'Mark', 'Space']
        # Get saved parity index
        self.get_parity_saved = self.settings.get_int("saved-serial-parity-index")
        self.parity_dropdown.set_model(Gtk.StringList.new(self.serial_parities))
        self.parity_dropdown.set_selected(self.get_parity_saved)

        self.serial_stop_bits = ['1', '1.5', '2']
        # Get Stop Bit index
        self.get_stop_bit_saved = self.settings.get_int("saved-serial-stop-bit-index")
        self.stop_bits_dropdown.set_model(Gtk.StringList.new(self.serial_stop_bits))
        self.stop_bits_dropdown.set_selected(self.get_stop_bit_saved)

        # Get TX line end index
        #self.get_TX_line_end_saved = self.settings.get_int("saved-serial-tx-line-end-index")
        #self.tx_line_end_dropdown.set_model(Gtk.StringList.new(self.win.serial_tx_line_endings))
        #self.tx_line_end_dropdown.set_selected(self.get_TX_line_end_saved)

        # Get RX line end index
        #self.get_RX_line_end_saved = self.settings.get_int("saved-serial-rx-line-end-index")
        #self.rx_line_end_dropdown.set_model(Gtk.StringList.new(self.win.serial_rx_line_endings))
        #self.rx_line_end_dropdown.set_selected(self.get_RX_line_end_saved)


    def setup_color_button(self, button, setting_key):
        """ Helper function to configure a GtkColorDialogButton."""
        button.set_dialog(self.color_dialog)
        color = Gdk.RGBA()
        color.parse(self.settings.get_string(setting_key))
        button.set_rgba(color)


    def connect_signals(self):
        """ Connects widget signals to their handler methods."""
        # --- Appearance ---
        self.font_spin_button.connect("value-changed", self.text_size_action)
        self.dark_mode_switch.connect("state-set", self.dark_mode_switch_action)
        self.notifications_switch.connect("state-set", self.notifications_switch_action)

        # --- Data View ---
        self.rx_format_dropdown.connect("notify::selected-item", self.rx_data_format_action)
        self.reset_data_format_button.connect("clicked", self.reset_data_format_button_action)

        self.timestamp_switch.connect("state-set", self.timestamp_switch_action)
        self.time_color_button.connect('notify::rgba', self.on_time_color_selected)
        self.reset_time_color_button.connect("clicked", self.reset_time_color_button_action)

        self.arrow_switch.connect("state-set", self.arrow_switch_action)
        self.arrow_color_button.connect('notify::rgba', self.on_arrow_color_selected)
        self.reset_arrow_color_button.connect("clicked", self.reset_arrow_color_button_action)

        self.out_color_button.connect('notify::rgba', self.on_out_color_selected)
        self.reset_out_color_button.connect("clicked", self.reset_out_color_button_action)

        self.in_color_button.connect('notify::rgba', self.on_in_color_selected)
        self.reset_in_color_button.connect("clicked", self.reset_in_color_button_action)

        self.show_line_end_switch.connect("state-set", self.show_line_end_switch_action)
        self.show_line_end_color_button.connect('notify::rgba', self.on_show_line_end_color_selected)
        self.reset_line_end_color_button.connect("clicked", self.reset_line_end_color_button_action)

        # --- Logging ---
        self.select_log_folder_button.connect("clicked", self.select_log_folder_button_action)

        # --- Serial ---
        self.data_bits_dropdown.connect('notify::selected-item', self.serial_data_bits_action)
        self.reset_data_bits_button.connect("clicked", self.reset_data_bits_button_action)

        self.parity_dropdown.connect('notify::selected-item', self.serial_parity_action)
        self.reset_parity_button.connect("clicked", self.reset_parity_button_action)

        self.stop_bits_dropdown.connect('notify::selected-item', self.serial_stop_bits_action)
        self.reset_stop_bits_button.connect("clicked", self.reset_stop_bits_button_action)

        #self.tx_line_end_dropdown.connect('notify::selected-item', self.serial_TX_line_end_action)
        #self.reset_tx_line_end_button.connect("clicked", self.reset_TX_line_end_button_action)

        #self.rx_line_end_dropdown.connect('notify::selected-item', self.serial_RX_line_end_action)
        #self.reset_rx_line_end_button.connect("clicked", self.reset_RX_line_end_button_action)


    def text_size_action(self, action):
        """ """
        new_size = action.get_value_as_int()
        self.win.change_font_size(new_size)
        # Save settings
        self.settings.set_int("font-size", new_size)


    def dark_mode_switch_action(self, widget, state):
        dark_mode = state

        style_manager = Adw.StyleManager.get_default()

        if dark_mode: # is True
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        self.settings.set_boolean("dark-mode", dark_mode)


    def notifications_switch_action(self, widget, state):
        """ """
        notifications_state = state
        # Save settings
        self.settings.set_boolean("notifications", notifications_state)


    def rx_data_format_action(self, drop_down, g_param_object):
        """ """
        print("Change RX format")
        string_object = drop_down.get_selected_item()
        index = drop_down.get_selected()
        new_format = string_object.get_string()
        print(f'Position: {index} - value: {string_object.get_string()}')
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


    def reset_data_format_button_action(self, widget):
        """ """
        print("Reset data format")
        # Get deffault
        default = self.settings.get_string("default-serial-rx-data-format")
        print(f"default:{default}")
        # Save setting
        self.settings.set_string("saved-serial-rx-data-format", default)
        # Reload UI
        index = self.serial_data_formats.index(default)
        print(f"index:{index}")
        self.rx_format_dropdown.set_selected(position=index)#TODO


    def timestamp_switch_action(self, widget, state):
        """ """
        timestamp_state = state
        # Save settings
        self.settings.set_boolean("timestamp", timestamp_state)


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
        self.time_color_button.set_rgba(default_color)


    def arrow_switch_action(self, widget, state):
        """ Display "-->" ON/OFF"""
        arrow_state = state
        # Save settings
        self.settings.set_boolean("arrow", arrow_state)


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
        self.arrow_color_button.set_rgba(default_color)

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
        self.out_color_button.set_rgba(default_color)


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
        self.in_color_button.set_rgba(default_color)



    def show_line_end_switch_action(self, widget, state):
        """
        Get show line endings settings change and save
        """
        show_line_end_state = state
        # Save settings
        self.settings.set_boolean("show-line-end", show_line_end_state)



    def on_show_line_end_color_selected(self, color_dialog_button, g_param_boxed):
        """
        Get and save line end tag color
        """
        gdk_rgba = color_dialog_button.get_rgba()
        print("Line End color " + gdk_rgba.to_string())
        # Save color settings
        self.settings.set_string("saved-show-line-end-color", gdk_rgba.to_string())
        # Update tag
        self.win.update_line_end_tag()


    def reset_line_end_color_button_action(self, widget):
        print("reset_line_end_color_button_action")
        default_color = Gdk.RGBA()
        default_color.parse(self.settings.get_string("default-show-line-end-color"))
        self.settings.set_string("saved-show-line-end-color", default_color.to_string())
        self.show_line_end_color_button.set_rgba(default_color)


    def select_log_folder_button_action(self, widget):
        """ Button to select logging folder action """
        self.filedialog.select_folder(
            self, cancellable=None,
            callback=self.on_filedialog_select_folder)


    def serial_data_bits_action(self, drop_down, g_param_object):
        """
        Function called when Serial Data Bits selection is changed in App preferences
        """
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


    def reset_data_bits_button_action(self, widget):
        """
        Function to reset Serial Data Bit to default value
        """
        defalut_value = self.settings.get_int("default-serial-data-bit-index")
        print(f"Reset Data Bit index to: {defalut_value}")
        # save setting
        self.settings.set_int("saved-serial-data-bit-index", defalut_value)
        # reload setting
        self.win.get_data_bit_saved = self.settings.get_int("saved-serial-data-bit-index")
        # reload UI from preferences.py
        self.data_bits_dropdown.set_selected(position=defalut_value)


    def serial_parity_action(self, drop_down, g_param_object):
        """
        Function called when Serial Parity selection is changed in App preferences
        """
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


    def reset_parity_button_action(self, widget):
        """
        Function to reset Serial Parity to default value
        """
        defalut_value = self.settings.get_int("default-serial-parity-index")
        print(f"Reset Parity index to: {defalut_value}")
        # Save setting
        self.settings.set_int("saved-serial-parity-index", defalut_value)
        # reload setting
        self.win.get_parity_saved = self.settings.get_int("saved-serial-parity-index")
        # reload UI from preferences.py
        self.parity_dropdown.set_selected(position=defalut_value)


    def serial_stop_bits_action(self, drop_down, g_param_object):
        """
        Function called when Serial Stop Bits selection is changed in App preferences
        """
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


    def reset_stop_bits_button_action(self, widget):
        """
        Function to reset Serial Stop Bit to default value
        """
        defalut_value = self.settings.get_int("default-serial-stop-bit-index")
        print(f"Reset Stop Bit index to: {defalut_value}")
        # save setting
        self.settings.set_int("saved-serial-stop-bit-index", defalut_value)
        # reload setting
        self.win.get_stop_bit_saved = self.settings.get_int("saved-serial-stop-bit-index")
        # reload UI from preferences.py
        self.stop_bits_dropdown.set_selected(position=defalut_value)


    def serial_TX_line_end_action(self, drop_down, g_param_object):
        """
        Function called when Serial Line End selection is changed in App preferences
        """
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


    def reset_TX_line_end_button_action(self, widget):
        """
        Function to reset Serial Line End to default value
        """
        defalut_value = self.settings.get_int("default-serial-tx-line-end-index")
        print(f"Reset Line End index to: {defalut_value}")
        # save setting
        self.settings.set_int("saved-serial-tx-line-end-index", defalut_value)
        # reload setting
        self.win.get_TX_line_end_saved = self.settings.get_int("saved-serial-tx-line-end-index")
        # reload UI from preferences.py
        self.tx_line_end_dropdown.set_selected(position=defalut_value)


    def serial_RX_line_end_action(self, drop_down, g_param_object):
        """
        Function called when Serial Line End selection is changed in App preferences
        RX
        """
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


    def reset_RX_line_end_button_action(self, widget):
        """
        Function to reset Serial Line End to default value
        RX
        """
        defalut_value = self.settings.get_int("default-serial-rx-line-end-index")
        print(f"Reset Line End index to: {defalut_value}")
        # save setting
        self.settings.set_int("saved-serial-rx-line-end-index", defalut_value)
        # reload setting
        self.win.get_RX_line_end_saved = self.settings.get_int("saved-serial-rx-line-end-index")
        # reload UI from preferences.py
        self.rx_line_end_dropdown.set_selected(position=defalut_value)


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

            self.entry_buffer = self.log_folder_entry.get_buffer()
            # Update label on preferences
            self.entry_buffer.set_text(self.log_folder_path, len(self.log_folder_path))
            # Update saved settings
            self.settings.set_string("log-folder", self.log_folder_path)

