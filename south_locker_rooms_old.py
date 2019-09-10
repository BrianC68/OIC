import requests
from bs4 import BeautifulSoup
import csv
from datetime import date, timedelta
import os

######################################################################
## This file will be run by cron job every Monday morning @ 4:30 AM ##
######################################################################

today = date.isoformat(date.today()).replace("-", "")

south_rink = []  # list that will hold south rink daily schedule
south_locker_rooms = [[6, 9], [5, 8], 7]  # Locker room numbers in South

def scrape_oic_schedule(date):
    '''Scrape OIC Facility schedule web page and append the days events to north_rink list'''
    url = f"http://wr.maxsolutions.com/files/Weblink/clients/ozaukee/facility_schedule/FS02_{date}.htm"
    # url = f"http://wr.maxsolutions.com/files/Weblink/clients/ozaukee/facility_schedule/FS02_20190112.htm"
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.find_all("tr")
    switch = "off"

    for row in rows:
        if row.find(class_="TblHeadingL1") and "South Rink" in row.find("td").get_text():
            switch = "on"
            continue
        elif row.find(class_="TblHeadingL1") and ("Commit Fitness" in row.find("td").get_text() or
                                                  "Party Room" in row.find("td").get_text() or "North Rink" in row.find("td").get_text()):
            switch = "off"
        elif row.find(class_="Footnote"):
            switch = "off"

        # if switch is on, save event data to south_rink[]
        if switch == "on":
            if row.attrs == {"bgcolor": "#ffffff"}:
                cols = row.find_all("font")
                south_rink.append([cols[0].get_text(), cols[1].get_text(),
                                   cols[2].get_text(), cols[3].get_text()])


def add_locker_rooms_to_schedule(locker_rooms, rink):
    '''Adds locker room assignments dynamically to south_rink list.'''
    # no locker rooms are needed for these events
    no_locker_room = ("Public Skate", "LTS", "Figure Skating")
    # these customers only need locker rooms during games for visiting teams
    need_game_locker_rooms = ("Cedarburg Hockey", "Homestead Hockey", "Lakeshore Lightning",
                              "Concordia ACHA", "Concordia University Men", "Concordia University Women")
    # these events need locker rooms assigned
    # need_locker_rooms = ("NA: South 1", "NA: South 2", "Camp", "Clinic",
    #                      "Game", "Tournament", "Practice", "Open Hockey", "Private", "Roller Hockey",
    #                      "Tryouts")

    lr_flag = 0
    na_south_flag = "on"
    x = 0  # index of rink list for appending locker room numbers
    na_locker_room_flag = False

    for (event, _, _, customer) in rink:
        if event in no_locker_room:
            rink[x].append(" ")
            rink[x].append(" ")
            if na_locker_room_flag == False:
                if lr_flag == 0:
                    lr_flag = 1
                else:
                    lr_flag = 0
                na_locker_room_flag = True
        elif event not in no_locker_room and customer in need_game_locker_rooms:
            # if the event is a practice do not assign locker rooms
            if event == "Practice":
                rink[x].append(" ")
                rink[x].append(" ")
                if lr_flag == 0:
                    lr_flag = 1
                else:
                    lr_flag = 0
            else:
                # if customer is the same, switch lr flag back to previous value
                if customer == rink[x-1][3]:
                    if lr_flag == 0:
                        lr_flag = 1
                    else:
                        lr_flag = 0
                    rink[x].append(locker_rooms[lr_flag][1])
                    rink[x].append(locker_rooms[lr_flag][0])
                elif customer in need_game_locker_rooms:
                    rink[x].append(locker_rooms[lr_flag][1])
                    rink[x].append(locker_rooms[lr_flag][0])
                else:
                    rink[x].append(locker_rooms[lr_flag][1])
                    rink[x].append(locker_rooms[lr_flag][0])
                if lr_flag == 0:
                    lr_flag = 1
                else:
                    lr_flag = 0
        elif event not in no_locker_room:
            if event == "Practice" and "vs" not in customer and customer != "Learn to Play":
                rink[x].append(locker_rooms[lr_flag][1])
                rink[x].append(" ")
            else:
                rink[x].append(locker_rooms[lr_flag][1])
                rink[x].append(locker_rooms[lr_flag][0])
            if event == "NA: South 1" and na_south_flag == "on":
                x += 1
                na_south_flag = "off"
                continue
            elif event == "NA: South 2" and na_south_flag == "on":
                x += 1
                na_south_flag = "off"
                continue
            elif event == "NA: South 2" or event == "NA: South 1" and na_south_flag == "off":
                if lr_flag == 0:
                    lr_flag = 1
                else:
                    lr_flag = 0
            else:
                if lr_flag == 0:
                    lr_flag = 1
                else:
                    lr_flag = 0
        x += 1

def save_schedule_to_file(south, date):
    '''Saves schedule with locker room assignments to CSV file.'''
    if os.name == "nt":
        file_path = f"OIC\\south\\south_lrs_{date}.csv"
    else:
        file_path = f"/home/pi/OIC/south/south_lrs_{date}.csv"

    with open(file_path, "w") as thefile:
        writer = csv.writer(thefile, lineterminator="\n")
        # writer.writerow(
        #     ["Event", "Start", "End", "Customer",  "Home LR", "Visitor LR"])
        for line in south:
            writer.writerow(line)
        # print("South locker rooms saved.")

# week = [today] # holds days of week in the format needed for scrap_oic_schedule() and save_schedule_to_file()

# Append six more days to week[]
# for x in range(1, 7):
#     week.append(date.isoformat(date.today() + timedelta(days=x)).replace("-", ""))

###################### THIS SECTION CAN BE USED TO GET SCHEDULES FOR THE ENTIRE WEEK ######################
# Save locker room schedules for the week, Monday through Sunday
# for day in week:
#     scrape_oic_schedule(day)
#     add_locker_rooms_to_schedule(south_locker_rooms, south_rink)
#     save_schedule_to_file(south_rink, day)
#     south_rink.clear()

# If it is not Saturday or Sunday, scrape and save the schedule to file
if date.weekday(date.today()) != 5 and date.weekday(date.today()) != 6:
    # get data from OIC schedule website
    scrape_oic_schedule(today)
    # add locker rooms to rink schedules
    add_locker_rooms_to_schedule(south_locker_rooms, south_rink)
    # save rink schedules to csv files
    save_schedule_to_file(south_rink, today)

# If it is Friday, scrape and save Saturday and Sunday schedules too
if date.weekday(date.today()) == 4:
    saturday = date.isoformat(date.today() + timedelta(days=1)).replace("-", "")
    south_rink.clear()
    scrape_oic_schedule(saturday)
    add_locker_rooms_to_schedule(south_locker_rooms, south_rink)
    save_schedule_to_file(south_rink, saturday)

    sunday = date.isoformat(date.today() + timedelta(days=2)).replace("-", "")
    south_rink.clear()
    scrape_oic_schedule(sunday)
    add_locker_rooms_to_schedule(south_locker_rooms, south_rink)
    save_schedule_to_file(south_rink, sunday)