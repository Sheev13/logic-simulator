"""Create mock data for testing the GUI."""

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


def getMockData():
    names = Names()
    devices = Devices(names)

    names.lookup(["SW1", "SW2", "SW3", "F1", "CLK1"])
    devices.make_device(names.query("SW1"), devices.device_types[1], 0)
    devices.make_device(names.query("SW2"), devices.device_types[1], 1)
    devices.make_device(names.query("SW3"), devices.device_types[1], 0)
    devices.make_device(names.query("F1"), devices.device_types[2])
    devices.make_device(names.query("CLK1"), devices.device_types[0], 4)

    network = Network(names, devices)

    network.make_connection(names.query("SW1"),names.query(None), names.query("F1"), names.query("SET"))
    network.make_connection(names.query("SW2"),names.query(None), names.query("F1"), names.query("DATA"))
    network.make_connection(names.query("CLK1"),names.query(None), names.query("F1"), names.query("CLK"))
    network.make_connection(names.query("SW3"),names.query(None), names.query("F1"), names.query("CLEAR"))

    return names, devices, network
