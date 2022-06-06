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



# Workaround to stop Python stealing _ for translations
# Necessary for tests to work
import sys
import wx
import builtins


def _hook(obj):
    if obj is not None:
        print(repr(obj))


builtins.__dict__['_'] = wx.GetTranslation
sys.displayhook = _hook


names = Names()
devices = Devices(names)
network = Network(names, devices)
monitors = Monitors(names, devices, network)

path = 'example_files/binary_counter.txt'

scanner = Scanner(path, names)
parser = Parser(names, devices, network, monitors, scanner)

if parser.parse_network():
    # Initialise an instance of the userint.UserInterface() class
    userint = UserInterface(names, devices, network, monitors)
    userint.command_interface()
