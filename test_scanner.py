"""Test the scanner module."""
import pytest

from names import Names
from scanner import Scanner

dir = "test_files/scanner_test_files/"


def new_scanner(path):
    """Return a Scanner class instance for given path."""
    new_names = Names()
    new_scanner = Scanner(path, new_names)
    return new_scanner


@pytest.fixture
def empty_scanner():
    """Return a Scanner object for an empty file"""
    path = dir + "empty_file.txt"
    return new_scanner(path)


@pytest.fixture
def whitespace_scanner():
    """Return a Scanner object for file with lots of whitespace"""
    path = dir + "whitespacey.txt"
    return new_scanner(path)


@pytest.fixture
def comment_scanner():
    """Return a Scanner object for file with only comments"""
    path = dir + "comment.txt"
    return new_scanner(path)


@pytest.fixture
def name_scanner():
    """Return a Scanner object for file containing valid name"""
    path = dir + "name.txt"
    return new_scanner(path)


@pytest.fixture
def keyword_scanner():
    """Return a Scanner object for file containing valid keyword"""
    path = dir + "keyword.txt"
    return new_scanner(path)


@pytest.fixture
def invalid_name_scanner():
    """Return a Scanner object for file containing invalid name"""
    path = dir + "invalid_name.txt"
    return new_scanner(path)


@pytest.fixture
def number_scanner():
    """Return a Scanner object for file containing valid number"""
    path = dir + "number.txt"
    return new_scanner(path)


@pytest.fixture
def invalid_number_scanner():
    """Return a Scanner object for file containing invalid number"""
    path = dir + "invalid_number.txt"
    return new_scanner(path)


@pytest.fixture
def punc_scanner():
    """Return a Scanner object for file containing punctuation"""
    path = dir + "punc.txt"
    return new_scanner(path)


@pytest.fixture
def invalid_char_scanner():
    """Return a Scanner object for file containing invalid char"""
    path = dir + "invalid_char.txt"
    return new_scanner(path)


@pytest.fixture
def midline_symbol_scanner():
    """Return a Scanner object for file containing a mid-line symbol"""
    path = dir + "midline.txt"
    return new_scanner(path)


@pytest.fixture
def linestart_symbol_scanner():
    """Return a Scanner object for file with symbol at start of line"""
    path = dir + "linestart.txt"
    return new_scanner(path)


def test__open_file():
    """Ensure that correct error raised in scenario of invalid path"""
    new_names = Names()
    with pytest.raises(FileNotFoundError):
        Scanner("invalid_path.txt", new_names)


def test_get_symbol(
    empty_scanner,
    whitespace_scanner,
    comment_scanner,
    name_scanner,
    keyword_scanner,
    invalid_name_scanner,
    number_scanner,
    invalid_number_scanner,
    punc_scanner,
    invalid_char_scanner,
):
    """Ensure scanner.get_symbol() behaves correctly on a range of scenarios"""
    symb1 = empty_scanner.get_symbol()
    symb2 = whitespace_scanner.get_symbol()
    symb3 = comment_scanner.get_symbol()
    symb4 = name_scanner.get_symbol()
    symb5 = keyword_scanner.get_symbol()
    symb6 = invalid_name_scanner.get_symbol()
    symb7 = number_scanner.get_symbol()
    symb8 = invalid_number_scanner.get_symbol()
    symb9 = punc_scanner.get_symbol()
    symb10 = invalid_char_scanner.get_symbol()

    assert symb1.type == Scanner.EOF
    assert symb1.id == None
    assert symb1.pos == 0
    assert symb1.line == 1

    assert symb2.type == Scanner.EOF
    assert symb2.id == None
    assert symb2.pos == 7
    assert symb2.line == 9

    assert symb3.type == Scanner.EOF
    assert symb3.id == None
    assert symb3.pos == 5
    assert symb3.line == 10

    assert symb4.type == Scanner.NAME
    assert symb4.pos == 0
    assert symb4.line == 1

    assert symb5.type == Scanner.KEYWORD
    assert symb5.pos == 0
    assert symb5.line == 1

    assert symb6.type == Scanner.INVALID_CHAR
    assert symb6.id == None
    assert symb6.pos == 0
    assert symb6.line == 1

    assert symb7.type == Scanner.NUMBER
    assert symb7.id == 69420
    assert symb7.pos == 0
    assert symb7.line == 1

    assert symb8.type == Scanner.INVALID_CHAR
    assert symb8.id == None
    assert symb8.pos == 0
    assert symb8.line == 1

    assert symb9.type == Scanner.PUNCTUATION
    assert symb9.pos == 0
    assert symb9.line == 1

    assert symb10.type == Scanner.INVALID_CHAR
    assert symb10.id == None
    assert symb10.pos == 0
    assert symb10.line == 1


def test_show_error(midline_symbol_scanner, linestart_symbol_scanner):
    """Ensure Scanner.show_error() behaves correctly on a range of scenarios"""
    symb1 = midline_symbol_scanner.get_symbol()
    assert midline_symbol_scanner.show_error(symb1) == (
        "# this is a comment # *DEVICES\n                      ^",
        2,
        22,
    )
    symb2 = linestart_symbol_scanner.get_symbol()
    assert linestart_symbol_scanner.show_error(symb2) == (
        "# this is a comment #\n                     ^",
        1,
        21,
    )
