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

        self.symbol = self.scanner.get_symbol()

        #print(type(self.symbol), self.names.get_name_string(self.symbol.id))

        if self.symbol.type == self.scanner.KEYWORD: #is this not redundant?
            # maybe for error reporting we can be specific and say a keyword
            # is missing...?
            if self.symbol.id == self.scanner.DEVICES_ID:
                # device_list has been found
                self.parse_device_list()
                devices_done = True
            # etc etc for other 'lists'


        #TODO: deal with connections coming before devices...


        return True


    def parse_device_list(self):
        # look for colon
        self.symbol = self.scanner.get_symbol()

        # this assumes that get_symbol will remove whitespace

        if self.symbol.id != self.scanner.COLON:
            self.error("syntax", "Expected a ':' symbol")

        self.symbol = self.scanner.get_symbol()

        if self.symbol.id != self.scanner.OPEN_SQUARE:
            self.error("syntax", "Expected a '[' symbol")

        parsing_devices = True
        first_device = True
        while parsing_devices:
            parsing_devices, first_device = self.parse_device(first_device)

        #self.symbol = self.scanner.get_symbol()
        if self.symbol.id != self.scanner.CLOSE_SQUARE:
            self.error("syntax", "Expected a ']' symbol")

        self.symbol = self.scanner.get_symbol()
        if self.symbol.id != self.scanner.SEMICOLON:
            self.error("syntax", "Expected a ';' symbol")

    def parse_device(self, first_device):
        print("parsing a device")
        if first_device:
            self.symbol = self.scanner.get_symbol()

        if self.symbol.id != self.scanner.OPEN_CURLY:
            self.error("syntax", "Expected a '{' symbol")

        self.symbol = self.scanner.get_symbol()
        if self.symbol.id == self.scanner.ID_KEYWORD_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.id == self.scanner.COLON:
                # TODO: check this statement
                # should it be "u provided a punctuation mark instead of a valid name"
                # or maybe just "name *%^&*% is invalid"
                self.symbol = self.scanner.get_symbol()
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

        self.symbol = self.scanner.get_symbol()
        if self.symbol.id != self.scanner.SEMICOLON:
            self.error("syntax", "Expected ';'")

        self.symbol = self.scanner.get_symbol()
        if self.symbol.id == self.scanner.KIND_KEYWORD_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.id == self.scanner.COLON:
                self.symbol = self.scanner.get_symbol()
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

        self.symbol = self.scanner.get_symbol()
        if self.symbol.id != self.scanner.SEMICOLON:
            self.error("syntax", "Expected ';'")

        if device_kind_id in self.expect_qualifier:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.id == self.scanner.QUAL_KEYWORD_ID:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.id == self.scanner.COLON:
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type == self.scanner.NUMBER:
                        #print("valid qualifier")
                        device_qualifier = self.symbol.id
                    else:
                        self.error("semantic", "Unsupported qualifier input")
                else:
                    self.error("syntax", "Expected ':' delimiter")
            else:
                self.error("syntax", "Expected 'qual'")

            self.symbol = self.scanner.get_symbol()
            if self.symbol.id != self.scanner.SEMICOLON:
                self.error("syntax", "Expected ';'")
        else:
            device_qualifier = None


        # TODO: need to clarify the error recovery stuff.... not sure this
        #  code will work anymore :/

        self.symbol = self.scanner.get_symbol()
        if self.symbol.id != self.scanner.CLOSE_CURLY:
            self.error("syntax", "Expected a '}' symbol")

        self.symbol = self.scanner.get_symbol()
        if self.symbol.id != self.scanner.SEMICOLON:
            self.error("syntax", "Expected ';'")

        if self.error_count == 0:
            print("no errors when parsing device --> proceed to build")
            error_type = self.devices.make_device(device_name,
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

        self.symbol = self.scanner.get_symbol()
        if self.symbol.id == self.scanner.OPEN_CURLY:
            keep_parsing = True
        elif self.symbol.id == self.scanner.CLOSE_SQUARE:
            keep_parsing = False
        else:
            self.error("syntax", "something")

        first_device = False
        return keep_parsing, first_device



    def error(self, error_type, message):
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