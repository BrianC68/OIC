import tkinter as tk
from PIL import ImageTk
import os

# Set correct path for Windows or Raspberry Pi(Linux)
if os.name == "nt":
    menu_path = "C:\\Users\\brian\\Documents\\Python\\OIC\\Concessions\\menu\\"
    msg_path = "C:\\Users\\brian\\Documents\\Python\\OIC\\Concessions\\messages\\"
else:
    menu_path = "/home/pi/Concessions/menu/"
    msg_path = "/home/pi/Concessions/messages/"

menu_image = os.listdir(menu_path)
display_msgs = os.listdir(msg_path)
menu_time = 25000
msg_time = 5000

root = tk.Tk()
root.attributes("-fullscreen", True)

menu = ImageTk.PhotoImage(file=f"{menu_path}{menu_image[0]}")
menulabel = tk.Label(root, image=menu)
menulabel.configure(background="#012444", anchor=tk.N)
menulabel.pack(side=tk.TOP, anchor=tk.W, fill=tk.BOTH, expand=True)

def show_msg():
    '''Shows messages from the messages folder for 5 seconds.'''
    request_message()
    menulabel.pack_forget()
    msglabel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    root.after(msg_time, show_menu)

def show_menu():
    '''Shows concessions menu for 30 seconds.'''
    msglabel.pack_forget()
    menulabel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    root.after(menu_time, show_msg)

def message_feed():
    '''Message Generator, yields messages from display_msgs list.'''
    while True:
        for message in display_msgs:
            yield message

display_msg = message_feed()

def request_message():
    '''Requests messages from message_feed() generator.'''
    msg_file = ImageTk.PhotoImage(file=f"{msg_path}{next(display_msg)}")
    msglabel.config(image=msg_file)
    msglabel.image = msg_file

# If there are messages in the messages folder, display the messages after 30 seconds
# If there are no messages, the concessions menu will be displayed constantly
if len(display_msgs) != 0:
    message = ImageTk.PhotoImage(file=f"{msg_path}{display_msgs[0]}")
    msglabel = tk.Label(root, image=message)
    msglabel.configure(background="white")
    root.after(menu_time, show_msg)

root.mainloop()