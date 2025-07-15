import customtkinter as ctk
from execution_algorithms import get_range, create_expression, create_vector
import math
from uuid import uuid4
DEF_HEIGHT = int(1080/2)
DEF_WIDTH = int(1920/2)


class Window(ctk.CTk):

    def __init__(self, width, height):
        super(Window, self).__init__()
        self.geometry(f"{width}x{height}")
        self.title("Graphing Calculator")
        self.window_init()

    def window_init(self):
        graphing_window = GraphingWindow(self, ExpressionFrame)
        graphing_window.pack(fill="both", expand=True)

        zoom_in_btn = ctk.CTkButton(self, text="zoom in", command=graphing_window.zoom_in)
        zoom_in_btn.place(relx=0, rely=0, relwidth=0.1, relheight=0.05)

        zoom_out_btn = ctk.CTkButton(self, text="zoom out", command=graphing_window.zoom_out)
        zoom_out_btn.place(relx=0, rely=0.06, relwidth=0.1, relheight=0.05)
        self.mainloop()


class GraphingWindow(ctk.CTkCanvas):
    graphing_window = None
    graphs = set()

    def __init__(self, parent, expression_frames):
        super(GraphingWindow, self).__init__(master=parent, bg="white")
        self.win_width = DEF_WIDTH   # width and height references for drawing the grid
        self.win_height = DEF_HEIGHT    # are set to default initially but get changed immediately to match the
        # screen dimensions due to the configure event

        self.start_x = None     # position of mouse cursor at start of drag click
        self.start_y = None

        self.expression_frames = expression_frames  # reference to the expression frame class

        self.bind("<Configure>", self.re_size)  # binding events
        self.bind("<B1-Motion>", self.shift_move)
        self.bind("<Button-1>", self.shift_start)

        self.resolution = 192   # default resolution (pixels per grid unit)
        self.displacement = self.get_displacement([0, 0], [-5, 5])  # default displacement
        GraphingWindow.graphing_window = self  # assigns the graphing window to a class variable, so it can be accessed
        # by the other parts of the program

    def get_displacement(self, window_point, plane_point):
        displacement = [plane_point[0] - 1/self.resolution * window_point[0], plane_point[1] + 1/self.resolution *
                        window_point[1]]    # uses a point that you know the window and plane version of and
        return displacement     # calculates a displacement vector

    def win_to_plane(self, window_point):
        plane_point = [self.displacement[0] + window_point[0]/self.resolution, self.displacement[1] -
                       window_point[1]/self.resolution]  # converts a window point into a plane point
        return plane_point

    def plane_to_win(self, plane_point):
        window_point = [self.resolution * (plane_point[0] - self.displacement[0]), self.resolution *
                        (self.displacement[1] - plane_point[1])]  # converts a plane point into a window point
        return window_point

    def plane_to_win_x(self, plane_x):
        return self.resolution * (plane_x - self.displacement[0])   # returns the x window coordinate of an x plane
        # coordinate

    def plane_to_win_y(self, plane_y):
        return self.resolution * (self.displacement[1] - plane_y)   # returns the y window coordinate of a y plane
    # coordinate

    def re_size(self, event):   # updates the width and height attributes of the plane for drawing the grid
        self.win_width = event.width    # resets height and width attributes
        self.win_height = event.height
        self.grid_init()    # redraws grid

    def shift_start(self, event):   # sets initial position of cursor at the start of a drag-click
        self.start_x = event.x
        self.start_y = event.y

    def shift_move(self, event):    # moves the plane when the user performs a drag-click
        dx = (event.x - self.start_x) / self.resolution  # gets change in x and change in y in plane coordinates
        dy = (event.y - self.start_y) / self.resolution

        self.displacement = [self.displacement[0] - dx, self.displacement[1] + dy]  # adds the change in the
        # displacement vector, since window coordinates have a flipped orientation dy needs to be added
        self.grid_init()    # redraws the grid

        self.start_x = event.x  # resets the initial cursor position
        self.start_y = event.y

    def grid_init(self):
        self.delete("grid_line")     # gets rid of any grid lines
        self.delete("plot")          # gets rid of all plotted graphs
        GraphingWindow.graphs = set()   # resets set of graphs on the plane

        top_left = self.win_to_plane([0, 0])    # gets the top left and bottom right corners in plane coords to get the
        bottom_right = self.win_to_plane([self.win_width, self.win_height])  # range for x/y

        x_start = top_left[0]
        y_start = bottom_right[1]

        x_end = bottom_right[0]
        y_end = top_left[1]

        # goes through visible integer x/y values in plane coords
        for i in range(math.ceil(x_start), math.floor(x_end) + 1):
            start = self.plane_to_win([i, 0])   # gets x coordinate in pixels for vertical lines
            self.create_line([start[0], 0], [start[0], self.win_height], tags="grid_line")  # tags needed to delete
                                                                                            # grid lines
        for j in range(math.ceil(y_start), math.floor(y_end) + 1):
            start = self.plane_to_win([0, j])   # gets y coordinate in pixels for horizontal lines
            self.create_line([0, start[1]], [self.win_width, start[1]], tags="grid_line")

        origin = self.plane_to_win([0, 0])      # converts origin to window coordinates
        self.create_line([origin[0], 0], [origin[0], self.win_height], tags="grid_line", width=3)
        self.create_line([0, origin[1]], [self.win_width, origin[1]], tags="grid_line", width=3)

        self.add_axes_numbers(x_start, x_end, y_start, y_end)   # labelling axes

        get_range([top_left, bottom_right])  # gets the range for the Expression classes

        self.expression_frames.plot_all()   # plots all expressions

    def zoom_in(self):

        center_window = [self.win_width / 2, self.win_height / 2]   # center will not change so they can be used
        center_plane = self.win_to_plane(center_window)             # to calculate the displacement vector

        self.resolution += 20   # increasing pixels per unit
        self.displacement = self.get_displacement(center_window, center_plane)  # recalculating displacement

        self.grid_init()    # redrawing the grid

    def zoom_out(self):
        if self.resolution-20 > 0:  # resolution cannot be 0
            center_window = [self.win_width / 2, self.win_height / 2]   # same as zoom_in
            center_plane = self.win_to_plane(center_window)

            self.resolution -= 20   # decreasing pixels per unit
            self.displacement = self.get_displacement(center_window, center_plane)  # recalculates displacement since
            # the center is invariant

            self.grid_init()    # redrawing the grid

    def add_axes_numbers(self, x_start, x_end, y_start, y_end):

        if 0 <= self.plane_to_win_y(0) <= self.win_height:  # checks if the x-axis is on the screen
            for i in range(math.ceil(x_start), math.floor(x_end) + 1):  # goes through integer x values
                pos = self.plane_to_win([i, 0])  # converts the plane coordinates of the position of the number
                # to window coordinates
                self.create_text(pos[0]-5, pos[1]+5, text=f"{i}", anchor="ne", tags="grid_line")
                # add number to pos with an offset to keep the numbers from touching the axes

        if 0 <= self.plane_to_win_x(0) <= self.win_width:   # checks if the y-axis is on the screen
            for j in range(math.ceil(y_start), math.floor(y_end) + 1):  # goes through integer y values
                pos = self.plane_to_win([0, j])  # converts the plane coordinates of the position of the number
                # to window coordinates
                self.create_text(pos[0]-5, pos[1]+5, text=f"{j}", anchor="ne", tags="grid_line")
                # add number to pos with an offset to keep the numbers from touching the axes


