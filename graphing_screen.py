import customtkinter as ctk
from datetime import date
from uuid import uuid4
from graphing_window import GraphingWindow, ExpressionFrame, VectorExpressionFrame
from keypad import Keypad
from custom_widgets import Toolbar, FullScreenMenu, MenuBtn, DynamicScrollFrame
import database_functions


DEF_HEIGHT = int(1080*0.7)
DEF_WIDTH = int(1920*0.7)


class Window(ctk.CTk):

    def __init__(self, width, height):
        super(Window, self).__init__()
        self.geometry(f"{width}x{height}")
        self.title("Graphing Calculator")
        self.window_init()

    def window_init(self):
        graphing_screen = GraphingScreen(self)
        graphing_screen.pack(expand=True, fill="both")
        self.mainloop()


class GraphingScreen(ctk.CTkFrame):

    def __init__(self, parent,
                 title="new_graph",     # data fields for the graphing screen
                 p_id=None,
                 p_date_created=None,
                 p_date_modified=None,
                 p_type="2d"):

        super(GraphingScreen, self).__init__(master=parent)

        self.graphing_window = None   # graphing screen's widgets
        self.keypad = None
        self.sidebar = None
        self.show_sidebar_btn = None
        self.toolbar = None

        self.previous = None    # The screen that comes before this one
        self.title = title

        # attributes for data stored about the graph
        if p_id is None:  # checks if existing ID has been passed in
            self.id = str(uuid4())  # generates a new random id must be converted to a string to avoid type error
        else:
            self.id = p_id  # sets to existing ID

        if p_date_modified is None:     # checks if existing date has been passed as a parameter
            self.date_modified = date.today()   # sets the date to the current day
        else:
            self.date_modified = p_date_modified

        if p_date_created is None:
            self.date_created = date.today()
        else:
            self.date_created = p_date_created

        self.type = p_type

        # a lookup table for the expression frame class
        self.expression_frame_dict = {"2d": ExpressionFrame, "vector": VectorExpressionFrame}
        self.expression_frame_class = self.expression_frame_dict[self.type]

        self.graphing_screen_init()

    def graphing_screen_init(self):     # creates and places widgets onto the graphing screen
        self.graphing_window = GraphingWindow(self, self.expression_frame_class)    # graphing window and keypad
        self.graphing_window.pack(fill="both", expand=True)   # need to access the expression frame class too

        self.show_sidebar_btn = ShowSidebarBtn(self, rel_height=0.05, start_pos=-0.05, end_pos=0, rely=0.06)   # sidebar
        self.sidebar = Sidebar(self, 0, -0.25, 0.03, self.show_sidebar_btn)  # and show sidebar button place themselves

        self.keypad = Keypad(self, self.expression_frame_class)  # keypad also places itself onto the screen

        # creates the zoom buttons
        zoom_in = ctk.CTkButton(self, text="+", command=self.graphing_window.zoom_in, corner_radius=3,
                                bg_color="white", anchor="center", font=(None, 18, "bold"))
        zoom_out = ctk.CTkButton(self, text="-", command=self.graphing_window.zoom_out, corner_radius=3,
                                 bg_color="white", anchor="center", font=(None, 18, "bold"))

        zoom_in.place(anchor="ne", relx=0.995, rely=0.055, relwidth=0.025, relheight=0.035)  # places the zoom buttons
        zoom_out.place(anchor="ne", relx=0.995, rely=0.105, relwidth=0.025, relheight=0.035)

        self.toolbar = GraphingToolbar(self, 0.03, self.title)  # toolbar places itself onto the screen


class GraphingToolbar(Toolbar):
    def __init__(self, parent, rel_height, title):
        super(GraphingToolbar, self).__init__(parent, rel_height, title)
        self.graphing_toolbar_init()

    def graphing_toolbar_init(self):
        save_menu = SaveMenu(self.master)   # creates menu to link to the file button
        file_btn = MenuBtn(self, "file", save_menu)  # links the file button to the save menu
        file_btn.place(anchor="ne", relx=1, rely=0, relheight=1)  # and adds it to the toolbar

    def go_back(self):
        super(GraphingToolbar, self).go_back()  # goes to the previous screen
        GraphingWindow.graphing_window = None   # resets any global variables for graphing window and expression frame
        GraphingWindow.graphs = set()
        screen = self.master
        for frame_class in screen.expression_frame_dict.values():   # goes through all types of expression frames
            frame_class.expression_frames = {}                      # and resets their variables
            frame_class.current = None


