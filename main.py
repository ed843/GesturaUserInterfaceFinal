import tkinter as tk


class FirstWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="First Window").pack(padx=10, pady=10)
        self.pack(padx=10, pady=10)



class SecondWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Second Window").pack(padx=10, pady=10)
        self.pack(padx=10, pady=10)

class ThirdWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Third Window").pack(padx=10, pady=10)
        self.pack(padx=10, pady=10)

class FourthWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Fourth Window").pack(padx=10, pady=10)
        self.pack(padx=10, pady=10)

class MainWindow():
    def __init__(self, master):
        mainframe = tk.Frame(master)
        mainframe.pack(padx=10, pady=10, fill='both',expand=1)
        self.index = 0

        self.frameList = [FirstWindow(mainframe), SecondWindow(mainframe),
                          ThirdWindow(mainframe), FourthWindow(mainframe)]
        self.frameList[1].forget()
        self.frameList[2].forget()
        self.frameList[3].forget()

        bottomframe = tk.Frame(master)
        bottomframe.pack(padx=10, pady=10)

        switch = tk.Button(bottomframe, text="Switch", command=self.changeWindow1)
        switch.pack(padx=10, pady=10)
        switch = tk.Button(bottomframe, text="Switch", command=self.changeWindow2)
        switch.pack(padx=10, pady=10)
        switch = tk.Button(bottomframe, text="Switch", command=self.changeWindow3)
        switch.pack(padx=10, pady=10)
        switch = tk.Button(bottomframe, text="Switch", command=self.changeWindow4)
        switch.pack(padx=10, pady=10)

    def changeWindow1(self):
        self.frameList[self.index].forget()
        self.index = 0
        self.frameList[self.index].tkraise()
        self.frameList[self.index].pack(padx=10, pady=10)
    def changeWindow2(self):
        self.frameList[self.index].forget()
        self.index = 1
        self.frameList[self.index].tkraise()
        self.frameList[self.index].pack(padx=10, pady=10)
    def changeWindow3(self):
        self.frameList[self.index].forget()
        self.index = 2
        self.frameList[self.index].tkraise()
        self.frameList[self.index].pack(padx=10, pady=10)
    def changeWindow4(self):
        self.frameList[self.index].forget()
        self.index = 3
        self.frameList[self.index].tkraise()
        self.frameList[self.index].pack(padx=10, pady=10)


root = tk.Tk()
window = MainWindow(root)
root.mainloop()
