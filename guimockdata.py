"""Create mock data for testing the GUI."""

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


def getMockData():
    """Get mock data for testing the GUI."""
    names = Names()
    devices = Devices(names)

    names.lookup(["SW1", "SW2", "SW3", "F1", "CLK1"])

    dNames = devices.names
    devices.make_device(dNames.query("SW1"), devices.device_types[1], 0)
    devices.make_device(dNames.query("SW2"), devices.device_types[1], 1)
    devices.make_device(dNames.query("SW3"), devices.device_types[1], 0)
    devices.make_device(dNames.query("F1"), devices.device_types[2])
    devices.make_device(dNames.query("CLK1"), devices.device_types[0], 4)

    network = Network(dNames, devices)
    nNames = network.names
    network.make_connection(nNames.query("SW1"),nNames.query(None), nNames.query("F1"), nNames.query("SET"))
    network.make_connection(nNames.query("SW2"),nNames.query(None), nNames.query("F1"), nNames.query("DATA"))
    network.make_connection(nNames.query("CLK1"),nNames.query(None), nNames.query("F1"), nNames.query("CLK"))
    network.make_connection(nNames.query("SW3"),nNames.query(None), nNames.query("F1"), nNames.query("CLEAR"))

    monitors = Monitors(nNames, devices, network)
    mNames = monitors.names
    monitors.make_monitor(mNames.query("F1"), mNames.query("Q"))
    monitors.make_monitor(mNames.query("F1"), mNames.query("QBAR"))

    return monitors.names, monitors.devices, monitors.network, monitors
