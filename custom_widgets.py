import customtkinter as ctk

DEF_HEIGHT = int(1080 * 0.7)
DEF_WIDTH = int(1920 * 0.7)


class Window(ctk.CTk):

    def __init__(self, width, height):
        super(Window, self).__init__()
        self.geometry(f"{width}x{height}")
        self.title("Graphing Calculator")
        self.test_menu = None
        self.window_init()

    def window_init(self):
        self.test_menu = FullScreenMenu(self, 0.5, 0.6, 0.2, 0.2, "s")
        btn = MenuBtn(self, "show", self.test_menu)
        btn.place(relx=0.3, rely=0.3)
        self.mainloop()


class Toolbar(ctk.CTkFrame):
    def __init__(self, parent, rel_height, title):
        super(Toolbar, self).__init__(master=parent)
        self.title = ctk.StringVar()    # string variable for the title label
        self.title.set(title)   # sets the title text
        self.toolbar_init()
        self.place(rely=0, relx=0, relheight=rel_height, relwidth=1)    # puts the toolbar at the top of the screen

    def toolbar_init(self):
        back_btn = ctk.CTkButton(self, text="<", command=self.go_back)  # creates and places back button
        back_btn.place(relx=0, rely=0, relwidth=0.1, relheight=1)

        title = ctk.CTkLabel(self, textvariable=self.title)     # creates and places title_label
        title.place(anchor="s", relx=0.5, rely=1.1)

    def go_back(self):
        screen = self.master    # navigates to screen
        screen.pack_forget()    # gets rid of the screen and packs the screen referenced by the previous attribute
        screen.previous.pack(fill="both", expand=True)


class MenuBtn(ctk.CTkButton):
    def __init__(self, parent, p_text, p_menu):
        super(MenuBtn, self).__init__(master=parent, text=p_text, command=self.on_click)
        self.menu = p_menu  # menu needs to be able to be accessed by menu button

    def on_click(self):
        menu = self.menu
        if menu.show:   # checks if menu button is on screen
            menu.place_forget()
            menu.show = False
        else:
            menu.place(relx=menu.x, rely=menu.y, relwidth=menu.width, relheight=menu.height, anchor=menu.anchor)
            menu.show = True    # if it is not on the screen it is placed onto the screen


class FullScreenMenu(ctk.CTkFrame):
    def __init__(self, parent, x, y, rel_width, rel_height, anchor):
        # creates background frame to cover up whole screen
        self.background_frame = ctk.CTkFrame(master=parent, fg_color="transparent")
        # menu is placed on the background frame
        super(FullScreenMenu, self).__init__(master=self.background_frame)
        self.x = x      # position attributes for exit button and other menu buttons
        self.y = y
        self.width = rel_width
        self.height = rel_height
        self.anchor = anchor
        self.show = False   # condition to check if menu is onscreen or not
        self.full_screen_menu_init()

    def full_screen_menu_init(self):
        exit_btn = MenuBtn(self, "x", self)  # creates exit button and adds exit button to menu
        exit_btn.place(anchor="ne", relx=1, rely=0, relwidth=0.2)

    def place(self, **kwargs):
        self.background_frame.tkraise()  # puts background frame above other widgets
        self.background_frame.place(relx=0, rely=0, relwidth=1, relheight=1)    # adds background frame to screen
        super(FullScreenMenu, self).place(**kwargs)  # adds menu to background frame

    def place_forget(self):
        self.background_frame.place_forget()    # removes background frame
        super(FullScreenMenu, self).place_forget()  # removes menu from background frame


class DynamicScrollFrame(ctk.CTkCanvas):

    def __init__(self, parent, item_class, item_pad_y, item_pad_x, item_size):
        super(DynamicScrollFrame, self).__init__(master=parent, bg="gray14")
        self.pack(expand=True, fill="both")  # packs scrollable frame onto screen (can be overriden)

        # creates a base frame to place widgets on
        self.base_frame = BaseFrame(self, item_class, item_pad_y, item_pad_x, item_size)

        self.scrollbar = ctk.CTkScrollbar(self, command=self.yview)  # creates scrollbar and
        self.configure(yscrollcommand=self.scrollbar.set)   # adds scroll command

        self.bind("<Configure>", self.update_size)  # binds re size event

    def update_size(self, event=None):
        width = self.winfo_width()  # gets width and height of the canvas
        height = self.winfo_height()
        cur_height = self.base_frame.item_size*self.base_frame.num_items  # gets the total height of items
        if cur_height > height:  # if this is higher than the canvas height a scrollbar needs to be added
            container_height = cur_height
            self.scrollbar.place(relx=1, rely=0, relheight=1, anchor="ne")
            self.configure(scrollregion=(0, 2, width, container_height-2))    # offset by 2 to avoid seeing white canvas
            width -= 19  # adjusts base frame size so the scrollbar does not cover the base frame
        else:
            container_height = height
            self.yview_moveto(0)    # scrolls back to the top to avoid
            self.scrollbar.place_forget()

        self.create_window(  # adds the base frame to the canvas with the correct size
            (-2, -2),
            window=self.base_frame,
            anchor="nw",
            width=width+4,      # offset is needed due to prevent white outline from being visible
            height=container_height+4
        )


class BaseFrame(ctk.CTkFrame):

    def __init__(self, parent, item_class, item_pad_y, item_pad_x, item_size):
        super(BaseFrame, self).__init__(master=parent, bg_color='gray14', corner_radius=0)
        self.padding_y = item_pad_y  # padding for items inside the base frame
        self.padding_x = item_pad_x
        self.item_size = item_size   # pixels
        self.item_class = item_class    # type of widget that is going to be inside the scrollable frame
        self.num_items = 0
        self.frames = []  # list of all frames

    def add(self, params=()):  # takes in parameters to pass into the item class init method
        frame = self.item_class(self, *params)  # creates a frame with specified parameters
        self.frames.append(frame)  # adds it to the list of all frames
        frame.pack(expand=False, fill="x", pady=self.padding_y, padx=self.padding_x, side="top")  # adds item frame
        self.num_items += 1  # increases item number accordingly

        expression_canvas = self.master   # navigates to the canvas the base frame is placed on
        expression_canvas.update_size()   # calls update size to check if the scrollbar needs to placed on the canvas

    def remove(self):
        self.num_items -= 1   # decrements number of items
        expression_canvas = self.master
        expression_canvas.update_size()

    def remove_all(self):
        self.num_items = 0  # resets number of items
        for i in self.frames:
            i.destroy()     # deletes frames
        self.frames = []    # resets list

        canvas = self.master
        canvas.update_size()    # calls update size to get rid of the scrollbar


if __name__ == "__main__":
    win = Window(DEF_WIDTH, DEF_HEIGHT)
