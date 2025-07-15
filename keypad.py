import customtkinter as ctk
from graphing_window import ExpressionFrame
from custom_widgets import MenuBtn

DEF_HEIGHT = int(1080/2)
DEF_WIDTH = int(1920/2)


class Window(ctk.CTk):

    def __init__(self, width, height):
        super(Window, self).__init__()
        self.geometry(f"{width}x{height}")
        self.title("Graphing Calculator")
        self.window_init()

    def window_init(self):
        Keypad(self)    # places keypad onto the screen
        self.mainloop()


class Keypad(ctk.CTkFrame):
    expression_frame_class = None   # global variable to reference the expression frame class

    def __init__(self, parent, expression_frame_class=ExpressionFrame):
        super(Keypad, self).__init__(master=parent, bg_color="white", corner_radius=3)
        self.x = 0.5    # position and dimensions for the menu buttons
        self.y = 1
        self.width = 0.45
        self.height = 0.4
        self.anchor = "s"
        self.show = False   # condition to check if the keypad needs to be shown on screen or not

        Keypad.expression_frame_class = expression_frame_class
        # sets expression frame class to be accessed by text buttons

        self.function_menu = FunctionMenu(self.master)  # creates function menu which will be placed on the screen
        self.keypad_init()

    def keypad_init(self):  # creates and places widgets
        self.columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)    # sets up rows and columns of the keypad
        self.rowconfigure((0, 1, 2, 3), weight=1)

        layout = [      # elements here are the button text
                 ["hide", "a^b", "(",  ")",  "7", "8", "9", "/"],
                 ["π", "e", "abs", "sqrt",  "4", "5", "6", "*"],
                 ["x", "y", "r",       "θ",  "1", "2", "3", "-"],
                 ["functions", "", "",  "",  "0", ".", "=", "+"]
        ]

        values = [  # elements here are the values that will be inserted into the text widget when the button is pressed
                 ["hide", "^", "(",     ")",  "7", "8", "9", "/"],  # except the hide and function button
                 ["π", "e", "abs(", "sqrt(",  "4", "5", "6", "*"],
                 ["x", "y", "r",        "θ",  "1", "2", "3", "-"],
                 ["functions", "", "",   "",  "0", ".", "=", "+"]
        ]

        for i in range(1, 8):   # adds all the buttons in the first row except the hide button
            btn = TextBtn(self, layout[0][i], values[0][i])
            btn.grid(row=0, column=i, sticky="nsew", padx=2, pady=5)

        for i in range(1, 3):   # goes through the other rows except the last row
            for j in range(0, 8):
                btn = TextBtn(self, layout[i][j], values[i][j])
                btn.grid(row=i, column=j, sticky="nsew", padx=2, pady=5)

        func_btn = MenuBtn(self, layout[3][0], self.function_menu)  # adds the function button to the last row
        func_btn.grid(row=3, column=0, sticky="nsew", columnspan=4, padx=2, pady=5)  # this spans 4 rows

        for i in range(4, 8):   # adds the rest of the buttons to the last row
            btn = TextBtn(self, layout[3][i], values[3][i])
            btn.grid(row=3, column=i, sticky="nsew", padx=2, pady=5)

        show_btn = ShowKeypadBtn(self.master, "keypad", self)   # creates show keypad button and links it to the keypad
        show_btn.place(anchor=show_btn.anchor, rely=show_btn.y, relx=show_btn.x)   # places it onscreen

        hide_btn = HideKeypadBtn(self, layout[0][0], self, show_btn)    # creates the hide button and adds it to the
        hide_btn.grid(row=0, column=0, sticky="nsew", padx=2, pady=5)   # first row


class TextBtn(ctk.CTkButton):
    def __init__(self, parent, p_text, p_value):    # p_text is the text on the button
        super(TextBtn, self).__init__(master=parent, text=p_text, command=self.keypad_btn_onclick)
        self.value = p_value    # value to be inserted into the selected text widget

    def keypad_btn_onclick(self):
        frames = Keypad.expression_frame_class  # accesses Keypad's expression frame class
        if frames.current is not None:      # checks if an expression frame is selected
            frame = frames.expression_frames[frames.current]    # if yes then the buttons value is
            frame.textbox.insert(ctk.INSERT, self.value)    # inserted into the frame's selected text widget
            frame.on_text_change()  # plots the graph if the new expression text is valid


class HideKeypadBtn(MenuBtn):
    def __init__(self, parent, p_text, p_menu, p_show_btn):     # the menu in this case is the keypad which the button
        super(HideKeypadBtn, self).__init__(parent, p_text, p_menu)    # will hide
        self.show_btn = p_show_btn    # needs to be able to access the show button to place it on screen when
        # clicked

    def on_click(self):
        super(HideKeypadBtn, self).on_click()   # hides the keypad
        func_menu = self.menu.function_menu     # gets the function menu through the keypad
        func_menu.place_forget()    # removes the function menu from the screen
        if func_menu.show:  # if the function menu was on screen then its show condition is set to false
            func_menu.show = False
        self.show_btn.place(relx=self.show_btn.x, rely=self.show_btn.y, anchor=self.show_btn.anchor) # places show
        # button onto the screen


class ShowKeypadBtn(MenuBtn):
    def __init__(self, parent, p_text, p_menu):
        super(ShowKeypadBtn, self).__init__(parent, p_text, p_menu)
        self.configure(bg_color="white", corner_radius=3)
        self.x = 0.98   # position attributes for the keypad button
        self.y = 0.98
        self.anchor = "se"

    def on_click(self):
        super(ShowKeypadBtn, self).on_click()   # places the keypad on screen
        self.place_forget()     # gets rid of show button from screen


class FunctionMenu(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super(FunctionMenu, self).__init__(master=parent)
        self.x = 0.75   # position attributes for the menu button
        self.y = 1
        self.width = 0.2
        self.height = 0.175
        self.anchor = "sw"
        self.show = False   # condition to see if the menu is being shown or not, set to false by default

        self.function_menu_init()

    def function_menu_init(self):
        self.columnconfigure((0, 1, 2), weight=1)   # sets up columns for the function menu

        layout = [  # text for the buttons
            ["sin", "cos", "tan"],
            ["csc", "sec", "cot"],
            ["arcsin", "arccos", "arctan"],
            ["sinh", "cosh", "tanh"],
            ["arcsinh", "arccosh", "arctanh"],
            ["ln"]
        ]

        values = [  # values inserted into selected text widget for buttons
            ["sin(", "cos(", "tan("],
            ["csc(", "sec(", "cot("],
            ["arcsin(", "arccos(", "arctan("],
            ["sinh(", "cosh(", "tanh("],
            ["arcsinh(", "arccosh(", "arctanh("],
            ["ln("]
        ]

        for i in range(len(layout)):    # goes through all buttons in the layout
            for j in range(len(layout[i])):
                btn = TextBtn(self, layout[i][j], values[i][j])   # creates and places them onto the grid
                btn.grid(row=i, column=j, sticky="nsew", padx=2, pady=5)


if __name__ == "__main__":
    win = Window(DEF_WIDTH, DEF_HEIGHT)
