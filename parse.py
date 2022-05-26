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



    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.

        self.symbol = self.scanner.get_symbol()

        print(type(self.symbol), self.names.get_name_string(self.symbol.id))

        if self.symbol.type == self.scanner.KEYWORD:
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

        if self.symbol.type != self.scanner.OPEN_SQUARE:
            self.error("syntax", "Expected a '[' symbol")

        parsing_devices = True
        while parsing_devices:
            parsing_devices = self.parse_device()

        #self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.CLOSE_SQAURE:
            self.error("syntax", "Expected a ']' symbol")

        self.symbol.type = self.scanner.get_symbol()
        if self.symbol != self.scanner.SEMICOLON:
            self.error("syntax", "Expected a ';' symbol")

    def parse_device(self):
        print("parsing a device")

        self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.OPEN_CURLY:
            self.error("syntax", "Expected a '{' symbol")

        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.ID_KEYWORD:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.COLON:
                # TODO: check this statement
                # should it be "u provided a punctuation mark instead of a valid name"
                # or maybe just "name *%^&*% is invalid"
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.NAME:
                    print("valid id for a device")
                    # make note of the device name for the build later (if no errors)
                    # dev_id = self.symbol.as_string  # maybe this is just
                    # lookup/query... sort out later
                else:
                    self.error("semantic",
                               "device name provided is invalid/eg. not "
                               "alnum")
            else:
                self.error("syntax", "Expected ':' delimiter")
        else:
            self.error("syntax", "Expected 'id'")

        self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.SEMICOLON:
            self.error("syntax", "Expected ';'")

        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.KIND_KEYWORD:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.COLON:
                self.symbol = self.scanner.get_symbol()
                # TODO: this might be instead: is symbol.as_string in
                #  allowed_devices_list?
                if self.symbol.type == self.scanner.DEV_KIND:
                    print("valid type of device")
                    # dev_kind
                else:
                    self.error("semantic", "Device type not supported")
            else:
                self.error("syntax", "Expected ':' delimiter")
        else:
            self.error("syntax", "Expected 'kind'")

        self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.SEMICOLON:
            self.error("syntax", "Expected ';'")

        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.QUAL_KEYWORD:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.COLON:
                self.symbol = self.scanner.get_symbol()
                # TODO: this might be instead: is symbol.as_string a valid qual?
                if self.symbol.type == self.scanner.DEV_QUAL:
                    print("valid qualifier")
                    # store for making device later
                    # qual = self.symbol
                else:
                    self.error("semantic", "Unsupported qualifier input")
            else:
                self.error("syntax", "Expected ':' delimiter")
        else:
            self.error("syntax", "Expected 'qual'")

        self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.SEMICOLON:
            self.error("syntax", "Expected ';'")

        # TODO: need to clarify the error recovery stuff.... not sure this
        #  code will work anymore :/

        self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.CLOSE_CURLY:
            self.error("syntax", "Expected a '}' symbol")

        self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.SEMICOLON:
            self.error("syntax", "Expected ';'")

        if self.error_count == 0:
            print("no errors when parsing device --> proceed to build")

        #TODO: figure out how to detect errors after the end of parsing...?
        # is it just when u go back to main function? probs

        self.symbol = self.scanner.get_symbol()
        if self.symbol == self.scanner.OPEN_CURLY:
            keep_parsing = True
        elif self.symbol == self.scanner.CLOSE_SQAURE:
            keep_parsing = False
        else:
            self.error("syntax", "something")

        return keep_parsing



    def error(self, error_type, message):
        # access to the offending symbol is via self.symbol
        # still a bit confused about error recovery / show all syntax errors
        # at once
        self.error_count += 1
        if error_type == "syntax":
            raise SyntaxError(message + f"received {self.names.get_name_string(self.symbol.id)}") 