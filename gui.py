"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
from django.shortcuts import redirect
from matplotlib.ft2font import VERTICAL
import wx
import os
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser

from userint import UserInterface
from guicommandint import GuiCommandInterface

switches = ["SW1", "SW2", "SW3", "SW4", "SW5", "SW6", "SW7", "SW8", "SW9"]
outputs = ["SW1", "SW2", "SW3", "SW4", "SW5", "SW6", "SW7", "SW8", "SW9", "G1", "G2", "F1.Q", "F1.QBAR"]
current_monitors = ["SW1", "SW2", "SW3", "SW4", "SW5", "SW6", "SW7", "SW8", "SW9", "G1", "G2", "F1.Q", "F1.QBAR"]
file_name_title = "example circuit"

class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw a sample signal trace
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(10):
            x = (i * 20) + 10
            x_next = (i * 20) + 30
            if i % 2 == 0:
                y = 75
            else:
                y = 100
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y)
        GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin_cycles(self, event): Event handler for when the user changes the number of cycles.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_command_line_input(self, event): Event handler for when the user enters a command.

    on_monitor_input(self, event): Event handler for when the user adds a monitor.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise circuit variables."""
        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network
        
        """Initialise user interface."""
        self.userint = UserInterface(names, devices, network, monitors)
        self.path = path
        self.help_string = help_string

        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu
        fileMenu = wx.Menu()
        userGuideMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        userGuideMenu.Append(wx.ID_HELP_COMMANDS, "&Command Line Inputs")
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(userGuideMenu, "&User Guide")
        self.SetMenuBar(menuBar)

        # Set background colour for GUI
        self.SetBackgroundColour(paleyellow)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Configure the widgets
        subHeadingFont = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD)

        self.file_name = wx.StaticText(self, wx.ID_ANY, f"{file_name_title}")
        self.file_name.SetFont(wx.Font(18, wx.DECORATIVE, wx.SLANT, wx.BOLD))
        self.browse = wx.Button(self, wx.ID_ANY, "Browse")

        if len(switches) > 0:
            self.switches_text = wx.StaticText(self, wx.ID_ANY,
                                    "Switches (toggle on/off):")
            self.switches_text.SetFont(subHeadingFont)
        else:
            self.switches_text = wx.StaticText(self, wx.ID_ANY,
                                    "No switches in this circuit")
        self.switch_buttons = {}
        for i in range(len(switches)):
            self.switch_buttons[switches[i]]= [wx.Button(self, i, switches[i]), False]
            self.switch_buttons[switches[i]][0].SetBackgroundColour(red)

        self.monitors_text = wx.StaticText(self, wx.ID_ANY, "Monitors:")
        self.monitors_text.SetFont(subHeadingFont)
        self.monitor_input = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER)
        self.monitor_input.SetHint("Add new monitor")
        self.monitors_help_text = wx.StaticText(self, wx.ID_ANY,
                                    "(click to remove)")
        self.monitorButtons = {}
        for curr in current_monitors:
            self.monitorButtons[curr] = wx.Button(self, wx.ID_ANY, curr)
            self.monitorButtons[curr].SetBackgroundColour(lightblue)

        go_font = wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.cycles_text = wx.StaticText(self, wx.ID_ANY, "Cycles:")
        self.cycles_text.SetFont(subHeadingFont)
        self.spin_cycles = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.run_button.SetFont(wx.Font(go_font))
        self.run_button.SetBackgroundColour(darkgreen)
        self.run_button.SetForegroundColour(white)
        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")
        self.continue_button.SetFont(wx.Font(go_font))
        self.continue_button.SetBackgroundColour(cornflower)
        self.continue_button.SetForegroundColour(white)
        self.command_line_input = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER, size=(300, 25))
        self.command_line_input.SetHint("Command line input. See User Guide for help.")

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.browse.Bind(wx.EVT_BUTTON, self.on_browse)
        for switch in [pair[0] for pair in self.switch_buttons.values()]:
            switch.Bind(wx.EVT_BUTTON, self.on_switch_button)
        for name in self.monitorButtons.keys():
            self.monitorButtons[name].Bind(wx.EVT_BUTTON, self.on_monitor_button)
        self.spin_cycles.Bind(wx.EVT_SPINCTRL, self.on_spin_cycles)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.command_line_input.Bind(wx.EVT_TEXT_ENTER, self.on_command_line_input)
        self.monitor_input.Bind(wx.EVT_TEXT_ENTER, self.on_monitor_input)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)
        #side_sizer.SetDimension(0, 0, 400, wx.EXPAND)

        # Sizers to be contained within side_sizer
        file_name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        manual_settings_sizer = wx.BoxSizer(wx.VERTICAL)
        switch_buttons_sizer = wx.FlexGridSizer(4)
        monitors_sizer = wx.BoxSizer(wx.HORIZONTAL)
        monitor_buttons_sizer = wx.FlexGridSizer(4)
        self.monitorButtonsSizer = monitor_buttons_sizer
        cycles_sizer = wx.BoxSizer(wx.HORIZONTAL)
        go_sizer = wx.BoxSizer(wx.HORIZONTAL)
        command_line_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add side_sizer and canvas to main_sizer
        main_sizer.Add(side_sizer, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.canvas, 10, wx.EXPAND | wx.ALL, 5)

        # Add sizers to side_szer
        side_sizer.Add(manual_settings_sizer, 1, wx.ALL, 5)
        #side_sizer.AddStretchSpacer()
        side_sizer.Add(cycles_sizer, 0, wx.LEFT, 5)
        side_sizer.Add(go_sizer, 0, wx.LEFT, 5)
        side_sizer.Add(command_line_sizer, 0, wx.LEFT, 5)
        

        #Add widgets to smaller sizers
        command_line_sizer.Add(self.command_line_input, 1, wx.ALL, 5)

        manual_settings_sizer.Add(file_name_sizer, 1, wx.TOP, 5)
        #manual_settings_sizer.AddStretchSpacer()
        manual_settings_sizer.Add(self.switches_text, 0, wx.ALL, 5)
        manual_settings_sizer.Add(switch_buttons_sizer, 0, wx.ALL, 5)
        manual_settings_sizer.Add(monitors_sizer)
        manual_settings_sizer.Add(monitor_buttons_sizer, 0, wx.ALL, 5)

        file_name_sizer.Add(self.file_name, 1, wx.ALL, 5)
        file_name_sizer.Add(self.browse, 0, wx.TOP, 6)

        for switch in [pair[0] for pair in self.switch_buttons.values()]:
            switch_buttons_sizer.Add(switch, 1, wx.TOP, 5)

        for mon in self.monitorButtons.values():
            monitor_buttons_sizer.Add(mon, 1, wx.TOP, 5)

        monitors_sizer.Add(self.monitors_text, 1, wx.ALL, 5)
        monitors_sizer.Add(self.monitor_input)
        monitors_sizer.Add(self.monitors_help_text, 1, wx.ALL, 5)

        cycles_sizer.Add(self.cycles_text, 1, wx.ALL, 5)
        cycles_sizer.Add(self.spin_cycles, 1, wx.ALL, 5)
        go_sizer.Add(self.run_button, 1, wx.ALL, 5)
        go_sizer.Add(self.continue_button, 1, wx.ALL, 5)
        
        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)
        
        self.Layout()


    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by pp490\n2022",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)
        if Id == wx.ID_HELP_COMMANDS:
            wx.MessageBox(self.help_string, "User Guide", wx.ICON_INFORMATION | wx.OK)


    def on_browse(self, event):
        """Handle the event when user wants to find circuit definition file."""
        openFileDialog= wx.FileDialog(self, "Open txt file", "", "", 
                            wildcard="TXT files (*.txt)|*.txt", style=wx.FD_OPEN+wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
           return
        path = openFileDialog.GetPath()
        label = os.path.basename(os.path.splitext(path)[0])
        if len(label) > 16:
            label = f"\"{label[0:13]}...\""
        self.file_name.SetLabel(label)
        self.path = path
        scanner = Scanner(path, None)
        parser = Parser(None, None, None, None, scanner)
        #TODO parser should return names, devices, network,monitors
        # if parser.parse_network():
        #     self.names = parser[0]
        #     self.devices = parser[1]
        #     self.network = parser[2]
        #     self.monitors = parser[3]

        
        
    def on_spin_cycles(self, event):
        """Handle the event when the user changes the number of cycles."""
        cycles = self.spin_cycles.GetValue()
        text = "".join(["Number of cycles: ", str(cycles)])
        self.canvas.render(text)


    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        self.canvas.render(text)


    def on_switch_button(self, event):
        """Handle the event when the user clicks the switch button."""
        button = event.GetEventObject()
        if self.switch_buttons[button.GetLabel()][1]:
            button.SetBackgroundColour(red)
            self.switch_buttons[button.GetLabel()][1] = False
            status = "off"
        else:
            button.SetBackgroundColour(green)
            self.switch_buttons[button.GetLabel()][1] = True
            status = "on"
        text = f"{button.GetLabel()} turned {status}."
        self.canvas.render(text)

    def destroyMonitor(self, monitor):
        """Destroy monitor."""
        if monitor is not None:
            [device, port] = monitor
            if self.monitors.remove_monitor(device, port):
                return "Successfully zapped monitor."
        return "Error! Could not zap monitor."

    def on_monitor_button(self, event):
        """Handle the event when the user clicks the monitor button."""
        button = event.GetEventObject()
        label = button.GetLabel()
        button.Destroy()
        current_monitors.remove(label)
        #text = self.destroyMonitor(monitor)
        text = f"Monitor {label} destroyed."
        self.canvas.render(text)
        self.Layout()

    def on_continue_button(self, event):
        """Handle the event when the user clicks the continue button."""
        text = "Continue button pressed."
        self.canvas.render(text)

    def on_command_line_set_switch(self, switch):
        """Change colour of switch button based on command line input."""
        switchName = switch[0]
        status = switch[1]
        button = self.switch_buttons[switchName][0]

        if status == 0:
            button.SetBackgroundColour(red)
            self.switch_buttons[switchName][1] = False
            now = "off"
        else:
            button.SetBackgroundColour(green)
            self.switch_buttons[switchName][1] = True
            now = "on"
        self.Layout()

    def on_command_line_add_monitor(self, monitorName):
        """Add monitor button based on command line input."""
        current_monitors.append(monitorName)
        newButton = wx.Button(self, wx.ID_ANY, monitorName)
        newButton.SetBackgroundColour(lightblue)
        newButton.Bind(wx.EVT_BUTTON, self.on_monitor_button)
        buttonSizer = self.monitorButtonsSizer
        buttonSizer.Add(newButton, 1, wx.TOP, 5)
        self.monitorButtons[monitorName] = newButton
        self.Layout()

    def on_command_line_zap_monitor(self, monitorName):
        """Destroy monitor button based on command line input."""
        button = self.monitorButtons[monitorName]
        label = button.GetLabel()
        button.Destroy()
        current_monitors.remove(label)
        self.Layout()

    def on_command_line_input(self, event):
        """Handle the event when the user enters command line text."""
        line = self.command_line_input.GetValue()
        commandint = GuiCommandInterface(line, self.names, self.devices, self.network, self.monitors)
        action = commandint.command_interface()
        command = action[0]
        text = action[1]
        extraInfo = action[2]
        if extraInfo is not None:
            if command == "s":
                self.on_command_line_set_switch(extraInfo)
            elif command == "m":
                self.on_command_line_add_monitor(extraInfo)
            elif command == "z":
                self.on_command_line_zap_monitor(extraInfo)

        self.canvas.render(text)

        self.names = action[3]
        self.devices = action[4]
        self.network = action[5]
        self.monitors = action[6]
        
        
    def makeMonitor(self, monitor):
        """Create a new monitoring point based on user selection, and add to list of buttons."""
        # if monitor is not None:
        #     [device, port] = monitor
        #     monitor_error = self.monitors.make_monitor(device, port,
        #                                                self.cycles_completed)
        #     if monitor_error == self.monitors.NO_ERROR:
        #         text = "Successfully made monitor."
        # else:
        #     return "Error! Could not make monitor."
        text = "Successfully made monitor."
        current_monitors.append(monitor)
        newButton = wx.Button(self, wx.ID_ANY, monitor)
        newButton.SetBackgroundColour(lightblue)
        newButton.Bind(wx.EVT_BUTTON, self.on_monitor_button)
        buttonSizer = self.monitorButtonsSizer
        buttonSizer.Add(newButton, 1, wx.TOP, 5)
        self.monitorButtons[monitor] = newButton
        self.Layout()
        return text

    def isMonitoring(self, monitor):
        """Return True if suggested monitor point is already being monitored."""
        return monitor in current_monitors

    def isValidMonitor(self, monitor):
        """Return True if suggested monitor point is a recognised output."""
        return monitor in outputs

    def on_monitor_input(self, event):
        """Handle the event when the user adds a monitor."""
        name = self.monitor_input.GetValue().upper()
        if self.isValidMonitor(name):
            if self.isMonitoring(name):
                text = f"Already monitoring {name}"
            else:
                self.makeMonitor(name)    
                text = "".join(["New monitor: ", name])
        else:
            text = "Invalid monitor"
        self.canvas.render(text)


paleyellow = wx.Colour(252, 251, 241)
lightblue = wx.Colour(225, 239, 246)
green = wx.Colour(208, 245, 206)
red = wx.Colour(244, 204, 199)
darkgreen = wx.Colour(76, 129, 73)
cornflower = wx.Colour(145, 143, 214)
white = wx.Colour(255, 255, 255)

help_string = "Enter command line inputs in the bottom left of the interface.\n" \
                            "\nPossible commands:" \
                            "\n \nr N\nRun simulator for N cycles" \
                            "\n \nc N\nContinue running simulation for N cycles" \
                            "\n \ns X N\nSet switch X to N (0 or 1)" \
                            "\n \nm X\nStart monitoring output signal X" \
                            "\n \nz X\nStop monitoring X"