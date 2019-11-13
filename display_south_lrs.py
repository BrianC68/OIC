from tkinter import Tk, Frame, Label, LEFT, BOTH, W, E, S, N, TOP, BOTTOM
from PIL import ImageTk
import csv
from datetime import date
import os

today = date.isoformat(date.today()).replace("-", "")
display_date = f"{today[4:6]}-{today[6:]}-{today[0:4]}"
font = "Verdana"
font_size = 28

# Set correct path for Windows and Raspberry Pi(Linux)
if os.name == "nt":
    logo_path = "C:\\Users\\brian\\Documents\\Python\\OIC\\oz_ice_logo.jpg"
    file_path = f"C:\\Users\\brian\\Documents\\Python\\OIC\\south\\south_lrs_{today}.csv"
    msg_path = "C:\\Users\\brian\\Documents\\Python\\OIC\\messages\\"
else:
    logo_path = "/home/pi/OIC/oz_ice_logo.jpg"
    file_path = f"/home/pi/OIC/south/south_lrs_{today}.csv"
    msg_path = "/home/pi/OIC/messages/"

days_of_the_week = {0:"Monday", 1:"Tuesday", 2:"Wednesday", 3:"Thursday", 4:"Friday", 5:"Saturday", 6:"Sunday"}

root = Tk()
root.attributes("-fullscreen", True)

mainframe = Frame(root, bg="#ffffff")
mainframe.pack(side=TOP, fill=BOTH, expand=True)

#Begin first row of display
rinklabel = Label(mainframe, text="South Rink\nLocker Room\nAssignments", font=(font, 32, "bold"), bg="#ffffff")
rinklabel.grid(row=0, columnspan=5, sticky=W, ipadx=200)
oiclogo = ImageTk.PhotoImage(file=logo_path)
oiclabel = Label(mainframe, image=oiclogo, bg="#ffffff")
oiclabel.grid(row=0, columnspan=5, ipady=5)
rinklabel_r = Label(mainframe, text=f"{days_of_the_week[date.weekday(date.today())]}\n{display_date}", font=(font, 32, "bold"), bg="#ffffff")
rinklabel_r.grid(row=0, columnspan=5, sticky=E, ipadx=180)

mainframe.grid_columnconfigure(0, weight=1)
mainframe.grid_columnconfigure(1, weight=1)
mainframe.grid_columnconfigure(2, weight=1)
mainframe.grid_columnconfigure(3, weight=1)
mainframe.grid_columnconfigure(4, weight=1)
#End first row of display

#Start second row of display, title row for locker room assignments
start_title = Label(mainframe, bg="green", fg="#ffffff", text="Start", font=(font, font_size, "bold"))
end_title = Label(mainframe, bg="green", fg="#ffffff", text="End", font=(font, font_size, "bold"))
customer_title = Label(mainframe, bg="green", fg="#ffffff", text="User Group", font=(font, font_size, "bold"))
home_lr_title = Label(mainframe, bg="green", fg="#ffffff", text="Home", font=(font, font_size, "bold"))
visitor_lr_title = Label(mainframe, bg="green", fg="#ffffff", text="Visitor", font=(font, font_size, "bold"))

start_title.grid(row=1, column=0, ipady=10, sticky=W+E)
end_title.grid(row=1, column=1, ipady=10, sticky=W+E)
customer_title.grid(row=1, column=2, ipady=10, sticky=W+E)
home_lr_title.grid(row=1, column=3, ipady=10, sticky=W+E)
visitor_lr_title.grid(row=1, column=4, ipady=10, sticky=W+E)
# End second row of display

events=[] # list that will hold the days events

# Open CSV file with events and locker room assignments
try:
    with open(file_path, "r") as thefile:
        filereader = csv.reader(thefile)
        for row in filereader:
            events.append(row)
        thefile.close()
    # If the days events exceed 12, reduce font size to 24
    if len(events) == 13:
        font_size = 24
    elif len(events) > 13:
        font_size = 20
except FileNotFoundError:
    err_message = Label(mainframe, text="File not found error, call or text Brian Christensen @ 262.339.4402", font=(font, font_size, "bold"), bg="#ffffff", fg="red")
    err_message.grid(row=2, columnspan=6, sticky=S, ipady=10)

# loop through the days events and add them to the display
x = 2 # Use x to start events in row 2 of the grid
# Alternate row colors with the following
blue = "#3b3b6c"
white = "#ffffff"
bg_color = blue
fg_color = white

