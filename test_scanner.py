"""Test the scanner module."""
import pytest

from names import Names
from scanner import Scanner

def new_scanner(path):
    """Return a Scanner class instance for given path."""
    new_names = Names()
    new_scanner = Scanner(path, new_names)
    return new_scanner