"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


class Parser:
    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file. Returns True
                         only if no syntax or semantic errors are found,
                         otherwise returns False.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        self.error_count = 0
        self.end_of_file = False  # if the end of file is reached

        self.symbol = None
        self.unclosed_comment = False  # if an unclosed comment is detected

        self.error_message_list = []  # list of terminal output to be passed
        # to GUI

    def parse_network(self):
        """Parse the circuit definition file."""
        devices_done = False
        connections_done = False
        monitors_done = False
        self._set_next()

        if self.symbol.type == self.scanner.EOF and not \
                self.unclosed_comment:
            # this is when we get an empty file - we would like to show
            # an error

            self._error(_("Empty definition file was loaded."),
                        [self.scanner.EOF])

            final_err = (
                    f"\n" + _("Completely parsed the definition file.") +
                    f" {self.error_count} "
                    + _("error(s) found in total.")
            )
            print(final_err)
            self.error_message_list.append(final_err)

            return False

        while True:

            if self.symbol.id == self.scanner.DEVICES_ID:
                if devices_done:
                    self._error(
                        _("Multiple device lists found."),
                        [
                            self.scanner.CONNECTIONS_ID,
                            self.scanner.MONITOR_ID,
                            self.scanner.EOF
                        ],
                    )
                else:
                    self._parse_devices_list()
                    devices_done = True

            elif self.symbol.id == self.scanner.CONNECTIONS_ID:
                if connections_done:
                    self._error(
                        _("Multiple connections lists found."),
                        [
                            self.scanner.MONITOR_ID,
                            self.scanner.EOF
                        ],
                    )
                else:
                    if devices_done:
                        self._parse_connections_list(self.error_count)
                        connections_done = True
                    else:
                        self._error(
                            _("can't parse connections if not done devices"),
                            [self.scanner.DEVICES_ID],
                        )
                        if self._is_eof():
                            break

            elif self.symbol.id == self.scanner.MONITOR_ID:
                if monitors_done:
                    self._error(
                        _("Multiple monitors lists found."),
                        [
                            self.scanner.CONNECTIONS_ID,
                            self.scanner.EOF
                        ],
                    )
                else:
                    if devices_done:
                        self._parse_monitors_list(self.error_count)
                        monitors_done = True
                    else:
                        self._error(
                            _("can't parse monitors if not done devices"),
                            [self.scanner.DEVICES_ID],
                        )
                        if self._is_eof():
                            break
            elif self._is_eof():
                break
            else:
                self._error(
                    _("not DEVICES, CONNECTIONS, MONITORS nor EOF"),
                    [
                        self.scanner.DEVICES_ID,
                        self.scanner.CONNECTIONS_ID,
                        self.scanner.MONITOR_ID,
                        self.scanner.EOF,
                    ],
                )
                if self._is_eof():
                    break

        if not self.network.check_network():
            unconnected = _("Network is incomplete") + \
                          _(" - all inputs must be connected.")
            self.error_count += 1
            print(unconnected)
            self.error_message_list.append(unconnected)

        final_msg = (_("Completely parsed the definition file.") +
                     f" {self.error_count} " + _("error(s) found in total."))
        print(final_msg)
        self.error_message_list.append(final_msg)

        if self.error_count == 0:  # syn + sem errors = 0
            return True
        else:
            return False

    def _parse_devices_list(self):
        """Parse list of devices."""
        self._set_next()
        if self.unclosed_comment:
            return

        while True:
            if self.symbol.id != self.scanner.OPEN_SQUARE:
                self._error(
                    _("expected") + " [", [
                        self.scanner.CONNECTIONS_ID, self.scanner.MONITOR_ID])
                break

            self._set_next()
            if self.unclosed_comment:
                break

            parsing_devices = True
            while parsing_devices:
                if self.end_of_file:
                    break

                if self.symbol.id == self.scanner.CLOSE_SQUARE:
                    # if empty DEVICES list
                    break

                missing_semicolon = self._parse_device(self.error_count)
                if missing_semicolon:
                    if self.end_of_file:
                        break
                    # print warning about error recovery strategy
                    # if a semicolon is missing it will skip the next device
                    # entirely to find the next 'outer' semi-colon to
                    # continue parsing with
                    warn = _("missed semicolon at end of device definition, ")\
                        + _("will end up skipping the device after")
                    print(warn)
                    self.error_message_list.append(warn)

                if self.symbol.id == self.scanner.OPEN_CURLY:
                    parsing_devices = True
                elif self.symbol.id == self.scanner.CLOSE_SQUARE:
                    parsing_devices = False
                elif (
                        self.symbol.id == self.scanner.MONITOR_ID
                        or self.symbol.id == self.scanner.CONNECTIONS_ID
                ):
                    # error skips to end of devices
                    break
                elif self.symbol.type == self.scanner.INVALID_CHAR:
                    # unknown character encountered
                    self._error(
                        _("invalid character encountered"), [
                            self.scanner.OPEN_CURLY])
                elif self.symbol.type == self.scanner.EOF:
                    # reached end of file through error recovery in inner loop
                    break
                else:
                    # problem is not getting { or ] - i.e. device is missing
                    # opening curly bracket perhaps, try and look for { or ],
                    # if not those then look for connections/monitors
                    # if not those then EOF

                    self._get_symbol_string()
                    self._error(_("Invalid input to a DEVICES list. Devices ")
                                + _(
                        "should start with '{', or the list should ")
                                + _("end with ']' "),
                                [self.scanner.OPEN_CURLY,
                                 self.scanner.CLOSE_SQUARE,
                                 self.scanner.CONNECTIONS_ID,
                                 self.scanner.MONITOR_ID,
                                 self.scanner.EOF])

                    if self.symbol.id == self.scanner.CLOSE_SQUARE:
                        break
                    elif self.symbol.id == self.scanner.OPEN_CURLY:
                        continue
                    elif self.end_of_file:
                        return
                    elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                            self.symbol.id == self.scanner.MONITOR_ID:
                        break

            if (
                    self.symbol.id == self.scanner.MONITOR_ID
                    or self.symbol.id == self.scanner.CONNECTIONS_ID
            ):
                break

            # no longer parsing devices
            if (self.symbol.id != self.scanner.CLOSE_SQUARE and
                    not self._is_eof()):
                self._error(
                    _("expected") + " ]",
                    [self.scanner.CONNECTIONS_ID, self.scanner.MONITOR_ID])
                break

            self._set_next()
            if self.unclosed_comment:
                break

            if self.symbol.id != self.scanner.SEMICOLON:
                self._error(
                    _("expected") + " ;", [
                        self.scanner.MONITOR_ID, self.scanner.CONNECTIONS_ID])
                break

            if self.error_count != 0:
                break

            print(_("Successfully parsed the DEVICES list! \n"))
            self._set_next()
            if self.unclosed_comment:
                return

            return True  # no meaning to boolean

        if self.end_of_file:
            pass
        elif (
                self.symbol.id != self.scanner.MONITOR_ID
                and self.symbol.id != self.scanner.CONNECTIONS_ID
        ):
            self._set_next()
            if self.unclosed_comment:
                return

        # print("Did not manage to parse the DEVICES list perfectly.")
        if self.error_count != 0:
            err = f"{self.error_count} " + _("error(s) found ") \
                  + _("when parsing the DEVICES list \n")
            print(err)
            self.error_message_list.append(err)
            return False

    def _parse_device(self, previous_errors):
        """Parse a single device."""
        # print("Parsing a single device.")
        missing_device_semicolon = False
        device_qual_symbol = None  # initialising for semantic reporting
        device_kind_symbol = None  # initialising for semantic reporting
        device_name = None
        while True:
            if self.symbol.id != self.scanner.OPEN_CURLY:
                self._error(
                    _("expected") + " {", [
                        self.scanner.OPEN_CURLY, self.scanner.CLOSE_CURLY])
                break

            self._set_next()
            if self.unclosed_comment:
                return True

            missing_semicolon, device_name, device_name_symbol = \
                self._parse_device_id()

            if missing_semicolon:
                if self.end_of_file:
                    return True
                # missed semicolon causes entire device to be skipped
                break

            (
                missing_semicolon,
                device_kind_string,
                device_kind_id,
                device_kind_symbol
            ) = self._parse_device_kind()

            if missing_semicolon:
                if self.end_of_file:
                    return True
                # missed semicolon causes entire device to be skipped
                break

            if self.symbol.id == self.scanner.QUAL_KEYWORD_ID:
                missing_semicolon, device_qual, device_qual_symbol = \
                    self._parse_device_qual()
                if missing_semicolon:
                    if self.end_of_file:
                        return True
                    # missed semicolon causes entire device to be skipped
                    break
            else:
                device_qual = None

            if self.symbol.id != self.scanner.CLOSE_CURLY:
                self._error(
                    _("expected") + " }", [
                        self.scanner.OPEN_CURLY, self.scanner.CLOSE_CURLY])
                break

            self._set_next()
            if self.unclosed_comment:
                return True

            if self.symbol.id != self.scanner.SEMICOLON:
                self._error(
                    _("expected") + " ;",
                    [
                        self.scanner.OPEN_CURLY,
                        self.scanner.CONNECTIONS_ID,
                        self.scanner.MONITOR_ID,
                    ],
                )
                # if MONITORS or CONNECTIONS, stop parsing devices
                missing_device_semicolon = True
                break

            # if we get here we have done a whole device
            # for each device there are no new syntax errors
            if self.error_count - previous_errors == 0:

                error_type = self.devices.make_device(
                    self.names.query(device_name), device_kind_id, device_qual
                )

                # if there is a semantic error
                if error_type != self.devices.NO_ERROR:
                    if error_type == self.devices.NO_QUALIFIER:
                        self._semantic_error(
                            f"{device_kind_string} " + _(
                                "qualifier not present."),
                            device_qual_symbol
                        )
                    elif error_type == self.devices.INVALID_QUALIFIER:
                        self._semantic_error(
                            f"{device_kind_string} " + _(
                                "qualifier is invalid."),
                            device_kind_symbol
                        )
                    elif error_type == self.devices.QUALIFIER_PRESENT:
                        self._semantic_error(
                            _(
                                "Qualifier provided for ") +
                            f"{device_kind_string} "
                            + _("when there should be none."),
                            device_qual_symbol
                        )
                    elif error_type == self.devices.BAD_DEVICE:
                        self._semantic_error(
                            _("Device kind") + f" {device_kind_string} "
                            + ("not recognised."), device_kind_symbol
                        )
                    elif error_type == self.devices.DEVICE_PRESENT:
                        self._semantic_error(
                            _("Device ") + f"{device_name} " + _(
                                "already present."),
                            device_name_symbol
                        )

                self._set_next()
                if self.unclosed_comment:
                    return True

                break
            else:
                # syntactic errors found when parsing the device
                self._set_next()
                if self.unclosed_comment:
                    return True
                break

        return missing_device_semicolon

    def _parse_device_id(self):
        """Parse a device id."""
        missing_semicolon = False
        device_name = None
        symbol_for_device_name = None
        while True:
            if self.symbol.id != self.scanner.ID_KEYWORD_ID:
                self._error(
                    _("expected id keyword here"), [
                        self.scanner.KIND_KEYWORD_ID])
                break

            self._set_next()
            if self.unclosed_comment:
                return True, device_name, symbol_for_device_name

            if self.symbol.id != self.scanner.COLON:
                self._error(_("expected") + " :",
                            [self.scanner.KIND_KEYWORD_ID])
                break

            self._set_next()
            if self.unclosed_comment:
                return True, device_name, symbol_for_device_name

            if self.symbol.type != self.scanner.NAME:
                # name provided is syntactically incorrect for a name
                if self.symbol.type == self.scanner.KEYWORD:
                    self._error(
                        _("Invalid name provided - ") +
                        _("a keyword cannot be used as a device name"), [
                            self.scanner.KIND_KEYWORD_ID])
                    break
                else:
                    self._error(
                        _("Invalid name provided - ") +
                        _("a device name should be alphanumeric"), [
                            self.scanner.KIND_KEYWORD_ID])
                    break
            else:
                device_name = self._get_symbol_string()
                symbol_for_device_name = self.symbol

            self._set_next()
            if self.unclosed_comment:
                return True, device_name, symbol_for_device_name

            if self.symbol.id != self.scanner.SEMICOLON:
                self._error(_("Missing semicolon"), [self.scanner.OPEN_CURLY])
                missing_semicolon = True
                break

            self._set_next()
            if self.unclosed_comment:
                return True, device_name, symbol_for_device_name

            break

        self._get_symbol_string()
        return missing_semicolon, device_name, symbol_for_device_name

    def _parse_device_kind(self):
        """Parse a device kind."""
        missing_semicolon = False
        device_kind_string = None  # may cause sem errors when creating devices
        device_kind_id = None
        symbol_for_device_kind = None
        while True:
            if self.symbol.id != self.scanner.KIND_KEYWORD_ID:
                self._error(
                    _("expected") + " 'kind'",
                    [self.scanner.QUAL_KEYWORD_ID, self.scanner.CLOSE_CURLY],
                )
                break
                # this causes small issue with error counting for unclosed
                # comments - deal with if time

            self._set_next()
            if self.unclosed_comment:
                return True, None, None, None

            if self.symbol.id != self.scanner.COLON:
                self._error(
                    _("expected") + " :",
                    [self.scanner.QUAL_KEYWORD_ID, self.scanner.CLOSE_CURLY],
                )
                break

            self._set_next()
            if self.unclosed_comment:
                return True, None, None, None

            if self.symbol.type != self.scanner.NAME:
                self._error(
                    _("Device type must be alphanumeric"),
                    [self.scanner.QUAL_KEYWORD_ID, self.scanner.CLOSE_CURLY],
                )
                break
            else:
                device_kind_string = self._get_symbol_string()
                [device_kind_id] = self.devices.names.lookup(
                    [device_kind_string])
                symbol_for_device_kind = self.symbol

            self._set_next()
            if self.unclosed_comment:
                return True, None, None, None

            if self.symbol.id != self.scanner.SEMICOLON:
                self._error(
                    _("Missing semicolon"),
                    [self.scanner.OPEN_CURLY, self.scanner.CLOSE_SQUARE],
                )
                missing_semicolon = True
                break

            self._set_next()
            if self.unclosed_comment:
                return True, None, None, None

            break

        return missing_semicolon, device_kind_string, device_kind_id, \
            symbol_for_device_kind

    def _parse_device_qual(self):
        """Parse a device qualifier."""
        missing_semicolon = False
        device_qual = None
        symbol_for_device_qual = None
        while True:
            if self.symbol.id != self.scanner.QUAL_KEYWORD_ID:
                self._error(
                    _("expected") + " 'qual",
                    [self.scanner.CLOSE_CURLY])
                break

            self._set_next()
            if self.unclosed_comment:
                return True, None, None

            if self.symbol.id != self.scanner.COLON:
                self._error(
                    _("expected") + " :",
                    [self.scanner.CLOSE_CURLY])
                break

            self._set_next()
            if self.unclosed_comment:
                return True, None, None

            if self.symbol.type != self.scanner.NUMBER:
                self._error(
                    _("unsupported qualifier input"), [
                        self.scanner.CLOSE_CURLY])
                break
            else:
                device_qual = self.symbol.id
                symbol_for_device_qual = self.symbol

            self._set_next()
            if self.unclosed_comment:
                return True, None, None

            if self.symbol.id != self.scanner.SEMICOLON:
                self._error(
                    "Missing semicolon",
                    [self.scanner.OPEN_CURLY, self.scanner.CLOSE_SQUARE],
                )
                missing_semicolon = True
                break

            self._set_next()
            if self.unclosed_comment:
                return True, None, None

            break

        return missing_semicolon, device_qual, symbol_for_device_qual

    def _parse_connections_list(self, previous_errors):
        """Parse list of connections."""
        self._set_next()

        while True:
            if self.end_of_file:
                break
            if self.symbol.id != self.scanner.OPEN_SQUARE:
                self._error(
                    _("expected") + " [", [
                        self.scanner.MONITOR_ID, self.scanner.EOF])
                # it could also be end of file, connections not necessary
                break
            self._set_next()

            parsing_connections = True
            while parsing_connections:
                if self.end_of_file:
                    break

                if self.symbol.id == self.scanner.CLOSE_SQUARE:
                    parsing_connections = False
                    break

                missing_semicolon = self._parse_connection(self.error_count)
                if self.end_of_file:
                    # if there has been an error within
                    # parse_connection that causes us to reach the end of
                    # the file we can break here
                    break
                if missing_semicolon:
                    if self.symbol.id == self.scanner.MONITOR_ID:
                        break
                    continue

                if self.symbol.type == self.scanner.NAME:
                    parsing_connections = True
                elif self.symbol.id == self.scanner.CLOSE_SQUARE:
                    parsing_connections = False
                    break
                elif self.symbol.id == self.scanner.MONITOR_ID:
                    parsing_connections = False
                    break
                elif self.symbol.type == self.scanner.INVALID_CHAR:
                    # unknown character encountered
                    self._error(
                        _("invalid character encountered"), [
                            self.scanner.NAME])
                elif self.symbol.type == self.scanner.KEYWORD:
                    self._error(_("Cannot use a KEYWORD for a signal name"),
                                [self.scanner.NAME])
                else:
                    self._error(_("Unknown Error"),
                                [self.scanner.NAME,
                                 self.scanner.CLOSE_SQUARE,
                                 self.scanner.MONITOR_ID,
                                 self.scanner.EOF
                                 ])
                    if self.symbol.id == self.scanner.CLOSE_SQUARE:
                        break
                    elif self.symbol.type == self.scanner.NAME:
                        continue
                    elif self.end_of_file:
                        break
                    elif self.symbol.id == self.scanner.MONITOR_ID:
                        break

            if self.end_of_file:
                break

            if self.symbol.id == self.scanner.MONITOR_ID:
                break

            # no longer parsing connections
            if self.symbol.id != self.scanner.CLOSE_SQUARE:
                self._error(
                    _("expected") + " ]", [
                        self.scanner.MONITOR_ID, self.scanner.EOF])
                break

            self._set_next()
            if self.unclosed_comment:
                return

            if self.symbol.id != self.scanner.SEMICOLON:
                self._error(
                    _("expected") + " ;", [
                        self.scanner.MONITOR_ID, self.scanner.EOF])
                break

            if self.error_count - previous_errors != 0:
                break

            print(_("Successfully parsed the CONNECTIONS list! \n"))
            self._set_next()
            if self.unclosed_comment:
                return

            return True

        if self.end_of_file:
            pass
        elif self.symbol.id != self.scanner.MONITOR_ID:
            self._set_next()
            if self.unclosed_comment:
                return

        if self.error_count - previous_errors != 0:
            err = (
                    f"{self.error_count - previous_errors} " +
                    _("error(s) found when parsing the ") +
                    _("CONNECTIONS list \n")
            )

            print(err)

            self.error_message_list.append(err)
            return False

    def _parse_connection(self, previous_errors):
        """Parse a single connection."""
        missing_signal_end_marker = False
        symbol_store_right = {}  # initialising for semantic error reporting
        while True:
            if self.symbol.id == self.scanner.SEMICOLON:
                self._error(
                    _("No connection found before semicolon"),
                    [self.scanner.NAME])
                break
            (
                missing_signal_end_marker,
                leftOutputId,
                leftPortId,
                leftSignalName,
                symbol_store_left
            ) = self._parse_signal()
            if self.end_of_file:
                break
            if missing_signal_end_marker:
                print(
                    _("missed colon in connection, ") +
                    _("will skip to next connection"))
                break
            self._set_next()
            if self.unclosed_comment:
                return True

            (
                missing_signal_end_marker,
                rightOutputId,
                rightPortId,
                rightSignalName,
                symbol_store_right
            ) = self._parse_signal()
            if self.end_of_file:
                break
            if missing_signal_end_marker:
                # if time, print a warning
                break

            if self.error_count - previous_errors == 0:
                # no syntax errors found when parsing connection
                error_type = self.network.make_connection(
                    leftOutputId, leftPortId, rightOutputId, rightPortId
                )

                if error_type != self.network.NO_ERROR:
                    if error_type == self.network.DEVICE_ABSENT:
                        self._semantic_error(
                            _("Either left or right device is absent"))
                    elif error_type == self.network.INPUT_CONNECTED:
                        self._semantic_error(
                            f"{rightSignalName} " +
                            _("input is already connected."),
                            symbol_store_right.get("device_id")
                        )
                    elif error_type == self.network.INPUT_TO_INPUT:
                        self._semantic_error(_("Both ports are inputs."))
                    elif error_type == self.network.PORT_ABSENT:
                        self._semantic_error(_("Right port id is invalid."),
                                             symbol_store_right.get("port_id"))
                    elif error_type == self.network.OUTPUT_TO_OUTPUT:
                        self._semantic_error(_("Both ports are outputs."))

                self._set_next()
                if self.unclosed_comment:
                    return True
                break

            else:
                # syntax errors found in connection
                self._set_next()
                if self.unclosed_comment:
                    return True

                break

        return missing_signal_end_marker

    def _parse_signal(self):
        """Parse a signal name."""
        missing_end_marker = False
        signalName = ""
        deviceId = None
        portId = None
        symbol_store = {}

        while True:
            if self.symbol.type != self.scanner.NAME:
                self._error(
                    _("Expected an output name here"),
                    [self.scanner.NAME]
                )
                break

            signalName += self.names.get_name_string(self.symbol.id)
            deviceId = self.symbol.id
            symbol_store["device_id"] = self.symbol
            self._set_next()
            if self.unclosed_comment:
                return True, None, None, None, None

            if self.symbol.id == self.scanner.DOT:
                signalName += "."
                self._set_next()
                if self.unclosed_comment:
                    return True, None, None, None, None

                if self.symbol.type != self.scanner.NAME:
                    self._error(
                        _("expected a port name here"), [
                            self.scanner.NAME])
                    break

                signalName += self.names.get_name_string(self.symbol.id)
                portId = self.symbol.id
                symbol_store["port_id"] = self.symbol

                self._set_next()
                if self.unclosed_comment:
                    return True, None, None, None, None

            if (
                    self.symbol.id != self.scanner.COLON
                    and self.symbol.id != self.scanner.SEMICOLON
            ):
                missing_end_marker = True
                self._error(
                    _("missing ':' or ';'"),
                    [
                        self.scanner.NAME,
                        self.scanner.CLOSE_SQUARE,
                        self.scanner.MONITOR_ID,
                    ],
                )
                break

            break

        return missing_end_marker, deviceId, portId, signalName, symbol_store

    def _parse_monitors_list(self, previous_errors):
        """Parse list of monitors."""
        self._set_next()
        while True:
            if self.end_of_file:
                break
            if self.symbol.id != self.scanner.OPEN_SQUARE:
                self._error(
                    _("expected") + " [", [
                        self.scanner.CONNECTIONS_ID, self.scanner.EOF])
                break
            self._set_next()

            parsing_monitors = True
            while parsing_monitors:
                if self.end_of_file:
                    break

                if self.symbol.id == self.scanner.CLOSE_SQUARE:
                    parsing_monitors = False
                    break

                missing_semicolon = self._parse_monitor(self.error_count)

                if self.end_of_file:
                    break
                if missing_semicolon:
                    # if an error is found in _parse_monitor we should break
                    # here
                    if self.symbol.id == self.scanner.CONNECTIONS_ID:
                        break

                    continue

                if self.symbol.type == self.scanner.NAME:
                    parsing_monitors = True
                elif self.symbol.id == self.scanner.CLOSE_SQUARE:
                    parsing_monitors = False
                elif self.symbol.id == self.scanner.CONNECTIONS_ID:
                    parsing_monitors = False
                    break
                elif self.symbol.type == self.scanner.INVALID_CHAR:
                    # unknown character encountered
                    self._error(
                        _("invalid character encountered"), [
                            self.scanner.NAME])
                else:
                    # To be tested further - kept now to prevent infinite loops
                    print(_("Unknown Error"))
                    self.error_count += 1
                    break

            if self.end_of_file:
                break

            if self.symbol.id == self.scanner.CONNECTIONS_ID:
                break

            # no longer parsing monitors
            if self.symbol.id != self.scanner.CLOSE_SQUARE:
                self._error(
                    _("expected") + " ]", [
                        self.scanner.CONNECTIONS_ID, self.scanner.EOF])
                break

            self._set_next()
            if self.unclosed_comment:
                break  # break instead of return to get error count

            if self.symbol.id != self.scanner.SEMICOLON:
                self._error(
                    _("expected") + " ;", [
                        self.scanner.EOF, self.scanner.CONNECTIONS_ID])
                break

            if self.error_count - previous_errors != 0:
                break

            print(_("Successfully parsed the MONITORS list! \n"))
            self._set_next()
            return True

        if (
                self.symbol.id != self.scanner.CONNECTIONS_ID
                and self.symbol.id != self.scanner.EOF
        ):
            self._set_next()

        if self.error_count - previous_errors != 0:
            err = (
                    f"{self.error_count - previous_errors} " +
                    _("error(s) found when parsing the ") +
                    _("MONITORS list \n")
            )

            print(err)

            self.error_message_list.append(err)
            return False

    def _parse_monitor(self, previous_errors):
        """Parse a single monitor."""
        missing_semicolon = False
        symbol_store = {}
        while True:
            if self.symbol.id == self.scanner.SEMICOLON:
                self._error(
                    _("No signal found before semicolon"), [
                        self.scanner.NAME])
                break
            (missing_semicolon, deviceId,
             portId, signalName, symbol_store) = self._parse_signal()
            if self.end_of_file:
                break
            if missing_semicolon:
                # skip to next monitor
                break

            if self.error_count - previous_errors == 0:
                # no syntax errors found when parsing monitor
                error_type = self.monitors.make_monitor(deviceId, portId)

                if error_type != self.monitors.NO_ERROR:
                    if error_type == self.network.DEVICE_ABSENT:
                        self._semantic_error(
                            _("Device you are trying to monitor is absent."),
                            symbol_store.get("device_id")
                        )
                    elif error_type == self.monitors.NOT_OUTPUT:
                        self._semantic_error(
                            f"{signalName} " +
                            _("is not an output."))
                    elif error_type == self.monitors.MONITOR_PRESENT:
                        self._semantic_error(
                            _("Already monitoring") + f" {signalName}.",
                            symbol_store.get("device_id"))

                self._set_next()
                # semantically correct
                break

            else:
                # syntax errors found, no checking of semantics will occur
                self._set_next()
                break

        return missing_semicolon

    def _set_next(self):
        """Shift current symbol to next."""
        self.symbol = self.scanner.get_symbol()

        if self.symbol.type == self.scanner.UNCLOSED:
            self.unclosed_comment = True

            self._error(
                "Unclosed comment found - did you want to use "
                "'/' instead of '#' for your comment?",
                [],
            )

            self.end_of_file = True

    def _get_symbol_string(self):
        """More easily print current symbol string."""
        try:
            return self.names.get_name_string(self.symbol.id)
        except TypeError:
            return "NONE"

    def _error(self, msg, expect_next_list):
        """Print error message and recover from next semicolon."""
        self.error_count += 1

        caret_msg, line_num, col_num = self.scanner.show_error(self.symbol)

        # loading empty file error handling
        if self.symbol.type == self.scanner.EOF:
            full_error_message = _("ERROR on line") + \
                                 f"{line_num} " + _("index") + \
                                 f"{col_num}: {msg} "
            print(full_error_message)
            self.error_message_list.append(full_error_message)
            self.end_of_file = True
            return

        self.end_of_file = False

        received_symbol = self._get_symbol_string()
        if received_symbol == "NONE":  # the case if not in names list,
            # i.e unclosed comment
            full_error_message = _("ERROR on line") + \
                                 f"{line_num} " + _("index") + \
                                 f"{col_num}: {msg} "

            print(full_error_message)
            self.error_message_list.append(full_error_message)
        else:
            full_error_message = _("ERROR on line ") + \
                                 f"{line_num} " + _("index ") + \
                                 f"{col_num}: {msg} " + \
                                 _(", received ") + \
                                 f"{self._get_symbol_string()} "
            print(full_error_message)
            self.error_message_list.append(full_error_message)

        self.error_message_list.append(caret_msg)
        print(caret_msg)

        while True:
            while self.symbol.id != self.scanner.SEMICOLON:

                self._set_next()
                if self.unclosed_comment:
                    return

                self._get_symbol_string()
                if self._is_eof():
                    message = _("Reached end of file without finding another")\
                              + \
                              _(" semicolon - cannot perform error recovery.")
                    print(message)
                    self.error_message_list.append(f"\n{message}")

                    self.end_of_file = True
                    break

            # found a semi colon, now need to check if the expected element
            # is next

            self._set_next()
            if self.unclosed_comment:
                return

            self._get_symbol_string()  # for pytest mocking
            if self._is_eof():
                # end of file is found before the error recovery symbol is
                # found
                break
            if (
                    self.symbol.id in expect_next_list
                    or self.symbol.type in expect_next_list
            ):
                # found the character we want to keep parsing, therefore we
                # resume in the parsing
                self._get_symbol_string()  # for pytest mocking
                break

    def _is_eof(self):
        """Check if current symbol is end of file."""
        return self.symbol.type == self.scanner.EOF

    def _semantic_error(self, msg, offending_symbol=None):
        """Print semantic error with message."""
        self.error_count += 1
        if offending_symbol:
            caret_msg, line_num, col_num = \
                self.scanner.show_error(offending_symbol)

        else:
            caret_msg, line_num, col_num = \
                self.scanner.show_error(self.symbol)
            caret_msg = caret_msg[:-2]  # don't show uninformative caret

        err = _("ERROR on line ") + \
            f"{line_num} " + _("index ") + \
            f"{col_num}: {msg} "

        print(err)
        print(caret_msg)

        self.error_message_list.append(err)
        self.error_message_list.append(caret_msg)
