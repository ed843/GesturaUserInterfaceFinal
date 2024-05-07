import threading
import multiprocessing
from multiprocessing import Queue, Process, Manager
from queue import Empty
import socket
import cv2
import numpy as np
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import kasa
from PIL import Image, ImageTk
import asyncio
from kasa import SmartDevice, Discover, SmartLightStrip
import imutils
import pyshine as ps
import pickle
import struct
import time
async def turn_off(device):
    await device.turn_off()

async def turn_on(device):
    await device.turn_on()
async def discover_devices():
    devices = await Discover.discover(target="10.211.140.255")
    return devices
last_gesture = None
index = "FrameOne"
connected_devices = []
connected_devices_name = []
devices_on_gesture = {}
devices_off_gesture = {}
connected_devices_len = 0
gesture_results_check = []
labels_dict = {0: 'two', 1: 'L', 2: 'five', 3: 'up', 4: 'down', 5: 'bunny', 6: 'fist', 7: 'B', 8: 'one', 9: 'S'}
class MainApplication(tk.Tk):
    def __init__(self, gesture_results):
        super().__init__()
        self.attributes('-fullscreen', True)
        self.title("Gestura User Interface")
        self.configure(background='#333333')
        self.frames = {}
        self.gesture_results = gesture_results
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.create_frames()
        self.show_frame("FrameOne")

    def create_frames(self):
        # Create instances of each frame class
        for F in (FrameOne, FrameTwo, FrameThree, FrameFour, FrameFive, FrameSix, FrameSeven):
            frame = F(self, self.gesture_results)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky='news')

    def show_frame(self, name):
        # Bring a frame to the top
        global index
        frame = self.frames[name]
        frame.tkraise()
        index = name


class FrameOne(tk.Frame):
    def __init__(self, parent, gesture_results):

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
        desired_size = (460, 460)  # Width, Height in pixels
        for i, path in enumerate(image_paths):
            img = Image.open(path)
            img = img.resize(desired_size)
            self.images[i] = ImageTk.PhotoImage(img)

    def create_buttons(self):
        rows = 2
        columns = 3
        frame_classes = [FrameTwo, FrameThree, FrameFour, FrameFive, FrameSix, FrameSeven]
        colors = ['#66CCCC', '#ADD8E6', '#ADD8E6', '#98FB98', '#FFFDD0', '#708090']
        button_texts = ['Recent Gestures', 'Connected Devices', 'Add New Devices', 'Gesture Linking', 'Add New Gestures',
                        'Settings']  # Add your button texts here
        for i in range(6):
            frame_name = frame_classes[i].__name__
            button = tk.Button(self, image=self.images[i], bg=colors[i], text=button_texts[i], compound='top',
                               command=lambda name=frame_name: self.show_frame(name), font=('Arial', 20, 'bold'))
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
    def __init__(self, parent, gesture_results):
        super().__init__(parent)
        # Add widgets to this frame
        self.parent = parent
        self.frames = parent.frames
        self.gesture_results = gesture_results
        tk.Label(self, text="Recent Gestures",font=('Arial', 25, 'bold')).pack()

        self.create_widgets()
        back_button = tk.Button(self, text="Back to Home", font=('Arial', 25), command=self.go_back)
        back_button.pack(side="bottom")

    def create_widgets(self):
        self.listbox = tk.Listbox(self, bg='black', fg='white', font=('Arial', 35))  # Add bg, fg, and font parameters
        self.listbox.pack(fill=tk.BOTH, expand=1)
        self.after(1000, self.update_gesture_results)  # Update the gesture results every 1 second

    def update_gesture_results(self):
        self.listbox.delete(0, tk.END)  # Clear the Listbox
        for gesture_result in self.gesture_results:  # Add each gesture result to the Listbox
            self.listbox.insert(0, gesture_result)  # Change this line
        self.after(1000, self.update_gesture_results)


    def go_back(self):
        self.parent.show_frame("FrameOne")


