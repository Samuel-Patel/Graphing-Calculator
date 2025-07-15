import customtkinter as ctk
from main_menu import MenuScreen
from load_graph_screen import LoadGraphScreen
from select_graph_screen import SelectGraphScreen

DEF_HEIGHT = int(1080*0.7)  # default height and width
DEF_WIDTH = int(1920*0.7)


class Window(ctk.CTk):

    def __init__(self, width, height):
        super(Window, self).__init__()
        self.geometry(f"{width}x{height}")
        self.title("Graphing Calculator")   # sets title and dimensions of window

        self.window_init()

    def window_init(self):
        select_graph_screen = SelectGraphScreen(self)   # creates select graph screen
        menu_screen = MenuScreen(self)  # creates menu screen
        load_screen = LoadGraphScreen(self)   # creates load graph screen

        menu_screen.mode_screen = select_graph_screen   # sets pointers of the menu screen to
        menu_screen.loading_screen = load_screen            # the select and load screens

        select_graph_screen.previous = menu_screen   # sets the previous pointers for the load
        load_screen.previous = menu_screen           # and select screens

        menu_screen.pack(fill="both", expand=True)  # packs menu onto the screen
        self.mainloop()   # starts infinite loop for window


if __name__ == "__main__":
    win = Window(DEF_WIDTH, DEF_HEIGHT)  # creates window
