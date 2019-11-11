import csv
import os
from datetime import date
from tkinter import Tk, Label, Entry, messagebox, Frame, TOP, BOTH, E, StringVar, OptionMenu, W, Button, DISABLED

today = date.isoformat(date.today()).replace("-", "")

# Set correct path for Windows and Raspberry Pi
if os.name == "nt":
    lrs_path = "C:\\Users\\brian\\Documents\\Python\\OIC\\north\\"
else:
    lrs_path = "/home/pi/OIC/north/"

def application(files):
    """Main Application: Accepts list of files in the OIC/north directory"""
    font = "Verdana"
    font_size = 10
    root = Tk()
    root.title("Edit North Locker Rooms")
    root.geometry("1000x400")
    entries = []

    def send_file_name():
        """Sends current value of drop down file list to get_file() and saves contents to events variable."""
        if value.get() == "----------------------":
            messagebox.showinfo("Choose File", "Please choose a file to edit.", parent=app_frame)
            return
        elif len(entries) != 0:
            messagebox.showinfo("Warning!", "You must first close the current file!", parent=app_frame)
            return

        events = get_file(value.get())
        # Call display_lr_assignments() and send events file to be displayed in the application window
        display_lr_assignments(events)

    def display_lr_assignments(events):
        """Receives events file and processes items for display in main application window."""
        num = 2 # Row index for use when displaying events, start in row 3
        for x in range(len(events)):
            new_row = []
            for y in range(len(events[x])):
                b = Entry(app_frame, text="")
                b.insert(0, events[x][y])
                # Disable contents of first column as they do not need editing
                if y == 0:
                    b.configure(state=DISABLED)
                b.grid(row=num, column=y)
                new_row.append(b)
            entries.append(new_row)
            num += 1

    def restart():
        """Restarts program when Clear button is pressed."""
        root.destroy()
        # Get list of locker room assignment files and send to main application for displaying
        lr_files = get_locker_room_assgnmnt_files_list()
        application(lr_files)

    def save_to_file():
        """Saves edited locker room assignments to csv file."""
        if value.get() == "----------------------":
            messagebox.showinfo("Choose File", "Please choose a file to edit.", parent=app_frame)
            return
        new_file = [] # save edited information to new_file list for writing to csv file
        for x in range(len(entries)):
            new_row = []
            for y in range(len(entries[x])):
                new_row.append(entries[x][y].get())
            new_file.append(new_row)

        file_to_save = value.get() # get name of file to write edited content to
        file_path = lrs_path + file_to_save
        with open(file_path, "w") as the_file:
            writer = csv.writer(the_file, lineterminator="\n")
            for line in new_file:
                writer.writerow(line)

        messagebox.showinfo("Message", "File has been saved.", parent=app_frame)
        
    app_frame = Frame(root)
    app_frame.pack(side=TOP, fill=BOTH, expand=True, padx=4)

    # Start first row of application
    choose = Label(app_frame, text="Choose file:", font=(font, font_size))
    choose.grid(row=0, column=0, sticky=E)
    value = StringVar(root)
    value.set("----------------------")
    dropdown = OptionMenu(app_frame, value, *files)
    dropdown.grid(row=0, column=1, columnspan=2, sticky=W)
    select = Button(app_frame, text="Open File", command=send_file_name)
    select.grid(row=0, column=3, sticky=W)
    clear = Button(app_frame, text="Close File", command=restart)
    clear.grid(row=0, column=4, sticky=W)
    save_file = Button(app_frame, text="Save File", command=save_to_file)
    save_file.grid(row=0, column=5, sticky=W)
    # End first row of application

    # Start second row of application with column headings
    col1_title = Label(app_frame, text="Event", width=17)
    col2_title = Label(app_frame, text="Start", width=17)
    col3_title = Label(app_frame, text="End", width=17)
    col4_title = Label(app_frame, text="User Group", width=17)
    col5_title = Label(app_frame, text="Home", width=17)
    col6_title = Label(app_frame, text="Away", width=17)

    # Add Second row headings to Frame
    col1_title.grid(row=1, column=0)
    col2_title.grid(row=1, column=1)
    col3_title.grid(row=1, column=2)
    col4_title.grid(row=1, column=3)
    col5_title.grid(row=1, column=4)
    col6_title.grid(row=1, column=5)
    # End second row of application

    root.mainloop()

def get_locker_room_assgnmnt_files_list():
    """Read file names in OIC/north folder"""
    files = os.listdir(lrs_path)
    files.sort(reverse=True) # Sort list newest to oldest
    return files

def get_file(file_to_edit):
    """Open the file to edit and read contents in to events list."""
    events = []
    file_path = lrs_path + file_to_edit
    with open(file_path, "r") as the_file:
        filereader = csv.reader(the_file)
        for row in filereader:
            events.append(row)
        the_file.close()
    return events
    

lr_files = get_locker_room_assgnmnt_files_list()
application(lr_files)