class SaveMenu(FullScreenMenu):
    def __init__(self, parent):
        super(SaveMenu, self).__init__(parent, 0.5, 0.6, 0.2, 0.2, "s")
        self.screen = parent    # this is a reference to the screen for the buttons
        self.save_menu_init()

    def save_menu_init(self):
        save_btn = ctk.CTkButton(self, text="save", command=self.save)  # creates and places buttons for the menu onto
        save_as_btn = ctk.CTkButton(self, text="save_as", command=self.save_as)  # the screen
        rename_btn = ctk.CTkButton(self, text="rename", command=self.rename)
        delete_btn = ctk.CTkButton(self, text="delete", command=self.delete)
        save_btn.pack()
        save_as_btn.pack()
        rename_btn.pack()
        delete_btn.pack()

    def get_expressions(self):
        output = []   # initialises empty list
        screen = self.screen
        for i in screen.expression_frame_class.expression_frames:   # "i" is the id of the expression frame
            frame = screen.expression_frame_class.expression_frames[i]
            expression_text = frame.get_expression()    # gets text from expression frame
            output.append((i, screen.id, expression_text))      # creates a list of values that can be used
        return output   # to save expressions- each tuple is a record in the Expressions table

    def save(self):
        screen = self.screen
        expressions = self.get_expressions()    # gets the expression records
        screen.date_modified = date.today()  # updates the date modified
        database_functions.save(graph_id=screen.id,     # saves the graph
                                graph_title=screen.title,
                                date_modified=screen.date_modified,
                                expressions=expressions)

    def rename(self):
        dialog = ctk.CTkInputDialog(text="New name:", title="rename")   # dialog box for user to enter the new name
        new_name = dialog.get_input()   # gets inputted text
        if new_name:    # checks if user cancelled
            self.screen.title = new_name    # sets the screens name to the new one
            self.screen.toolbar.title.set(new_name)  # sets title shown on the screen's toolbar to the new one
            self.screen.date_modified = date.today()    # updates the data modified
            database_functions.update_graph(self.screen.id, self.screen.title, self.screen.date_modified)
            # updates the database records

    def save_as(self):
        dialog = ctk.CTkInputDialog(text="Save as:", title="Save As")   # dialog box for user to enter the new name
        new_name = dialog.get_input()   # gets inputted text
        if new_name:    # checks if user cancelled
            screen = self.screen
            screen.title = new_name  # updates the graph's name
            screen.toolbar.title.set(new_name)   # sets the text that will be on the toolbar

            screen.id = str(uuid4())    # gets all new data fields to add in a new record to Graphs table
            screen.date_modified = date.today()
            screen.date_created = date.today()
            output = self.get_expressions()

            database_functions.save_as(graph_id=screen.id,  # adds in new graph to the database
                                       graph_title=screen.title,
                                       g_type=screen.type,
                                       date_created=screen.date_created,
                                       date_modified=screen.date_modified,
                                       expressions=output)

    def delete(self):
        screen = self.screen
        database_functions.delete_graph(screen.id)  # deletes the graph from the database
        screen.toolbar.go_back()    # goes back to the previous screen


class Sidebar(ctk.CTkFrame):

    def __init__(self, parent, start_pos, end_pos, rely, show_sidebar_btn):
        super(Sidebar, self).__init__(master=parent)
        self.show_sidebar_btn = show_sidebar_btn    # sidebar widgets
        self.btn_frame = None
        self.expression_section = None

        self.start_pos = start_pos      # position and sizing attributes for animation logic
        self.end_pos = end_pos
        self.width = abs(start_pos-end_pos)
        self.rely = rely

        self.pos = start_pos
        self.in_start_pos = True    # condition to check if the sidebar is in the correct position

        self.sidebar_init()

    def sidebar_init(self):
        sidebar_btn_frame_height = 0.05
        self.btn_frame = SidebarBtnFrame(self)      # creates and places button frame onto the sidebar
        self.btn_frame.place(relx=0, rely=0, relwidth=1, relheight=sidebar_btn_frame_height)

        # creates expression section and places it under the button frame
        self.expression_section = DynamicScrollFrame(self, self.master.expression_frame_class, 3, 5, 257)
        self.expression_section.place(relx=0, rely=sidebar_btn_frame_height, relwidth=1,
                                      relheight=1-sidebar_btn_frame_height)

        # places the sidebar onto the screen
        self.place(relx=self.start_pos, rely=self.rely, relwidth=self.width, relheight=1 - self.rely)

    def animate(self):
        if self.in_start_pos:   # checks if the sidebar is in its start position to determine which way it should move
            self.animate_forwards()  # hides sidebar
            self.show_sidebar_btn.animate()  # puts show button onto the screen
        else:
            self.show_sidebar_btn.animate()  # removes show button from the screen
            self.animate_backwards()    # shows the sidebar

    def animate_forwards(self):
        if self.pos > self.end_pos:  # checks to see if the animation has been completed
            self.pos -= 0.01    # decrements position gradually to give the illusion of movement
            # original place is overriden
            self.place(relx=self.pos, rely=self.rely, relwidth=self.width, relheight=1 - self.rely)
            self.after(10, self.animate_forwards)   # after 10ms the next decrement will occur
        else:
            self.in_start_pos = False   # once the animation has been completed the sidebar will no longer be in the
        # start position

    def animate_backwards(self):    # same as animate forward but incrementing position to move in the opposite direct-
        if self.pos < self.start_pos:   # ion
            self.pos += 0.01
            self.place(relx=self.pos, rely=self.rely, relwidth=self.width, relheight=1 - self.rely)
            self.after(10, self.animate_backwards)
        else:
            self.in_start_pos = True    # once the animation is done the sidebar will be back in its original position
        # where it is visible


