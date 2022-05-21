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

switches = ["SW1", "SW2", "SW3", "SW4", "SW5", "SW6", "SW7", "SW8", "SW9"]
outputs = ["SW1", "SW2", "SW3", "G1", "G2", "F1.Q", "F1.QBAR"]
current_monitors = ["SW1", "SW2", "SW3", "G1", "G2", "F1.Q", "F1.QBAR"]
file_name_title = "circuit"

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

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_command_line_input(self, event): Event handler for when the user enters a command.

    on_monitor_input(self, event): Event handler for when the user adds a monitor.
    """

    def __init__(self, title, path, names, devices, network, monitors):
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

        self.SetBackgroundColour(wx.Colour(252, 251, 241))

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Configure the widgets
        self.file_name = wx.StaticText(self, wx.ID_ANY, f"{file_name_title}")
        self.browse = wx.Button(self, wx.ID_ANY, "Browse")

        if len(switches) > 0:
            self.switches_text = wx.StaticText(self, wx.ID_ANY, "Switches (toggle on/off):")
        else:
            self.switches_text = wx.StaticText(self, wx.ID_ANY, "No switches in this circuit")

        self.switch_buttons = {}
        for i in range(len(switches)):
            self.switch_buttons[switches[i]]= [wx.Button(self, i, switches[i]), False]
            self.switch_buttons[switches[i]][0].SetBackgroundColour(wx.Colour(244, 204, 199))

        self.monitors_text = wx.StaticText(self, wx.ID_ANY, "Monitors:")
        self.monitor_input = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER)
        self.monitor_input.SetHint("Add new monitor")
        self.monitors_help = wx.StaticText(self, wx.ID_ANY, "Click signal to stop monitoring")
        self.mons = {}
        for curr in current_monitors:
            self.mons[curr] = wx.Button(self, wx.ID_ANY, curr)

        self.cycles_text = wx.StaticText(self, wx.ID_ANY, "Number of cycles:")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")
        self.command_line_input = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER, size=(350, -1))
        self.command_line_input.SetHint("Command line input")

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.browse.Bind(wx.EVT_BUTTON, self.on_browse)
        for switch in [pair[0] for pair in self.switch_buttons.values()]:
            switch.Bind(wx.EVT_BUTTON, self.on_switch_button)
        for sigName in self.mons.keys():
            self.mons[sigName].Bind(wx.EVT_BUTTON, self.on_monitor_button)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.command_line_input.Bind(wx.EVT_TEXT_ENTER, self.on_command_line_input)
        self.monitor_input.Bind(wx.EVT_TEXT_ENTER, self.on_monitor_input)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)
        file_name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        manual_settings_sizer = wx.BoxSizer(wx.VERTICAL)
        switch_buttons_sizer = wx.WrapSizer()
        monitors_sizer = wx.BoxSizer(wx.HORIZONTAL)
        monitor_buttons_sizer = wx.WrapSizer()
        command_line_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cycles_sizer = wx.BoxSizer(wx.HORIZONTAL)

        main_sizer.Add(side_sizer, 1, wx.ALL, 5)
        main_sizer.Add(self.canvas, 10, wx.EXPAND | wx.ALL, 5)

        side_sizer.Add(manual_settings_sizer, 1, wx.ALL, 5)
        side_sizer.Add(cycles_sizer, 1, wx.ALL, 5)
        side_sizer.Add(command_line_sizer, 1, wx.ALL, 5)

        manual_settings_sizer.Add(file_name_sizer, 1, wx.TOP, 10)

        file_name_sizer.Add(self.file_name, 1, wx.ALL, 5)
        file_name_sizer.Add(self.browse)

        manual_settings_sizer.Add(self.switches_text, 1, wx.ALL, 5)
        manual_settings_sizer.Add(switch_buttons_sizer,  1, wx.ALL, 5)

        for switch in [pair[0] for pair in self.switch_buttons.values()]:
            switch_buttons_sizer.Add(switch, 1, wx.TOP, 5)

        manual_settings_sizer.Add(monitors_sizer,  1, wx.ALL, 5)
        manual_settings_sizer.Add(self.monitors_help, 1, wx.ALL, 1)
        manual_settings_sizer.Add(monitor_buttons_sizer,  1, wx.ALL, 5)
        for mon in self.mons.values():
            monitor_buttons_sizer.Add(mon, 1, wx.TOP, 5)

        monitors_sizer.Add(self.monitors_text, 1, wx.TOP, 10)
        monitors_sizer.Add(self.monitor_input, 1, wx.ALL, 5)

        cycles_sizer.Add(self.cycles_text, 1, wx.TOP, 10)
        cycles_sizer.Add(self.spin, 1, wx.ALL, 5)
        cycles_sizer.Add(self.run_button, 1, wx.ALL, 5)
        cycles_sizer.Add(self.continue_button, 1, wx.ALL, 5)

        command_line_sizer.Add(self.command_line_input, 1, wx.BOTTOM, 5)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Priyanka Patel\n2022",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)
        if Id == wx.ID_HELP_COMMANDS:
            wx.MessageBox("Enter command line inputs beneath the signal display space.\n" \
                            "\nPossible commands:" \
                            "\n \nr N\nRun simulator for N cycles" \
                            "\n \nc N\n Continue running simulation for N cycles" \
                            "\n \ns X N\nset switch X to N (0 or 1)" \
                            "\n \nm X\n start monitoring output signal X" \
                            "\n \nz X\nstop monitoring X",
                            "User Guide", wx.ICON_INFORMATION | wx.OK)


    def on_browse(self, event):
        """Handle the event when user wants to find circuit definition file."""
        openFileDialog= wx.FileDialog(self, "Open txt file", "", "", wildcard="TXT files (*.txt)|*.txt", style=wx.FD_OPEN+wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
           return
        self.file_name.SetLabel(os.path.basename(os.path.splitext(openFileDialog.GetPath())[0]))
        

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        self.canvas.render(text)

    def on_switch_button(self, event):
        """Handle the event when the user clicks the run button."""
        button = event.GetEventObject()
        if self.switch_buttons[button.GetLabel()][1]:
            button.SetBackgroundColour(wx.Colour(244, 204, 199))
            self.switch_buttons[button.GetLabel()][1] = False
            status = "off"
        else:
            button.SetBackgroundColour(wx.Colour(208, 245, 206))
            self.switch_buttons[button.GetLabel()][1] = True
            status = "on"
        text = f"{button.GetLabel()} turned {status}."
        self.canvas.render(text)
    
    def on_monitor_button(self, event):
        """Handle the event when the user clicks the run button."""
        button = event.GetEventObject()
        text = f"Monitor {button.GetLabel()} destroyed."
        self.canvas.render(text)
        current_monitors.remove(button.GetLabel())
        button.Destroy()

    def on_continue_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Continue button pressed."
        self.canvas.render(text)

    def on_command_line_input(self, event):
        """Handle the event when the user enters command line text."""
        command = self.command_line_input.GetValue()
        text = "".join(["New command: ", command])
        self.canvas.render(text)

    def on_monitor_input(self, event):
        """Handle the event when the user adds a monitor."""
        monitor = self.monitor_input.GetValue().upper()
        text = "".join(["New monitor: ", monitor])
        self.canvas.render(text)
        if isValidMonitor(monitor):
            if isMonitoring(monitor):
                text = f"Already monitoring {monitor}"
            else:
                makeMonitor(monitor)    
                text = "".join(["New monitor: ", monitor])
        else:
            text = "Invalid monitor"
        self.canvas.render(text)

def makeMonitor(monitor):
    """Create a new monitoring point based on user selection."""
    current_monitors.append(monitor)

def isMonitoring(monitor):
    """Return True if suggested monitor point is already being monitored."""
    return monitor in current_monitors

def isValidMonitor(monitor):
    """Return True if suggested monitor point is a recognised output."""
    return monitor in outputs
