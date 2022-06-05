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
import wx.lib.agw.gradientbutton as gb
import wx.lib.dialogs as dlgs
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
from gui_utils.gui_utils import *


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

        # Initialise for signal display
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

    def render(self, text, clearAll=False):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        top = 975
        self.render_text(text, 10, top)

        # Draw signal traces
        if not clearAll:
            low = 5
            high = 25
            signalData = self.monitors.display_signals_gui(high=high, low=low)
            axis = top-45
            for monitor in signalData.keys():
                desc, X, Y, device_kind = signalData[monitor]
                if len(X) > 0:
                    margin = len(desc)*10
                    Y = [axis+y for y in Y]
                    X = [x+margin+10 for x in X]
                    rgb = self._trace_colour(device_kind)
                    self.render_text(desc, X[0]-margin, axis+12)
                    self._draw_trace(X, Y, axis, rgb)
                    axis -= 100

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def _draw_trace(self, X, Y, axis, rgb):
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

        # Draw x axis with ticks
        GL.glColor3f(0, 0, 0)  # x axis is black
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(len(X)):
            GL.glVertex2f(X[i], axis)
            GL.glVertex2f(X[i], axis-3)
            GL.glVertex2f(X[i], axis)
        GL.glEnd()

        # x axis numbers
        t = 0
        while t < len(X):
            self.render_text(str(int(t/2)), X[t], axis-14)
            t += 4

    def _trace_colour(self, device_kind):
        """Colour code trace based on device kind."""
        gate_strings = ["AND", "NOT", "OR", "NAND", "NOR", "XOR"]
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

        text = _("Welcome to the Logic Simulator! ") + \
            _("See User Guide for help.")
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
        self, text, x_pos, y_pos, font=GLUT.GLUT_BITMAP_HELVETICA_18
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

    on_browse(self, event): Event handler for browse button.

    on_delete_connection(self, event): Event handler for deleting a connection.

    on_spin_cycles(self, event): Handle event when user changes cycles.

    on_enter_device_button(self, event): Prevents colour change on hover of
                                device.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_continue_button(self, event): Event handler for when the user clicks the
                                continue button.

    on_clear_button(self, event): Event handler for when the user clicks the
                                Clear Canvas button.

    on_switch_button(self, event): Event handler for when the user clicks a
                                switch button.

    on_monitor_button(self, event): Event handler for when the user clicks a
                                monitor button.

    on_clear_all_monitors_button(self, event): Event handler for when the user
                                clears all monitors.

    on_monitor_input(self, event): Handle event when user adds a monitor.

    on_command_line_input(self, event): Handle user commands.

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

        """Initialise utils."""
        self.click = wx.Cursor(wx.Image("gui_utils/smallclick.png"))
        self.standard_button_size = wx.Size(85, 36)

        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu
        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        guideMenu = wx.Menu()
        fileMenu.Append(wx.ID_OPEN, "&" + _("Open"))
        fileMenu.Append(wx.ID_ABOUT, "&" + _("About"))
        fileMenu.Append(wx.ID_EXIT, "&" + _("Exit"))
        guideMenu.Append(wx.ID_HELP_COMMANDS, "&" + _("Command Line Guide"))
        guideMenu.Append(wx.ID_CONTEXT_HELP, "&" + _("Canvas Controls"))
        guideMenu.Append(wx.ID_HELP_PROCEDURES, "&" + _("Sidebar Guide"))
        menuBar.Append(fileMenu, "&" + _("File"))
        menuBar.Append(guideMenu, "&" + _("User Guide"))
        self.SetMenuBar(menuBar)

        # Set background colour for GUI
        self.SetBackgroundColour(paleyellow)

        # Set fonts
        fileFont = wx.Font(wx.FontInfo(18).FaceName("Mono").Bold())
        genBtnFont = wx.Font(wx.FontInfo(10).FaceName("Mono").Bold())
        helpFont = wx.Font(wx.FontInfo(10).FaceName("Mono"))
        self.subHeadingFont = wx.Font(wx.FontInfo(12).FaceName("Mono"))
        inputBoxFont = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL)
        go_font = wx.Font(wx.FontInfo(14).FaceName("Rockwell"))
        self.delete_font = wx.Font(wx.FontInfo(10).FaceName("Rockwell"))
        self.errorBoxFont = wx.Font(wx.FontInfo(10).FaceName("Consolas"))

        # Canvas for drawing signals
        self.scrollable = wx.ScrolledCanvas(self, wx.ID_ANY)
        self.scrollable.SetScrollbars(20, 20, 15, 10)
        self.canvas = MyGLCanvas(
            self.scrollable, wx.Size(1500, 1000), devices, monitors, names
        )

        # Configure the widgets
        self.file_name = wx.StaticText(
            self, wx.ID_ANY, f"", size=wx.Size(350, 30)
        )
        self.file_name.SetFont(fileFont)
        self.browse = wx.Button(self, wx.ID_ANY, _("Browse"))
        self.browse.SetFont(genBtnFont)
        self.browse.SetCursor(self.click)

        self.switches_text = wx.StaticText(self, wx.ID_ANY, "")
        self.switches_text.SetFont(self.subHeadingFont)
        self.switch_buttons = {}

        self.devices_heading = wx.StaticText(self, wx.ID_ANY, _("Devices:"))
        self.devices_heading.SetFont(self.subHeadingFont)

        self.device_buttons = []

        self.monitors_text = wx.StaticText(self, wx.ID_ANY, _("Monitors:"))
        self.monitors_text.SetFont(self.subHeadingFont)
        self.monitor_input = wx.TextCtrl(
            self,
            wx.ID_ANY,
            "",
            style=wx.TE_PROCESS_ENTER,
            size=wx.Size(175, 25)
        )
        self.monitor_input.SetHint(_("Add new monitor"))
        self.monitor_input.SetFont(inputBoxFont)
        self.monitors_help_text = wx.StaticText(
            self, wx.ID_ANY, _("(click to remove)")
        )
        self.monitors_help_text.SetFont(helpFont)
        self.clear_all_monitors = wx.Button(self, wx.ID_ANY, _("Clear All"))
        self.clear_all_monitors.SetCursor(self.click)
        self.clear_all_monitors.SetFont(genBtnFont)
        self.monitor_buttons = {}

        self.cycles_text = wx.StaticText(self, wx.ID_ANY, _(" Cycles: "))
        self.cycles_text.SetFont(self.subHeadingFont)
        self.spin_cycles = wx.SpinCtrl(self, wx.ID_ANY, "10")

        self.run_button = gb.GradientButton(self, wx.ID_ANY, label=_("Run"))
        self.run_button.SetCursor(self.click)
        self.run_button.SetFont(wx.Font(go_font))
        self._change_button_colours(self.run_button, darkgreen, midgreen)

        self.continue_button = gb.GradientButton(
            self,
            wx.ID_ANY,
            label=_("Continue")
        )
        self.continue_button.SetFont(wx.Font(go_font))
        self._change_button_colours(
            self.continue_button,
            darkpurple,
            lightpurple
        )
        self.continue_button.SetCursor(self.click)

        self.clear_button = gb.GradientButton(
            self,
            wx.ID_ANY,
            label=_("Clear Canvas")
        )
        self.clear_button.SetCursor(self.click)
        self.clear_button.SetFont(wx.Font(go_font))

        self.command_line_input = wx.TextCtrl(
            self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER, size=(450, 25)
        )
        self.command_line_input.SetHint(
            _("Command line input. See User Guide for help.")
        )
        self.command_line_input.SetFont(inputBoxFont)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.browse.Bind(wx.EVT_BUTTON, self.on_browse)
        self.spin_cycles.Bind(wx.EVT_SPINCTRL, self.on_spin_cycles)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear_button)
        self.monitor_input.Bind(wx.EVT_TEXT_ENTER, self.on_monitor_input)
        self.command_line_input.Bind(
            wx.EVT_TEXT_ENTER,
            self.on_command_line_input
        )
        self.clear_all_monitors.Bind(
            wx.EVT_BUTTON, self.on_clear_all_monitors_button
        )

        # Configure sizers for overall layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.side_sizer = wx.BoxSizer(wx.VERTICAL)

        # Sizers and windows to be contained within side sizer
        self.file_name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.manual_settings_sizer = wx.BoxSizer(wx.VERTICAL)
        self.devices_sizer = wx.FlexGridSizer(4)
        self.devices_window = wx.ScrolledWindow(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.Size(420, 60),
            wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL,
            name="devices"
        )
        self.devices_window.SetSizer(self.devices_sizer)
        self.devices_window.SetScrollRate(10, 10)
        self.devices_window.SetAutoLayout(True)

        self.switch_buttons_sizer = wx.FlexGridSizer(4)
        self.switches_window = wx.ScrolledWindow(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.Size(420, 60),
            wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL,
            name="switches"
        )
        self.switches_window.SetSizer(self.switch_buttons_sizer)
        self.switches_window.SetScrollRate(10, 10)
        self.switches_window.SetAutoLayout(True)

        self.monitor_buttons_sizer = wx.FlexGridSizer(4)
        self.monitors_window = wx.ScrolledWindow(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.Size(420, 60),
            wx.SUNKEN_BORDER | wx.HSCROLL | wx.VSCROLL,
            name="monitors"
        )
        self.monitors_window.SetSizer(self.monitor_buttons_sizer)
        self.monitors_window.SetScrollRate(10, 10)
        self.monitors_window.SetAutoLayout(True)

        self.devices_heading_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.monitors_help_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cycles_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.command_line_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add side sizer and canvas to main sizer
        main_sizer.Add(self.side_sizer, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.scrollable, 10, wx.EXPAND | wx.ALL, 5)

        # Add sizers to side_sizer
        self.side_sizer.Add(self.file_name_sizer, 0, wx.ALL, 5)
        self.side_sizer.Add(self.manual_settings_sizer, 1, wx.ALL, 5)
        self.side_sizer.Add(self.cycles_sizer, 0, wx.ALL, 5)
        self.side_sizer.Add(self.command_line_sizer, 0, wx.ALL, 5)

        # add widgets to smaller sizers
        self.file_name_sizer.Add(self.file_name, 0, wx.ALIGN_CENTER, 5)
        self.file_name_sizer.AddStretchSpacer()
        self.file_name_sizer.Add(self.browse, 0, wx.ALIGN_CENTER, 5)

        self.devices_heading_sizer.Add(
            self.devices_heading,
            0,
            wx.ALIGN_CENTER,
            5
        )
        self.devices_heading_sizer.AddStretchSpacer()

        self.monitors_help_sizer.Add(self.monitors_text, 0, wx.ALIGN_CENTER, 5)
        self.monitors_help_sizer.Add(self.monitor_input, 0, wx.ALL, 5)

        self.monitors_help_sizer.Add(
            self.clear_all_monitors,
            1,
            wx.ALIGN_CENTER,
            5
        )
        self.monitors_help_sizer.Add(
            self.monitors_help_text, 0, wx.ALIGN_CENTER, 5
        )

        self.cycles_sizer.Add(self.cycles_text, 0, wx.ALIGN_CENTER, 5)
        self.cycles_sizer.Add(self.spin_cycles, 0, wx.ALIGN_CENTER, 5)
        self.cycles_sizer.AddStretchSpacer()
        self.cycles_sizer.Add(self.run_button, 0, wx.ALL, 5)
        self.cycles_sizer.Add(self.continue_button, 0, wx.ALL, 5)
        self.cycles_sizer.Add(self.clear_button, 0, wx.ALL, 5)

        self.command_line_sizer.Add(self.command_line_input, 1, wx.ALL, 5)

        self.manual_settings_sizer.Add(
            self.devices_heading_sizer,
            0,
            wx.ALL,
            5
        )
        self.manual_settings_sizer.Add(
            self.devices_window,
            1,
            wx.EXPAND | wx.ALL,
            5
        )
        self.manual_settings_sizer.Add(self.switches_text, 0, wx.ALL, 5)
        self.manual_settings_sizer.Add(
            self.switches_window,
            1,
            wx.EXPAND | wx.ALL,
            5
        )
        self.manual_settings_sizer.Add(self.monitors_help_sizer, 0, wx.ALL, 5)
        self.manual_settings_sizer.Add(
            self.monitors_window,
            1,
            wx.EXPAND | wx.ALL,
            5
        )

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)
        self.Layout()

        self.path = path

        # If path is None, prompt user to choose a valid file
        if self.path is None:
            self._choose_file(first=True)
            success = True

        # Parse file given from command line
        else:
            scanner = Scanner(path, names)
            parser = Parser(names, devices, network, monitors, scanner)
            success = parser.parse_network()
            if success:
                self._update_new_circuit(first=True)

        if not success:
            # Display errors from file given from command line
            self._display_errors(parser.error_message_list, first=True)
            self._choose_file(first=True)
            success = True

    def _choose_file(self, first=False):
        """Allow user to find circuit definition file."""
        openFileDialog = wx.FileDialog(
            self, _("Open"), "", "",
            wildcard="TXT files (*.txt)|*.txt",
            style=wx.FD_OPEN+wx.FD_FILE_MUST_EXIST
        )
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            if not first:
                return
            else:
                # if this is the first time, exit GUI
                wx.MessageBox(
                    _("No file selected. Exiting GUI."),
                    _("Exiting GUI"),
                    wx.ICON_INFORMATION | wx.OK
                )
                self.Close(True)

        self.path = openFileDialog.GetPath()
        names = Names()
        devices = Devices(names)
        network = Network(names, devices)
        monitors = Monitors(names, devices, network)
        scanner = Scanner(self.path, names)
        parser = Parser(names, devices, network, monitors, scanner)
        success = parser.parse_network()
        if success:
            self.names = names
            self.devices = devices
            self.network = network
            self.monitors = monitors
            self._update_new_circuit(first)
        else:
            self._display_errors(parser.error_message_list, first)
            if first:
                self._choose_file(first)

        self.Layout()

    def _display_errors(self, error_message_list, first=False):
        """Display errors in dialog box."""
        errors = ""
        for error in error_message_list:
            errors += f"\n{error}"
        if first:
            message = f"{errors} \n \n{self.first_parse_error_string()}"
        else:
            message = f"{errors} \n \n{self.parse_error_string()}"
        errorBox = dlgs.ScrolledMessageDialog(
            self,
            message,
            error_message_list[-1],
            style=wx.DEFAULT_DIALOG_STYLE+wx.RESIZE_BORDER,
            size=wx.Size(750, 500)
        )
        text = errorBox.GetChildren()[0]
        text.SetFont(self.errorBoxFont)
        errorBox.ShowModal()

    def _update_new_circuit(self, first=False):
        """Configure widgets for new circuit and bind events."""
        self._set_file_title(self.path)
        self.cycles_completed = 0
        self._update_current_connections(first)

        # find new switches
        switches = self.devices.find_devices(self.names.query("SWITCH"))
        if len(switches) > 0:
            self.switches_text.SetLabel(_("Switches (toggle on/off):"))
        else:
            self.switches_text.SetLabel(_("No switches in this circuit."))

        if not first:
            # destroy current switch buttons
            for switch in [pair[0] for pair in self.switch_buttons.values()]:
                switch.Destroy()

            # destroy current device list in sidebars
            for button in self.device_buttons:
                button.Destroy()

            # destroy current monitor buttons
            for monitor in self.monitor_buttons.values():
                monitor.Destroy()

        # add new switches
        self.switch_buttons = {}
        for s in switches:
            name = self.names.get_name_string(s)
            state = self.devices.get_device(s).switch_state
            shortName = self._shorten(name)
            button = gb.GradientButton(
                self.switches_window,
                s,
                label=shortName,
                size=self.standard_button_size
            )
            button.SetToolTip(name)
            button.SetCursor(self.click)
            if state == 0:
                self._change_button_colours(button, darkred, red)
            else:
                self._change_button_colours(button, blue, lightblue)
            self.switch_buttons[name] = [button, state]

        # bind switch buttons to event
        for switch in [pair[0] for pair in self.switch_buttons.values()]:
            switch.Bind(wx.EVT_BUTTON, self.on_switch_button)

        # add switches to sizer
        for switch in [pair[0] for pair in self.switch_buttons.values()]:
            self.switch_buttons_sizer.Add(
                switch, 1, wx.ALL, 9
            )

        # find new devices
        self.device_descs = []
        for gate_type in self.devices.gate_types:
            gates = self.devices.find_devices(gate_type)
            for gateId in gates:
                gate = self.devices.get_device(gateId)
                label = self._shorten(
                    self.names.get_name_string(gate.device_id)
                )
                extra = f": {str(len(gate.inputs.keys()))} " + _("inputs")
                self.device_descs.append([gateId, label, extra])

        for dev_type in self.devices.device_types:
            other_devices = self.devices.find_devices(dev_type)
            for id in other_devices:
                d = self.devices.get_device(id)
                label = self._shorten(self.names.get_name_string(d.device_id))
                kind = self.names.get_name_string(d.device_kind)
                extra = ""
                if kind == "CLOCK":
                    extra = ": " + _("half-period") + f" {d.clock_half_period}"
                self.device_descs.append([id, label, extra])

        # add new devices to displayed list
        self.device_buttons = []
        for d in self.device_descs:
            [id, label, extra] = d
            device_button = gb.GradientButton(
                self.devices_window,
                id,
                label=self._shorten(f"{label}{extra}"),
                size=self.standard_button_size
            )
            c = wx.Cursor(wx.Image('gui_utils/smallinfo.png'))
            device_button.SetCursor(c)
            kindId = self.devices.get_device(id).device_kind
            kindLabel = self.names.get_name_string(kindId)
            device_button.SetToolTip(f"{label}, {kindLabel}{extra}")
            device_button.SetTopStartColour(self._get_device_colour(kindId)[0])
            device_button.SetBottomEndColour(
                self._get_device_colour(kindId)[0]
            )
            device_button.Bind(
                wx.EVT_ENTER_WINDOW,
                self.on_enter_device_button
            )

            self.device_buttons.append(device_button)

        # add new device list to sizer
        for device in self.device_buttons:
            self.devices_sizer.Add(device, 1, wx.ALL, 9)

        # add new monitor buttons
        self.monitor_buttons = {}
        self.current_monitors = self.monitors.get_signal_names()[0]
        for curr in self.current_monitors:
            currId = self.names.lookup([curr])[0]
            button = gb.GradientButton(
                self.monitors_window,
                currId,
                label=curr,
                size=self.standard_button_size
            )
            self._change_button_colours(button, blue, lightblue)
            button.SetCursor(self.click)
            self.monitor_buttons[curr] = button

        # bind monitor buttons to event
        for name in self.monitor_buttons.keys():
            self.monitor_buttons[name].Bind(
                wx.EVT_BUTTON, self.on_monitor_button
            )

        # add new monitor buttons to sizer
        for mon in self.monitor_buttons.values():
            self.monitor_buttons_sizer.Add(mon, 1, wx.ALL, 9)

        text = _("New circuit loaded.")

        self.canvas.monitors = self.monitors
        self.canvas.devices = self.devices
        self.canvas.names = self.names

        if not first:
            self.canvas.render(text)
        self.Layout()

    def _update_current_connections(self, first=False):
        """Update current connections after user changes."""
        # If this is not the first time a circuit is loaded,
        # must destroy the existing widgets for connections
        if not first:
            self.connections_spinner.Destroy()
            self.delete_connection.Destroy()

        self.connections = {}
        for device in self.devices.devices_list:
            device_id = device.device_id
            for input in device.inputs.keys():
                self.connections[(device_id, input)] = device.inputs[input]
        self.connections_info = []
        for input, output in self.connections.items():
            inputName = self._get_signal_name(input[0], input[1])
            outputName = self._get_signal_name(output[0], output[1])
            self.connections_info.append([
                _("from") + f" {outputName} " + _("to") + f" {inputName}",
                input,
                output
            ])

        self.connections_spinner = wx.Choice(
            self,
            wx.ID_ANY,
            choices=[cnxn[0] for cnxn in self.connections_info],
            name=_("Current Connections")
        )
        self.connections_spinner.SetSelection(0)

        self.delete_connection = gb.GradientButton(
            self,
            wx.ID_ANY,
            label=_("Delete Connection")
        )

        self.delete_connection.SetCursor(self.click)
        self.delete_connection.SetFont(wx.Font(self.delete_font))

        self.devices_heading_sizer.Add(
            self.connections_spinner, 0, wx.ALL, 5
        )
        self.devices_heading_sizer.Add(
            self.delete_connection,
            1,
            wx.ALIGN_CENTER,
            5
        )
        self.delete_connection.Bind(wx.EVT_BUTTON, self.on_delete_connection)
        self.Layout()

    def _set_file_title(self, path):
        """Display name of open file at top of screen."""
        label = os.path.basename(os.path.splitext(path)[0])
        if len(label) > 20:
            label = f"\"{label[0:17]}...\""
        self.file_name.SetLabel(label)
        self.Layout()

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox(
                _("Logic Simulator") + "\n" + _("Created by")
                + " Priyanka Patel (霹雳阳科), Tommy Rochussen "
                "(托米), Jessye Tu (涂净兮)\n2022",
                _("About Logsim"),
                wx.ICON_INFORMATION | wx.OK
            )
        if Id == wx.ID_OPEN:
            self._choose_file()
        if Id == wx.ID_HELP_COMMANDS:
            wx.MessageBox(
                self.help_string(),
                _("Command Line Guide"),
                wx.ICON_INFORMATION | wx.OK
            )
        if Id == wx.ID_CONTEXT_HELP:
            wx.MessageBox(
                self.canvas_controls_string(),
                _("Canvas Controls"),
                wx.ICON_INFORMATION | wx.OK
            )

        if Id == wx.ID_HELP_PROCEDURES:
            wx.MessageBox(
                self.sidebar_guide_string(),
                _("Sidebar Guide"),
                wx.ICON_INFORMATION | wx.OK
            )

    def on_browse(self, event):
        """Handle event when user clicks browse button."""
        self._choose_file()

    def on_delete_connection(self, event):
        """Handle event when user presses delete connection."""
        connectionIndex = self.connections_spinner.GetSelection()
        [inputIds, outputIds] = self.connections_info[connectionIndex][1:3]
        input_device_id = inputIds[0]
        input_port_id = inputIds[1]

        int = GuiCommandInterface(
            "",
            self.names,
            self.devices,
            self.network,
            self.monitors
        )
        int.delete_connection(
            input_device_id,
            input_port_id,
        )

        allOutputNames = []
        allOutputIds = []

        for i in [(d.device_id, d.outputs) for d in self.devices.devices_list]:
            for output in i[1]:
                allOutputIds.append((i[0], output))
                allOutputNames.append(self._get_signal_name(i[0], output))

        newConnection = wx.SingleChoiceDialog(
            self,
            _("Choose a new output to connect input ") +
            f"{self.getSignalName(input_device_id, input_port_id)}",
            _("Replace Connection"),
            allOutputNames,
            style=wx.CHOICEDLG_STYLE
        )
        newConnection.SetBackgroundColour(paleyellow)

        while newConnection.ShowModal() == wx.ID_CANCEL:
            wx.MessageBox(
                _("You must select a new connection for this input."),
                _("Error - Connection Needed"),
                wx.ICON_ERROR
            )

        if newConnection.ShowModal() == wx.ID_OK:
            choice = newConnection.GetSelection()
            (dev, port) = allOutputIds[choice]
            int = GuiCommandInterface(
                "",
                self.names,
                self.devices,
                self.network,
                self.monitors
            )
            text, success = int.make_connection(
                input_device_id,
                input_port_id,
                dev,
                port
            )
            self.canvas.render(text)
            if success:
                newConnection.Destroy()
                self._update_current_connections()

    def on_spin_cycles(self, event):
        """Handle the event when the user changes the number of cycles."""
        self.cycles_to_run = self.spin_cycles.GetValue()
        text = "".join([_("Number of cycles: "), str(self.cycles_to_run)])
        self.canvas.render(text)

    def on_enter_device_button(self, event):
        """Stop colour change when user hovers over device button."""
        btn = event.GetEventObject()
        deviceKindId = self.devices.get_device(btn.GetId()).device_kind
        btn.SetTopStartColour(self._get_device_colour(deviceKindId)[0])
        btn.SetBottomEndColour(self._get_device_colour(deviceKindId)[0])
        self.Layout()

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

    def on_clear_button(self, event):
        """Handle the event when the user clicks Clear Canvas."""
        int = GuiCommandInterface(
            f"0",
            self.names,
            self.devices,
            self.network,
            self.monitors
        )
        text, cycles = int.run_command()
        self.cycles_completed = cycles
        self.canvas.render(text)
        text = _("Canvas cleared. Press run to start simulation again.")
        self.canvas.render(text, clearAll=True)

    def on_switch_button(self, event):
        """Handle the event when the user clicks a switch button."""
        button = event.GetEventObject()
        switchId = button.GetId()
        switchName = self.names.get_name_string(switchId)

        if self.switch_buttons[switchName][1] == 1:
            self._change_button_colours(button, darkred, red)
            self.switch_buttons[switchName][1] = 0
        else:
            self._change_button_colours(button, blue, lightblue)
            self.switch_buttons[switchName][1] = 1
        newStatus = self.switch_buttons[switchName][1]
        self.devices.set_switch(switchId, newStatus)

        text = f"{switchName} " + _("turned") + " {newStatus}."
        self.canvas.render(text)

    def on_monitor_button(self, event):
        """Handle the event when the user clicks a monitor button."""
        button = event.GetEventObject()
        monitorName = self.names.get_name_string(button.GetId())
        text = self._destroy_monitor(monitorName)
        self.monitor_buttons.pop(monitorName)
        self.canvas.render(text)
        button.Destroy()
        self.Layout()

    def on_clear_all_monitors_button(self, event):
        """Handle the event when the user clears all monitors."""
        for button in self.monitor_buttons.values():
            button.Destroy()
        for monitorName in self.monitors._get_signal_names()[0]:
            commandint = GuiCommandInterface(
                monitorName,
                self.names,
                self.devices,
                self.network,
                self.monitors
            )
            [deviceId, portId] = commandint.read_signal_name()
            self.monitors.remove_monitor(deviceId, portId)
            self.monitor_buttons.pop(monitorName, "")
        self.canvas.render(_("All monitors destroyed."))
        self.Layout()

    def on_monitor_input(self, event):
        """Handle the event when the user adds a monitor."""
        name = self.monitor_input.GetValue()
        if self._is_valid_monitor(name):
            if self._is_monitoring(name):
                text = _("Already monitoring") + " {name}"
            else:
                text = self._make_monitor(name)
                self._add_monitor_button(name)
        else:
            text = _("Invalid monitor")
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
                self._on_command_line_set_switch(extraInfo)
            elif command == "m":
                # extraInfo = monitors, [device_id, port_id]
                self._on_command_line_add_monitor(
                    extraInfo[1][0], extraInfo[1][1]
                )
            elif command == "z":
                # extraInfo = monitors, [device_id, port_id]
                self._on_command_line_zap_monitor(
                    extraInfo[1][0], extraInfo[1][1]
                )
            elif command == "r":
                self._on_command_line_run(extraInfo)  # extraInfo = cycles
            elif command == "c":
                self._on_command_line_cont(extraInfo)  # extraInfo = cycles

        self.canvas.render(text)

    def _on_command_line_run(self, cycles):
        """Handle signal display when run command issued via command line."""
        self.cycles_completed = cycles

    def _on_command_line_cont(self, cycles):
        """Handle signal display when run command issued via command line."""
        self.cycles_completed += cycles

    def _on_command_line_set_switch(self, switch):
        """Change colour of switch button based on command line input."""
        switchName = self.names.get_name_string(switch[0])
        status = switch[1]
        button = self.switch_buttons[switchName][0]
        self.switch_buttons[switchName][1] = status

        if status == 0:
            self._change_button_colours(button, darkred, red)
        else:
            self._change_button_colours(button, blue, lightblue)
        self.Layout()

    def _on_command_line_add_monitor(self, deviceId, portId):
        """Add monitor button based on command line input."""
        monitorName = self._get_signal_name(deviceId, portId)
        if monitorName not in self.monitor_buttons.keys():
            self._add_monitor_button(monitorName)

    def _on_command_line_zap_monitor(self, deviceId, portId):
        """Destroy monitor button based on command line input."""
        monitorName = self._get_signal_name(deviceId, portId)
        button = self.monitor_buttons[monitorName]
        button.Destroy()
        self.monitor_buttons.pop(monitorName)
        self.Layout()

    def _get_signal_name(self, deviceId, portId):
        """Get name of monitor from device id and port id."""
        deviceName = self.names.get_name_string(deviceId)
        if portId is None:
            monitorName = deviceName
        else:
            portName = self.names.get_name_string(portId)
            monitorName = f"{deviceName}.{portName}"
        return monitorName

    def _make_monitor(self, monitorName):
        """Create a new monitoring point based on user selection."""
        commandint = GuiCommandInterface(
            monitorName,
            self.names,
            self.devices,
            self.network,
            self.monitors,
            complete=self.cycles_completed
        )
        text, [self.monitors, monitor] = commandint.monitor_command()
        self.canvas.render(text)
        return text

    def _destroy_monitor(self, monitorName):
        """Destroy monitor."""
        commandint = GuiCommandInterface(
            monitorName, self.names, self.devices, self.network, self.monitors
        )
        text, [self.monitors, monitor] = commandint.zap_command()
        self.canvas.render(text)
        return text

    def _is_monitoring(self, monitor):
        """Return True if monitor point is already being monitored."""
        return monitor in self.monitors.get_signal_names()[0]

    def _is_valid_monitor(self, monitor):
        """Return True if suggested monitor point is a recognised output."""
        signalNames = self.monitors.get_signal_names()
        return monitor in signalNames[0] or monitor in signalNames[1]

    def _add_monitor_button(self, name):
        """Add monitor button when monitor successfully created."""
        shortName = self._shorten(name)
        id = self.names.lookup([name])[0]
        newButton = gb.GradientButton(
            self.monitors_window,
            id,
            label=shortName,
            size=self.standard_button_size
        )
        self._change_button_colours(newButton, blue, lightblue)
        newButton.Bind(wx.EVT_BUTTON, self.on_monitor_button)
        newButton.SetToolTip(name)
        newButton.SetCursor(self.click)
        self.monitor_buttons_sizer.Add(
            newButton, 1, wx.ALL, 9
        )

        self.monitor_buttons[name] = newButton
        self.Layout()

    def _shorten(self, name):
        """Get shortened name for button label."""
        if len(name) > 8:
            return f"'{name[0:5]}...'"
        else:
            return name

    def _get_device_colour(self, kind):
        """Colour code device button."""
        if kind in self.devices.gate_types:
            return [blue, lightblue]
        elif self.names.get_name_string(kind) == "CLOCK":
            return [darkgreen, midgreen]
        elif self.names.get_name_string(kind) == "DTYPE":
            return [darkred, red]
        elif self.names.get_name_string(kind) == "SWITCH":
            return [darkpink, lightpink]
        else:
            return white

    def _change_button_colours(self, button, outer, inner):
        button.SetTopStartColour(outer)
        button.SetTopEndColour(inner)
        button.SetBottomStartColour(inner)
        button.SetBottomEndColour(outer)

    def help_string(self):
        return _("Enter command line inputs in the bottom left of") \
                    + _(" the interface.") + "\n" \
                    "\n" + _("Possible commands:") + \
                    "\n \nr N\n" + _("Run simulator for N cycles") \
                    + "\n \nc N\n" + _("Continue running simulation")\
                    + _(" for N cycles") + \
                    "\n \ns X N\n" + _("Set switch X to N (0 or 1)") +\
                    "\n \nm X\n" + _("Start monitoring output signal X")\
                    + "\n \nz X\n" + _("Stop monitoring X")

    def canvas_controls_string(self):
        return _("Signals on the canvas can be manipulated to") \
                    + _(" better view them.") + "\n" \
                    "\n" + _("Scroll in to zoom in") + \
                    "\n \n" + \
                    _("Scroll out to zoom out - this may ") \
                    + _("be useful if you have many monitors") \
                    + "\n \n" \
                    + _("Click and hold to drag the signals ")\
                    + _("around the space")

    def sidebar_guide_string(self):
        return _("The sidebar can be used to adjust simulation ") \
                    + _("settings") + ".\n\n" + \
                    _("Click 'Browse' to load a new circuit file.") \
                    + "\n \n" + \
                    _("See the list of devices to decide what you ") \
                    + _("want to monitor. Hover on a device to see ") \
                    + _("its full name, kind and qualifier information.") \
                    + "\n \n" +\
                    _("To remove a connection before or during a ") \
                    + _("simulation, choose from the dropdown list ") \
                    + _("next to 'Devices' and click 'Delete Connection.") \
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
                    + _("simulation.")\


    def parse_error_string(self):
        return _("Unable to load file. Old file will remain loaded.")

    def first_parse_error_string(self):
        return _("Unable to load file. Please choose valid file.")
