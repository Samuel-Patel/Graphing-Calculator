import customtkinter as ctk

DEF_HEIGHT = int(1080*0.7)
DEF_WIDTH = int(1920*0.7)


class Window(ctk.CTk):

    def __init__(self, width, height):
        super(Window, self).__init__()
        self.geometry(f"{width}x{height}")
        self.title("Graphing Calculator")
        self.window_init()

    def window_init(self):
        menu_screen = MenuScreen(self)
        menu_screen.pack(expand=True, fill="both")
        self.mainloop()


class MenuScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super(MenuScreen, self).__init__(master=parent)
        self.mode_screen = None     # pointers to the select mode screen and load graph screen
        self.loading_screen = None
        self.menu_screen_init()

    def menu_screen_init(self):     # creating and placing widgets onto the screen
        mode_btn = ctk.CTkButton(self, text="Select Graphing Mode", anchor="center", font=(None, 16), corner_radius=15,
                                 command=lambda: self.new_screen(self.mode_screen))
        load_btn = ctk.CTkButton(self, text="Load Saved Graphs", anchor="center", font=(None, 16), corner_radius=15,
                                 command=lambda: self.new_screen(self.loading_screen))

        wrapper_frame = ctk.CTkFrame(self, corner_radius=20)      # adds title label to a wrapper frame for title's
        title = ctk.CTkLabel(wrapper_frame, text="Graphing Calculator", font=(None, 72), anchor="s")  # background
        title.pack(expand=True)

        # places title and buttons onto the screen
        wrapper_frame.place(anchor="s", relx=0.5, rely=0.55, relwidth=0.5, relheight=0.3)
        mode_btn.place(anchor="n", relx=0.5, rely=0.6, relwidth=0.14, relheight=0.05)
        load_btn.place(anchor="n", relx=0.5, rely=0.675, relwidth=0.14, relheight=0.05)

    def new_screen(self, screen):
        self.pack_forget()  # removes current screen
        screen.pack(fill="both", expand=True)   # puts new screen onto the window


if __name__ == "__main__":
    win = Window(DEF_WIDTH, DEF_HEIGHT)
