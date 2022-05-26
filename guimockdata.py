"""Create mock data for testing the GUI."""

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


def getMockData1():
    """Get set 1 of mock data for testing the GUI - clock, switches and dtype."""
    names = Names()
    devices = Devices(names)

    names.lookup(["SW1", "SW2", "SW3", "F1", "CLKasdfasdfasdfasdfasdfasdfghjkl1"])

    dNames = devices.names
    devices.make_device(dNames.query("SW1"), devices.device_types[1], 0)
    devices.make_device(dNames.query("SW2"), devices.device_types[1], 1)
    devices.make_device(dNames.query("SW3"), devices.device_types[1], 0)
    devices.make_device(dNames.query("F1"), devices.device_types[2])
    devices.make_device(dNames.query("CLKasdfasdfasdfasdfasdfasdfghjkl1"), devices.device_types[0], 4)

    network = Network(dNames, devices)
    nNames = network.names
    network.make_connection(nNames.query("SW1"),nNames.query(None), nNames.query("F1"), nNames.query("SET"))
    network.make_connection(nNames.query("SW2"),nNames.query(None), nNames.query("F1"), nNames.query("DATA"))
    network.make_connection(nNames.query("CLKasdfghjkl1"),nNames.query(None), nNames.query("F1"), nNames.query("CLK"))
    network.make_connection(nNames.query("SW3"),nNames.query(None), nNames.query("F1"), nNames.query("CLEAR"))

    monitors = Monitors(nNames, devices, network)
    mNames = monitors.names
    monitors.make_monitor(mNames.query("F1"), mNames.query("Q"))
    monitors.make_monitor(mNames.query("F1"), mNames.query("QBAR"))

    return monitors.names, monitors.devices, monitors.network, monitors

def getMockData2():
    """Get set 2 of mock data for testing the GUI - switches and logic gates."""
    names = Names()
    devices = Devices(names)

    names.lookup(["A", "B", "C", "G1", "G2", "G3"])

    dNames = devices.names
    devices.make_device(dNames.query("A"), devices.device_types[1], 0)
    devices.make_device(dNames.query("B"), devices.device_types[1], 1)
    devices.make_device(dNames.query("C"), devices.device_types[1], 1)
    devices.make_device(dNames.query("G1"), devices.gate_types[3], 2)
    devices.make_device(dNames.query("G2"), devices.gate_types[0], 2)
    devices.make_device(dNames.query("G3"), devices.gate_types[1], 2)

    network = Network(dNames, devices)
    nNames = network.names
    network.make_connection(nNames.query("A"),nNames.query(None), nNames.query("G1"), nNames.query("I1"))
    network.make_connection(nNames.query("B"),nNames.query(None), nNames.query("G1"), nNames.query("I2"))
    network.make_connection(nNames.query("B"),nNames.query(None), nNames.query("G2"), nNames.query("I1"))
    network.make_connection(nNames.query("C"),nNames.query(None), nNames.query("G2"), nNames.query("I2"))
    network.make_connection(nNames.query("G1"),nNames.query(None), nNames.query("G3"), nNames.query("I1"))
    network.make_connection(nNames.query("G2"),nNames.query(None), nNames.query("G3"), nNames.query("I2"))

    monitors = Monitors(nNames, devices, network)
    mNames = monitors.names
    monitors.make_monitor(mNames.query("G3"), mNames.query(None))

    return monitors.names, monitors.devices, monitors.network, monitors
