"""Implement the interactive GUI command interface.

Used in the Logic Simulator project to enable the user to enter commands
to run the simulation in the GUI, or adjust the network properties.

Classes:
--------
GuiCommandInterface - reads and parses user commands.
"""
import wx


class GuiCommandInterface:
    """Read and parse user commands.

    This class allows the user to enter certain commands.
    These commands enable the user to run or continue the simulation for a
    number of cycles, set switches, and add or zap monitors.

    Parameters
    -----------
    line: user input from GUI command line.
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    cycles_completed: number of completed cycles.

    Public methods:
    ---------------
    command_interface(self): Reads in the commands and calls the corresponding
                             functions.

    read_command(self): Returns the first non-whitespace character.

    get_character(self): Moves the cursor forward by one character in the user
                         entry.

    skip_spaces(self): Skips whitespace characters until a non-whitespace
                       character is reached.

    read_string(self): Returns the next alphanumeric string.

    read_name(self): Returns the name ID of the current string.

    read_signal_name(self): Returns the device and port IDs of the current
                            signal name.

    read_number(self, lower_bound, upper_bound): Returns the current number.

    switch_command(self): Sets the specified switch to the specified signal
                          level.

    monitor_command(self): Sets the specified monitor.

    zap_command(self): Removes the specified monitor.

    run_network(self, cycles): Runs the network for the specified number of
                               simulation cycles.

    run_command(self): Runs the simulation from scratch.

    continue_command(self): Continues a previously run simulation.

    make_connection(self, input_device_id, input_port_id, dev, port): Make
                                a new connection.

    delete_connection(self, input_device_id, input_port_id): Delete a
                                connection.
    """

    def __init__(self, line, names, devices, network, monitors, complete=0):
        """Initialise variables."""
        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network
        self.line = line

        self.cycles_completed = complete

        self.character = ""  # current character
        self.cursor = 0  # cursor position

    def command_interface(self):
        """Read the command entered and call the corresponding function."""
        command = self.read_command()  # read the first character
        if command == "s":
            text, extra = self.switch_command()
        elif command == "m":
            text, extra = self.monitor_command()
        elif command == "z":
            text, extra = self.zap_command()
        elif command == "r":
            text, extra = self.run_command()
        elif command == "c":
            text, extra = self.continue_command()
        else:
            text, extra = _("Invalid command. See User Guide for help."), None
        return [
            command,
            text,
            extra,
            self.names,
            self.devices,
            self.network,
            self.monitors
        ]

    def read_command(self):
        """Return the first non-whitespace character."""
        self.skip_spaces()
        return self.character

    def get_character(self):
        """Move the cursor forward by one character in the user entry."""
        if self.cursor < len(self.line):
            self.character = self.line[self.cursor]
            self.cursor += 1
        else:  # end of the line
            self.character = ""

    def skip_spaces(self):
        """Skip whitespace until a non-whitespace character is reached."""
        self.get_character()
        while self.character.isspace():
            self.get_character()

    def read_string(self):
        """Return the next alphanumeric string."""
        self.skip_spaces()
        name_string = ""
        if not self.character.isalpha():  # the string must start with a letter
            print(_("Error! Expected a name."))
            return None
        while self.character.isalnum():
            name_string = "".join([name_string, self.character])
            self.get_character()
        return name_string

    def read_name(self):
        """Return the name ID of the current string if valid.

        Return None if the current string is not a valid name string.
        """
        name_string = self.read_string()
        if name_string is None:
            return None
        else:
            name_id = self.names.query(name_string)
        if name_id is None:
            print(_("Error! Unknown name."))
        return name_id

    def read_signal_name(self):
        """Return the device and port IDs of the current signal name.

        Return None if either is invalid.
        """
        device_id = self.read_name()
        if device_id is None:
            return None
        elif self.character == ".":
            port_id = self.read_name()
            if port_id is None:
                return None
        else:
            port_id = None
        return [device_id, port_id]

    def read_number(self, lower_bound, upper_bound):
        """Return the current number.

        Return None if no number is provided or if it falls outside the valid
        range.
        """
        self.skip_spaces()
        number_string = ""
        if not self.character.isdigit():
            print(_("Error! Expected a number."))
            return None
        while self.character.isdigit():
            number_string = "".join([number_string, self.character])
            self.get_character()
        number = int(number_string)

        if upper_bound is not None:
            if number > upper_bound:
                print(_("Number out of range."))
                return None

        if lower_bound is not None:
            if number < lower_bound:
                print("Number out of range.")
                return None

        return number

    def switch_command(self):
        """Set the specified switch to the specified signal level."""
        id = self.read_name()
        state = None
        if id is not None:
            state = self.read_number(0, 1)
            if state is not None:
                if self.devices.set_switch(id, state):
                    return _("Successfully set switch."), [id, state]
        return _("Error! Invalid switch."), None

    def monitor_command(self):
        """Set the specified monitor."""
        monitor = self.read_signal_name()
        if monitor is not None:
            [device, port] = monitor
            monitor_error = self.monitors.make_monitor(device, port,
                                                       self.cycles_completed)
            if monitor_error == self.monitors.NO_ERROR:
                return _("Successfully made monitor."), \
                       [self.monitors, monitor]
        return _("Error! Could not make monitor."), [self.monitors, monitor]

    def zap_command(self):
        """Remove the specified monitor."""
        monitor = self.read_signal_name()
        if monitor is not None:
            [device, port] = monitor
            if self.monitors.remove_monitor(device, port):
                return _("Successfully zapped monitor."), \
                       [self.monitors, monitor]
        return _("Error! Could not zap monitor."), [self.monitors, monitor]

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print(_("Error! Network oscillating."))
                return False
        return True

    def run_command(self):
        """Run the simulation from scratch."""
        self.cycles_completed = 0
        cycles = self.read_number(0, None)

        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles
            return " ".join([
                _("Running for"),
                str(cycles),
                _("cycles.")]), cycles
        return _("Invalid number of cycles."), cycles

    def continue_command(self):
        """Continue a previously run simulation."""
        cycles = self.read_number(0, None)
        if cycles is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                return _("Error! Nothing to continue. Run first."), 0
            elif self.run_network(cycles):
                self.cycles_completed += cycles
                return " ".join([
                    _("Continuing for"),
                    str(cycles),
                    _("cycles."),
                    "Total:",
                    str(self.cycles_completed)]), cycles
        return _("Error! Invalid number of cycles."), cycles

    def make_connection(self, input_device_id, input_port_id,
                        dev, port):
        """Make a connection."""
        connection_error = self.network.make_connection(
            input_device_id,
            input_port_id,
            dev,
            port
        )
        if connection_error == self.network.NO_ERROR:
            return _("Successfully made new connection."), True
        else:
            return _("Could not make connection."), False

    def delete_connection(self, input_device_id, input_port_id):
        """Delete a connection."""
        self.network.delete_connection(input_device_id, input_port_id)
