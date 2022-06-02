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
    parse_network(self): Parses the circuit definition file.
    
    parse_devices_list(self): Parses the devices list.
    
    parse_device(self, previous_errors): Parses a device.
    
    parse_device_id(self): Parses a device id.

    parse_device_kind(self): Parses a device kind.

    parse_device_qual(self): Parses a device qualifier.

    parse_connections_list(self, previous_errors): Parses a 
                            connections list.

    parse_connection(self, previous_errors): Parses a connection.
    
    parse_signal(self): Parses the name of a signal.
    
    parse_monitors_list(self, previous_errors): Parses monitors list.

    parse_monitors_list(self, previous_errors): Parses a single monitor.
    
    set_next(self): Shifts current symbol to the next.

    get_symbol_string(self): Gets the string of current symbol.

    error(self): Produces error message and recovers from next ';'.
    
    semantic_error(self, msg): Prints semantic error with message.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        self.error_count = 0
        self.end_of_file = False

        self.symbol = None
        self.unclosed_comment = False

        self.error_message_list = []


    def parse_network(self):
        """Parse the circuit definition file."""
        devices_done = False
        connections_done = False
        monitors_done = False
        self.set_next()

        if self.symbol.type == self.scanner.EOF and not \
                self.unclosed_comment:

            # this is when we get an empty file - we would like to show
            # an error
            # oh no are my tests going to screw up?

            self.error("Empty definition file was loaded.", [self.scanner.EOF])

            print("ERROR: Empty definition file was loaded.")
            self.error_count += 1
            print(
                f"Completely parsed the definition file. {self.error_count} "
                f"error(s) found in total."
            )
            return False

        while True:

            if self.symbol.id == self.scanner.DEVICES_ID:
                if devices_done:
                    self.error(
                        "Multiple device lists found.",
                        [
                            self.scanner.CONNECTIONS_ID,
                            self.scanner.MONITOR_ID,
                            self.scanner.EOF
                        ],
                    )
                else:
                    self.parse_devices_list()
                    devices_done = True

            elif self.symbol.id == self.scanner.CONNECTIONS_ID:
                if connections_done:
                    self.error(
                        "Multiple connections lists found.",
                        [
                            self.scanner.MONITOR_ID,
                            self.scanner.EOF
                        ],
                    )
                else:
                    if devices_done:
                        self.parse_connections_list(self.error_count)
                        connections_done = True
                    else:
                        self.error(
                            "can't parse connections if not done devices",
                            [self.scanner.DEVICES_ID],
                        )
                        if self._is_eof():
                            break

            elif self.symbol.id == self.scanner.MONITOR_ID:
                if monitors_done:
                    self.error(
                        "Multiple monitors lists found.",
                        [
                            self.scanner.CONNECTIONS_ID,
                            self.scanner.EOF
                        ],
                    )
                else:
                    if devices_done:
                        self.parse_monitors_list(self.error_count)
                        monitors_done = True
                    else:
                        self.error(
                            "can't parse monitors if not done devices",
                            [self.scanner.DEVICES_ID],
                        )
                        if self._is_eof():
                            break
            elif self._is_eof():
                break
            else:
                self.error(
                    "not DEVICES, CONNECTIONS, MONITORS nor EOF",
                    [
                        self.scanner.DEVICES_ID,
                        self.scanner.CONNECTIONS_ID,
                        self.scanner.MONITOR_ID,
                        self.scanner.EOF,
                    ],
                )
                if self._is_eof():
                    break

        final_error_count = f"{self.error_count} error(s) found"
        self.error_message_list.append(final_error_count)
        print(
            f"Completely parsed the definition file. {final_error_count} in total."
        )
        if self.error_count == 0:  # syn + sem errors = 0
            return True
        else:
            return False

    def parse_devices_list(self):
        """Parse list of devices."""
        self.set_next()
        while True:
            if self.symbol.id != self.scanner.OPEN_SQUARE:
                self.error(
                    "expected [", [
                        self.scanner.CONNECTIONS_ID, self.scanner.MONITOR_ID])
                # it could also be end of file? here/only devices
                break

            self.set_next()
            parsing_devices = True
            while parsing_devices:
                if self.end_of_file:
                    break

                if self.symbol.id == self.scanner.CLOSE_SQUARE:
                    # if empty DEVICES list
                    break

                missing_semicolon = self.parse_device(self.error_count)
                if missing_semicolon:
                    print(
                        "missed semicolon at end of device definition, "
                        "will end up skipping the device after"
                    )
                    if self.end_of_file:
                        break

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
                    self.error(
                        "invalid character encountered", [
                            self.scanner.OPEN_CURLY])
                elif self.symbol.type == self.scanner.EOF:
                    # reached end of file through error recovery in inner loop
                    #break
                    return
                else:
                    # problem is not getting { or ] - i.e. device is missing
                    # opening curly bracket perhaps, try and look for { or ],
                    # if not those then look for connections/monitors
                    # if not those then EOF

                    self.get_symbol_string()
                    self.error("Invalid input to a DEVICES list. Devices "
                               "should start with '{', or the list should "
                               "end with ']' ",
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
                        # TODO: need to check this
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
                self.error(
                    "expected ]", [
                        self.scanner.CONNECTIONS_ID, self.scanner.MONITOR_ID])
                break

            self.set_next()

            if self.symbol.id != self.scanner.SEMICOLON:
                self.error(
                    "expected ;", [
                        self.scanner.MONITOR_ID, self.scanner.CONNECTIONS_ID])
                break

            if self.error_count != 0:
                break

            # print("Successfully parsed the DEVICES list! \n")
            self.set_next()
            return True

        if (
            self.symbol.id != self.scanner.MONITOR_ID
            and self.symbol.id != self.scanner.CONNECTIONS_ID
        ):
            self.set_next()

        #print("Did not manage to parse the DEVICES list perfectly.")
        if self.error_count != 0:
            print(
                f"Found {self.error_count} error(s) when parsing the "
                f"DEVICES list \n"
            )
            return False

    def parse_device(self, previous_errors):
        """Parse a single device."""
        #print("Parsing a single device.")
        missing_device_semicolon = False
        while True:
            if self.symbol.id != self.scanner.OPEN_CURLY:
                self.error(
                    "expected {", [
                        self.scanner.OPEN_CURLY, self.scanner.CLOSE_CURLY])
                break

            self.set_next()
            missing_semicolon, device_name = self.parse_device_id()

            if missing_semicolon:
                print(
                    "missed a semicolon in device id, will skip to next "
                    "device")
                break

            (
                missing_semicolon,
                device_kind_string,
                device_kind_id,
            ) = self.parse_device_kind()

            if missing_semicolon:
                print(
                    "missed a semicolon in device kind, will skip to next "
                    "device")
                break

            if self.symbol.id == self.scanner.QUAL_KEYWORD_ID:
                missing_semicolon, device_qual = self.parse_device_qual()
                if missing_semicolon:
                    print(
                        "missed a semicolon in device qual, will skip to "
                        "next device")
                    break
            else:
                device_qual = None

            if self.symbol.id != self.scanner.CLOSE_CURLY:
                self.error(
                    "expected }", [
                        self.scanner.OPEN_CURLY, self.scanner.CLOSE_CURLY])
                break

            self.set_next()
            if self.symbol.id != self.scanner.SEMICOLON:
                self.error(
                    "expected ;",
                    [
                        self.scanner.OPEN_CURLY,
                        self.scanner.CONNECTIONS_ID,
                        self.scanner.MONITOR_ID,
                    ],
                )
                # if MONITORS or CONNECTIONS, stop parsing devices
                missing_device_semicolon = True
                break

            # if we get here we have done a whole device!
            # for each device there are no new errors
            if self.error_count - previous_errors == 0:
                # print(
                #     f"syntactically parsed the device: "
                #     f"{device_name}-{device_kind_string}-{device_qual}"
                # )

                error_type = self.devices.make_device(
                    self.names.query(device_name), device_kind_id, device_qual
                )
                if error_type != self.devices.NO_ERROR:
                    if error_type == self.devices.NO_QUALIFIER:
                        self.semantic_error(
                            f"{device_kind_string} qualifier not present."
                        )
                    elif error_type == self.devices.INVALID_QUALIFIER:
                        self.semantic_error(
                            f"{device_kind_string} qualifier is invalid."
                        )
                    elif error_type == self.devices.QUALIFIER_PRESENT:
                        self.semantic_error(
                            f"Qualifier provided for {device_kind_string} "
                            f"when there should be none."
                        )
                    elif error_type == self.devices.BAD_DEVICE:
                        self.semantic_error(
                            f"Device kind {device_kind_string} not recognised."
                        )
                #else:
                    # print(
                    #     f"semantically parsed & built the device:"
                    #     f" {device_name}-"
                    #     f"{device_kind_string}-{device_qual}"
                    # )

                self.set_next()
                break
            else:
                # print(
                #     f"did not syntactically parse the device: "
                #     f"{device_name}-{device_kind_string}-{device_qual}"
                # )
                # print("no attempts to build/check semantics will occur")
                self.set_next()
                break

        return missing_device_semicolon

    def parse_device_id(self):
        """Parse a device id."""
        missing_semicolon = False
        device_name = None
        while True:
            if self.symbol.id != self.scanner.ID_KEYWORD_ID:
                self.error(
                    "expected id keyword here", [
                        self.scanner.KIND_KEYWORD_ID])
                break

            self.set_next()
            if self.symbol.id != self.scanner.COLON:
                self.error("expected : here", [self.scanner.KIND_KEYWORD_ID])
                break

            self.set_next()
            if self.symbol.type != self.scanner.NAME:
                # name provided is syntactically incorrect for a name
                if self.symbol.type == self.scanner.KEYWORD:
                    self.error(
                    "Invalid name provided - a keyword cannot be used as a device name", [
                        self.scanner.KIND_KEYWORD_ID])
                    break
                else:
                    self.error(
                    "Invalid name provided - a device name should be alphanumeric", [
                        self.scanner.KIND_KEYWORD_ID])
                    break
            else:
                device_name = self.get_symbol_string()

            self.set_next()
            if self.symbol.id != self.scanner.SEMICOLON:
                self.error("Missing semicolon", [self.scanner.OPEN_CURLY])
                missing_semicolon = True
                print(self.get_symbol_string())
                break

            self.set_next()
            break

        self.get_symbol_string()
        return missing_semicolon, device_name

    def parse_device_kind(self):
        """Parse a device kind."""
        missing_semicolon = False
        device_kind_string = None  # may cause sem errors when creating devices
        device_kind_id = None

        while True:
            if self.symbol.id != self.scanner.KIND_KEYWORD_ID:
                self.error(
                    "expected kind keyword here",
                    [self.scanner.QUAL_KEYWORD_ID, self.scanner.CLOSE_CURLY],
                )
                break

            self.set_next()
            if self.symbol.id != self.scanner.COLON:
                self.error(
                    "expected : here",
                    [self.scanner.QUAL_KEYWORD_ID, self.scanner.CLOSE_CURLY],
                )
                break

            self.set_next()
            if self.symbol.type != self.scanner.NAME:
                self.error(
                    "Device type must be at least alphanumeric",
                    [self.scanner.QUAL_KEYWORD_ID, self.scanner.CLOSE_CURLY],
                )
                break
            else:
                device_kind_string = self.get_symbol_string()
                [device_kind_id] = self.devices.names.lookup(
                    [device_kind_string])

            self.set_next()
            if self.symbol.id != self.scanner.SEMICOLON:
                self.error(
                    "missing semicolon",
                    [self.scanner.OPEN_CURLY, self.scanner.CLOSE_SQUARE],
                )
                missing_semicolon = True
                break

            self.set_next()
            break

        return missing_semicolon, device_kind_string, device_kind_id

    def parse_device_qual(self):
        """Parse a device qualifier."""
        missing_semicolon = False
        device_qual = None
        while True:
            if self.symbol.id != self.scanner.QUAL_KEYWORD_ID:
                self.error(
                    "expected qual keyword here", [
                        self.scanner.CLOSE_CURLY])
                break

            self.set_next()
            if self.symbol.id != self.scanner.COLON:
                self.error("expected : here", [self.scanner.CLOSE_CURLY])
                break

            self.set_next()
            if self.symbol.type != self.scanner.NUMBER:
                self.error(
                    "unsupported qualifier input", [
                        self.scanner.CLOSE_CURLY])
                break
            else:
                device_qual = self.symbol.id

            self.set_next()
            if self.symbol.id != self.scanner.SEMICOLON:
                self.error(
                    "missing semicolon",
                    [self.scanner.OPEN_CURLY, self.scanner.CLOSE_SQUARE],
                )
                missing_semicolon = True
                break

            self.set_next()
            break

        return missing_semicolon, device_qual

    def parse_connections_list(self, previous_errors):
        """Parse list of connections."""
        self.set_next()
        while True:
            if self.end_of_file:
                break
            if self.symbol.id != self.scanner.OPEN_SQUARE:
                self.error(
                    "expected [", [
                        self.scanner.MONITOR_ID, self.scanner.EOF])
                # it could also be end of file, connections not necessary
                break
            self.set_next()

            parsing_connections = True
            while parsing_connections:
                if self.end_of_file:
                    break

                if self.symbol.id == self.scanner.CLOSE_SQUARE:
                    parsing_connections = False
                    break

                missing_semicolon = self.parse_connection(self.error_count)
                if self.end_of_file:
                    break
                if missing_semicolon:
                    # print(
                    #     "missed semicolon at end of connection definition, "
                    #     "will end up skipping the connection after"
                    # )
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
                    self.error(
                        "invalid character encountered", [
                            self.scanner.NAME])
                    # i think this should be different error recvoery?
                    # did i write this code?
                else:
                    self.error("what have we got here",
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
                        # TODO: need to check this
                        return
                    elif self.symbol.id == self.scanner.MONITOR_ID:
                        break

            if self.end_of_file:
                break

            if self.symbol.id == self.scanner.MONITOR_ID:
                break

            # no longer parsing connections
            if self.symbol.id != self.scanner.CLOSE_SQUARE:
                self.error(
                    "expected ]", [
                        self.scanner.MONITOR_ID, self.scanner.EOF])
                break

            self.set_next()

            if self.symbol.id != self.scanner.SEMICOLON:
                self.error(
                    "expected ;", [
                        self.scanner.MONITOR_ID, self.scanner.EOF])
                break

            if self.error_count - previous_errors != 0:
                break

            print("Successfully parsed the CONNECTIONS list! \n")
            self.set_next()
            return True

        if self.symbol.id != self.scanner.MONITOR_ID:
            self.set_next()

        #print("Did not manage to parse the connections list perfectly")

        if self.error_count - previous_errors != 0:
            print(
                f"Found {self.error_count - previous_errors} "
                f"error(s) when parsing the "
                f"CONNECTIONS list \n"
            )
            return False

    def parse_connection(self, previous_errors):
        """Parse a single connection."""
        #print("Parsing a single connection.")
        missing_signal_end_marker = False
        while True:
            if self.symbol.id == self.scanner.SEMICOLON:
                self.error(
                    "No connection found before semicolon", [
                        self.scanner.NAME])
                break
            (
                missing_signal_end_marker,
                leftOutputId,
                leftPortId,
                leftSignalName,
            ) = self.parse_signal()
            if self.end_of_file:
                break
            if missing_signal_end_marker:
                print(
                    "missed colon in connection, will skip to next "
                    "connection")
                break
            self.set_next()

            (
                missing_signal_end_marker,
                rightOutputId,
                rightPortId,
                rightSignalName,
            ) = self.parse_signal()
            if self.end_of_file:
                break
            if missing_signal_end_marker:
                # print(
                #     "missed semicolon at end of connection, will skip "
                #     "to next connection"
                # )
                break

            if self.error_count - previous_errors == 0:
                # print("No errors when parsing connection -->" +
                #       "proceed to build.")
                error_type = self.network.make_connection(
                    leftOutputId, leftPortId, rightOutputId, rightPortId
                )

                if error_type != self.network.NO_ERROR:
                    if error_type == self.network.DEVICE_ABSENT:
                        self.semantic_error(
                            "Either left or right device is " "absent")
                    elif error_type == self.network.INPUT_CONNECTED:
                        self.semantic_error(
                            f"Input {rightSignalName} is already connected."
                        )
                    elif error_type == self.network.INPUT_TO_INPUT:
                        self.semantic_error(f"Both ports are inputs.")
                    elif error_type == self.network.PORT_ABSENT:
                        self.semantic_error(f"Right port id is invalid.")
                    elif error_type == self.network.OUTPUT_TO_OUTPUT:
                        self.semantic_error(f"Both ports are outputs.")
                
                # else:
                #     print(
                #         f"Successfully built connection from "
                #         f"{leftSignalName} to {rightSignalName}."
                #     )

                self.set_next()
                break

            else:
                # print(f"Could not syntactically parse the connection.")
                # print("No attempts to build/check semantics will occur.")
                self.set_next()
                break

        return missing_signal_end_marker

    def parse_signal(self):
        """Parse a signal name."""
        missing_end_marker = False
        signalName = ""
        deviceId = None
        portId = None

        while True:
            if self.symbol.type != self.scanner.NAME:
                self.error("Expected an output name here", [self.scanner.NAME])
                break

            signalName += self.names.get_name_string(self.symbol.id)
            deviceId = self.symbol.id
            self.set_next()

            if self.symbol.id == self.scanner.DOT:
                signalName += "."
                self.set_next()

                if self.symbol.type != self.scanner.NAME:
                    self.error(
                        "expected a port name here", [
                            self.scanner.NAME])
                    break

                signalName += self.names.get_name_string(self.symbol.id)
                portId = self.symbol.id
                self.set_next()
            if (
                self.symbol.id != self.scanner.COLON
                and self.symbol.id != self.scanner.SEMICOLON
            ):
                missing_end_marker = True
                self.error(
                    "missing ':' or ';'",
                    [
                        self.scanner.NAME,
                        self.scanner.CLOSE_SQUARE,
                        self.scanner.MONITOR_ID,
                    ],
                )
                break

            break

        return missing_end_marker, deviceId, portId, signalName

    def parse_monitors_list(self, previous_errors):
        """Parse list of monitors."""
        self.set_next()
        while True:
            if self.end_of_file:
                break
            if self.symbol.id != self.scanner.OPEN_SQUARE:
                self.error(
                    "expected [", [
                        self.scanner.CONNECTIONS_ID, self.scanner.EOF])
                # it could also be end of file, monitors not necessary
                break
            self.set_next()

            parsing_monitors = True
            while parsing_monitors:
                if self.end_of_file:
                    break

                if self.symbol.id == self.scanner.CLOSE_SQUARE:
                    parsing_monitors = False
                    break

                missing_semicolon = self.parse_monitor(self.error_count)

                if self.end_of_file:
                    break
                if missing_semicolon:
                    # print(
                    #     "missed semicolon at end of monitor, "
                    #     "will end up skipping the monitor after"
                    # )
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
                    self.error(
                        "invalid character encountered", [
                            self.scanner.NAME])
                else:
                    # unknown problem
                    print("unknown error has occurred")
                    self.error_count += 1
                    break

            if self.end_of_file:
                break

            if self.symbol.id == self.scanner.CONNECTIONS_ID:
                break

            # no longer parsing monitors
            if self.symbol.id != self.scanner.CLOSE_SQUARE:
                self.error(
                    "expected ]", [
                        self.scanner.CONNECTIONS_ID, self.scanner.EOF])
                break

            self.set_next()

            if self.symbol.id != self.scanner.SEMICOLON:
                self.error(
                    "expected ;", [
                        self.scanner.EOF, self.scanner.CONNECTIONS_ID])
                break

            if self.error_count - previous_errors != 0:
                break

            print("Successfully parsed the MONITORS list! \n")
            self.set_next()
            return True

        #print("Did not manage to parse the MONITORS list perfectly")

        if (
            self.symbol.id != self.scanner.CONNECTIONS_ID
            and self.symbol.id != self.scanner.EOF
        ):
            self.set_next()

        if self.error_count - previous_errors != 0:
            print(
                f"Found {self.error_count - previous_errors} "
                "error(s) when parsing the MONITORS list \n"
            )
            return False

    def parse_monitor(self, previous_errors):
        """Parse a single monitor."""
        #print("Parsing a monitor.")
        missing_semicolon = False
        while True:
            if self.symbol.id == self.scanner.SEMICOLON:
                self.error(
                    "No signal found before semicolon", [
                        self.scanner.NAME])
                break
            (missing_semicolon, deviceId,
                portId, signalName) = self.parse_signal()
            if self.end_of_file:
                break
            if missing_semicolon:
                #print("missed a semicolon, will skip to next monitor")
                break

            if self.error_count - previous_errors == 0:
                #print("No errors when parsing monitor --> proceed to build.")
                error_type = self.monitors.make_monitor(deviceId, portId)

                if error_type != self.monitors.NO_ERROR:
                    if error_type == self.network.DEVICE_ABSENT:
                        self.semantic_error(
                            "Device you are trying to monitor is absent."
                        )
                    elif error_type == self.monitors.NOT_OUTPUT:
                        self.semantic_error(f"{signalName} is not an output.")
                    elif error_type == self.monitors.MONITOR_PRESENT:
                        self.semantic_error(
                            f"Already monitoring {signalName}.")
                
                self.set_next()
                # else:
                #     print(f"Successfully built monitor {signalName}.")
                break

            else:
                # print(f"Could not syntactically parse the monitor.")
                # print("No attempts to build/check semantics will occur.")
                self.set_next()
                break

        return missing_semicolon

    def set_next(self):
        """Shift current symbol to next."""
        self.symbol = self.scanner.get_symbol()
        # added to deal with unclosed comments
        # if self.symbol.type == self.scanner.UNCLOSED:
        #     self.symbol = self.scanner.get_symbol()

        if self.symbol.type == self.scanner.UNCLOSED:

            self.unclosed_comment = True
            self.error(
                "Unclosed Comment Found - did you want to use '/' instead of "
                "'#' for your comment?",
                [],
            )



    def get_symbol_string(self):
        """More easily print current symbol string."""
        try:
            return self.names.get_name_string(self.symbol.id)
        except TypeError:
            return "NONE"

    def error(self, msg, expect_next_list):
        """Print error message and recover from next semicolon."""
        self.error_count += 1



        caret_msg, line_num, col_num = self.scanner.show_error(self.symbol)
        


        # if len(expect_next_list) == 0:
        #     #for unclosed comments
        #     full_error_message = f"\nERROR on line {line_num} " \
        #                          f"index {col_num}: " + msg
        #
        #     print(full_error_message)
        #     self.error_message_list.append(full_error_message)
        #     return

        if self.symbol.type == self.scanner.EOF:
            full_error_message = f"\nERROR on line {line_num} " \
                                 f"index {col_num}: " + msg
            print(full_error_message)
            self.error_message_list.append(full_error_message)
            self.end_of_file = True
            return

        self.end_of_file = False

        received_symbol = self.get_symbol_string()
        if received_symbol == "NONE":  #the case if not in names list
            full_error_message = f"\nERROR on line {line_num} " \
                                 f"index {col_num}: " + msg

            print(full_error_message)
            self.error_message_list.append(full_error_message)
        else:
            full_error_message =  f"\nERROR on line {line_num} index " \
                                  f"{col_num}: " \
                                  + msg + f", received {self.get_symbol_string()}"
            print(full_error_message)
            self.error_message_list.append(full_error_message)



        self.error_message_list.append(caret_msg)
        print(caret_msg)

        while True:
            while self.symbol.id != self.scanner.SEMICOLON:
                self.set_next()
                self.get_symbol_string()
                if self._is_eof():
                    message = "Reached end of file without finding another " \
                              "semicolon - cannot perform error recovery"
                    print(message)
                    self.error_message_list.append(f"\n{message}")
                    self.end_of_file = True
                    break
            # found a semi colon, now need to check if the expected element
            # is next
            self.set_next()
            self.get_symbol_string()
            if self._is_eof():
                # print("Reached end of file without finding expected symbol "
                #       "for error recovery")
                break
            if (
                self.symbol.id in expect_next_list
                or self.symbol.type in expect_next_list
            ):
                # found the character we want to keep parsing, therefore we
                # resume in the parsing
                self.get_symbol_string()
                # necessary for unit testing of error recovery
                break

    def _is_eof(self):
        """Check if current symbol is end of file."""
        return self.symbol.type == self.scanner.EOF

    def semantic_error(self, msg):
        """Print semantic error with message."""

        caret_msg, line_num, col_num = self.scanner.show_error(self.symbol)



        err = f"\nERROR on line {line_num} index {col_num}: " + msg

        print(err)
        self.error_message_list.append(err)



        print(caret_msg[:-2]) #if time try to store semantic error symbol

        self.error_count += 1
