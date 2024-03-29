import requests
from bs4 import BeautifulSoup
import mechanicalsoup
import csv
from datetime import date, timedelta
import os

######################################################################
## This file will be run by cron job every morning @ 4:30 AM        ##
######################################################################

months = {"01": "January", "02": "February", "03": "March", "04": "April", "05": "May", 
            "06": "June", "07": "July", "08": "August", "09": "September", "10": "October", "11": "November", "12": "December"}

today = date.isoformat(date.today())
# today = "2019-10-12" # Used for testing a particular date

south_rink = []  # list that will hold south rink daily schedule
south_locker_rooms = [[6, 9], [5, 8], 7]  # Locker room numbers in South
cuw_acha_locker_room = 7

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
    browser["ctl00_ContentPlaceHolder1_cboSortBy_ClientState"] = '{"logEntries":[],"value":"2","text":"Start Time","enabled":true,"checkedIndices":[],"checkedItemsTextOverflows":false}'
    browser["ctl00$ContentPlaceHolder1$txtFromDate"] = today
    browser["ctl00$ContentPlaceHolder1$txtFromDate$dateInput"] = xx_xx_xxxx
    browser["ctl00_ContentPlaceHolder1_txtFromDate_calendar_AD"] = '[[1980,1,1],[2099,12,30],['+xxxx_xx_xx+']]'
    browser["ctl00_ContentPlaceHolder1_txtFromDate_calendar_SD"] = '[['+xxxx_xx_xx+']]'
    browser["ctl00$ContentPlaceHolder1$txtThroughDate"] = today
    browser["ctl00$ContentPlaceHolder1$txtThroughDate$dateInput"] = xx_xx_xxxx
    browser["ctl00_ContentPlaceHolder1_txtThroughDate_calendar_AD"] = '[[1980,1,1],[2099,12,30],['+xxxx_xx_xx+']]'
    browser["ctl00_ContentPlaceHolder1_txtThroughDate_calendar_SD"] = '[['+xxxx_xx_xx+']]'
    browser["ctl00_ContentPlaceHolder1_cboFacility_ClientState"] = '{"logEntries":[],"value":"","text":"3 items checked","enabled":true,"checkedIndices":[5,6,7],"checkedItemsTextOverflows":true}'
    browser["ctl00$ContentPlaceHolder1$cboFacility"] = 'South 1, South 2, South Rink'

    response = browser.submit_selected()
    html = response.text.replace('</br>', '').replace('<br>', '')
    browser.close()

    # Parse the returned page for the days events
    soup = BeautifulSoup(html, 'html.parser')
    try:
        rows = soup.find(class_="clear listTable").find_all('tr')
    except AttributeError:
        return
    # print(rows)
    for row in rows:
        cols = row.find_all(attrs={"class": "tableColumn borderRight"})
        if len(cols) > 0:
            south_rink.append([cols[5].get_text().strip(), cols[0].get_text().strip(), cols[1].get_text().strip(), cols[4].get_text().strip(), cols[3].get_text().strip()])
        # print(cols) # Used for testing
    # print(south_rink) # Used for testing