class FrameThree(tk.Frame):
    def __init__(self, parent, gesture_results):

        super().__init__(parent)
        self.parent = parent
        # Add widgets to this frame
        tk.Label(self, text="Connected Devices", font=('Arial', 25, 'bold')).pack()
        self.create_widgets()
        back_button = tk.Button(self, text="Back to Home", font=('Arial',25), command=self.go_back)
        back_button.pack(side="bottom")


    def create_widgets(self):
        self.listbox = tk.Listbox(self, bg='black', fg='white', font=('Arial', 35))  # Add bg, fg, and font parameters
        self.listbox.pack(fill=tk.BOTH, expand=1)
        self.after(1000, self.update_connected_devices)  # Update the gesture results every 1 second

    def update_connected_devices(self):
        self.listbox.delete(0, tk.END)  # Clear the Listbox
        for device in connected_devices:  # Add each gesture result to the Listbox
            self.listbox.insert(0, f"{device.alias} - {device.model}")  # Change this line
        self.after(1000, self.update_connected_devices)
    def go_back(self):
        self.parent.show_frame("FrameOne")

class FrameFour(tk.Frame):
    def __init__(self, parent, gesture_results):
        super().__init__(parent)
        self.parent = parent
        # Add widgets to this frame
        tk.Label(self, text="Linking Devices", font=('Arial', 25, 'bold')).pack()
        self.after(5000, self.check_and_discover)
        self.device_labels = []
        label = tk.Label(self, text="Searching for devices...", font=('Arial', 25))
        label.pack()
        self.device_labels.append(label)
        back_button = tk.Button(self, text="Back to Home", font=('Arial',25),command=self.go_back)
        back_button.pack(side="bottom")

    def check_and_discover(self):
        if index == "FrameFour":
            self.discover_kasa_devices()
        self.after(5000, self.check_and_discover)

    def discover_kasa_devices(self):
        # Discover Kasa devices
        devices = asyncio.run(discover_devices())
        device_strip = None

        for label in self.device_labels:
            label.destroy()
        self.device_labels = []

        if not devices:
            print("No Kasa devices found.")
            label = tk.Label(self, text="No Kasa devices found.", font=('Arial', 25))
            label.pack()
            self.device_labels.append(label)
            return

        print("Available Kasa devices:")
        for i, (ip, device) in enumerate(devices.items(), start=1):
            label_text = f"{i}. {device.model} (\'{device.alias}\')"
            label = tk.Label(self, text=label_text, font = ('Arial', 25))
            label.pack()
            print(device.model)
            if (device.model == 'KL400L5(US)'):
                device_strip = SmartLightStrip(ip)
                asyncio.run(device_strip.update())
                button = tk.Button(self, text=f"Connect to {device.alias}", font = ('Arial', 25),
                                   command=lambda device=device_strip: self.connect_to_device(device))
                button.pack()
                self.device_labels.append(button)
            if (device.model == 'EP10(US)'):
                device_plug = kasa.SmartPlug(ip)
                asyncio.run(device_plug.update())
                button = tk.Button(self, text=f"Connect to {device.alias}", font = ('Arial', 25),
                                   command=lambda device=device_plug: self.connect_to_device(device))
                button.pack()
                self.device_labels.append(button)

            self.device_labels.append(label)




    def connect_to_device(self, selected_device):
        print(f"Connecting to {selected_device.alias}...")
        global connected_devices
        global connected_devices_len
        if(selected_device not in connected_devices):
            connected_devices.append(selected_device)
            connected_devices_len+=1
        # Implement your connection logic here (e.g., turn on/off, change settings, etc.)
        # For example:
        # await selected_device.turn_on()
            print(connected_devices)
            print(f"Connected to {selected_device.alias}!")
        else:
            print(f"{selected_device.alias} is already connected.")


    def go_back(self):
        self.parent.show_frame("FrameOne")


