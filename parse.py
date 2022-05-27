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
        # given by scanner
        # symbol object which has properties:
        # type (eg. keyword), id (names table thing)
        # symbol line number, symbol position
        # also string representation of the symbol?
        # symbol.as_string ? something like

        self.expect_qualifier = [self.devices.AND, self.devices.NAND,
                                 self.devices.OR, self.devices.NOR,
                                 self.devices.CLOCK, self.devices.SWITCH]
        # if the symb.type is one of these, we need qualifier...

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        devices_done = False
        connections_done = False
        monitors_done = False
        self.setNext()

        #print(type(self.symbol), self.names.get_name_string(self.symbol.id))

        if self.symbol.type == self.scanner.KEYWORD: #is this not redundant?
            # maybe for error reporting we can be specific and say a keyword
            # is missing...?
            if self.symbol.id == self.scanner.DEVICES_ID:
                # device_list has been found
                self.parse_device_list()
                devices_done = True
            else:
                self.error("syntax", "no devices found")
        else:
            self.error("syntax", "no DEVICES keyword found")

        self.setNext()

        if self.symbol.type == self.scanner.KEYWORD:
            if self.symbol.id == self.scanner.CONNECTIONS_ID:
                if not devices_done:
                    self.error("syntax", "No devices found before connections")
                self.parse_connections_list()  # TODO: PRIYANKA PLS <3
                connections_done = True

        if connections_done:
            self.setNext()

        if self.symbol.id == self.scanner.MONITOR_ID:
            if not devices_done:
                self.error("syntax", "no devices found, impossible to "
                                     "monitor anything")
                # I dont think we will ever get here...?
                # note that don't have to have connections to monitor since
                # devices automatically create outputs i believe

            self.parse_monitor_list()  #TODO
            monitors_done = True

        if monitors_done:
            self.setNext()

        if self.symbol.type == self.scanner.EOF:
            # TODO close file routine?
            pass

        print("Succesfully parsed entire definition file!")

        return True


    def parse_device_list(self):
        """Parse list of devices."""
        self.setNext()

        if self.symbol.id != self.scanner.COLON:
            self.error("syntax", "Expected a ':' symbol")

        self.setNext()

        if self.symbol.id != self.scanner.OPEN_SQUARE:
            self.error("syntax", "Expected a '[' symbol")

        parsing_devices = True
        first_device = True
        while parsing_devices:
            parsing_devices, first_device = self.parse_device(first_device)

        if self.symbol.id != self.scanner.CLOSE_SQUARE:
            self.error("syntax", "Expected a ']' symbol")

        self.setNext()
        if self.symbol.id != self.scanner.SEMICOLON:
            self.error("syntax", "Expected a ';' symbol")

    def parse_device(self, first_device):
        """Parse a single device."""
        print("parsing a device")
        if first_device:
            self.setNext()

        if self.symbol.id != self.scanner.OPEN_CURLY:
            self.error("syntax", "Expected a '{' symbol")

        self.setNext()
        if self.symbol.id == self.scanner.ID_KEYWORD_ID:
            self.setNext()
            if self.symbol.id == self.scanner.COLON:
                # TODO: check this statement
                # should it be "u provided a punctuation mark instead of a valid name"
                # or maybe just "name *%^&*% is invalid"
                self.setNext()
                if self.symbol.type == self.scanner.NAME:
                    print("valid name for a device")
                    # make note of the device name for the build later (if no errors)
                    device_name = self.names.get_name_string(self.symbol.id)
                    #is this device id?? i think so? :/ the userdefined one
                else:
                    self.error("semantic",
                               "device name provided is invalid/eg. not "
                               "alnum")
            else:
                self.error("syntax", "Expected ':' delimiter")
        else:
            self.error("syntax", "Expected 'id'")

        self.setNext()
        if self.symbol.id != self.scanner.SEMICOLON:
            self.error("syntax", "Expected ';'")

        self.setNext()
        if self.symbol.id == self.scanner.KIND_KEYWORD_ID:
            self.setNext()
            if self.symbol.id == self.scanner.COLON:
                self.setNext()
                if self.symbol.type == self.scanner.NAME:
                    # this only tells us its alphanum aka TODO still syntax?
                    device_kind_string = self.names.get_name_string(
                        self.symbol.id)
                    [device_kind_id] = self.devices.names.lookup(
                        [device_kind_string])

                else:
                    self.error("semantic", "Device type not supported")
            else:
                self.error("syntax", "Expected ':' delimiter")
        else:
            self.error("syntax", "Expected 'kind'")

        self.setNext()
        if self.symbol.id != self.scanner.SEMICOLON:
            self.error("syntax", "Expected ';'")

        if device_kind_id in self.expect_qualifier:
            self.setNext()
            if self.symbol.id == self.scanner.QUAL_KEYWORD_ID:
                self.setNext()
                if self.symbol.id == self.scanner.COLON:
                    self.setNext()
                    if self.symbol.type == self.scanner.NUMBER:
                        #print("valid qualifier")
                        device_qualifier = self.symbol.id
                    else:
                        self.error("semantic", "Unsupported qualifier input")
                else:
                    self.error("syntax", "Expected ':' delimiter")
            else:
                self.error("syntax", "Expected 'qual'")

            self.setNext()
            if self.symbol.id != self.scanner.SEMICOLON:
                self.error("syntax", "Expected ';'")
        else:
            device_qualifier = None


        # TODO: need to clarify the error recovery stuff.... not sure this
        #  code will work anymore :/

        self.setNext()
        if self.symbol.id != self.scanner.CLOSE_CURLY:
            self.error("syntax", "Expected a '}' symbol")

        self.setNext()
        if self.symbol.id != self.scanner.SEMICOLON:
            self.error("syntax", "Expected ';'")

        if self.error_count == 0:
            print("no errors when parsing device --> proceed to build")
            error_type = self.devices.make_device(self.names.query(device_name),
                                                  device_kind_id,
                                                  device_qualifier)
            if error_type != self.devices.NO_ERROR:
                self.error("semantic", "something :///// will we ever get "
                                       "here?")
            else:
                print(f"successfully built a device {device_name}-"
                      f"{device_kind_id}-{device_qualifier}")

        #TODO: figure out how to detect errors after the end of parsing...?
        # is it just when u go back to main function? probs

        self.setNext()
        if self.symbol.id == self.scanner.OPEN_CURLY:
            keep_parsing = True
        elif self.symbol.id == self.scanner.CLOSE_SQUARE:
            keep_parsing = False
        else:
            self.error("syntax", "something")

        first_device = False
        return keep_parsing, first_device

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
                if error_type == self.network.INPUT_CONNECTED:
                    self.error("semantic", f"Input {rightSignalName} is already connected.")
                if error_type == self.network.INPUT_TO_INPUT:
                    self.error("semantic", f"Both ports are inputs.")
                if error_type == self.network.PORT_ABSENT:
                    self.error("semantic", f"Right port id is invalid.")
                if error_type == self.network.OUTPUT_TO_OUTPUT:
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

            else:
                self.error("syntax", f"Expected port id or ':' separating connection ends.")

        else:
            self.error("semantic", f"Output name {self.names.get_name_string(self.symbol.id)} is invalid.")

        return outputId, portId, signalName
        
    
    def parse_monitor_list(self):
        """Parse list of monitors."""
        pass

    def setNext(self):
        """Shift current symbol to next."""
        self.symbol = self.scanner.get_symbol()

    def strSymbol(self):
        """For use in testing to more easily print symbol string."""
        return self.names.get_name_string(self.symbol.id)
    
    def error(self, error_type, message):
        """Handle errors."""
        # access to the offending symbol is via self.symbol
        # still a bit confused about error recovery / show all syntax errors
        # at once
        self.error_count += 1
        if error_type == "syntax":
            raise SyntaxError(message + f" received"
                                        f" {self.names.get_name_string(self.symbol.id)}")
        elif error_type == "semantic":
            raise ValueError(message + f" received "
                                      f"{self.names.get_name_string(self.symbol.id)}")