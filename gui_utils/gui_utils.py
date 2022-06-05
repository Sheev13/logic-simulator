"""Utils for GUI implementation."""
import wx


class Utils:
    """Defines GUI Utils.

    This class allows gui.py to access all utils.
    It is necessary instead of just import variables because
    translatable strings need to be defined within an instance
    of a wx class.
    """

    def __init__(self):
        """Initialise colours."""
        self.paleyellow = wx.Colour(252, 251, 241)
        self.lightblue = wx.Colour(32, 95, 151)
        self.green = wx.Colour(208, 245, 206)
        self.red = wx.Colour(220, 69, 69)
        self.darkgreen = wx.Colour(0, 100, 0)
        self.midgreen = wx.Colour(51, 153, 85)
        self.darkpurple = wx.Colour(80, 24, 132)
        self.lightpurple = wx.Colour(158, 84, 226)
        self.white = wx.Colour(255, 255, 255)
        self.brightgreen = wx.Colour(40, 100, 0)
        self.darkpink = wx.Colour(170, 51, 106)
        self.lightpink = wx.Colour(218, 73, 158)
        self.blue = wx.Colour(0, 0, 139)
        self.darkred = wx.Colour(139, 0, 0)
        self.black = wx.Colour(0, 0, 0)

        """Initialise long strings."""
        self.first_parse_error_string = \
            _("Unable to load file. Please choose valid file.")
        self.parse_error_string = \
            _("Unable to load file. Old file will remain loaded.")
        self.help_string = \
            _("Enter command line inputs in the bottom left of") \
            + _(" the interface.") + "\n" \
            "\n" + _("Possible commands:") + \
            "\n \nr N\n" + _("Run simulator for N cycles") \
            + "\n \nc N\n" + _("Continue running simulation")\
            + _(" for N cycles") + \
            "\n \ns X N\n" + _("Set switch X to N (0 or 1)") +\
            "\n \nm X\n" + _("Start monitoring output signal X")\
            + "\n \nz X\n" + _("Stop monitoring X")
        self.canvas_controls_string = \
            _("Signals on the canvas can be manipulated to") \
            + _(" better view them.") + "\n" \
            "\n" + _("Scroll in to zoom in") + \
            "\n \n" + \
            _("Scroll out to zoom out - this may ") \
            + _("be useful if you have many monitors") \
            + "\n \n" \
            + _("Click and hold to drag the signals ")\
            + _("around the space")
        self.sidebar_guide_string = \
            _("The sidebar can be used to adjust simulation ") \
            + _("settings") + ".\n\n" + \
            _("Click 'Browse' to load a new circuit file.") \
            + "\n \n" + \
            _("See the list of devices to decide what you ") \
            + _("want to monitor. Hover on a device to see ") \
            + _("its full name, kind and qualifier information.") \
            + "\n \n" +\
            _("To remove a connection before or during a ") \
            + _("simulation, choose from the dropdown list ") \
            + _("next to 'Devices' and click 'Delete Connection.")\
            + _("Select a new output ") \
            + _("to connect to the input from the deleted ") \
            + _("connection.") \
            + "\n \n" + \
            _("Click the switch buttons to toggle on or off.") \
            + "\n \n" + \
            _("Type the name of an output in the 'Add new ") \
            + _("monitor' box to add to monitors.") \
            + _(" Press 'Clear All' to remove all monitors.") \
            + _(" Click on an individual monitor button to ") \
            + _("remove it.")\
            + "\n \n" + \
            _("Adjust the number of cycles with the spinner.")\
            + "\n \n" + \
            _("Press 'Run' or 'Continue' to start the ") \
            + _("simulation.")\
            + "\n \n" + \
            _("Press 'Clear Canvas' to reset the ") \
            + _("simulation.")
