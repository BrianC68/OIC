from kivy.app import App
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.uix.image import AsyncImage
from datetime import date, timedelta
from kivy.core.window import Window
import requests
from bs4 import BeautifulSoup

# today = date.isoformat(date.today())
# today = today.split("-")
# today = [today[1], today[2], today[0]]
# today = "-".join(today)

# text = f"[b]{today}[/b]"

class ScheduleApp(App):
    def build(self):
        Window.clearcolor = (1,1,1,1)
        schedule = Carousel(direction="right")
        image = AsyncImage(source="ozlogo_shadow_small.jpg")
        schedule.add_widget(image)
        sch_label_text = ""

        for x in range(0, 11):
            the_date = date.isoformat(date.today() + timedelta(days=x))
            sch_date = the_date.replace("-", "")
            the_date = the_date.split("-")
            the_date = [the_date[1], the_date[2], the_date[0]]
            the_date = "-".join(the_date)
            scrape_oic_schedule(sch_date)
            sch_label_text = "\n[b]North Rink[/b]\n"
            for n in range(len(north_rink)):
                sch_label_text += f"{north_rink[n][0]} to {north_rink[n][1]} - {north_rink[n][2]}\n"
            sch_label_text += "\n[b]South Rink[/b]\n"
            for s in range(len(south_rink)):
                sch_label_text += f"{south_rink[s][0]} to {south_rink[s][1]} - {south_rink[s][2]}\n"
            sch_label_text += "[/color]"
            my_label = Label(text=f"[color='#000000'][b]{the_date}[/b]\n[size=10]{sch_label_text}[/size][/color]", markup=True, halign="center", valign="top")
            schedule.add_widget(my_label)
            sch_label_text = ""
            north_rink.clear()
            south_rink.clear()

        return schedule

north_rink = []  # list that will hold north rink daily schedule
south_rink = []

def scrape_oic_schedule(date):
    '''Scrape OIC Facility schedule web page and append the days events to north_rink list'''
    url = f"http://wr.maxsolutions.com/files/Weblink/clients/ozaukee/facility_schedule/FS02_{date}.htm"
    # url = f"http://wr.maxsolutions.com/files/Weblink/clients/ozaukee/facility_schedule/FS02_20190217.htm"
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.find_all("tr")
    switch = "off"
    rink = ""

    for row in rows:
        if row.find(class_="TblHeadingL1") and "North Rink" in row.find("td").get_text():
            switch = "on"
            rink = "North"
            continue
        if row.find(class_="TblHeadingL1") and "South Rink" in row.find("td").get_text():
            switch = "on"
            rink = "South"
            continue
        elif row.find(class_="TblHeadingL1") and ("Commit Fitness" in row.find("td").get_text() or
                                                  "Party Room" in row.find("td").get_text()):
            switch = "off"
        elif row.find(class_="Footnote"):
            switch = "off"

        # if switch is on, save event data to north_rink[]
        if switch == "on" and rink == "North":
            if row.attrs == {"bgcolor": "#ffffff"}:
                cols = row.find_all("font")
                north_rink.append([cols[1].get_text(), cols[2].get_text(), cols[3].get_text()])

        if switch == "on" and rink == "South":
            if row.attrs == {"bgcolor": "#ffffff"}:
                cols = row.find_all("font")
                south_rink.append([cols[1].get_text(), cols[2].get_text(), cols[3].get_text()])


ScheduleApp().run()