class ExpressionFrame(ctk.CTkFrame):
    expression_frames = {}  # lookup table for all expression frames
    current = None  # the selected expression frame

    def __init__(self, parent, p_id=None, text=""):
        super(ExpressionFrame, self).__init__(master=parent)
        self.textbox = None     # widgets
        self.indicator_label = None
        self.destroy_button = None
        self.hide_button = None

        # expression frame info
        if p_id is None:    # checks if existing ID has been entered
            self.id = str(uuid4())  # creates new ID
        else:
            self.id = p_id  # sets ID to existing ID
        self.status = None      # "visible", "hidden", "error"
        self.colour = None     # colour of graph
        self.text_variable = ctk.StringVar()    # string variable for text widget
        self.text_variable.set(text)    # sets the value of the string variable
        self.expression = None

        self.bind("<Button-1>", self.set_current)   # binds event to set the current frame
        self.expression_frame_init()

    def expression_frame_init(self):
        self.textbox_init()

        # creating and placing the indicator label
        self.indicator_label = ctk.CTkLabel(self, height=1, font=(None, 20), text="", bg_color="white")
        self.indicator_label.place(relx=0.025, rely=0.425, relwidth=0.1)
        self.indicator_label.bind("<Button-1>", self.set_current)   # binding click event to set the current frame

        self.destroy_button = ctk.CTkButton(self, text="X", command=self.destroy_frame)  # button to get rid of frame
        self.destroy_button.place(relx=0.95, rely=0.1, relwidth=0.1, anchor="ne")   # placing button

        self.hide_button = ctk.CTkButton(self, text="hide", command=self.hide_graph)    # button to hide frame
        self.hide_button.place(anchor="se", relx=0.95, rely=0.9)
        self.hide_button.bind("<Button-1>", self.set_current)

        self.set_current()  # makes the newest frame the current one
        self.__class__.expression_frames.update({self.id: self})  # adds this to the dictionary of frames for reference
        self.get_colour()   # gets the colour of the graph associated with the expression frame

        self.on_text_change()   # updates the state of the graphing window to show any already passed expressions or
        # put the frame in an error state due to there being no text entered

    def textbox_init(self):     # creates textbox, places it, and binds any events
        self.textbox = ctk.CTkEntry(self, height=1, font=(None, 20), textvariable=self.text_variable)
        self.textbox.place(relx=0.175, rely=0.412, relwidth=0.70)
        self.text_variable.trace_add("write", self.on_text_change)  # calls on_text_change when text is added
        self.textbox.bind("<Button-1>", self.set_current)

    def on_text_change(self, *args):
        self.expression = create_expression(self.textbox.get())    # creates the correct expression object based
        # on entered text
        self.validated_plot()   # plots the graph if valid

    def validated_plot(self):
        if self.id in GraphingWindow.graphs:    # checks if graph is on the canvas
            GraphingWindow.graphs.remove(self.id)   # removes it from set of graphs on the canvas
            GraphingWindow.graphing_window.delete(str(self.id))     # removes it from the plane

        if self.expression is False:    # checks if the expression is valid
            self.error()    # frame goes into error state if not valid
        else:
            self.indicator_label.configure(bg_color="white")  # plots graph on screen if expression is valid
            self.status = "visible"   # updates status to visible since graph will be plotted
            self.plot_expression()

    def plot_expression(self):
        try:    # draws the graph of the expression onto the screen
            self.expression.plot(GraphingWindow.graphing_window, self.id, self.colour)
        except TypeError:   # catches any invalid expressions that my own validation can't
            self.error()
        except SyntaxError:
            self.error()

    @classmethod
    def plot_all(cls):
        for expression_frame in cls.expression_frames.values():  # goes through all expression frames
            if expression_frame.status == "visible":    # checks for all expression frames have visible graphs
                expression_frame.plot_expression()

    def error(self):
        self.status = "error"   # sets the expression frame's state to error
        self.indicator_label.configure(bg_color="red")  # changes the indicator label to red to show user that the
        # expression is invalid

    def destroy_frame(self):
        self.__class__.expression_frames.pop(self.id)   # gets rid of the frame from the lookup table
        if self.id in GraphingWindow.graphs:  # checks if the frame's expression is on the plane
            GraphingWindow.graphs.remove(self.id)   # removes the expression from set of drawn graphs
            GraphingWindow.graphing_window.delete(str(self.id))   # removes the graph from the plane

        if self.id == self.__class__.current:   # checks if this frame is the current one
            self.__class__.current = None   # if it is then there are no selected graphs
        self.destroy()  # gets rid of frame

        expression_container = self.master  # resizes the expression section on the sidebar as needed
        expression_container.remove()

    def hide_graph(self):
        if self.status == "visible":    # checks if graph is visible
            self.status = "hidden"  # sets the graph to hidden
            GraphingWindow.graphing_window.delete(str(self.id))  # deletes the graph from the graphing plane
        elif self.status == "hidden":   # if graph is hidden
            self.on_text_change()       # the entered expression is validated then
            # the graph gets plotted and its status gets changed to visible

    def get_colour(self):
        colours = ["red", "blue", "purple", "green"]    # colours to cycle through
        self.colour = colours[len(self.__class__.expression_frames) % len(colours) - 1]  # assigns a colour to the
        # graph depending on how many expression frames there are

    def get_expression(self):   # for saving graphs
        return self.textbox.get()   # returns the entered text

    def set_current(self, event=None):
        self.__class__.current = self.id    # sets selected expression frame


