import tkinter as tk
from tkinter import *

import kasa
from PIL import Image, ImageTk
import asyncio
from kasa import SmartDevice, Discover
import asyncio
from kasa import SmartDevice, Discover


async def discover_devices():
    devices = await Discover.discover()
    return devices

index = "FrameOne"

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.attributes('-fullscreen', True)
        self.title("Gestura User Interface")
        self.configure(background='#333333')
        self.frames = {}
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.create_frames()
        self.show_frame("FrameOne")

    def create_frames(self):
        # Create instances of each frame class
        for F in (FrameOne, FrameTwo, FrameThree, FrameFour, FrameFive, FrameSix, FrameSeven):
            frame = F(self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky='news')

    def show_frame(self, name):
        # Bring a frame to the top
        global index
        frame = self.frames[name]
        frame.tkraise()
        index = name


class FrameOne(tk.Frame):
    def __init__(self, parent):

        super().__init__(parent)
        self.configure(background='#F3F3F3')
        self.frames = parent.frames
        self.images = {}
        self.load_images()
        self.create_buttons()
        self.grid(sticky='nsew')
    def load_images(self):
        # Load and resize images for buttons
        image_paths = ['icon1.png', 'icon2.png', 'icon3.png', 'icon4.png', 'icon5.png', 'icon6.png']
        desired_size = (595, 500)  # Width, Height in pixels
        for i, path in enumerate(image_paths):
            img = Image.open(path)
            img = img.resize(desired_size)
            self.images[i] = ImageTk.PhotoImage(img)

    def create_buttons(self):
        rows = 2
        columns = 3
        frame_classes = [FrameTwo, FrameThree, FrameFour, FrameFive, FrameSix, FrameSeven]
        colors = ['#66CCCC', '#ADD8E6', '#ADD8E6', '#98FB98', '#FFFDD0', '#708090']
        for i in range(6):
            frame_name = frame_classes[i].__name__
            button = tk.Button(self, image=self.images[i], bg=colors[i], command=lambda name=frame_name: self.show_frame(name))
            row_position = i // columns
            column_position = i % columns
            button.grid(row=row_position, column=column_position, padx=20, pady=20)
    def show_frame(self, name):
        # Bring a frame to the top
        global index
        frame = self.frames[name]
        frame.tkraise()
        index = name

class FrameTwo(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Add widgets to this frame
        tk.Label(self, text="Recent Gestures",font=('Arial', 25, 'bold')).pack()



class FrameThree(tk.Frame):
    def __init__(self, parent):

        super().__init__(parent)
        # Add widgets to this frame
        tk.Label(self, text="Add New Devices", font=('Arial', 25, 'bold')).pack()

class FrameFour(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Add widgets to this frame
        tk.Label(self, text="Linking Devices",font=('Arial', 25, 'bold')).pack()
        self.after(1000, self.check_and_discover)
        self.device_labels = []
        label = tk.Label(self, text="Searching for devices...")
        label.pack()
        self.device_labels.append(label)


    def check_and_discover(self):
        if index == "FrameFour":
            self.discover_kasa_devices()
        self.after(1000, self.check_and_discover)
    def discover_kasa_devices(self):
        # Discover Kasa devices
        devices = asyncio.run(discover_devices())

        for label in self.device_labels:
            # potentially a bug if the labels get destroyed while the user is pressing the button
            label.destroy()
        self.device_labels = []

        if not devices:
            print("No Kasa devices found.")
            label = tk.Label(self, text="No Kasa devices found.", )
            label.pack()
            self.device_labels.append(label)
            return

        print("Available Kasa devices:")
        for i, device in enumerate(devices, start=1):
            label_text = f"{i}. {device.alias} ({device.model})"
            label = tk.Label(self, text=label_text)
            label.grid(row=i + 2, column=1)
            # Adjust row position as needed
            self.device_labels.append(label)

            # Create a button for each device
            button = tk.Button(self, text=f"Connect to {device.alias}",
                               command=lambda dev=device: self.connect_to_device(dev))
            button.grid(row=i + 2, column=2)
            self.device_labels.append(button)

        # Store the discovered devices or update your UI accordingly

        # Example: Connect to the first discovered device
        selected_device = devices[0]
        print(f"Connecting to {selected_device.alias}...")

        # Implement your connection logic here (e.g., turn on/off, change settings, etc.)
        # For example:
        # await selected_device.turn_on()

        print(f"Connected to {selected_device.alias}!")

    def connect_to_device(self, selected_device):
        print(f"Connecting to {selected_device.alias}...")

            # Implement your connection logic here (e.g., turn on/off, change settings, etc.)
            # For example:
            # await selected_device.turn_on()

        print(f"Connected to {selected_device.alias}!")

class FrameFive(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.options = [
            "Gesture 1",
            "Gesture 2",
            "Gesture 3",
            "Gesture 4",
            "Gesture 5",
            "Gesture 6",
            "Gesture 7",
            "Gesture 8",
            "Gesture 9",
            "Gesture 10"
        ]
        tk.Label(self, text="Gesture Linking", font=('Arial', 25, 'bold')).pack()
        variable = tk.StringVar(self)
        variable.set(self.options[0])
        w = tk.OptionMenu(self, variable, *self.options)
        w.pack()
        # Add widgets to this frame


class FrameSix(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Add widgets to this frame
        tk.Label(self, text="This is Frame Six").pack()
class FrameSeven(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(5, weight=1)
        # Add widgets to this frame
        label = tk.Label(self, text="Settings", font=('Arial', 25, 'bold'))
        #label.pack(pady=10, padx=10)
        label2 = tk.Label(self, text="System Information\n", font=('Arial', 25, 'bold'))
        label3 = tk.Label(self, text="Raspberry Pi Model 4 B\n", font=('Arial', 15))
        label4 = tk.Label(self, text="Version 1.0\n", font=('Arial', 15))
        label5 = tk.Label(self, text="64 GB\n", font=('Arial', 15))
        #label2.pack(pady=10, padx=10)
       # entry1.pack(pady=10, padx=10)
        label.grid(row=0, column=0, padx=10, pady=10)
        label2.grid(row=1, column=3, padx=10, pady=10)
        label3.grid(row=2, column=3)
        label4.grid(row=3, column=3)
        label5.grid(row=4, column=3)





# Repeat for other frames (FrameTwo, FrameThree, etc.)
if __name__ == '__main__':
    app = MainApplication()
    app.mainloop()
