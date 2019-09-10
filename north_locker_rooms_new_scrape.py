import mechanicalsoup
from bs4 import BeautifulSoup
from datetime import date, timedelta

# today = date.isoformat(date.today())
today = "2019-10-12"
north_rink = []

def scrape_oic_schedule(date):
    xx_xx_xxxx = f"{date[5:7]}/{date[8:]}/{date[0:4]}"
    xxxx_xx_xx = f"{date[0:4]},{date[5:7]},{date[8:]}"
    today_with_time = date + "-00-00-00"

    # print(xx_xx_xxxx)
    # print(xxxx_xx_xx)
    # print(today_with_time)

    browser = mechanicalsoup.StatefulBrowser()

    browser.open("https://ozaukeeicecenter.maxgalaxy.net/ScheduleList.aspx?ID=2")

    browser.get_current_page()
    # print(page)
    browser.select_form('form[action="./ScheduleList.aspx?ID=2"]')
    # browser.get_current_form().print_summary()

    browser["ctl00_ContentPlaceHolder1_txtFromDate_dateInput_ClientState"] = '{"enabled":true,"emptyMessage":"","validationText":"'+today_with_time+'","valueAsString":"'+today_with_time+'","minDateStr":"1980-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00","lastSetTextBoxValue":"'+xx_xx_xxxx+'"}'
    browser["ctl00_ContentPlaceHolder1_txtThroughDate_dateInput_ClientState"] = '{"enabled":true,"emptyMessage":"","validationText":"'+today_with_time+'","valueAsString":"'+today_with_time+'","minDateStr":"1980-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00","lastSetTextBoxValue":"'+xx_xx_xxxx+'"}'
    browser["ctl00_ContentPlaceHolder1_cboSortBy_ClientState"] = '{"logEntries":[],"value":"11","text":"Facility","enabled":true,"checkedIndices":[],"checkedItemsTextOverflows":false}'
    browser["ctl00$ContentPlaceHolder1$txtFromDate"] = today
    browser["ctl00$ContentPlaceHolder1$txtFromDate$dateInput"] = xx_xx_xxxx
    browser["ctl00_ContentPlaceHolder1_txtFromDate_calendar_AD"] = '[[1980,1,1],[2099,12,30],['+xxxx_xx_xx+']]'
    browser["ctl00$ContentPlaceHolder1$txtThroughDate"] = today
    browser["ctl00$ContentPlaceHolder1$txtThroughDate$dateInput"] = xx_xx_xxxx
    browser["ctl00_ContentPlaceHolder1_txtThroughDate_calendar_AD"] = '[[1980,1,1],[2099,12,30],['+xxxx_xx_xx+']]'
    browser["ctl00_ContentPlaceHolder1_cboFacility_ClientState"] = '{"logEntries":[],"value":"","text":"North Rink","enabled":true,"checkedIndices":[0],"checkedItemsTextOverflows":false}'
    browser["ctl00$ContentPlaceHolder1$cboFacility"] = 'North Rink'

    response = browser.submit_selected()
    # print(response.text)
    browser.close()

    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        rows = soup.find(class_="clear listTable").find_all('tr')
    except AttributeError:
        return

    for row in rows:
        cols = row.find_all(attrs={"class": "tableColumn borderRight"})
        if len(cols) > 0:
            north_rink.append([cols[5].get_text().strip(), cols[0].get_text().strip(), cols[1].get_text().strip(), cols[4].get_text().strip()])
        # print(cols)

    print(north_rink)

scrape_oic_schedule(today)