def scrape_oyha_teams(the_date):
    '''Scrapes OIC Rink League Schedule website for OYHA and Opponent teams.'''

    oyha_events = [] # list that will hold OYHA teams to merge with south_rink[]
    today_split = the_date.split("-")
    today_string = f"{months[today_split[1]]} {today_split[2].lstrip('0')}, {today_split[0]}"

    url = "https://ozaukeeicecenter.maxgalaxy.net/LeagueScheduleList.aspx?ID=13"
    response = requests.get(url)

    # Request the web page
    soup = BeautifulSoup(response.text, "html.parser")
    # Get all div's with class = "activityGroupName"
    dates = soup.find_all(class_="activityGroupName")

    # Loop through and find today's date then find the next table with the days events
    table = []
    for each in dates:
        if today_string in each.get_text():
            table = each.find_next("table")

    # Get all rows from the table
    if len(table) == 0:
        return
    else:
        rows = table.find_all("tr")

    # Collect pertinent data from the rows
    for row in rows:
        cols = row.find_all("td")
        # If it's the header row or it's for North Rink, skip the row
        if cols[0].get_text().strip() == "Start Time" or cols[3].get_text().strip() in ["North Rink", "North 1", "North 2", "North 3"]:
            continue
        else:
            oyha_events.append([cols[0].get_text().strip(), cols[6].get_text().strip(), cols[4].get_text().strip(), cols[3].get_text().strip()])

    # Merge OYHA team names with south_rink[] list of events
    # If oyha_events[] list is empty, skip the merge
    if len(oyha_events) == 0:
        pass
    else:
        for event in oyha_events:
            for item in south_rink:
                if event[0] == item[1] and event[3] == item[4]:
                    if event[2] == "":
                        item[3] = event[1]
                    else:
                        item[3] = f"{event[1]} vs {event[2]}"

    # Replace some strings so the Locker Room Display board displays correctly 
    for item in south_rink:
        if "Ozaukee Youth Hockey Association" in item[3] or item[3] == "":
            item[3] = "OYHA"
            # Adds teams who are practicing to display
            # if  "Practice-" in item[0]:
            #     item[3] += f'{item[0].replace("Practice-", " ")}'
        elif "Wisconsin Elite Hockey League" in item[3]:
            item[3] = "WEHL"
        elif "OWHL" in item[3]:
            item[3] = "OWHL"


def scrape_ochl_games():
    '''Scrapes OCHL League Schedule website for OCHL teams.'''

    ochl_games = [] # List that will hold OCHL game data for South Rink

    url = "https://www.ozaukeeicecenter.org/schedule/day/league_instance/128332?subseason=714101"
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")
    # Get game schedule table
    table = soup.find(class_="statTable")
    # Get table body which contains game or practice rows
    tbody = table.find_next("tbody")

    # Get the rows
    rows = tbody.find_all("tr")

    # Get the data from the pertinent table cells: home, visitor, rink, start time
    for row in rows:
        cols = row.find_all("td")
        if "South Rink" in cols[4].get_text():
            ochl_games.append([cols[2].find("a").get_text(), cols[0].find("a").get_text(), cols[4].find("div").get_text().strip(), cols[5].find("span").get_text().strip(" CDT").strip(" CST")])

    # Merge OCHL games with south_rink[] list of events
    # If ochl_games[] list is empty, skip the merge
    if len(ochl_games) == 0:
        pass
    else:
        for game in ochl_games:
            for item in south_rink:
                if game[3] == item[1]:
                    item[3] = f"{game[0]} vs {game[1]}"


def add_locker_rooms_to_schedule(locker_rooms, rink):
    '''Adds locker room assignments dynamically to south_rink list.'''

    # no locker rooms are needed for these events
    no_locker_room = ("Public Skate", "Learn to Skate", "Open Figure Skating", "Kettle Moraine Figure Skating Club")
    # these customers only need locker rooms during games for visiting teams
    need_game_locker_rooms = ("Cedarburg Hockey", "Homestead Hockey", "Lakeshore Lightning",
                              "Concordia ACHA", "Concordia University Men", "Concordia University Women")

    lr_flag = 0 # This variable is used to toggle which locker room pairs to use
    na_south_flag = "on"
    x = 0  # index of rink list for appending locker room numbers
    na_locker_room_flag = False

    for (event, _, _, customer) in rink:
        if event == "Practice": # Added this check for COVID-19, remove when locker rooms are assigned to practices again.
            rink[x].append(" ")
            rink[x].append(" ")
            x += 1
            continue
        elif customer in no_locker_room:
            rink[x].append(" ")
            rink[x].append(" ")
            if na_locker_room_flag == False:
                if lr_flag == 0:
                    lr_flag = 1
                else:
                    lr_flag = 0
                na_locker_room_flag = True
        elif customer not in no_locker_room and customer in need_game_locker_rooms:
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
                    # rink[x].append(locker_rooms[lr_flag][1])
                    if customer == "Concordia ACHA":
                        rink[x].append(cuw_acha_locker_room)
                    else:
                        rink[x].append(" ")
                    rink[x].append(locker_rooms[lr_flag][0])
                else:
                    rink[x].append(locker_rooms[lr_flag][1])
                    rink[x].append(locker_rooms[lr_flag][0])
                if lr_flag == 0:
                    lr_flag = 1
                else:
                    lr_flag = 0
        elif customer not in no_locker_room:
            if  "Practice" in event and "vs" not in customer and customer != "Learn to Play":
                if "Mite" in customer:
                    rink[x].append(locker_rooms[lr_flag][1])
                    rink[x].append(locker_rooms[lr_flag][0])
                else:
                    rink[x].append(locker_rooms[lr_flag][1])
                    rink[x].append(" ") # THIS SHOULD BE USED WHEN "TEAM VS TEAM" COMES BACK ON THE SCHEDULE
                    # rink[x].append(locker_rooms[lr_flag][0])
            else:
                rink[x].append(locker_rooms[lr_flag][1])
                rink[x].append(locker_rooms[lr_flag][0])
            # Check for mite practices and games and keep the same locker rooms for split ice
            if "Mite" in customer and na_south_flag == "on": # Removed (and "vs" in customer) condition in case only one mite team is practicing
                x += 1
                na_south_flag = "off"
                continue
            elif "Mite" in customer and na_south_flag == "off": # Removed (and "vs" in customer) condition in case only one mite team is practicing
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

