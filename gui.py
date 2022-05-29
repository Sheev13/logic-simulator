"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
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
from gui_utils import *

import numpy as np


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
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

    def __init__(self, parent, size, devices, monitors, names):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1, size=size,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)
        self.monitors = monitors
        self.devices = devices
        self.names = names

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
        top = 675
        self.render_text(text, 10, top)

        # Draw signal traces
        low = 5
        high = 25
        signalData = self.monitors.display_signals_gui(high=high, low=low)
        axis = top-45
        for monitor in signalData.keys():
            desc, X, Y, device_kind = signalData[monitor]
            if len(X) > 0:
                margin = len(desc)*6
                Y = [axis+y for y in Y]
                X = [x+margin+10 for x in X]
                rgb = self.traceColour(device_kind)
                self.render_text(desc, X[0]-margin, axis+12)
                self.drawTrace(X, Y, axis, rgb)
                axis -= 100

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def drawTrace(self, X, Y, axis, rgb):
        """Draw a signal trace."""
        # Draw trace
        GL.glShadeModel(GL.GL_FLAT)
        GL.glColor3f(rgb[0], rgb[1], rgb[2])
        GL.glBegin(GL.GL_LINE_STRIP)
        i = 1
        while i < len(X):
            if Y[i] == axis:
                GL.glColor3f(1, 1, 1)
                GL.glVertex2f(X[i-1], Y[i-1])
                GL.glVertex2f(X[i], Y[i])
                GL.glColor3f(rgb[0], rgb[1], rgb[2])
            else:
                if i > 1 and Y[i-2] == axis:
                    GL.glColor3f(1, 1, 1)
                    GL.glVertex2f(X[i-1], Y[i-1])
                    GL.glColor3f(rgb[0], rgb[1], rgb[2])
                    GL.glVertex2f(X[i], Y[i])
                else:
                    GL.glVertex2f(X[i-1], Y[i-1])
                    GL.glVertex2f(X[i], Y[i])
            i += 2
        GL.glEnd()

        # Draw x axis
        GL.glColor3f(0, 0, 0)  # x axis is black
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(len(X)):
            GL.glVertex2f(X[i], axis)
            GL.glVertex2f(X[i], axis-3)
            GL.glVertex2f(X[i], axis)
        GL.glEnd()

        t = 0
        while t < len(X):
            self.render_text(str(int(t/2)), X[t]-4, axis-14)
            t += 4

    def traceColour(self, device_kind):
        """Colour code trace based on device kind."""
        gate_strings = ["AND", "OR", "NAND", "NOR", "XOR"]
        if self.names.get_name_string(device_kind) in gate_strings:
            return [0, 0, 1]
        if self.names.get_name_string(device_kind) == "CLOCK":
            return [0, 1, 0]
        if self.names.get_name_string(device_kind) == "SWITCH":
            return [1, 0, 1]
        if self.names.get_name_string(device_kind) == "DTYPE":
            return [1, 0, 0]
        else:
            return [0, 0, 0]

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        text = "Welcome to the Logic Simulator! " \
            "See User Guide for canvas controls "\
            "and a guide to command line input."
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

        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False

        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False

        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False

        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(
        self, text, x_pos, y_pos, font=GLUT.GLUT_BITMAP_HELVETICA_12
    ):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)

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

    on_spin_cycles(self, event): Handle event when user changes cycles.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_command_line_input(self, event): Handle user commands.

    on_monitor_input(self, event): Handle event when user adds a monitor.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise circuit variables."""
        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network
        self.cycles_completed = 0
        self.cycles_to_run = 10

        """Initialise user interface."""
        self.path = path
        self.userint = UserInterface(names, devices, network, monitors)
        self.help_string = help_string
        self.canvas_control_string = canvas_control_string
        self.parse_error_string = parse_error_string
        self.click = wx.Cursor(wx.Image("click.png"))

        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu
        fileMenu = wx.Menu()
        userGuideMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        userGuideMenu.Append(wx.ID_HELP_COMMANDS, "&Command Line Guide")
        userGuideMenu.Append(wx.ID_CONTEXT_HELP, "&Canvas Controls")
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(userGuideMenu, "&User Guide")
        self.SetMenuBar(menuBar)

        # Set background colour for GUI
        self.SetBackgroundColour(paleyellow)

        # Canvas for drawing signals
        self.scrollable = wx.ScrolledCanvas(self, wx.ID_ANY)
        self.scrollable.SetVirtualSize(500, 500)
        self.scrollable.ShowScrollbars(wx.SHOW_SB_ALWAYS, wx.SHOW_SB_DEFAULT)
        self.scrollable.SetScrollbars(20, 20, 15, 10)
        self.canvas = MyGLCanvas(
            self.scrollable, wx.Size(1500, 700), devices, monitors, names
        )
        # Configure the widgets
        self.subHeadingFont = wx.Font(wx.FontInfo(12).FaceName("Rockwell"))
        self.file_name = wx.StaticText(
            self, wx.ID_ANY, f"", size=wx.Size(300, 30)
        )
        fileFont = wx.Font(wx.FontInfo(18).FaceName("Rockwell").Bold())
        helpFont = wx.Font(wx.FontInfo(10).FaceName("Rockwell"))
        self.file_name.SetFont(fileFont)
        self.browse = wx.Button(self, wx.ID_ANY, "Browse")
        self.browse.SetFont(helpFont)
        self.browse.SetCursor(self.click)

        self.switches_text = wx.StaticText(self, wx.ID_ANY, "")
        self.switches_text.SetFont(self.subHeadingFont)
        self.switch_buttons = {}

        self.devices_heading = wx.StaticText(self, wx.ID_ANY, "Devices:")
        self.devices_heading.SetFont(self.subHeadingFont)
        self.device_buttons = []

        self.monitors_text = wx.StaticText(self, wx.ID_ANY, "Monitors:")
        self.monitors_text.SetFont(self.subHeadingFont)
        self.monitor_input = wx.TextCtrl(
            self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER
        )
        self.monitor_input.SetHint("Add new monitor")
        self.monitors_help_text = wx.StaticText(
            self, wx.ID_ANY, "(click signals below to remove)"
        )
        self.monitors_help_text.SetFont(helpFont)
        self.clear_all_monitors = wx.Button(self, wx.ID_ANY, "Clear All")
        self.clear_all_monitors.SetCursor(self.click)
        self.clear_all_monitors.SetFont(helpFont)
        self.monitorButtons = {}

        go_font = wx.Font(wx.FontInfo(14).FaceName("Rockwell"))
        self.cycles_text = wx.StaticText(self, wx.ID_ANY, "Cycles:")
        self.cycles_text.SetFont(self.subHeadingFont)
        self.spin_cycles = wx.SpinCtrl(self, wx.ID_ANY, "10")

        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.run_button.SetCursor(self.click)
        self.run_button.SetFont(wx.Font(go_font))
        self.run_button.SetBackgroundColour(darkgreen)
        self.run_button.SetForegroundColour(white)

        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")
        self.continue_button.SetFont(wx.Font(go_font))
        self.continue_button.SetBackgroundColour(cornflower)
        self.continue_button.SetForegroundColour(white)
        self.continue_button.SetCursor(self.click)

        commandLineFont = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.command_line_input = wx.TextCtrl(
            self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER, size=(400, 25)
        )
        self.command_line_input.SetHint(
            "Command line input. See User Guide for help."
        )
        self.command_line_input.SetFont(commandLineFont)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.browse.Bind(wx.EVT_BUTTON, self.on_browse)
        self.spin_cycles.Bind(wx.EVT_SPINCTRL, self.on_spin_cycles)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.monitor_input.Bind(wx.EVT_TEXT_ENTER, self.on_monitor_input)
        self.command_line_input.Bind(
            wx.EVT_TEXT_ENTER,
            self.on_command_line_input
        )
        self.clear_all_monitors.Bind(
            wx.EVT_BUTTON, self.on_clear_all_monitors_button
        )

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)

        # Sizers to be contained within side_sizer
        file_name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        manual_settings_sizer = wx.BoxSizer(wx.VERTICAL)

        self.devices_sizer = wx.FlexGridSizer(4)
        self.devices_window = wx.ScrolledWindow(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.Size(375, 120),
            wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL
        )
        self.devices_window.SetSizer(self.devices_sizer)
        self.devices_window.SetScrollRate(10, 10)
        self.devices_window.SetAutoLayout(True)

        self.switch_buttons_sizer = wx.FlexGridSizer(4)
        self.switch_window = wx.ScrolledWindow(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.Size(375, 60),
            wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL
        )
        self.switch_window.SetSizer(self.switch_buttons_sizer)
        self.switch_window.SetScrollRate(10, 10)
        self.switch_window.SetAutoLayout(True)

        self.monitor_buttons_sizer = wx.FlexGridSizer(4)
        self.monitors_window = wx.ScrolledWindow(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.Size(375, 60),
            wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL
        )
        self.monitors_window.SetSizer(self.monitor_buttons_sizer)
        self.monitors_window.SetScrollRate(10, 10)
        self.monitors_window.SetAutoLayout(True)

        monitors_sizer = wx.BoxSizer(wx.HORIZONTAL)
        monitors_help_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cycles_sizer = wx.BoxSizer(wx.HORIZONTAL)
        command_line_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add side_sizer and canvas to main_sizer
        main_sizer.Add(side_sizer, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.scrollable, 10, wx.EXPAND | wx.ALL, 5)

        # Add sizers to side_sizer
        side_sizer.Add(manual_settings_sizer, 1, wx.ALL, 5)
        side_sizer.Add(cycles_sizer, 0, wx.LEFT, 5)
        side_sizer.Add(command_line_sizer, 0, wx.LEFT, 5)

        # add widgets to smaller sizers
        command_line_sizer.Add(self.command_line_input, 1, wx.ALL, 5)

        manual_settings_sizer.Add(file_name_sizer, 1, wx.TOP, 5)
        manual_settings_sizer.Add(self.devices_heading, 0, wx.ALL, 5)
        manual_settings_sizer.Add(self.devices_window, 0, wx.ALL, 5)
        manual_settings_sizer.Add(self.switches_text, 0, wx.ALL, 5)
        manual_settings_sizer.Add(self.switch_window, 0, wx.ALL, 5)
        manual_settings_sizer.Add(monitors_sizer, 0, wx.TOP, 5)
        manual_settings_sizer.Add(monitors_help_sizer)
        manual_settings_sizer.Add(self.monitors_window, 0, wx.ALL, 5)

        file_name_sizer.Add(self.file_name, 1, wx.ALL, 5)
        file_name_sizer.Add(self.browse, 0, wx.TOP, 6)

        monitors_sizer.Add(self.monitors_text, 1, wx.ALL, 5)

        monitors_help_sizer.Add(self.monitor_input, 0, wx.ALL, 5)
        monitors_help_sizer.Add(self.clear_all_monitors, 0, wx.ALL, 5)
        monitors_help_sizer.Add(self.monitors_help_text, 0, wx.ALL, 10)

        cycles_sizer.Add(self.cycles_text, 0, wx.TOP, 10)
        cycles_sizer.Add(self.spin_cycles, 0, wx.LEFT+wx.TOP, 10)
        cycles_sizer.Add(self.run_button, 1, wx.ALL, 5)
        cycles_sizer.Add(self.continue_button, 1, wx.ALL, 5)

        self.updateNewCircuit(first=True)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)
        self.Layout()

    def setFileTitle(self, path):
        """Display name of open file at top of screen."""
        label = os.path.basename(os.path.splitext(path)[0])
        if len(label) > 22:
            label = f"\"{label[0:20]}...\""
        self.file_name.SetLabel(label)
        self.Layout()

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox(
                "Logic Simulator\nCreated by pp490, tnr22, jt741\n2022",
                "About Logsim", wx.ICON_INFORMATION | wx.OK
            )
        if Id == wx.ID_HELP_COMMANDS:
            wx.MessageBox(
                self.help_string,
                "Command Line Guide",
                wx.ICON_INFORMATION | wx.OK
            )
        if Id == wx.ID_CONTEXT_HELP:
            wx.MessageBox(
                self.canvas_control_string,
                "Canvas Controls",
                wx.ICON_INFORMATION | wx.OK
            )

    def on_browse(self, event):
        """Handle the event when user wants to find circuit definition file."""
        openFileDialog = wx.FileDialog(
            self, "Open txt file", "", "",
            wildcard="TXT files (*.txt)|*.txt",
            style=wx.FD_OPEN+wx.FD_FILE_MUST_EXIST
        )
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return
        path = openFileDialog.GetPath()
        names = Names()
        devices = Devices(names)
        network = Network(names, devices)
        monitors = Monitors(names, devices, network)
        scanner = Scanner(path, names)
        parser = Parser(names, devices, network, monitors, scanner)
        if parser.parse_network():
            self.path = path
            self.names = names
            self.devices = devices
            self.network = network
            self.monitors = monitors
            self.updateNewCircuit()
        else:
            wx.MessageBox(
                self.parse_error_string,
                "Unable to parse file.",
                wx.ICON_INFORMATION | wx.OK
            )

    def updateNewCircuit(self, first=False):
        """Configure widgets for new circuit and bind events."""
        self.setFileTitle(self.path)
        self.cycles_completed = 0

        # find new switches
        switches = self.devices.find_devices(self.names.query("SWITCH"))
        if len(switches) > 0:
            self.switches_text.SetLabel("Switches (toggle on/off):")
        else:
            self.switches_text.SetLabel("No switches in this circuit.")

        if not first:
            # destroy current switch buttons
            for switch in [pair[0] for pair in self.switch_buttons.values()]:
                switch.Destroy()

            # destroy current device list in sidebars
            for button in self.device_buttons:
                button.Destroy()

            # destroy current monitor buttons
            for monitor in self.monitorButtons.values():
                monitor.Destroy()

        # add new switches
        self.switch_buttons = {}
        for s in switches:
            name = self.names.get_name_string(s)
            state = self.devices.get_device(s).switch_state
            shortName = self.shorten(name)
            button = wx.Button(self.switch_window, s, shortName)
            button.SetToolTip(name)
            button.SetCursor(self.click)
            if state == 0:
                button.SetBackgroundColour(red)
            else:
                button.SetBackgroundColour(lightblue)
            self.switch_buttons[name] = [button, state]

        # bind switch buttons to event
        for switch in [pair[0] for pair in self.switch_buttons.values()]:
            switch.Bind(wx.EVT_BUTTON, self.on_switch_button)

        # add switches to sizer
        for switch in [pair[0] for pair in self.switch_buttons.values()]:
            self.switch_buttons_sizer.Add(
                switch, 1, wx.TOP+wx.LEFT+wx.RIGHT, 5
            )

        # find new devices
        self.device_descs = []
        for gate_type in self.devices.gate_types:
            gates = self.devices.find_devices(gate_type)
            for gateId in gates:
                gate = self.devices.get_device(gateId)
                label = self.shorten(
                    self.names.get_name_string(gate.device_id)
                )
                extra = f": {str(len(gate.inputs.keys()))} inputs"
                self.device_descs.append([gateId, label, extra])

        for dev_type in self.devices.device_types:
            other_devices = self.devices.find_devices(dev_type)
            for id in other_devices:
                d = self.devices.get_device(id)
                label = self.shorten(self.names.get_name_string(d.device_id))
                kind = self.names.get_name_string(d.device_kind)
                extra = ""
                if kind == "CLOCK":
                    extra = f": half-period {d.clock_half_period}"
                self.device_descs.append([id, label, extra])

        # add new devices to displayed list
        self.device_buttons = []
        for d in self.device_descs:
            print(d)
            [id, label, extra] = d
            device_button = wx.Button(
                self.devices_window, id, self.shorten(f"{label}{extra}")
            )
            c = wx.Cursor(wx.Image('info.png'))
            device_button.SetCursor(c)
            kindId = self.devices.get_device(id).device_kind
            kindLabel = self.names.get_name_string(kindId)
            device_button.SetToolTip(f"{label}, {kindLabel}{extra}")

            device_button.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            device_button.SetBackgroundColour(self.getDeviceColour(kindId))
            device_button.SetForegroundColour(white)
            self.device_buttons.append(device_button)

        # add new device list to sizer
        for device in self.device_buttons:
            self.devices_sizer.Add(device, 0, wx.ALL, 5)

        # add new monitor buttons
        self.monitorButtons = {}
        self.current_monitors = self.monitors.get_signal_names()[0]
        for curr in self.current_monitors:
            currId = self.names.lookup([curr])[0]
            button = wx.Button(
                self.monitors_window, currId, curr
            )
            button.SetBackgroundColour(lightblue)
            button.SetCursor(self.click)
            self.monitorButtons[curr] = button

        # bind monitor buttons to event
        for name in self.monitorButtons.keys():
            self.monitorButtons[name].Bind(
                wx.EVT_BUTTON, self.on_monitor_button
            )

        # add new monitor buttons to sizer
        for mon in self.monitorButtons.values():
            self.monitor_buttons_sizer.Add(mon, 1, wx.TOP+wx.RIGHT+wx.LEFT, 5)

        text = "New circuit loaded."

        self.canvas.monitors = self.monitors
        self.canvas.devices = self.devices
        self.canvas.names = self.names
        self.canvas.render(text)
        self.Layout()

    def on_spin_cycles(self, event):
        """Handle the event when the user changes the number of cycles."""
        self.cycles_to_run = self.spin_cycles.GetValue()
        text = "".join(["Number of cycles: ", str(self.cycles_to_run)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        int = GuiCommandInterface(
            f"{self.cycles_to_run}",
            self.names,
            self.devices,
            self.network,
            self.monitors
        )
        text, cycles = int.run_command()
        self.cycles_completed = cycles
        self.canvas.render(text)

    def on_continue_button(self, event):
        """Handle the event when the user clicks the continue button."""
        int = GuiCommandInterface(
            f"{self.cycles_to_run}",
            self.names,
            self.devices,
            self.network,
            self.monitors,
            complete=self.cycles_completed
        )
        text, cycles = int.continue_command()
        self.cycles_completed += cycles
        self.canvas.render(text)

    def on_switch_button(self, event):
        """Handle the event when the user clicks the switch button."""
        button = event.GetEventObject()
        switchId = button.GetId()
        switchName = self.names.get_name_string(switchId)

        if self.switch_buttons[switchName][1] == 1:
            button.SetBackgroundColour(red)
            self.switch_buttons[switchName][1] = 0
        else:
            button.SetBackgroundColour(lightblue)
            self.switch_buttons[switchName][1] = 1
        newStatus = self.switch_buttons[switchName][1]
        self.devices.set_switch(switchId, newStatus)

        text = f"{switchName} turned {newStatus}."
        self.canvas.render(text)

    def on_monitor_button(self, event):
        """Handle the event when the user clicks the monitor button."""
        button = event.GetEventObject()
        monitorName = self.names.get_name_string(button.GetId())
        text = self.destroyMonitor(monitorName)
        button.Destroy()
        self.monitorButtons.pop(monitorName)
        self.canvas.render(text)
        self.Layout()

    def on_clear_all_monitors_button(self, event):
        """Handle the event when the user clears all monitors."""
        for button in self.monitorButtons.values():
            button.Destroy()

        for monitorName in self.monitors.get_signal_names()[0]:
            commandint = GuiCommandInterface(
                monitorName,
                self.names,
                self.devices,
                self.network,
                self.monitors
            )
            [deviceId, portId] = commandint.read_signal_name()
            self.monitors.remove_monitor(deviceId, portId)
            self.monitorButtons.pop(monitorName, "")
        self.Layout()

    def on_monitor_input(self, event):
        """Handle the event when the user adds a monitor."""
        name = self.monitor_input.GetValue()
        if self.isValidMonitor(name):
            if self.isMonitoring(name):
                text = f"Already monitoring {name}"
            else:
                text = self.makeMonitor(name)
                self.addMonitorButton(name)
        else:
            text = "Invalid monitor"

        self.canvas.render(text)

    def on_command_line_input(self, event):
        """Handle the event when the user enters command line text."""
        line = self.command_line_input.GetValue()
        commandint = GuiCommandInterface(
            line,
            self.names,
            self.devices,
            self.network,
            self.monitors,
            complete=self.cycles_completed
        )
        action = commandint.command_interface()
        command = action[0]
        text = action[1]
        extraInfo = action[2]
        self.names = action[3]
        self.devices = action[4]
        self.network = action[5]
        self.monitors = action[6]

        if extraInfo is not None:
            if command == "s":
                # extraInfo = switch_state
                self.on_command_line_set_switch(extraInfo)
            elif command == "m":
                # extraInfo = monitors, [device_id, port_id]
                self.on_command_line_add_monitor(
                    extraInfo[1][0], extraInfo[1][1]
                )
            elif command == "z":
                # extraInfo = monitors, [device_id, port_id]
                self.on_command_line_zap_monitor(
                    extraInfo[1][0], extraInfo[1][1]
                )
            elif command == "r":
                self.on_command_line_run(extraInfo)  # extraInfo = cycles
            elif command == "c":
                self.on_command_line_cont(extraInfo)  # extraInfo = cycles

        self.canvas.render(text)

    def on_command_line_run(self, cycles):
        """Handle signal display when run command issued via command line."""
        self.cycles_completed = cycles

    def on_command_line_cont(self, cycles):
        """Handle signal display when run command issued via command line."""
        self.cycles_completed += cycles

    def on_command_line_set_switch(self, switch):
        """Change colour of switch button based on command line input."""
        switchName = self.names.get_name_string(switch[0])
        status = switch[1]
        button = self.switch_buttons[switchName][0]
        self.switch_buttons[switchName][1] = status
        if status == 0:
            button.SetBackgroundColour(red)
        else:
            button.SetBackgroundColour(lightblue)
        self.Layout()

    def on_command_line_add_monitor(self, deviceId, portId):
        """Add monitor button based on command line input."""
        monitorName = self.getMonitorName(deviceId, portId)
        self.addMonitorButton(monitorName)

    def on_command_line_zap_monitor(self, deviceId, portId):
        """Destroy monitor button based on command line input."""
        monitorName = self.getMonitorName(deviceId, portId)
        button = self.monitorButtons[monitorName]
        button.Destroy()
        self.monitorButtons.pop(monitorName)
        self.Layout()

    def getMonitorName(self, deviceId, portId):
        """Get name of monitor from device id and port id."""
        deviceName = self.names.get_name_string(deviceId)
        if portId is None:
            monitorName = deviceName
        else:
            portName = self.names.get_name_string(portId)
            monitorName = f"{deviceName}.{portName}"
        return monitorName

    def makeMonitor(self, monitorName):
        """Create a new monitoring point based on user selection."""
        commandint = GuiCommandInterface(
            monitorName, self.names, self.devices, self.network, self.monitors
        )
        text, [self.monitors, monitor] = commandint.monitor_command()
        self.canvas.render(text)
        return text

    def destroyMonitor(self, monitorName):
        """Destroy monitor."""
        commandint = GuiCommandInterface(
            monitorName, self.names, self.devices, self.network, self.monitors
        )
        text, [self.monitors, monitor] = commandint.zap_command()
        self.canvas.render(text)
        return text

    def isMonitoring(self, monitor):
        """Return True if monitor point is already being monitored."""
        return monitor in self.monitors.get_signal_names()[0]

    def isValidMonitor(self, monitor):
        """Return True if suggested monitor point is a recognised output."""
        signalNames = self.monitors.get_signal_names()
        return monitor in signalNames[0] or monitor in signalNames[1]

    def addMonitorButton(self, name):
        """Add monitor button when monitor successfully created."""
        shortName = self.shorten(name)
        id = self.names.lookup([name])[0]
        newButton = wx.Button(self.monitors_window, id, shortName)
        newButton.SetBackgroundColour(lightblue)
        newButton.Bind(wx.EVT_BUTTON, self.on_monitor_button)
        newButton.SetToolTip(name)
        newButton.SetCursor(self.click)
        self.monitor_buttons_sizer.Add(
            newButton, 1, wx.TOP+wx.RIGHT+wx.LEFT, 5
        )
        self.monitorButtons[name] = newButton
        self.Layout()

    def shorten(self, name):
        """Get shortened name for button label."""
        if len(name) > 8:
            return f"'{name[0:6]}...'"
        else:
            return name

    def getDeviceColour(self, kind):
        """Colour code device button."""
        if kind in self.devices.gate_types:
            return blue
        elif self.names.get_name_string(kind) == "CLOCK":
            return darkgreen
        elif self.names.get_name_string(kind) == "DTYPE":
            return darkred
        elif self.names.get_name_string(kind) == "SWITCH":
            return darkpink
        else:
            return white
