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
                success = self.parse_device_list()
                devices_done = True

            elif self.symbol.id == self.scanner.CONNECTIONS_ID:
                if devices_done:
                    success = self.parse_connections_list()
                else:
                    self.error("can't parse connections if not done devices",
                               [self.scanner.DEVICES_ID])
                    # error recovery should look for devices
                    # maybe user put devices after connections accidentally?
                    # TODO: confirm this error recovery strategy
            elif self.symbol.id == self.scanner.MONITOR_ID:
                if devices_done:
                    success = self.parse_monitor_list()
                else:
                    self.error("can't parse monitors if not done devices",
                               [self.scanner.DEVICES_ID])
            elif self.symbol.id == self.scanner.EOF:
                print("reached end of file!")
                # TODO: close file routine?
                break
            else:
                self.error("not DEVICES, CONNECTIONS, MONITORS nor EOF",
                           [self.scanner.DEVICES_ID,
                            self.scanner.CONNECTIONS_ID,
                            self.scanner.MONITOR_ID,
                            self.scanner.EOF
                            ])
                # TODO: !!!!!! what if they put eg. DEVICES twice! will it
                #  still work?



        #hopefully we will always reach EOF symbol...

        print("Done the definition file")
        if self.error_count == 0:
            return True
        else:
            return False



    def parse_device_list(self):
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
                missing_semi_colon = self.parse_device(self.error_count)
                # TODO: still need to check if there is an unique issue with
                #  missing semi-colon
                if missing_semi_colon:
                    print("missed semi colon at end of device definition, "
                          "will end up skipping the device after")
                    continue


                if self.symbol.id == self.scanner.OPEN_CURLY:
                    parsing_devices = True
                elif self.symbol.id == self.scanner.CLOSE_SQUARE:
                    parsing_devices = False
                else:
                    # TODO: what if it is neither of those???
                    # is this when there is an error at the end of device
                    # lists?
                    print("sort this problem out")

            # no longer parsing devices
            if self.symbol.id != self.scanner.CLOSE_SQUARE:
                self.error("expected ]", [self.scanner.CONNECTIONS_ID,
                                          self.scanner.MONITOR_ID])
                break

            self.setNext()
            if self.symbol.id != self.scanner.SEMICOLON:
                self.error("expected ;", [self.scanner.MONITOR_ID])
                # TODO: not sure if it's connections/monitors
                break

            # TODO: tidy up the logic below here
            # I mean it has to be 0 surely?
            # i think maybe residue errors?
            if self.error_count == 0:
                print("successfully parsed a device list!")
                self.setNext()  #to sync with error recovery
                return True
            else:
                print(f"found {self.error_count} error(s)")
                break

        #i think we need a self.next here somewhere...

        # only get here if there is an error with the 'outer' device list
        # wrapper
        print("did not manage to parse the device list perfectly")
        # wish this could be more informative.......
        # maybe thats for self.error / scanner
        # what is the point of this code below huhh/???
        if self.error_count != 0:
            return False



    def parse_device(self, previous_errors):
        """Parse a single device."""
        missing_device_semi_colon = False
        while True:
            if self.symbol.id != self.scanner.OPEN_CURLY:
                self.error("expected {",
                           [self.scanner.OPEN_CURLY,
                            self.scanner.CLOSE_CURLY])
                # TODO: this is where the error of searching expected
                #  linearly crops up i believeeeee ... see onennote
                break

            self.setNext()
            missing_semi_colon, device_name = self.parse_device_id()

            if missing_semi_colon:
                print("missed a semi colon in device id, will skip to next "
                      "device")
                break

            missing_semi_colon, device_kind_string, device_kind_id = \
                self.parse_device_kind()

            if missing_semi_colon:
                print("missed a semi colon in device kind, will skip to next "
                      "device")
                break

            if self.symbol.id == self.scanner.QUAL_KEYWORD_ID:
                missing_semi_colon, device_qual = self.parse_device_qual()
                if missing_semi_colon:
                    print(
                        "missed a semi colon in device qual, will skip to "
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
                            self.scanner.CLOSE_SQUARE]
                           )
                missing_device_semi_colon = True
                break

            # if we get here we have done a whole device!
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


                # this is here so that error recover + normal operation are
                # in sync
                self.setNext()
                break
            else:
                print(f"did not syntactically parse the device: "
                      f"{device_name}-{device_kind_string}-{device_qual}")
                print("no attempts to build/check semantics will occur")
                self.setNext()
                break

        return missing_device_semi_colon


    def parse_device_id(self):
        missing_semi_colon = False
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
                missing_semi_colon = True
                break

            self.setNext()
            break

        return missing_semi_colon, device_name

    def parse_device_kind(self):
        missing_semi_colon = False
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

                missing_semi_colon = True
                break

            self.setNext()
            break

        return missing_semi_colon, device_kind_string, device_kind_id

    def parse_device_qual(self):
        missing_semi_colon = False
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

                missing_semi_colon = True
                break

            self.setNext()
            break

        return missing_semi_colon, device_qual



    def parse_connections_list(self):
        """Parse list of connections."""
        self.setNext()

        if self.symbol.id != self.scanner.COLON:
            self.error("syntax", "Expected a ':' symbol.")

        self.setNext()

        if self.symbol.id != self.scanner.OPEN_SQUARE:
            self.error("syntax", "Expected a '[' symbol.")

        parsing_connections = True
        self.setNext()
        while parsing_connections:
            if self.symbol.id == self.scanner.CLOSE_SQUARE:
                #allow for no connections
                print("No connections present.")
                parsing_connections = False
                break
            else:
                parsing_connections = self.parse_connection()

        if self.symbol.id != self.scanner.CLOSE_SQUARE:
            self.error("syntax", "Expected a ']' symbol.")

        self.setNext()
        if self.symbol.id != self.scanner.SEMICOLON:
            self.error("syntax", "Expected a ';' symbol.")

    def parse_connection(self):
        """Parse a single connection."""
        print("Parsing a connection.")
        leftOutputId, leftPortId, leftSignalName = self.parse_signal()
    
        if self.symbol.id == self.scanner.COLON:
            self.setNext()
            rightOutputId, rightPortId, rightSignalName = self.parse_signal()

        else:
            self.error("syntax", f"Expected ':' separating connection ends.")

        if self.symbol.id != self.scanner.SEMICOLON:
            self.error("syntax", "Expected ';'.")

        if self.error_count == 0:
            print("No errors when parsing connection --> proceed to build.")
            error_type = self.network.make_connection(leftOutputId, leftPortId, rightOutputId, rightPortId)

            if error_type != self.network.NO_ERROR:
                if error_type == self.network.DEVICE_ABSENT:
                    self.error("semantic", "One device absent.")
                elif error_type == self.network.INPUT_CONNECTED:
                    self.error("semantic", f"Input {rightSignalName} is already connected.")
                elif error_type == self.network.INPUT_TO_INPUT:
                    self.error("semantic", f"Both ports are inputs.")
                elif error_type == self.network.PORT_ABSENT:
                    self.error("semantic", f"Right port id is invalid.")
                elif error_type == self.network.OUTPUT_TO_OUTPUT:
                    self.error("semantic", f"Both ports are outputs.")
            else:
                print(f"Successfully built connection from {leftSignalName} to {rightSignalName}.")

        self.setNext()

        if self.symbol.type == self.scanner.NAME:
            keep_parsing = True

        elif self.symbol.id == self.scanner.CLOSE_SQUARE:
            keep_parsing = False
        
        else:
            self.error("syntax", "something")

        return keep_parsing

    def parse_signal(self):
        """Parse a signal name."""
        signalName = ""

        if self.symbol.type == self.scanner.NAME:
            signalName += self.names.get_name_string(self.symbol.id)
            outputId = self.symbol.id
            self.setNext()

            if self.symbol.id == self.scanner.DOT:
                signalName += "."
                self.setNext()

                if self.symbol.type == self.scanner.NAME:
                    signalName += self.names.get_name_string(self.symbol.id)
                    portId = self.symbol.id
                    self.setNext()

                else:
                    self.error("semantic", f"Port {self.names.get_name_string(self.symbol.id)} is invalid.")

            elif self.symbol.id == self.scanner.COLON:
                portId = None

            elif self.symbol.id == self.scanner.SEMICOLON:
                portId = None

            else:
                self.error("syntax", f"Expected port id, ':' separating connection ends, or ';' for end of monitor.")

        else:
            self.error("semantic", f"Output name {self.names.get_name_string(self.symbol.id)} is invalid.")

        return outputId, portId, signalName

    def parse_monitor_list(self):
        """Parse list of monitors."""
        self.setNext()

        if self.symbol.id != self.scanner.COLON:
            self.error("syntax", "Expected a ':' symbol.")

        self.setNext()

        if self.symbol.id != self.scanner.OPEN_SQUARE:
            self.error("syntax", "Expected a '[' symbol.")

        parsing_monitors = True
        self.setNext()

        while parsing_monitors:
            if self.symbol.id == self.scanner.CLOSE_SQUARE:
                #allow for no monitors
                print("No monitors present.")
                parsing_monitors = False
                break
            else:
                parsing_monitors = self.parse_monitor()

        if self.symbol.id != self.scanner.CLOSE_SQUARE:
            self.error("syntax", "Expected a ']' symbol.")

        self.setNext()
        if self.symbol.id != self.scanner.SEMICOLON:
            self.error("syntax", "Expected a ';' symbol.")

    def parse_monitor(self):
        """Parse a single monitor."""
        print("Parsing a monitor.")
        deviceId, portId, signalName = self.parse_signal()
    
        if self.symbol.id != self.scanner.SEMICOLON:
            self.error("syntax", "Expected ';'.")

        if self.error_count == 0:
            print("No errors when parsing monitor --> proceed to build.")
            error_type = self.monitors.make_monitor(deviceId, portId)

            if error_type != self.monitors.NO_ERROR:
                if error_type == self.monitors.DEVICE_ABSENT:
                    self.error("semantic", "Device you are trying to monitor is absent.")
                elif error_type == self.monitors.NOT_OUTPUT:
                    self.error("semantic", f"{signalName} is not an output.")
                elif error_type == self.monitors.MONITOR_PRESENT:
                    self.error("semantic", f"Already monitoring {signalName}.")
            else:
                print(f"Successfully built monitor {signalName}.")

        self.setNext()

        if self.symbol.type == self.scanner.NAME:
            keep_parsing = True

        elif self.symbol.id == self.scanner.CLOSE_SQUARE:
            keep_parsing = False
        
        else:
            self.error("syntax", "something")

        return keep_parsing

    def setNext(self):
        """Shift current symbol to next."""
        self.symbol = self.scanner.get_symbol()

    def strSymbol(self):
        """For use in testing to more easily print symbol string."""
        return self.names.get_name_string(self.symbol.id)

    def error(self, msg, expect_next_list):
        end_of_file = False
        recovered = False
        print(f"ERROR at index TBD!!: " + msg +
              f", received {self.strSymbol()}")
        self.error_count += 1

        while True:
            while self.symbol.id != self.scanner.SEMICOLON:
                self.setNext()
            # found a semi colon, now need to check if the expected element
            # is next
            try:
                self.setNext()
            except IndexError:
                print("reached end of file!")
                end_of_file = True
                break

            if self.symbol.id in expect_next_list:
                # found the character we want to keep parsing, therefore we
                # resume in the parsing
                break


    def semantic_error(self, msg):
        print("SEMANTIC ERROR: "+ msg)
        # no error recovery stuff here? :0