###################### THIS SECTION CAN BE USED TO GET SCHEDULES FOR THE ENTIRE WEEK ######################

# week = [today] # holds days of week in the format needed for scrap_oic_schedule() and save_schedule_to_file()

# Append six more days to week[]
# for x in range(1, 7):
#     week.append(date.isoformat(date.today() + timedelta(days=x)).replace("-", ""))

# Save locker room schedules for the week, Monday through Sunday
# for day in week:
#     scrape_oic_schedule(day)
#     add_locker_rooms_to_schedule(south_locker_rooms, south_rink)
#     save_schedule_to_file(south_rink, day)
#     south_rink.clear()
###########################################################################################################

# If it is not Saturday or Sunday, scrape and save the schedule to file
if date.weekday(date.today()) != 5 and date.weekday(date.today()) != 6:
    # get data from OIC schedule website
    scrape_oic_schedule(today)
    # add OYHA teams to south_rink[]
    # try:
    #     scrape_oyha_teams(today)
    # except Exception as e:
    #     print(f"{e}, scrape_oyha_teams(today)")
    # Remove rink from south_rink before adding locker room assignments
    for item in south_rink:
        item.pop()
        # Add blank locker room assignments
        # item.append('')
        # item.append('')
    # add locker rooms to rink schedules
    add_locker_rooms_to_schedule(south_locker_rooms, south_rink)
    # save rink schedules to csv files
    save_schedule_to_file(south_rink, today)

# If it is Friday, scrape and save Saturday and Sunday schedules too
if date.weekday(date.today()) == 4:
    saturday = date.isoformat(date.today() + timedelta(days=1))
    south_rink.clear()
    scrape_oic_schedule(saturday)
    # try:
    #     scrape_oyha_teams(saturday)
    # except Exception as e:
    #     print(f"{e}, scrape_oyha_teams(saturday)")
    # Remove rink from south_rink before adding locker room assignments
    for item in south_rink:
        item.pop()
        # Add blank locker room assignments
        # item.append('')
        # item.append('')
    add_locker_rooms_to_schedule(south_locker_rooms, south_rink)
    save_schedule_to_file(south_rink, saturday)

    sunday = date.isoformat(date.today() + timedelta(days=2))
    south_rink.clear()
    scrape_oic_schedule(sunday)
    # try:
    #     scrape_oyha_teams(sunday)
    # except Exception as e:
    #     print(f"{e}, scrape_oyha_teams(sunday)")
    try:
        scrape_ochl_games()
    except Exception as e:
        print(f"{e}, scrape_ochl_games(sunday)")
    # Remove rink from south_rink before adding locker room assignments
    for item in south_rink:
        item.pop()
        # Add blank locker room assignments
        # item.append('')
        # item.append('')
    add_locker_rooms_to_schedule(south_locker_rooms, south_rink)
    save_schedule_to_file(south_rink, sunday)
