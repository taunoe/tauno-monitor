# window.py
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

from gi.repository import Adw, Gtk, Gio, GObject
import serial
import serial.tools.list_ports
import time

@Gtk.Template(resource_path='/art/taunoerik/TaunoMonitor/window.ui')

class TaunoMonitorWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'TaunoMonitorWindow'

    input_text_view = Gtk.Template.Child()
    open_button = Gtk.Template.Child()
    send_button = Gtk.Template.Child()
    send_cmd = Gtk.Template.Child()
    port_drop_down = Gtk.Template.Child()
    port_drop_down_list = Gtk.Template.Child()
    baud_drop_down = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings(schema_id="art.taunoerik.TaunoMonitor")

        self.settings.bind("window-width", self, "default-width",
                            Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-height", self, "default-height",
                            Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-maximized", self, "maximized",
                            Gio.SettingsBindFlags.DEFAULT)


        # Button Open action
        open_action = Gio.SimpleAction(name="open")
        open_action.connect("activate", self.open_serial_port)
        self.add_action(open_action)

        # Button Send
        send_action = Gio.SimpleAction(name="send")
        send_action.connect("activate", self.send_to_serial_port)
        self.add_action(send_action)

        # list available serial ports
        self.scan_serial_ports()

        # Get Serial instance, open later
        self.myserial = serial.Serial()


    def scan_serial_ports(self):
        self.port_drop_down_list.remove(0) # Removes: not available

        serial.tools.list_ports.comports()

        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            self.port_drop_down_list.append(str(port[0]))
            #print(port[1])  # info


    def open_serial_port(self, action, _):
        print("Btn Open")

        # Close if open
        if self.myserial.is_open:
            self.myserial.close()
            if self.myserial.is_open is False:
                print("Serial is closed")
                self.open_button.set_label("Open")
        # Open Serial
        else:
            # Selected Port
            port_obj = self.port_drop_down.get_selected_item()
            selected_port = port_obj.get_string()
            print(selected_port)
            # selected Baud Rate
            baud_obj = self.baud_drop_down.get_selected_item()
            selected_baud_rate = baud_obj.get_string()
            print(selected_baud_rate)
            # Open Serial import
            self.myserial.baudrate = selected_baud_rate
            self.myserial.port = selected_port
            self.myserial.open()

            if self.myserial.is_open:
                print("Serial is open")
                self.open_button.set_label("Close")

            # Start read serial
            self.read_serial_port()


    def send_to_serial_port(self, action, _):
        print("Btn Send")
        buffer = self.send_cmd.get_buffer()
        text = buffer.get_text()
        print(f"Enter CMD: {text}")

        if self.myserial.is_open:
            self.myserial.write(text.encode('utf-8'))

        buffer.delete_text(0, len(text))

    def read_serial_port(self):
        if self.myserial.is_open:

            tauno_serial = TaunoSerial()

            async_worker = AsyncWorker(
                operation = tauno_serial.read,
                operation_callback = tauno_serial.close
            )
            async_worker.start()



    def async_read(self):
        print("async_read")
        try:
            data_in = self.myserial.readline().decode('utf8')
            print(data_in)
        except Exception as ex:
            print(ex)



    def add_serial_output_to_text_view(self, data):
        try:
            text = data.decode('utf-8')
        except Exception:
            print(Exception)
            return

        buffer = self.input_text_view.get_buffer()


class TaunoSerial():

    def init(self):
        self.serial_instance = serial.Serial()

    def open(self):
        print("Tauno Serial Open")

    def close(self):
        print("Tauno Serial Close")


    def read(self):
        time.sleep(1)
        print("Tauno Serial Read")



