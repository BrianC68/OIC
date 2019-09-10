import requests
from bs4 import BeautifulSoup
import mechanicalsoup
import csv
from datetime import date, timedelta
import os

######################################################################
## This file will be run by cron job every morning @ 4:30 AM        ##
######################################################################

today = date.isoformat(date.today())
# today = "2019-10-12" # Used for testing a particular date

south_rink = []  # list that will hold south rink daily schedule
south_locker_rooms = [[6, 9], [5, 8], 7]  # Locker room numbers in South

def scrape_oic_schedule(date):
    '''Scrapes OIC Rink Schedule website for daily schedule of events.'''

    # Format dates for use in form submission
    xx_xx_xxxx = f"{date[5:7]}/{date[8:]}/{date[0:4]}"
    xxxx_xx_xx = f"{date[0:4]},{date[5:7]},{date[8:]}"
    today_with_time = date + "-00-00-00"

    browser = mechanicalsoup.StatefulBrowser()

    browser.open("https://ozaukeeicecenter.maxgalaxy.net/ScheduleList.aspx?ID=2")

    browser.get_current_page()
    # print(page)
    browser.select_form('form[action="./ScheduleList.aspx?ID=2"]')
    # browser.get_current_form().print_summary()

    # The following lines set form fields on the requested page to search for south rink events by date
    browser["ctl00_ContentPlaceHolder1_txtFromDate_dateInput_ClientState"] = '{"enabled":true,"emptyMessage":"","validationText":"'+today_with_time+'","valueAsString":"'+today_with_time+'","minDateStr":"1980-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00","lastSetTextBoxValue":"'+xx_xx_xxxx+'"}'
    browser["ctl00_ContentPlaceHolder1_txtThroughDate_dateInput_ClientState"] = '{"enabled":true,"emptyMessage":"","validationText":"'+today_with_time+'","valueAsString":"'+today_with_time+'","minDateStr":"1980-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00","lastSetTextBoxValue":"'+xx_xx_xxxx+'"}'
    browser["ctl00_ContentPlaceHolder1_cboSortBy_ClientState"] = '{"logEntries":[],"value":"11","text":"Facility","enabled":true,"checkedIndices":[],"checkedItemsTextOverflows":false}'
    browser["ctl00$ContentPlaceHolder1$txtFromDate"] = today
    browser["ctl00$ContentPlaceHolder1$txtFromDate$dateInput"] = xx_xx_xxxx
    browser["ctl00_ContentPlaceHolder1_txtFromDate_calendar_AD"] = '[[1980,1,1],[2099,12,30],['+xxxx_xx_xx+']]'
    browser["ctl00$ContentPlaceHolder1$txtThroughDate"] = today
    browser["ctl00$ContentPlaceHolder1$txtThroughDate$dateInput"] = xx_xx_xxxx
    browser["ctl00_ContentPlaceHolder1_txtThroughDate_calendar_AD"] = '[[1980,1,1],[2099,12,30],['+xxxx_xx_xx+']]'
    browser["ctl00_ContentPlaceHolder1_cboFacility_ClientState"] = '{"logEntries":[],"value":"","text":"South Rink","enabled":true,"checkedIndices":[1],"checkedItemsTextOverflows":false}'
    browser["ctl00$ContentPlaceHolder1$cboFacility"] = 'South Rink'

    response = browser.submit_selected()
    # print(response.text)
    browser.close()

    # Parse the returned page for the days events
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        rows = soup.find(class_="clear listTable").find_all('tr')
    except AttributeError:
        return

    for row in rows:
        cols = row.find_all(attrs={"class": "tableColumn borderRight"})
        if len(cols) > 0:
            south_rink.append([cols[5].get_text().strip(), cols[0].get_text().strip(), cols[1].get_text().strip(), cols[4].get_text().strip()])
        # print(cols) # Used for testing
    # print(south_rink) # Used for testing


def add_locker_rooms_to_schedule(locker_rooms, rink):
    '''Adds locker room assignments dynamically to south_rink list.'''

    # no locker rooms are needed for these events
    no_locker_room = ("Public Skate", "Learn to Skate", "Figure Skating")
    # these customers only need locker rooms during games for visiting teams
    need_game_locker_rooms = ("Cedarburg Hockey", "Homestead Hockey", "Lakeshore Lightning",
                              "Concordia ACHA", "Concordia University Men", "Concordia University Women")
    # these events need locker rooms assigned
    # need_locker_rooms = ("NA: South 1", "NA: South 2", "Camp", "Clinic",
    #                      "Game", "Tournament", "Practice", "Open Hockey", "Private", "Roller Hockey",
    #                      "Tryouts")

    lr_flag = 0 # This variable is used to toggle which locker room pairs to use
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
    
    # Remove dashes from date in filename
    date = date.replace("-", "")
    # Set file path for Windows or Raspberry Pi(Linux)
    if os.name == "nt":
        file_path = f"C:\\Users\\brian\\Documents\\Python\\OIC\\south\\south_lrs_{date}.csv"
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
    saturday = date.isoformat(date.today() + timedelta(days=1))
    south_rink.clear()
    scrape_oic_schedule(saturday)
    add_locker_rooms_to_schedule(south_locker_rooms, south_rink)
    save_schedule_to_file(south_rink, saturday)

    sunday = date.isoformat(date.today() + timedelta(days=2))
    south_rink.clear()
    scrape_oic_schedule(sunday)
    add_locker_rooms_to_schedule(south_locker_rooms, south_rink)
    save_schedule_to_file(south_rink, sunday)