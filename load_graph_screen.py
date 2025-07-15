import customtkinter as ctk
from custom_widgets import Toolbar, DynamicScrollFrame, FullScreenMenu, MenuBtn
from graphing_screen import GraphingScreen
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
        load_graph_screen = LoadGraphScreen(self)
        load_graph_screen.pack(fill="both", expand=True)
        self.mainloop()


class LoadGraphScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super(LoadGraphScreen, self).__init__(master=parent)
        self.searchbar = None   # widgets
        self.result_section = None
        self.toolbar = None
        self.mode = ctk.StringVar(value="all")      # sets the default value for the
        self.sort_by = ctk.StringVar(value="name")  # option menus

        self.previous = None    # pointer to the last screen for the toolbar

        self.load_graph_screen_init()

    def load_graph_screen_init(self):   # creates and adds widgets
        self.toolbar = Toolbar(self, 0.03, "Load Graph")    # creates and places toolbar

        self.searchbar = Searchbar(self)  # creates and places searchbar
        self.searchbar.place(anchor="sw", relx=0.025, rely=0.15, relwidth=0.675, relheight=0.05)

        # creates option menus
        mode_menu = ctk.CTkOptionMenu(self, values=["all", "2d", "vector"], variable=self.mode,
                                      command=self.searchbar.search)
        sort_by_menu = ctk.CTkOptionMenu(self, values=["name", "date created", "date modified"], variable=self.sort_by,
                                         command=self.searchbar.search)

        # creates labels for option menus
        mode_label = ctk.CTkLabel(self, text="Mode:")
        sort_by_label = ctk.CTkLabel(self, text="Sort By:")

        # places option menus and labels
        mode_label.place(anchor="sw", relx=0.7, rely=0.15, relwidth=0.04, relheight=0.05)
        mode_menu.place(anchor="sw", relx=0.74, rely=0.145)

        sort_by_label.place(anchor="sw", relx=0.85, rely=0.15, relwidth=0.04, relheight=0.05)
        sort_by_menu.place(anchor="sw", relx=0.89, rely=0.145)

        result_section_wrapper = ctk.CTkFrame(self)     # adds results section to the screen
        self.result_section = DynamicScrollFrame(result_section_wrapper, Result, 3, 5, 257)
        result_section_wrapper.place(relx=0, rely=0.205, relwidth=1, relheight=0.795)

    def pack(self, **kwargs):
        self.searchbar.search()     # ensures that the result section is populated when the user goes to this screen
        super(LoadGraphScreen, self).pack(**kwargs)


class Searchbar(ctk.CTkEntry):
    def __init__(self, parent):
        super(Searchbar, self).__init__(master=parent)
        self.bind("<KeyRelease>", self.search)

    def search(self, event=None):
        search_item = self.get()    # gets entered string
        screen = self.master    # navigates to screen and result section base frame
        results = screen.result_section.base_frame
        results.remove_all()    # resets the result section

        mode = screen.mode.get()    # gets extra search criteria
        sort_by = screen.sort_by.get()
        # maps the option menu text to the correct field name to sort by
        sort_dict = {"name": "name", "date created": "date_created", "date modified": "date_modified"}
        sort_by = sort_dict[sort_by]

        graphs = database_functions.get_graphs(search_item, sort_by, mode)  # gets all graphs with the search item
        # as a substring according to search criteria
        for graph in graphs:    # goes through all results and adds them to the result section
            graph_id, graph_title, g_type, date_created, date_modified = graph[0], graph[1], graph[2], graph[3],\
                                                                         graph[4]
            results.add((screen, graph_id, graph_title, g_type, date_created, date_modified))