# ASYNCHRONOUS WORKER
# https://discourse.gnome.org/t/how-do-you-run-a-blocking-method-asynchronously-with-gio-task-in-a-python-gtk-app/10651/3
class AsyncWorker(GObject.Object):
    """Represents an asynchronous worker.

    An async worker's job is to run a blocking operation in the
    background using a Gio.Task to avoid blocking the app's main thread
    and freezing the user interface.

    The terminology used here is closely related to the Gio.Task API.

    There are two ways to specify the operation that should be run in
    the background:

    1. By passing the blocking operation (a function or method) to the
       constructor.
    2. By defining the work() method in a subclass.

    An example of (1) can be found in AppWindow.on_start_button_clicked.

    Constructor parameters:

    OPERATION (callable)
      The function or method that needs to be run asynchronously. This
      is only necessary when using a direct instance of AsyncWorker, not
      when using an instance of a subclass of AsyncWorker, in which case
      an AsyncWorker.work() method must be defined by the subclass
      instead.

    OPERATION_INPUTS (tuple)
      Input data for OPERATION, if any.

    OPERATION_CALLBACK (callable)
      A function or method to call when the OPERATION is complete.

      See AppWindow.on_lunch_finished for an example of such callback.

    OPERATION_CALLBACK_INPUTS (tuple)
      Optional. Additional input data for OPERATION_CALLBACK.

    CANCELLABLE (Gio.Cancellable)
      Optional. It defaults to None, meaning that the blocking
      operation is not cancellable.

    """
    def __init__(
            self,
            operation=None,
            operation_inputs=(),
            operation_callback=None,
            operation_callback_inputs=(),
            cancellable=None
    ):
        super().__init__()
        self.operation = operation
        self.operation_inputs = operation_inputs
        self.operation_callback = operation_callback
        self.operation_callback_inputs = operation_callback_inputs
        self.cancellable = cancellable

        # Holds the actual data referenced from the Gio.Task created
        # in the AsyncWorker.start method.
        self.pool = {}

    def start(self):
        """Schedule the blocking operation to be run asynchronously.

        The blocking operation is either self.operation or self.work,
        depending on how the AsyncWorker was instantiated.

        This method corresponds to the function referred to as
        "blocking_function_async" in GNOME Developer documentation.

        """
        task = Gio.Task.new(
            self,
            self.cancellable,
            self.operation_callback,
            self.operation_callback_inputs
        )

        if self.cancellable is None:
            task.set_return_on_cancel(False)  # The task is not cancellable.

        data_id = id(self.operation_inputs)
        self.pool[data_id] = self.operation_inputs
        task.set_task_data(
            data_id,
            # FIXME: Data destroyer function always gets None as argument.
            #
            # This function is supposed to take as an argument the
            # same value passed as data_id to task.set_task_data, but
            # when the destroyer function is called, it seems it always
            # gets None as an argument instead. That's why the "key"
            # parameter is not being used in the body of the anonymous
            # function.
            lambda key: self.pool.pop(data_id)
        )

        task.run_in_thread(self._thread_callback)

    def _thread_callback(self, task, worker, task_data, cancellable):
        """Run the blocking operation in a worker thread."""
        # FIXME: task_data is always None for Gio.Task.run_in_thread callback.
        #
        # The value passed to this callback as task_data always seems to
        # be None, so we get the data for the blocking operation as
        # follows instead.
        data_id = task.get_task_data()
        data = self.pool.get(data_id)

        # Run the blocking operation.
        if self.operation is None:  # Assume AsyncWorker was extended.
            outcome = self.work(*data)
        else:  # Assume AsyncWorker was instantiated directly.
            outcome = self.operation(*data)

        task.return_value(outcome)

    def return_value(self, result):
        """Return the value of the operation that was run
        asynchronously.

        This method corresponds to the function referred to as
        "blocking_function_finish" in GNOME Developer documentation.

        This method is called from the view where the asynchronous
        operation is started to update the user interface according
        to the resulting value.

        RESULT (Gio.AsyncResult)
          The asyncronous result of the blocking operation that is
          run asynchronously.

        RETURN VALUE (object)
          Any of the return values of the blocking operation. If
          RESULT turns out to be invalid, return an error dictionary
          in the form

          {"AsyncWorkerError": "Gio.Task.is_valid returned False."}

        """
        value = None

        if Gio.Task.is_valid(result, self):
            value = result.propagate_value().value
        else:
            error = "Gio.Task.is_valid returned False."
            value = {"AsyncWorkerError": error}

        return value

