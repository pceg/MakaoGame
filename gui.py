import tkinter as tk
from game import Player


class DemandDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Demand")

        self.geometry("500x200")

        window_width = self.winfo_reqwidth()
        window_height = self.winfo_reqheight()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.geometry(f"+{x}+{y}")

        self.configure(bg='lightblue')

        label = tk.Label(self, text="What's your demand?:", bg='lightblue', font=('Arial', 14))
        label.pack(pady=(20, 10))

        # Create a frame to hold the buttons
        frame = tk.Frame(self, bg='lightblue')
        frame.pack(pady=10)

        options = ["5", "6", "7", "8", "9", "10", None]

        for idx, option in enumerate(options):
            if option is None:
                btn_text = "pass"
            else:
                btn_text = option
            btn = tk.Button(frame, text=btn_text, command=lambda opt=option: self.choose_option(opt),
                            font=('Arial', 12), bg='#0eb7eb', fg='white', activebackground='#97e1f7', width=5)
            btn.grid(row=0, column=idx, padx=5, pady=5)

    def choose_option(self, option):
        if option != "pass":
            Player.demand = option
        self.destroy()


class SuitChangeDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Change of suit")

        self.geometry("500x150")
        window_width = self.winfo_reqwidth()
        window_height = self.winfo_reqheight()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.geometry(f"+{x}+{y}")

        self.configure(bg='lightblue')

        label = tk.Label(self, text="Choose suit:", bg='lightblue', font=('Arial', 14))
        label.pack(pady=(20, 10))

        frame = tk.Frame(self, bg='lightblue')
        frame.pack(pady=10)

        options = ["Hearts", "Clubs", "Spades", "Diamonds"]

        for idx, option in enumerate(options):
            btn = tk.Button(frame, text=option, command=lambda opt=option: self.choose_option(opt),
                            font=('Arial', 12), bg='#0eb7eb', fg='white', activebackground='#97e1f7', width=10)
            btn.grid(row=0, column=idx, padx=5, pady=5)

    def choose_option(self, option):
        Player.change_of_suit = option
        self.destroy()
