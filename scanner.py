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
        self.pos = None
        self.line = None
        self.linestart = None


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
        self.linestart = 1
        self.prev_linestart = 1
        self.linecount = 1
        self.names = names

        self.current_char = " "  # start as a whitespace to avoid EOF

        self.symbol_types = [
            self.PUNCTUATION,
            self.KEYWORD,
            self.NUMBER,
            self.NAME,
            self.EOF,
            self.INVALID_CHAR,
            self.UNCLOSED
        ] = range(7)

        self.keywords = [
            "CIRCUIT",
            "DEVICES",
            "CONNECTIONS",
            "MONITORS",
            "id",
            "kind",
            "qual",
        ]
        [
            self.CIRCUIT_ID,
            self.DEVICES_ID,
            self.CONNECTIONS_ID,
            self.MONITOR_ID,
            self.ID_KEYWORD_ID,
            self.KIND_KEYWORD_ID,
            self.QUAL_KEYWORD_ID,
        ] = self.names.lookup(self.keywords)

        self.puncs = [":", "[", "]", "{", "}", ";", ",", "."]
        [
            self.COLON,
            self.OPEN_SQUARE,
            self.CLOSE_SQUARE,
            self.OPEN_CURLY,
            self.CLOSE_CURLY,
            self.SEMICOLON,
            self.COMMA,
            self.DOT,
        ] = self.names.lookup(self.puncs)

    def _open_file(self, path):
        """Open and return the file specified by path."""
        directory = pathlib.Path().resolve()

        try:
            return open(path, "rb")  # use binary mode due to unix line endings
        except FileNotFoundError:
            print(
                "File '",
                path,
                "' either does not exist or is not in '",
                directory,
                "'",
                sep="",
            )
            sys.exit()

    def _next(self):
        """Read the next character in the definition file."""
        if self.current_char == "\n":
            self.prev_linestart = self.linestart
            self.linestart = self.f.tell() + 1
            self.linecount += 1
        self.current_char = self.f.read(1).decode("UTF-8")
        return self.current_char

    def _next_non_ws(self):
        """Read the next non-whitespace character in the definition file."""
        while self._next().isspace():
            pass  # keep looping
        return self.current_char

    def _invalid_current(self):
        """Return True if current character is invalid."""
        char = self.current_char
        if not char.isspace() and not char.isalnum():
            if char != "" and char not in self.puncs:
                return True
        return False

    def _next_name(self, symb):
        """Read the file as necessary to return the next name string.

        Assumes current_char at time of function call is alphabetic
        """
        name = ""
        inv = False
        symb.pos = self.f.tell()
        symb.line = self.linecount
        symb.linestart = self.linestart
        while self.current_char.isalnum() or self._invalid_current():
            if self._invalid_current():
                inv = True
            name += self.current_char
            self._next()
        return name, inv

    def _next_number(self, symb):
        """Read the file as necessary to return the next number as an int.

        Assumes current_char at time of function call is numeric
        """
        n = ""
        inv = False
        symb.pos = self.f.tell()
        symb.line = self.linecount
        symb.linestart = self.linestart
        while self.current_char.isdigit() or self._invalid_current():
            if self._invalid_current():
                inv = True
                return None, inv
            n += self.current_char
            self._next()
        return int(n), inv

    def _skip_comment(self):
        """Advance the file object reader pointer to after the current comment.

        Assumes current character is either # or /.
        Open comments denoted by / , closed comments by #...#
        Return True and comment start pos if closed comment has not been closed.
        """
        end = False

        if self.current_char == "#":
            start = self.f.tell()
            line = self.linecount
            linestart = self.linestart
            self._next()
            while self.current_char != "#":
                if self.current_char == "":
                    end = True
                    return True, start, line, linestart
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

        return False, None, None, None

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        sym = Symbol()
        uc_comment = False

        if self.current_char.isspace():
            self._next_non_ws()

        # comment
        while self.current_char in ["#", "/"]:
            uc_comment, uc_start, uc_line, uc_ls = self._skip_comment()

        #  unclosed comment
        if uc_comment:
            sym.pos = uc_start
            sym.line = uc_line
            sym.type = self.UNCLOSED
            sym.linestart = uc_ls

        # name/keyword
        elif self.current_char.isalpha():
            name_string, inv = self._next_name(sym)
            if inv:
                sym.type = self.INVALID_CHAR
            elif name_string in self.keywords:
                sym.type = self.KEYWORD
                [sym.id] = self.names.lookup([name_string])
            else:
                sym.type = self.NAME
                [sym.id] = self.names.lookup([name_string])

        # number
        elif self.current_char.isdigit():
            sym.id, inv = self._next_number(sym)
            if inv:
                sym.type = self.INVALID_CHAR
            else:
                sym.type = self.NUMBER

        # punctuation
        elif self.current_char in self.puncs:
            sym.pos = self.f.tell()
            sym.line = self.linecount
            sym.linestart = self.linestart
            sym.type = self.PUNCTUATION
            sym.id = self.names.query(self.current_char)
            self._next()

        # end of file
        elif self.current_char == "":
            sym.pos = self.f.tell()
            sym.line = self.linecount
            sym.linestart = self.linestart
            sym.type = self.EOF

        # invalid character
        else:
            sym.type = self.INVALID_CHAR
            sym.pos = self.f.tell()
            sym.line = self.linecount
            sym.linestart = self.linestart
            self._next()

        return sym

    def _get_error_line(self):
        """Return erroneous line as a string."""
        line = ""
        self._next()
        while self.current_char not in ["\n", ""]:
            line += self.current_char
            self._next()
        return line

    def show_error(self, symbol):
        """Print current input line with caret pointing to error location."""
        char = self.current_char
        file_pos = self.f.tell()
        linecount = self.linecount
        file_linestart = self.linestart

        error_pos = symbol.pos
        error_line_num = symbol.line
        error_linestart = symbol.linestart
        prev_linestart = self.prev_linestart
        col = 0

        if error_pos == error_linestart:  # "if symbol is at start of line"
            # "if there is a previous line and symbol is not unclosed comment"
            if error_linestart != 1 and symbol.type != self.UNCLOSED:  
                self.f.seek(prev_linestart - 1)
                errorline1 = self._get_error_line()

                caretline = " " * len(errorline1) + "^"
                self.f.seek(error_linestart - 1)
                errorline2 = self._get_error_line()
                message = errorline1 + "\n" + caretline + "\n" + errorline2 + "\n"
                error_line_num -= 1
                col = len(errorline1)
            else:  # "if no previous line or symbol is unclosed comment"
                self.f.seek(error_linestart - 1)
                errorline = self._get_error_line()
                caretline = "^"
                message = errorline + "\n" + caretline
                col = error_pos - error_linestart
        else:
            self.f.seek(error_linestart - 1)
            errorline = self._get_error_line()
            caretline = " " * (error_pos - error_linestart) + "^"
            message = errorline + "\n" + caretline
            col = error_pos - error_linestart

        # return file object pointers to prior settings
        self.linestart = file_linestart
        self.prev_linestart = prev_linestart
        self.linecount = linecount
        self.f.seek(file_pos)
        self.current_char = char

        return message, error_line_num, col
