"""Utils for GUI implementation."""
import wx

paleyellow = wx.Colour(252, 251, 241)
lightblue = wx.Colour(32, 95, 151)
green = wx.Colour(208, 245, 206)
red = wx.Colour(220, 69, 69)
darkgreen = wx.Colour(0, 100, 0)
midgreen = wx.Colour(51, 153, 85)
darkpurple = wx.Colour(80, 24, 132)
lightpurple = wx.Colour(158, 84, 226)
white = wx.Colour(255, 255, 255)
brightgreen = wx.Colour(40, 100, 0)
darkpink = wx.Colour(170, 51, 106)
lightpink = wx.Colour(218, 73, 158)
blue = wx.Colour(0, 0, 139)
darkred = wx.Colour(139, 0, 0)
black = wx.Colour(0, 0, 0)

help_string = "Enter command line inputs in the bottom left of " \
                        "the interface.\n" \
                        "\nPossible commands:" \
                        "\n \nr N\nRun simulator for N cycles" \
                        "\n \nc N\nContinue running simulation "\
                        "for N cycles" \
                        "\n \ns X N\nSet switch X to N (0 or 1)" \
                        "\n \nm X\nStart monitoring output signal X" \
                        "\n \nz X\nStop monitoring X"

canvas_control_string = "Signals on the canvas can be manipulated to " \
                            "better view them.\n" \
                            "\nScroll in to zoom in" \
                            "\n \n" \
                            "Scroll out to zoom out - this may " \
                            "be useful if you have many monitors" \
                            "\n \n" \
                            "Click and hold to drag the signals "\
                            "around the space"

sidebar_guide_string = "The sidebar can be used to set device properties " \
                            "and monitors.\n" \
                            "\nClick 'Browse' to load a new circuit file." \
                            "\n \n" \
                            "See the list of devices to decide what you " \
                            "want to monitor." \
                            "\n \n" \
                            "Click the switch buttons to toggle on or off." \
                            "\n \n" \
                            "Type the name of an output in the 'Add new " \
                            "monitor' box to add to monitors."\
                            " Press 'Clear All' to remove all monitors." \
                            " Click on an individual monitor button to " \
                            "remove it."\
                            "\n \n" \
                            "Adjust the number of cycles with the spinner." \
                            "\n \n" \
                            "Press 'Run' or 'Continue' to start the " \
                            "simulation."\
                            "\n \n" \
                            "Press 'Clear Canvas' to reset the " \
                            "simulation."\

parse_error_string = "Unable to parse file. Old file will remain loaded."
first_parse_error_string = "Unable to parse file. Please choose a valid circuit file."