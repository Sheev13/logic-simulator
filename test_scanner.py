"""Test the scanner module."""
import pytest

from names import Names
from scanner import Scanner

def new_scanner(path):
    """Return a Scanner class instance for given path."""
    new_names = Names()
    new_scanner = Scanner(path, new_names)
    return new_scanner

@pytest.fixture
def empty_scanner():
    """Return a Scanner object for an empty file"""
    path = "test_files/scanner_test_files/empty_file.txt"
    return new_scanner(path)

@pytest.fixture
def whitespace_scanner():
    """Return a Scanner object for file with lots of whitespace"""
    path = "test_files/scanner_test_files/whitespacey.txt"
    return new_scanner(path)

@pytest.fixture
def comment_scanner():
    """Return a Scanner object for file with only comments"""
    path = "test_files/scanner_test_files/comment.txt"
    return new_scanner(path)