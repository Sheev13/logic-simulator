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
        self. monitors = monitors
        self.scanner = scanner

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

        if self.symbol.type == self.scanner.KEYWORD:
            if self.symbol.id == self.scanner.DEVICES:
                # device_list has been found
                self.parse_device_list()

            # etc etc for other 'lists'




        return True


    def parse_device_list(self):
        # look for colon
        self.symbol = self.scanner.get_symbol()

        # this assumes that get_symbol will remove whitespace

        if self.symbol.type != self.scanner.COLON:
            self.error("syntax", "Expected a ':' symbol")
            return False

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type != self.scanner.OPEN_SQUARE:
            self.error("syntax", "Expected a '[' symbol")
            return False

        parsing_devices = True
        while parsing_devices:
            parsing_devices = self.parse_device()

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type != self.scanner.CLOSE_SQAURE:
            self.error("syntax", "Expected a ']' symbol")
            return False

        self.symbol.type = self.scanner.get_symbol()
        if self.symbol != self.scanner.SEMICOLON:
            self.error("syntax", "Expected a ';' symbol")
            return False

        return True

    def parse_device(self):
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.OPEN_CURLY:
            self.error("syntax", "Expected a '{' symbol")
            return False  # not sure about these anymore

        self.symbol = self.scanner.get_symbol()
        self.device()
        # TODO: need to change EBNF so we can do this
        # TODO: change from semicolon to comma? or not necessary
        while self.symbol.type == self.scanner.SEMICOLON:
            self.symbol = self.scanner.get_symbol()  # write helper function
            self.device()

        if self.symbol.type == self.scanner.CLOSE_CURLY:
            self.symbol = self.scanner.get_symbol()
        else:
            self.error("syntax", "Expected a '}' symbol")

        if self.symbol.type == self.scanner.SEMICOLON:
            self.symbol = self.scanner.get_symbol()
        else:
            self.error("syntax", "Expected a ';' symbol")

    def device(self):
        # find 'id' --> then find : and name() and ;
        # find kind --> then find : and name() and ;
        # find qual --> then find : and int() and ;

        # maybe the curly braces go in here?
        pass






    def error(self, error_type, message):
        # access to the offending symbol is via self.symbol
        # still a bit confused about error recovery / show all syntax errors
        # at once
        pass