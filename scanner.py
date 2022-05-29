"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""
import sys
import pathlib


class Symbol:
    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None
        self.line = None
        self.pos = None


class Scanner:
    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        self.f = self._open_file(path)
        self.names = names
        self.symbol_types = [self.PUNCTUATION, self.KEYWORD,
            self.NUMBER, self.NAME, self.EOF] = range(5)

        self.keywords = ["CIRCUIT", "DEVICES", "CONNECTIONS", "MONITOR",
                         "id", "kind", "qual"]
        [self.CIRCUIT_ID, self.DEVICES_ID, self.CONNECTIONS_ID,
         self.MONITOR_ID, self.ID_KEYWORD_ID, self.KIND_KEYWORD_ID,
         self.QUAL_KEYWORD_ID] = self.names.lookup(self.keywords)

        self.puncs = [":", "[", "]", "{", "}", ";", ",", "."]
        [self.COLON, self.OPEN_SQUARE, self.CLOSE_SQUARE, self.OPEN_CURLY,
            self.CLOSE_CURLY, self.SEMICOLON, self.COMMA,
            self.DOT] = self.names.lookup(self.puncs)

        self.current_char = " "  # start as a whitespace

    def _open_file(self, path):
        """Open and return the file specified by path."""
        directory = pathlib.Path().resolve()

        try:
            return open(path)
        except FileNotFoundError:
            print("File '", path, "' either does not exist or is not in '",
                directory, "'", sep='')
            sys.exit()

    def _next(self):
        """Read the next character in the definition file."""
        self.current_char = self.f.read(1)
        return self.current_char

    def _next_non_ws(self):
        """Read the next non-whitespace character in the definition file."""
        while self._next().isspace():
            pass  # keep looping
        return self.current_char

    def _next_name(self):
        """Read the file as necessary to return the next name string.

        Assumes current_char at time of function call is alphabetic
        """
        name = ""
        while self.current_char.isalnum():
            name += self.current_char
            self._next()
        return name

    def _next_number(self):
        """Read the file as necessary to return the next number as an int.

        Assumes current_char at time of function call is numeric
        """
        n = ""
        while self.current_char.isdigit():
            n += self.current_char
            self._next()
        return int(n)

    def _skip_comment(self):
        """Advance the file object reader pointer to after the current comment.

        Assumes current character is either # or /.
        Open comments denoted by / , closed comments by #...#
        """
        end = False

        if self.current_char == "#":
            self._next()
            while self.current_char != "#":
                if self.current_char == "":
                    end = True
                    break
                self.next()
            if not end:
                self.next()

        elif self.current_char == "/":
            self._next()
            while self.current_char != "\n":
                if self.current_char == "":
                    end = True
                    break
                self._next()
            if not end:
                self._next()

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        sym = Symbol()
        if self.current_char.isspace():
            self._next_non_ws()

        # name/keyword
        if self.current_char.isalpha():
            name_string = self._next_name()
            if name_string in self.keywords:
                sym.type = self.KEYWORD
            else:
                sym.type = self.NAME
            [sym.id] = self.names.lookup([name_string])

        # number
        elif self.current_char.isdigit():
            sym.type = self.NUMBER
            sym.id = self._next_number()

        # punctuation
        elif self.current_char in self.puncs:
            sym.type = self.PUNCTUATION
            sym.id = self.names.query(self.current_char)
            self._next()

        # comment
        elif self.current_char in ["#", "/"]:
            self._skip_comment()

        # end of file
        elif self.current_char == "":
            sym.type = self.EOF

        # newline character
        elif self.current_char == "\n":
            self._next()
            # TODO: i don't think we ever get here? new line = whitespace

        # invalid char
        else:
            self._next()
            # TODO
            # throw error? just move on?

        return sym

    def _get_error_line(self):
        """Return erroneous line as a string."""
        pass
        # TODO

    def show_error(self):
        """Print current input line with carat pointing to error location."""
        print("there is an error here I think")
        # TODO