class SidebarBtnFrame(ctk.CTkFrame):    # contains the sidebar buttons to add an expression and hide the sidebar

    def __init__(self, parent):
        super(SidebarBtnFrame, self).__init__(master=parent, corner_radius=0)
        self.sidebar_btn_frame_init()

    def sidebar_btn_frame_init(self):   # creates and places the buttons onto the screen
        create_expression_btn = CreateExpressionBtn(self)   # places create expression button
        create_expression_btn.place(relx=0.01, rely=0.1, relwidth=0.485, relheight=0.8)

        hide_sidebar_btn = HideSidebarBtn(self)  # places hide sidebar expression button
        hide_sidebar_btn.place(anchor="ne", relx=0.99, rely=0.1, relwidth=0.485, relheight=0.8)


class CreateExpressionBtn(ctk.CTkButton):

    def __init__(self, parent):
        super(CreateExpressionBtn, self).__init__(master=parent, text="+", command=self.on_click)

    def on_click(self):
        sidebar = self.master.master    # navigates to the sidebar
        sidebar.expression_section.base_frame.add()  # adds an expression frame to the sidebar


class HideSidebarBtn(ctk.CTkButton):

    def __init__(self, parent):
        super(HideSidebarBtn, self).__init__(master=parent, text="<<", command=self.hide_sidebar)

    def hide_sidebar(self):
        sidebar = self.master.master    # navigates to the sidebar
        sidebar.animate()   # hides the sidebar


class ShowSidebarBtn(ctk.CTkButton):

    def __init__(self, parent, start_pos, end_pos, rel_height, rely):
        super(ShowSidebarBtn, self).__init__(master=parent, text=">>", command=self.show_sidebar, bg_color="white",
                                             corner_radius=3)
        self.start_pos = start_pos  # position attributes for the animation logic
        self.end_pos = end_pos
        self.width = abs(start_pos - end_pos)
        self.rel_height = rel_height
        self.rely = rely

        self.pos = start_pos
        self.in_start_pos = True    # condition to check if sidebar is in its initial position

        # places button onto the screen
        self.place(relx=start_pos, rely=self.rely, relwidth=self.width, relheight=rel_height)
    
    def show_sidebar(self):
        sidebar = self.master.sidebar   # navigates to the sidebar and shows it
        sidebar.animate()

    def animate(self):
        if self.in_start_pos:   # checks if the show button is hidden or not
            self.animate_forwards()  # if it is then it will be moved to be shown
        else:
            self.animate_backwards()    # otherwise it will be hidden

    def animate_forwards(self):
        if self.pos < self.end_pos:  # checks if the animation is completed
            self.pos += 0.002       # increments position like the sidebar
            self.place(relx=self.pos, rely=self.rely, relwidth=self.width, relheight=self.rel_height)
            self.after(10, self.animate_forwards)
        else:
            self.in_start_pos = False   # at the end of the animation the button is no longer in its start position

    def animate_backwards(self):    # same as with last method but decrements position to move button backwards
        if self.pos > self.start_pos:
            self.pos -= 0.002
            self.place(relx=self.pos, rely=self.rely, relwidth=self.width, relheight=self.rel_height)
            self.after(10, self.animate_backwards)
        else:
            self.in_start_pos = True    # at the end of the animation the button is in its start position


if __name__ == "__main__":
    win = Window(DEF_WIDTH, DEF_HEIGHT)