class Result(ctk.CTkFrame):
    selected_graph_id = None    # global variable for delete menu to access the selected graph

    def __init__(self, parent, p_screen, p_graph_id, p_graph_title, p_type, p_date_created, p_date_modified):
        super(Result, self).__init__(master=parent)
        self.graph_id = p_graph_id  # data about graph that needs to be displayed on the frame
        self.graph_title = p_graph_title
        self.type = p_type
        self.date_created = p_date_created
        self.date_modified = p_date_modified

        self.delete_menu = DeleteMenu(p_screen)   # delete menu to ask for confirmation if the user wants to delete
        # the graph

        self.screen = p_screen  # needed to call the pack_forget method for the screen in the load graph method
        self.result_init()

    def result_init(self):
        wrapper = ctk.CTkFrame(self)    # Wrapper frame for widgets to placed in
        wrapper.rowconfigure(0, weight=1)   # sets up columns and rows of this frame
        wrapper.columnconfigure((0, 1, 2, 3, 4), weight=1)

        go_to_graph_btn = ctk.CTkButton(wrapper, text=self.graph_title, command=self.load_graph)   # creates widgets
        type_label = ctk.CTkLabel(wrapper, text="Mode: " + self.type)                              # to show data/
        date_created_label = ctk.CTkLabel(wrapper, text="Date Created: " + self.date_created)      # interact with graph
        date_modified_label = ctk.CTkLabel(wrapper, text="Date Modified: " + self.date_modified)
        delete_btn = DeleteBtn(wrapper, "delete", self.delete_menu)

        go_to_graph_btn.grid(row=0, column=0, sticky="nsew", padx=2, pady=5)    # adds widgets to the wrapper using grid
        type_label.grid(row=0, column=1, sticky="nsew", padx=2, pady=5)
        date_created_label.grid(row=0, column=2, sticky="nsew", padx=2, pady=5)
        date_modified_label.grid(row=0, column=3, sticky="nsew", padx=2, pady=5)
        delete_btn.grid(row=0, column=4, sticky="nsew", padx=2, pady=5)

        wrapper.place(relx=0, rely=0, relheight=1, relwidth=1)  # places the wrapper onto the result frame

    def load_graph(self):
        window = self.screen.master  # navigates to window
        graphing_screen = GraphingScreen(window,    # creates graphing screen passing in existing data fields
                                         self.graph_title,
                                         self.graph_id,
                                         self.date_created,
                                         self.date_modified,
                                         self.type)
        graphing_screen.previous = self.screen  # sets previous pointer for graphing screen
        self.screen.pack_forget()   # removes the current screen
        graphing_screen.pack(fill="both", expand=True)  # packs new graphing screen onto the window
        graphing_screen.graphing_window.grid_init()  # draws grid onto the plane
        # loop through all expressions and add them to the expression container
        expressions = database_functions.get_expressions(self.graph_id)  # gets expressions of the saved graph
        for expression in expressions:  # iterates through expressions and adds them to the graphing window
            expression_id, expression_text = expression[0], expression[1]
            graphing_screen.sidebar.expression_section.base_frame.add((expression_id, expression_text))


class DeleteBtn(MenuBtn):
    def __init__(self, parent, text, menu):
        super(DeleteBtn, self).__init__(parent, text, menu)

    def on_click(self):
        # accesses the graph_id from the result frame to set Result.selected_graph_id
        Result.selected_graph_id = self.master.master.graph_id  # must be self.master.master due to the wrapper frame
        super(DeleteBtn, self).on_click()

# Can't use message box because custom tkinter does not support it and would look weird with regular tkinter


class DeleteMenu(FullScreenMenu):
    def __init__(self, parent):
        super(DeleteMenu, self).__init__(parent, 0.5, 0.6, 0.2, 0.2, "s")
        self.screen = parent    # pointer to screen is used for the yes button to more easily access the searchbar

        # creates widgets
        self.yes_btn = YesBtn(self, "yes", self)
        self.no_btn = MenuBtn(self, "no", self)
        self.yes_no_menu_init()

    def yes_no_menu_init(self):
        self.yes_btn.pack(padx=5, pady=5)   # places widgets with correct padding
        self.no_btn.pack(padx=5, pady=5)


class YesBtn(MenuBtn):
    def __init__(self, parent, text, menu):
        super(YesBtn, self).__init__(parent, text, menu)

    def on_click(self):
        # delete function using Result.selected_graph_id
        database_functions.delete_graph(Result.selected_graph_id)
        super(YesBtn, self).on_click()
        self.master.screen.searchbar.search()   # navigates to the delete menu to access the screen and its searchbar,
        # this is used to refresh the result section


if __name__ == "__main__":
    win = Window(DEF_WIDTH, DEF_HEIGHT)
