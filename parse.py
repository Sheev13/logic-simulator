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

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        devices_done = False
        connections_done = False
        monitors_done = False
        self.setNext()
        while True:
            if self.symbol.id == self.scanner.DEVICES_ID:
                success = self.parse_devices_list()
                #this success parameter is completely redundant
                devices_done = True

            elif self.symbol.id == self.scanner.CONNECTIONS_ID:
                if devices_done:
                    success = self.parse_connections_list(self.error_count)
                    connections_done = True
                else:
                    self.error("can't parse connections if not done devices",
                               [self.scanner.DEVICES_ID])
                    if self.eof():
                        break
                    # error recovery should look for devices
                    # maybe user put devices after connections accidentally?
                    # TODO: confirm this error recovery strategy

            elif self.symbol.id == self.scanner.MONITOR_ID:
                if devices_done:
                    success = self.parse_monitors_list(self.error_count)
                    monitors_done = True
                else:
                    self.error("can't parse monitors if not done devices",
                               [self.scanner.DEVICES_ID])
                    if self.eof():
                        break
            elif self.symbol.type == self.scanner.EOF:
                break
            else:
                self.error("not DEVICES, CONNECTIONS, MONITORS nor EOF",
                           [self.scanner.DEVICES_ID,
                            self.scanner.CONNECTIONS_ID,
                            self.scanner.MONITOR_ID,
                            self.scanner.EOF
                            ])
                if self.eof():
                    break
                # TODO: !!!!!! what if they put eg. DEVICES twice! will it
                #  still work?

        #hopefully we will always reach EOF symbol...

        print(f"Completely parsed the definition file. {self.error_count} "
              f"error(s) found in total.")
        if self.error_count == 0:  # TOTAL number of errors = 0
            return True
        else:
            return False

    def parse_devices_list(self):
        """Parse list of devices."""
        self.setNext()
        while True:
            if self.symbol.id != self.scanner.OPEN_SQUARE:
                self.error("expected [", [self.scanner.CONNECTIONS_ID,
                                          self.scanner.MONITOR_ID])  # but
                # it could also be end of file????? here/only devices
                break

            self.setNext()
            parsing_devices = True
            while parsing_devices:
                missing_semicolon = self.parse_device(self.error_count)
                # TODO: still need to check if there is an unique issue with
                #  missing semi-colon

                # this is definitely cursed below TODO
                if missing_semicolon:
                    # this is also cropping up at the wrong place
                    print("missed semicolon at end of device definition, "
                          "will end up skipping the device after")
                    
                    # this is also way too hacky
                    if self.end_of_file:
                        # TODO: SORT THIS OUT
                        break
                    #continue
                    #i don't think this is necessary because we should have an open curly in the next if statement

                if self.symbol.id == self.scanner.OPEN_CURLY:
                    parsing_devices = True
                elif self.symbol.id == self.scanner.CLOSE_SQUARE:
                    parsing_devices = False
                elif self.symbol.id == self.scanner.MONITOR_ID or self.symbol.id == self.scanner.CONNECTIONS_ID:
                    # case when an error causes us to skip to the end of
                    # devices
                    # oh but what if we never recover.... i think that is
                    # the else statement
                    break
                
                else:
                    # TODO: what if it is neither of those???
                    # is this when there is an error at the end of device
                    # lists?
                    print("device list problem", self.strSymbol())
                    print("sort this problem out")

            if self.symbol.id == self.scanner.MONITOR_ID or self.symbol.id == self.scanner.CONNECTIONS_ID:
                break

            # no longer parsing devices
            if self.symbol.id != self.scanner.CLOSE_SQUARE and self.symbol.type != self.scanner.EOF:
                self.error("expected ]", [self.scanner.CONNECTIONS_ID,
                                          self.scanner.MONITOR_ID])
                break

            self.setNext()

            if self.symbol.id != self.scanner.SEMICOLON:
                self.error("expected ;", [self.scanner.MONITOR_ID,
                                          self.scanner.CONNECTIONS_ID])
                # TODO: not sure if it's connections/monitors
                break

            if self.error_count != 0:
                break

            print("Successfully parsed the DEVICES list! \n")
            self.setNext()
            return True


        self.setNext()

        print("Did not manage to parse the DEVICES list perfectly.")
        # wish this could be more informative.......
        # maybe thats for self.error / scanner
        # what is the point of this code below huhh/???
        if self.error_count != 0:
            print(f"Found {self.error_count} error(s) when parsing the "
                  f"DEVICES list \n")
            return False

    def parse_device(self, previous_errors):
        """Parse a single device."""
        print("Parsing a single device.")
        missing_device_semicolon = False
        while True:
            if self.symbol.id != self.scanner.OPEN_CURLY:
                self.error("expected {",
                           [self.scanner.OPEN_CURLY,
                            self.scanner.CLOSE_CURLY])
                # TODO: this is where the error of searching expected
                #  linearly crops up i believeeeee ... see onennote
                break

            self.setNext()
            missing_semicolon, device_name = self.parse_device_id()

            if missing_semicolon:
                print("missed a semicolon in device id, will skip to next "
                      "device")
                break

            missing_semicolon, device_kind_string, device_kind_id = \
                self.parse_device_kind()

            if missing_semicolon:
                print("missed a semicolon in device kind, will skip to next "
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
                self.error("expected }",
                           [self.scanner.OPEN_CURLY,
                            self.scanner.CLOSE_CURLY]
                           )
                break

            self.setNext()
            if self.symbol.id != self.scanner.SEMICOLON:
                self.error("expected ;",
                           [self.scanner.OPEN_CURLY,
                            self.scanner.CONNECTIONS_ID,
                            self.scanner.MONITOR_ID]
                           )
                # if we get MONITORS or CONNECTIONS, we don't want to parse devices anymore
                missing_device_semicolon = True
                break

            # if we get here we have done a whole device!
            # for each device there are no new errors
            if self.error_count - previous_errors == 0:
                print(f"syntactically parsed the device: "
                      f"{device_name}-{device_kind_string}-{device_qual}")

                error_type = self.devices.make_device(
                    self.names.query(device_name),
                    device_kind_id,
                    device_qual)
                if error_type != self.devices.NO_ERROR:
                    if error_type == self.devices.NO_QUALIFIER:
                        self.semantic_error(f"{device_kind_string} qualifier not present.")
                    elif error_type == self.devices.INVALID_QUALIFIER:
                        self.semantic_error(f"{device_kind_string} qualifier is invalid.")
                    elif error_type == self.devices.QUALIFIER_PRESENT:
                        self.semantic_error( f"Qualifier provided for {device_kind_string} when there should be none.")
                    elif error_type == self.devices.BAD_DEVICE:
                        self.semantic_error(f"Device kind {device_kind_string} not recognised.")
                else:
                    print(f"semantically parsed & built the device:"
                          f" {device_name}-"
                          f"{device_kind_string}-{device_qual}")

                self.setNext()
                break
            else:
                print(f"did not syntactically parse the device: "
                      f"{device_name}-{device_kind_string}-{device_qual}")
                print("no attempts to build/check semantics will occur")
                self.setNext()
                break

        return missing_device_semicolon


    def parse_device_id(self):
        missing_semicolon = False
        device_name = None
        while True:
            if self.symbol.id != self.scanner.ID_KEYWORD_ID:
                self.error("expected id keyword here", [self.scanner.KIND_KEYWORD_ID])
                break

            self.setNext()
            if self.symbol.id != self.scanner.COLON:
                self.error("expected : here", [self.scanner.KIND_KEYWORD_ID])
                break

            self.setNext()
            if self.symbol.type != self.scanner.NAME:
                # name provided is syntactically incorrect for a name
                # (according to our EBNF file)
                self.error("bad name provided syntacicatlly", [self.scanner.KIND_KEYWORD_ID])
                break
            else:
                device_name = self.strSymbol()

            self.setNext()
            if self.symbol.id != self.scanner.SEMICOLON:
                self.error("missing semicolon", [self.scanner.OPEN_CURLY])
                missing_semicolon = True
                break

            self.setNext()
            break

        return missing_semicolon, device_name

    def parse_device_kind(self):
        missing_semicolon = False
        device_kind_string = None  # are these going to cause issues later
        device_kind_id = None   # when creating devices for semantic errors?

        while True:
            if self.symbol.id != self.scanner.KIND_KEYWORD_ID:
                self.error("expected kind keyword here",
                           [self.scanner.QUAL_KEYWORD_ID,
                            self.scanner.CLOSE_CURLY])
                # TODO: can tidy up if the expected list is defined as
                #  an entity before the while loop
                break

            self.setNext()
            if self.symbol.id != self.scanner.COLON:
                self.error("expected : here",
                           [self.scanner.QUAL_KEYWORD_ID,
                            self.scanner.CLOSE_CURLY]
                           )
                break

            self.setNext()
            if self.symbol.type != self.scanner.NAME:
                self.error("bad type provided syntactically",
                           [self.scanner.QUAL_KEYWORD_ID,
                            self.scanner.CLOSE_CURLY])
                break
            else:
                device_kind_string = self.strSymbol()
                [device_kind_id] = self.devices.names.lookup([device_kind_string])

            self.setNext()
            if self.symbol.id != self.scanner.SEMICOLON:
                self.error("missing semicolon", [self.scanner.OPEN_CURLY])
                # TODO: should we not also be expecting a close square....?
                #  :/ in case its the last device which has the error?

                missing_semicolon = True
                break

            self.setNext()
            break

        return missing_semicolon, device_kind_string, device_kind_id

    def parse_device_qual(self):
        missing_semicolon = False
        device_qual = None
        while True:
            if self.symbol.id != self.scanner.QUAL_KEYWORD_ID:
                self.error("expected qual keyword here",
                           [self.scanner.CLOSE_CURLY])
                break

            self.setNext()
            if self.symbol.id != self.scanner.COLON:
                self.error("expected : here",
                           [self.scanner.CLOSE_CURLY])
                break

            self.setNext()
            if self.symbol.type != self.scanner.NUMBER:
                self.error("unsupported qualifier input",
                           [self.scanner.CLOSE_CURLY])
                break
            else:
                device_qual = self.symbol.id
                # i think the id is simply the number?

            self.setNext()
            if self.symbol.id != self.scanner.SEMICOLON:
                self.error("missing semicolon", [self.scanner.OPEN_CURLY])
                # TODO: should we not also be expecting a close square....?
                #  :/ in case its the last device which has the error?

                missing_semicolon = True
                break

            self.setNext()
            break

        return missing_semicolon, device_qual

    def parse_connections_list(self, previous_errors):
        """Parse list of connections."""
        self.setNext()
        while True:
            if self.end_of_file:
                break
            if self.symbol.id != self.scanner.OPEN_SQUARE:
                self.error("expected [", [self.scanner.MONITOR_ID, self.scanner.EOF])
                # it could also be end of file, connections not necessary
                break
            self.setNext()

            parsing_connections = True
            while parsing_connections:
                if self.end_of_file:
                    break

                if self.symbol.id == self.scanner.CLOSE_SQUARE:
                    parsing_connections = False
                    break
                
                missing_semicolon = self.parse_connection(self.error_count)
                # TODO: still need to check if there is an unique issue with
                #  missing semi-colon
                if self.end_of_file:
                    break
                if missing_semicolon:
                    print("missed semicolon at end of connection definition, "
                          "will end up skipping the connection after")
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
                else:
                    # TODO: what if it is neither of those???
                    # is this when there is an error at the end of connection
                    # lists?
                    print("sort this problem out")
                    print("Unexpected symbol: ", self.strSymbol())

            if self.end_of_file:
                break

            if self.symbol.id == self.scanner.MONITOR_ID:
                break
            
            # no longer parsing connections
            if self.symbol.id != self.scanner.CLOSE_SQUARE:
                self.error("expected ]", [self.scanner.MONITOR_ID, self.scanner.EOF])
                break

            self.setNext()
            
            if self.symbol.id != self.scanner.SEMICOLON:
                self.error("expected ;", [self.scanner.MONITOR_ID, self.scanner.EOF])
                break

            if self.error_count - previous_errors != 0:
                break

            print("Successfully parsed the CONNECTIONS list! \n")
            self.setNext()
            return True

        if self.symbol.id != self.scanner.MONITOR_ID:
            self.setNext()

        print("Did not manage to parse the connections list perfectly")

        if self.error_count - previous_errors != 0:
            print(f"Found {self.error_count - previous_errors} error(s) when parsing "
                  f"the "
                  f"CONNECTIONS list \n")
            return False

    def parse_connection(self, previous_errors):
        """Parse a single connection."""
        print("Parsing a single connection.")
        missing_signal_end_marker = False
        while True:
            if self.symbol.id == self.scanner.SEMICOLON:
                self.error(
                    "No connection found before semicolon",
                    [self.scanner.NAME]
                )
                break
            missing_signal_end_marker, leftOutputId, leftPortId, leftSignalName = self.parse_signal()
            if self.end_of_file:
                break
            if missing_signal_end_marker:
                print("missed colon in connection, will skip to next "
                      "connection")
                break
            self.setNext()

            missing_signal_end_marker, rightOutputId, rightPortId, rightSignalName = self.parse_signal()
            if self.end_of_file:
                break
            if missing_signal_end_marker:
                print("missed semicolon at end of connection, will skip to next "
                      "connection")
                break

            if self.error_count - previous_errors == 0:
                print("No errors when parsing connection --> proceed to build.")
                error_type = self.network.make_connection(leftOutputId, leftPortId, rightOutputId, rightPortId)

                if error_type != self.network.NO_ERROR:
                    if error_type == self.network.DEVICE_ABSENT:
                        self.semantic_error("Either left or right device is "
                                            "absent")
                    elif error_type == self.network.INPUT_CONNECTED:
                        self.semantic_error(f"Input {rightSignalName} is already connected.")
                    elif error_type == self.network.INPUT_TO_INPUT:
                        self.semantic_error(f"Both ports are inputs.")
                    elif error_type == self.network.PORT_ABSENT:
                        self.semantic_error(f"Right port id is invalid.")
                    elif error_type == self.network.OUTPUT_TO_OUTPUT:
                        self.semantic_error(f"Both ports are outputs.")
                else:
                    print(f"Successfully built connection from {leftSignalName} to {rightSignalName}.")
        
                self.setNext()
                break

            else:
                print(f"Could not syntactically parse the connection.")
                print("No attempts to build/check semantics will occur.")
                self.setNext()
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
            self.setNext()

            if self.symbol.id == self.scanner.DOT:
                signalName += "."
                self.setNext()

                if self.symbol.type != self.scanner.NAME:
                    self.error("expected a port name here", [self.scanner.NAME])
                    break
            
                signalName += self.names.get_name_string(self.symbol.id)
                portId = self.symbol.id
                self.setNext()
            if self.symbol.id != self.scanner.COLON and self.symbol.id != self.scanner.SEMICOLON:
                missing_end_marker = True
                self.error("missing ':' or ';'", [self.scanner.NAME, self.scanner.CLOSE_SQUARE, self.scanner.MONITOR_ID])
                break

            break

        return missing_end_marker, deviceId, portId, signalName

    def parse_monitors_list(self, previous_errors):
        """Parse list of monitors."""
        self.setNext()
        while True:
            if self.end_of_file:
                break
            if self.symbol.id != self.scanner.OPEN_SQUARE:
                self.error("expected [", [self.scanner.CONNECTIONS_ID, self.scanner.EOF])
                # it could also be end of file, monitors not necessary
                break
            self.setNext()

            parsing_monitors = True
            while parsing_monitors:
                if self.end_of_file:
                    break

                if self.symbol.id == self.scanner.CLOSE_SQUARE:
                    parsing_monitors = False
                    break

                missing_semicolon = self.parse_monitor(self.error_count)
                # TODO: still need to check if there is an unique issue with
                    #  missing semi-colon
                if self.end_of_file:
                    break
                if missing_semicolon:
                    print("missed semicolon at end of monitor, "
                        "will end up skipping the monitor after")
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
                else:
                    # TODO: what if it is neither of those???
                    # is this when there is an error at the end of connection
                    # lists?
                    print("sort this problem out")
                    print("Unexpected symbol: ", self.strSymbol())

            if self.end_of_file:
                break
            
            if self.symbol.id == self.scanner.CONNECTIONS_ID:
                break

            # no longer parsing monitors
            if self.symbol.id != self.scanner.CLOSE_SQUARE:
                self.error("expected ]", [self.scanner.CONNECTIONS_ID, self.scanner.EOF])
                break

            self.setNext()

            if self.symbol.id != self.scanner.SEMICOLON:
                self.error("expected ;", [self.scanner.EOF, self.scanner.CONNECTIONS_ID])
                break

            if self.error_count - previous_errors != 0:
                break

            print("Successfully parsed the MONITORS list! \n")
            self.setNext()
            return True

        print("Did not manage to parse the MONITORS list perfectly")

        if self.symbol.id != self.scanner.CONNECTIONS_ID and self.symbol.id != self.scanner.EOF:
            self.setNext()

        if self.error_count - previous_errors != 0:
            print(f"Found {self.error_count - previous_errors} error(s) when parsing the MONITORS list")
            return False

    def parse_monitor(self, previous_errors):
        """Parse a single monitor."""
        print("Parsing a monitor.")
        missing_semicolon = False
        while True:
            if self.symbol.id == self.scanner.SEMICOLON:
                self.error(
                    "No signal found before semicolon",
                    [self.scanner.NAME]
                )
                break
            missing_semicolon, deviceId, portId, signalName = self.parse_signal()
            if self.end_of_file:
                break
            if missing_semicolon:
                print("missed a semicolon, will skip to next monitor")
                break
            self.setNext()

            if self.error_count - previous_errors == 0:
                print("No errors when parsing monitor --> proceed to build.")
                error_type = self.monitors.make_monitor(deviceId, portId)

                if error_type != self.monitors.NO_ERROR:
                    if error_type == self.network.DEVICE_ABSENT:
                        self.semantic_error("Device you are trying to monitor is absent.")
                    elif error_type == self.monitors.NOT_OUTPUT:
                        self.semantic_error(f"{signalName} is not an output.")
                    elif error_type == self.monitors.MONITOR_PRESENT:
                        self.semantic_error(f"Already monitoring {signalName}.")
                else:
                    print(f"Successfully built monitor {signalName}.")
                break

            else:
                print(f"Could not syntactically parse the monitor.")
                print("No attempts to build/check semantics will occur.")
                self.setNext()
                break

        return missing_semicolon

    def setNext(self):
        """Shift current symbol to next."""
        self.symbol = self.scanner.get_symbol()

    def strSymbol(self):
        """For use in testing to more easily print symbol string."""
        try:
            return self.names.get_name_string(self.symbol.id)
        except:
            return "NONE"

    def error(self, msg, expect_next_list):
        self.end_of_file = False
        carat_msg, line_num, col_num = self.scanner.show_error(self.symbol)
        print(f"ERROR on line {line_num} index {col_num}: " + msg +
              f", received {self.strSymbol()}")
        print(carat_msg)
        self.error_count += 1
        while True:
            while self.symbol.id != self.scanner.SEMICOLON:
                self.setNext()
                self.strSymbol()
                if self.symbol.type == self.scanner.EOF:
                    print("reached end of file without another semicolon")
                    self.end_of_file = True
                    break
            # found a semi colon, now need to check if the expected element
            # is next
            self.setNext()
            self.strSymbol()
            if self.symbol.type == self.scanner.EOF:
                print("reached end of file without finding expected symbol")
                self.end_of_file = True
                break
            if self.symbol.id in expect_next_list or self.symbol.type in expect_next_list:
                # found the character we want to keep parsing, therefore we
                # resume in the parsing
                break

    def eof(self):
        return self.symbol.type == self.scanner.EOF
    
    def semantic_error(self, msg):
        print("SEMANTIC ERROR: "+ msg)
        self.error_count += 1
        # no error recovery stuff here? :0
