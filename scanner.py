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
        self.pos = 0


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
        self.linestart = 0
        self.names = names
        self.symbol_types = [self.PUNCTUATION, self.KEYWORD,
            self.NUMBER, self.NAME, self.EOF, self.INVALID_CHAR] = range(6)

        self.keywords = ["CIRCUIT", "DEVICES", "CONNECTIONS", "MONITORS",
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
        if self.current_char == "\n":
            self.linestart = self.f.tell() + 1
        self.current_char = self.f.read(1)
        return self.current_char

    def _next_non_ws(self):
        """Read the next non-whitespace character in the definition file."""
        while self._next().isspace():
            pass  # keep looping
        return self.current_char

    def _next_name(self, symb):
        """Read the file as necessary to return the next name string.

        Assumes current_char at time of function call is alphabetic
        """
        name = ""
        symb.pos = self.f.tell()
        while self.current_char.isalnum():
            name += self.current_char
            self._next()
        return name

    def _next_number(self, symb):
        """Read the file as necessary to return the next number as an int.

        Assumes current_char at time of function call is numeric
        """
        n = ""
        symb.pos = self.f.tell()
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
                self._next()
            if not end:
                self._next()

        elif self.current_char == "/":
            self._next()
            while self.current_char != "\n":
                if self.current_char == "":
                    end = True
                    break
                self._next()
            if not end:
                self._next()
        
        if self.current_char.isspace():
            self._next_non_ws()

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        sym = Symbol()

        if self.current_char.isspace():
            self._next_non_ws()

        # comment
        if self.current_char in ["#", "/"]:
            self._skip_comment()

        # name/keyword
        if self.current_char.isalpha():
            name_string = self._next_name(sym)
            if name_string in self.keywords:
                sym.type = self.KEYWORD
            else:
                sym.type = self.NAME
            [sym.id] = self.names.lookup([name_string])

        # number
        elif self.current_char.isdigit():
            sym.type = self.NUMBER
            sym.id = self._next_number(sym)

        # punctuation
        elif self.current_char in self.puncs:
            sym.pos = self.f.tell()
            sym.type = self.PUNCTUATION
            sym.id = self.names.query(self.current_char)
            self._next()

        # end of file
        elif self.current_char == "":
            sym.pos = self.f.tell()
            sym.type = self.EOF

        # invalid character
        else:
            sym.type = self.INVALID_CHAR
            self._next()

        return sym

    def _get_error_line(self):
        """Return erroneous line as a string."""
        line = ""
        while self.current_char not in ["\n", ""]:
            line += self.current_char
            self._next()
        return line

    def show_error(self, symbol):
        """Print current input line with carat pointing to error location."""
        file_pos = self.f.tell()
        error_pos = symbol.pos
        linestart = self.linestart

        self.f.seek(linestart)
        errorline = self._get_error_line()
        caratline = " "*(error_pos - linestart) + "^"
        message = errorline + "\n" + caratline

        # return file object pointers to prior settings
        self.linestart = linestart
        self.f.seek(file_pos)

        return message