# Create rows of the days events, alternating BG color and FG color
for event in events:
    for row in event:
        start = Label(mainframe, text=f"{event[1]}", font=(font, font_size, "bold"), bg=f"{bg_color}", fg=f"{fg_color}")
        end = Label(mainframe, text=f"{event[2]}", font=(font, font_size, "bold"), bg=f"{bg_color}", fg=f"{fg_color}")
        customer = Label(mainframe, text=f"{event[3]}", font=(font, font_size, "bold"), bg=f"{bg_color}", fg=f"{fg_color}")
        home_lr = Label(mainframe, text=f"{event[4]}", font=(font, font_size, "bold"), bg=f"{bg_color}", fg=f"{fg_color}")
        visitor_lr = Label(mainframe, text=f"{event[5]}", font=(font, font_size, "bold"), bg=f"{bg_color}", fg=f"{fg_color}")

        start.grid(row=x, column=0, ipady=5, sticky=W+E)
        end.grid(row=x, column=1, ipady=5, sticky=W+E)
        customer.grid(row=x, column=2, ipady=5, sticky=W+E)
        home_lr.grid(row=x, column=3, ipady=5, sticky=W+E)
        visitor_lr.grid(row=x, column=4, ipady=5, sticky=W+E)
    x += 1
    if bg_color == blue:
        bg_color = white
        fg_color = blue
    else:
        bg_color = blue
        fg_color = white

concessions = Label(mainframe, text="<<< Concessions in South Lobby", font=(font, 14, "bold"), bg="#ffffff")
concessions.grid(row=x+1, column=0, columnspan=2, ipady=10)
creator = Label(mainframe, text="Programmed in Python by Brian Christensen for the Ozaukee Ice Center", font=(font, 14, "bold"), bg="#ffffff")
creator.grid(row=x+1, column=2, ipady=10)
proshop = Label(mainframe, text="Proshop in North Lobby >>>", font=(font, 14, "bold"), bg="#ffffff")
proshop.grid(row=x+1, column=3, columnspan=2, ipady=10)

def show_msg():
    '''Shows messages from the messages folder for 5 seconds.'''
    request_message()
    mainframe.pack_forget()
    msg_frame.pack(side=TOP, fill=BOTH, expand=True)
    root.after(5000, show_lrs)

def show_lrs():
    '''Shows locker room schedule for 10 seconds.'''
    msg_frame.pack_forget()
    mainframe.pack(side=TOP, fill=BOTH, expand=True)
    root.after(10000, show_msg)

# construct list of files to be show from ./OIC/messages
display_msgs = os.listdir(msg_path)

def message_feed():
    '''Message Generator, yields messages from display_msgs list.'''
    while True:
        for message in display_msgs:
            yield message

display_msg = message_feed()

def request_message():
    '''Requests messages from message_feed() generator.'''
    msg_file = ImageTk.PhotoImage(file=f"{msg_path}{next(display_msg)}")
    msg.config(image=msg_file)
    msg.image = msg_file

# If there are messages in the message folder, display the messages after 10 seconds
# If there are no messages, the locker room schedule will be displayed constantly
if len(display_msgs) != 0:

    # frame used to swap up message file
    msg_frame = Frame(root, bg="#ffffff")
    msg_rinklabel = Label(msg_frame, text="South Rink\nLocker Room\nAssignments", font=(font, 32, "bold"), bg="#ffffff")
    msg_rinklabel.grid(row=0, columnspan=5, sticky=W, ipadx=200)
    msg_oiclogo = ImageTk.PhotoImage(file=logo_path)
    msg_oiclabel = Label(msg_frame, image=oiclogo, bg="#ffffff")
    msg_oiclabel.grid(row=0, columnspan=5, ipady=5)
    msg_rinklabel_r = Label(msg_frame, text=f"{days_of_the_week[date.weekday(date.today())]}\n{display_date}", font=(font, 32, "bold"), bg="#ffffff")
    msg_rinklabel_r.grid(row=0, columnspan=5, sticky=E, ipadx=180)
    msg_file = ImageTk.PhotoImage(file=f"{msg_path}{display_msgs[0]}")
    msg = Label(msg_frame, image=msg_file, bg="#ffffff")

    msg_frame.grid_columnconfigure(0, weight=1)
    msg_frame.grid_columnconfigure(1, weight=1)
    msg_frame.grid_columnconfigure(2, weight=1)
    msg_frame.grid_columnconfigure(3, weight=1)
    msg_frame.grid_columnconfigure(4, weight=1)
    msg.grid(row=1, column=0, columnspan=5)

    root.after(10000, show_msg)

root.mainloop()