class VectorExpressionFrame(ExpressionFrame):
    def __init__(self, parent, p_id=None, text="|"):   # vector expressions are stored as "x component | y component"
        self.text_variable_x = ctk.StringVar()  # variables for entry widgets
        self.text_variable_y = ctk.StringVar()
        vector = text.split(sep="|")    # creates an array of the vector's components [x, y]
        self.text_variable_x.set(vector[0])   # sets the inputted values for x/y to be the ones passed as parameters
        self.text_variable_y.set(vector[1])   # or empty by default

        # text widgets
        self.textbox_x = None   # current textbox being used will be self.textbox- this is the value accessed by
        self.textbox_y = None   # the keypad

        super(VectorExpressionFrame, self).__init__(parent, p_id, text)

    def textbox_init(self):
        # creates text widget for x component and binds events
        self.textbox_x = ctk.CTkEntry(self, height=1, font=(None, 20), textvariable=self.text_variable_x)
        self.textbox_x.place(relx=0.175, rely=0.312, relwidth=0.70)
        self.text_variable_x.trace_add("write", self.on_text_change)
        self.textbox_x.bind("<Button-1>", lambda event, arg=self.textbox_x: self.set_current_textbox(event, arg))
        # depending on the textbox clicked the current textbox will be different

        # creates text widget for y component and binds events
        self.textbox_y = ctk.CTkEntry(self, height=1, font=(None, 20), textvariable=self.text_variable_y)
        self.textbox_y.place(relx=0.175, rely=0.512, relwidth=0.70)
        self.text_variable_y.trace_add("write", self.on_text_change)
        self.textbox_y.bind("<Button-1>", lambda event, arg=self.textbox_y: self.set_current_textbox(event, arg))

        self.textbox = self.textbox_x

    def set_current_textbox(self, event, textbox):
        self.__class__.current = self.id  # makes this frame the current one
        self.textbox = textbox  # makes the selected textbox the current one

    def on_text_change(self, *args):
        x = self.textbox_x.get()    # gets inputted x and y components
        y = self.textbox_y.get()
        self.expression = create_vector(x, y)   # creates vector object
        self.validated_plot()   # validates and plots the vector field

    def get_expression(self):
        return self.textbox_x.get() + "|" + self.textbox_y.get()  # combines x/y components for saving the expression


if __name__ == "__main__":
    win = Window(DEF_WIDTH, DEF_HEIGHT)
