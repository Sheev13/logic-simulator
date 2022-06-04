import getopt
import sys

# import wx

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from userint import UserInterface
# from gui import Gui

names = Names()
devices = Devices(names)
network = Network(names, devices)
monitors = Monitors(names, devices, network)

path = 'test_files/parser_maintenance.txt'

scanner = Scanner(path, names)
parser = Parser(names, devices, network, monitors, scanner)

if parser.parse_network():
    # Initialise an instance of the userint.UserInterface() class
    userint = UserInterface(names, devices, network, monitors)
    userint.command_interface()
