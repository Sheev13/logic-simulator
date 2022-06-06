#!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py <file path>
"""
import getopt
import os
import sys
import builtins

import wx
from wx.lib.mixins.inspection import InspectionMixin

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from userint import UserInterface
from gui import Gui

# language domain
langDomain = "LOGIC SIMULATOR"
supportedLangs = {
    u"en": wx.LANGUAGE_ENGLISH,
    u"es": wx.LANGUAGE_SPANISH
}

def _hook(obj):
    if obj is not None:
        print (repr(obj))

builtins.__dict__['_'] = wx.GetTranslation

class App(wx.App, InspectionMixin):
    def OnInit(self):
        self.Init()
        sys.displayhook = _hook
        self.appName = "Logic Simulator"
        self.doConfig()

        self.locale = None
        wx.Locale.AddCatalogLookupPathPrefix('locale')
        self.updateLanguage(self.appConfig.Read(u"Language"))

        return True

    def doConfig(self):
        """Setup an application configuration file"""
        # configuration folder
        sp = wx.StandardPaths.Get()
        self.configLoc = sp.GetUserConfigDir()
        self.configLoc = os.path.join(self.configLoc, self.appName)
        # win: C:\Users\userid\AppData\Roaming\appName
        # nix: \home\userid\appName

        if not os.path.exists(self.configLoc):
            os.mkdir(self.configLoc)

        # AppConfig stuff is here
        self.appConfig = wx.FileConfig(appName=self.appName,
                                       vendorName=u'who you wish',
                                       localFilename=os.path.join(
                                       self.configLoc, "AppConfig"))
    
        if not self.appConfig.HasEntry(u'Language'):
            # on first run we default to English
            self.appConfig.Write(key=u'Language', value=u'en')
            
        self.appConfig.Flush()


    def updateLanguage(self, lang):
        """
        Update the language to the requested one.
        Make *sure* any existing locale is deleted before the new
        one is created.
        """
        # if an unsupported language is requested default to English
        if lang in supportedLangs:
            setLang = supportedLangs[lang]
        else:
            setLang = wx.LANGUAGE_ENGLISH
        print(setLang)

        if self.locale:
            assert sys.getrefcount(self.locale) <= 2
            del self.locale

        # create a locale object for this language
        self.locale = wx.Locale(setLang)
        if self.locale.IsOk():
            self.locale.AddCatalog(langDomain)
        else:
            self.locale = None



def main(arg_list):
    """Parse the command line options and arguments specified in arg_list.

    Run either the command line user interface, the graphical user interface,
    or display the usage message.
    """
    usage_message = ("Usage:\n"
                     "Show help: logsim.py -h\n"
                     "Command line user interface: logsim.py -c <file path>\n"
                     "Graphical user interface: logsim.py <file path>")
    try:
        options, arguments = getopt.getopt(arg_list, "hc:")
    except getopt.GetoptError:
        print("Error: invalid command line arguments\n")
        print(usage_message)
        sys.exit()

    # Initialise instances of the four inner simulator classes
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    for option, path in options:
        if option == "-h":  # print the usage message
            print(usage_message)
            sys.exit()
        elif option == "-c":  # use the command line user interface
            scanner = Scanner(path, names)
            parser = Parser(names, devices, network, monitors, scanner)
            if parser.parse_network():
                # Initialise an instance of the userint.UserInterface() class
                userint = UserInterface(names, devices, network, monitors)
                userint.command_interface()

    if not options:  # no option given, use the graphical user interface

        if len(arguments) != 1:  # wrong number of arguments
            path = None
        else:
            [path] = arguments
        # Initialise an instance of the gui.Gui() class
        app = App()
        builtins._ = wx.GetTranslation
        locale = wx.Locale()
        locale.Init(wx.LANGUAGE_DEFAULT)
        locale.AddCatalogLookupPathPrefix('locales')
        locale.AddCatalog('base')
        gui = Gui("Logic Simulator", path, names, devices, network,
                    monitors)
        gui.Show(True)
        app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
