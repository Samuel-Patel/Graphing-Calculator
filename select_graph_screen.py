import customtkinter as ctk
from custom_widgets import Toolbar
from graphing_screen import GraphingScreen

DEF_HEIGHT = int(1080 * 0.7)
DEF_WIDTH = int(1920 * 0.7)


class Window(ctk.CTk):

    def __init__(self, width, height):
        super(Window, self).__init__()
        self.geometry(f"{width}x{height}")
        self.title("Graphing Calculator")

        self.window_init()

    def window_init(self):
        select_graph_screen = SelectGraphScreen(self)
        select_graph_screen.pack(fill="both", expand=True)
        self.mainloop()


class SelectGraphScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super(SelectGraphScreen, self).__init__(master=parent)
        self.toolbar = None  # widgets
        self.mode_section = None
        self.header = None

        self.previous = None    # pointer to last screen for toolbar

        self.select_graph_screen_init()

    def select_graph_screen_init(self):
        self.toolbar = Toolbar(self, 0.03, "Select Graphing Mode")  # creates and places toolbar

        # creates and places label
        self.header = ctk.CTkLabel(self, anchor="center", font=(None, 32), text="Select Your Mode:")
        self.header.place(anchor="s", relx=0.5, rely=0.25)

        # adds section with buttons to select graphing mode
        self.mode_section = ModeSection(self)
        self.mode_section.place(anchor="center", relx=0.5, rely=0.6, relwidth=0.9, relheight=0.6)


class ModeSection(ctk.CTkFrame):
    def __init__(self, parent):
        super(ModeSection, self).__init__(master=parent, corner_radius=20)
        self.mode_2d_btn = None  # widgets
        self.mode_vector_btn = None

        self.mode_section_init()

    def mode_section_init(self):
        # creates buttons
        self.mode_2d_btn = ctk.CTkButton(self, text="2d", corner_radius=20, font=(None, 36, "bold"),
                                         command=lambda arg="2d": self.load_screen(arg))
        self.mode_vector_btn = ctk.CTkButton(self, text="vector", corner_radius=20, font=(None, 36, "bold"),
                                             command=lambda arg="vector": self.load_screen(arg))
        # places buttons
        self.mode_vector_btn.pack(side="right", expand=True, fill="both", padx=5, pady=5)
        self.mode_2d_btn.pack(side="left", expand=True, fill="both", padx=5, pady=5)

    def new_screen(self, screen):
        cur_screen = self.master    # gets rid of old screen
        cur_screen.pack_forget()    # and packs the new screen onto the window
        screen.pack(fill="both", expand=True)

    def load_screen(self, p_type):
        cur_screen = self.master    # navigates to screen and window
        window = cur_screen.master

        next_screen = GraphingScreen(window, p_type=p_type)  # creates the graphing screen with the correct type
        next_screen.previous = cur_screen   # adds pointer to the last screen
        self.new_screen(next_screen)


if __name__ == "__main__":
    win = Window(DEF_WIDTH, DEF_HEIGHT)