class FrameFive(tk.Frame):
    def __init__(self, parent, gesture_results):
        super().__init__(parent)
        self.parent = parent
        self.device_labels = []
        self.options = [
            'two',
            'L',
            'five',
            'up',
            'down',
            'bunny',
            'fist',
            'B',
            'one',
            'S'
        ]

        # Create a frame for the title and back button
        self.static_frame = tk.Frame(self)
        self.static_frame.pack()

        tk.Label(self.static_frame, text="Gesture Linking", font=('Arial', 25, 'bold')).pack()
        back_button = tk.Button(self.static_frame, text="Back to Home", font = ('Arial', 25),command=self.go_back)
        back_button.pack(side="bottom")

        # Create a frame for the updating widgets
        self.updating_frame = tk.Frame(self)
        self.updating_frame.pack()

        # Initialize the StringVars
        self.on_variables = {}
        self.off_variables = {}

        self.update_connected_devices()

    def update_connected_devices(self):
        # Destroy all current widgets in the updating frame
        for widget in self.updating_frame.winfo_children():
            widget.destroy()

        global devices_on_gesture
        global devices_off_gesture
        devices_on_gesture = {}
        devices_off_gesture = {}

        # Code to update connected devices...
        for device in connected_devices:
            tk.Label(self.updating_frame, text=f"{device.alias} Gestures", font = ('Arial', 25)).pack()

            tk.Label(self.updating_frame, text="Turn On", font = ('Arial', 25)).pack()
            if device.alias not in self.on_variables:
                self.on_variables[device.alias] = tk.StringVar(self.updating_frame)
                self.on_variables[device.alias].set(self.options[0])
            on_option_menu = tk.OptionMenu(self.updating_frame, self.on_variables[device.alias], *self.options,)
            on_option_menu.config(font = ('Arial', 35))
            menu_on = self.nametowidget(on_option_menu.menuname)  # Get menu widget.
            menu_on.config(font=('Arial',25))
            on_option_menu.pack()

            tk.Label(self.updating_frame, text="Turn Off", font = ('Arial', 25)).pack()
            if device.alias not in self.off_variables:
                self.off_variables[device.alias] = tk.StringVar(self.updating_frame)
                self.off_variables[device.alias].set(self.options[0])
            off_option_menu = tk.OptionMenu(self.updating_frame, self.off_variables[device.alias], *self.options)
            off_option_menu.config(font=('Arial', 35))
            menu_off = self.nametowidget(on_option_menu.menuname)  # Get menu widget.
            menu_off.config(font=('Arial', 25))
            off_option_menu.pack()

            devices_on_gesture[device.alias] = self.on_variables[device.alias].get()
            devices_off_gesture[device.alias] = self.off_variables[device.alias].get()

            #print(devices_on_gesture)
            #print(devices_off_gesture)

        # Call this function again after 5000 ms (5 seconds)
        self.after(5000, self.update_connected_devices)



    def go_back(self):
        self.parent.show_frame("FrameOne")


class FrameSix(tk.Frame):
    def __init__(self, parent, gesture_results):
        super().__init__(parent)
        # Add widgets to this frame
        self.parent = parent
        tk.Label(self, text="COMING SOON", font=('Arial', 25, 'bold')).pack()
        back_button = tk.Button(self, text="Back to Home", command=self.go_back)
        back_button.pack(side="bottom")
    def go_back(self):
        self.parent.show_frame("FrameOne")
class FrameSeven(tk.Frame):
    def __init__(self, parent, gesture_results):
        super().__init__(parent)
        self.parent = parent
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(5, weight=1)
        # Add widgets to this frame
        label = tk.Label(self, text="Settings", font=('Arial', 25, 'bold'))
        label.pack()
        label2 = tk.Label(self, text="System Information\n", font=('Arial', 25, 'bold'))
        label3 = tk.Label(self, text="Raspberry Pi Model 4 B\n", font=('Arial', 15))
        label4 = tk.Label(self, text="Version 1.0\n", font=('Arial', 15))
        label5 = tk.Label(self, text="64 GB\n", font=('Arial', 15))
        #label2.pack(pady=10, padx=10)
       # entry1.pack(pady=10, padx=10)
        label2.pack()
        label3.pack()
        label4.pack()
        label5.pack()
        back_button = tk.Button(self, text="Back to Home", command=self.go_back)
        back_button.pack(side="bottom")
    def go_back(self):
        self.parent.show_frame("FrameOne")
