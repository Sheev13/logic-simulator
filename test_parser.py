"""Test the parser module."""
from this import d
import pytest

from names import Names
from network import Network
from devices import Devices
from monitors import Monitors
from parse import Parser
from scanner import Scanner


def new_parser(path):
    """Return a Parser class instance for given path."""
    new_names = Names()
    new_devices = Devices(new_names)
    new_network = Network(new_names, new_devices)
    new_monitors = Monitors(new_names, new_devices, new_network)
    new_scanner = Scanner(path, new_names)
    new_parser = Parser(
        new_names,
        new_devices,
        new_network,
        new_monitors,
        new_scanner
    )
    return new_parser


@pytest.fixture
def new_parser_good_devices():
    """Return a Parser class instance for good devices."""
    path = "test_files/devices.txt"
    return new_parser(path)


@pytest.fixture
def new_parser_bad_devices():
    """Return a Parser class instance for bad devices."""
    path = "test_files/broken_devices.txt"
    return new_parser(path)


@pytest.fixture
def new_parser_good_devices_and_connections():
    """Return a Parser class instance for good devices and connections."""
    path = "test_files/devices_and_connections.txt"
    return new_parser(path)


@pytest.fixture
def new_parser_bad_devices_and_connections():
    """Return a Parser class instance for bad devices and connections."""
    path = "test_files/broken_devices_and_connections.txt"
    return new_parser(path)


@pytest.fixture
def new_parser_good_devices_and_monitors():
    """Return a Parser class instance for good devices and monitors."""
    path = "test_files/devices_and_monitors.txt"
    return new_parser(path)


@pytest.fixture
def new_parser_bad_devices_and_monitors():
    """Return a Parser class instance for bad devices and monitors."""
    path = "test_files/broken_devices_and_monitors.txt"
    return new_parser(path)


@pytest.fixture
def new_parser_devices_connections_monitors():
    """Return a Parser class instance for correct file of devices,
        connections and monitors in that order."""
    path = "test_files/devices_connections_monitors.txt"
    return new_parser(path)


@pytest.fixture
def new_parser_devices_monitors_connections():
    """Return a Parser class instance for correct file of devices,
        monitors and connections in that order."""
    path = "test_files/devices_monitors_connections.txt"
    return new_parser(path)


@pytest.fixture
def new_parser_all_three_bad_devices():
    """Return a Parser class instance for all three present, bad devices."""
    path = "test_files/all_three_bad_devices.txt"
    return new_parser(path)


@pytest.fixture
def new_parser_all_three_bad_connections():
    """Return a Parser class instance for devices,
            connections and monitors present, bad connections."""
    path = "test_files/all_three_bad_connections.txt"
    return new_parser(path)


@pytest.fixture
def new_parser_all_three_bad_monitors():
    """Return a Parser class instance for all three present, bad monitors."""
    path = "test_files/all_three_bad_monitors.txt"
    return new_parser(path)


@pytest.fixture
def new_parser_comments():
    """Return a Parser class instance for comments in text file."""
    path = "test_files/comments.txt"
    return new_parser(path)


def test_parse_network_no_errors(
    new_parser_good_devices,
    new_parser_good_devices_and_connections,
    new_parser_good_devices_and_monitors,
    new_parser_devices_connections_monitors,
    new_parser_devices_monitors_connections
):
    """Test parse network works when no errors present in any simple files."""
    assert new_parser_good_devices.parse_network()
    assert new_parser_good_devices_and_connections.parse_network()
    assert new_parser_good_devices_and_monitors.parse_network()
    assert new_parser_devices_connections_monitors.parse_network()
    assert new_parser_devices_monitors_connections.parse_network()


def test_parse_network_with_errors(
    new_parser_bad_devices,
    new_parser_bad_devices_and_connections,
    new_parser_bad_devices_and_monitors,
    new_parser_all_three_bad_devices,
    new_parser_all_three_bad_connections,
    new_parser_all_three_bad_monitors
):
    """Test if parse network returns False when errors present in files."""
    assert not new_parser_bad_devices.parse_network()
    assert not new_parser_bad_devices_and_connections.parse_network()
    assert not new_parser_bad_devices_and_monitors.parse_network()
    assert not new_parser_all_three_bad_devices.parse_network()
    assert not new_parser_all_three_bad_connections.parse_network()
    assert not new_parser_all_three_bad_monitors.parse_network()


def test_parse_network_comments(new_parser_comments):
    """Test parse network works when no comments present in a simple file."""
    assert new_parser_comments.parse_network()