# Your existing code here...
def send_image():
    # Welcome to PyShine
    # lets make the client code
    # In this code client is sending video to server
    import socket, cv2, pickle, struct
    import pyshine as ps  # pip install pyshine
    import imutils  # pip install imutils
    camera = True
    if camera == True:
        vid = cv2.VideoCapture(0)
    else:
        vid = cv2.VideoCapture('videos/mario.mp4')
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = '104.196.110.107'  # Here according to your server ip write the address

    port = 3389
    client_socket.connect((host_ip, port))

    if client_socket:
        while (vid.isOpened()):
            try:
                img, frame = vid.read()
                frame = imutils.resize(frame, width=380)
                a = pickle.dumps(frame)
                message = struct.pack("Q", len(a)) + a
                client_socket.sendall(message)
                cv2.imshow(f"TO: {host_ip}", frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    client_socket.close()
            except:
                print('VIDEO FINISHED!')
                break

import time

import select

def run_socket_program(queue, gesture_results):
    vid = cv2.VideoCapture(0)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = '104.196.110.107'  # Here according to your server ip write the address

    port = 3389
    client_socket.connect((host_ip, port))
    global last_gesture

    if client_socket:
        while (vid.isOpened()):
            try:
                img, frame = vid.read()
                frame = imutils.resize(frame, width=380)
                a = pickle.dumps(frame)
                message = struct.pack("Q", len(a)) + a
                client_socket.sendall(message)
                cv2.imshow(f"TO: {host_ip}", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    client_socket.close()

                start_time = time.time()
                while time.time() - start_time < 0.1:  # 100 milliseconds
                    ready = select.select([client_socket], [], [], 0.050)
                    if ready[0]:
                        response_data = client_socket.recv(4 * 1024)
                        gesture_result = response_data.decode()
                        print("Received gesture result:", gesture_result)
                        if(gesture_result != last_gesture):
                            gesture_results.append(gesture_result)
                            last_gesture = gesture_result
                        if len(gesture_results) > 10:  # If more than 10 gestures, remove the oldest one
                            gesture_results.pop(0)
                        print(gesture_results)
                    else:
                        #print("No response from server, moving to next frame.")
                        break

            except:
                print('VIDEO FINISHED!')
                break






            # Read the response size first
import threading
import time
async def update_device(device):
    await device.update()

async def run_check_gesture(gesture_results):
    while True:
        global devices_on_gesture
        global devices_off_gesture
        global connected_devices
        global connected_devices_len
        print(connected_devices_len)
        print(connected_devices)
        gesture_results.reverse()
        devices = await discover_devices()
        for i, (ip, device) in enumerate(devices.items(), start=1):
            if (device.model == 'KL400L5(US)'):
                device_strip = SmartLightStrip(ip)
                try:
                    await device_strip.update()
                except:
                    pass
            if (device.model == 'EP10(US)'):
                device_plug = kasa.SmartPlug(ip)
                try:
                    await device_plug.update()
                except:
                    pass

        if (gesture_results and devices_on_gesture):
            print(gesture_results)
            print(devices_off_gesture)
            if gesture_results[0] == devices_on_gesture['Light']:
                print("Turning on device...")  # Debug print
                try:
                    await turn_on(device_strip)
                except:
                    print("failed to change state")
            elif gesture_results[0] == devices_on_gesture['Plug1']:
                print("Turning on device...")  # Debug print
                try:
                    await turn_on(device_plug)
                except:
                    print("failed to change state")
            elif gesture_results[0] == devices_off_gesture['Light']:
                print("Turning off device...")  # Debug print
                try:
                    await turn_off(device_strip)
                except:
                    print("failed to change state")
            elif gesture_results[0] == devices_off_gesture['Plug1']:
                print("Turning off device...")  # Debug print
                try:
                    await turn_off(device_plug)
                except:
                    print("failed to change state")
            else:
                print("no gesture results")
        await asyncio.sleep(1)  # Sleep for a while before checking again  # Sleep for a while before checking again



# Start the run_check_gesture function in a separate thread






def run_tkinter_program(queue, gesture_results):
    # Your tkinter program code here...
    app = MainApplication(gesture_results)
    app.after(1000,check_queue,app,queue)
    app.mainloop()

def check_queue(app, queue):
    try:
        message = queue.get_nowait()
        if(index != 'FrameFive'):
            app.iconify()  # Minimize the application window
            messagebox.showerror("Connection Error", message)
            app.deiconify()  # Restore the application window
    except Empty:
        pass
    finally:
        app.after(1000, check_queue, app, queue)

import threading
import queue

async def main():
    await asyncio.create_task(run_check_gesture(gesture_results))

if __name__ == '__main__':
    # Create threads for each program
    q = queue.Queue()
    gesture_results = []

    # Create the threads
    thread1 = threading.Thread(target=run_socket_program, args=(q, gesture_results,))
    thread2 = threading.Thread(target=run_tkinter_program, args=(q, gesture_results,))
    # Remove thread3

    # Start the threads
    thread1.start()
    thread2.start()
    # Remove thread3

    # Run the asyncio event loop
    asyncio.run(main())

    # Wait for all threads to finish
    thread1.join()
    thread2.join()

