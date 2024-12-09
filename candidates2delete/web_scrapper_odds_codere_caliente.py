import time

from bs4 import BeautifulSoup
from prettytable import PrettyTable
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait

# preparing options to avoid opening the browser
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')  # Last I checked this was necessary.

with webdriver.Firefox(options=options) as driver:
    wait = WebDriverWait(driver, 5)

    # url = 'https://apuestas.codere.mx/es_MX/t/19157/Premier-League'
    url = 'https://sports.caliente.mx/es_MX/Premier-League'
    # url = 'https://apuestas.codere.mx/es_MX/t/45349/Liga-MX'

    driver.get(url)
    time.sleep(3)
    source = driver.page_source
    soup = BeautifulSoup(source, 'html.parser')
    # print(soup.prettify())

    title = soup.title.text  # Access the <title> element's text content
    print(title.strip())

    find_all_elements = soup.find_all(name="tr", class_=["mkt", "mkt_content"])
    print(f"\ndivs ({len(find_all_elements)}): \n{find_all_elements}")

    select_elements = soup.select("tr.mkt.mkt_content")
    print(f"\ndivs ({len(select_elements)}): \n{select_elements}")

    table = PrettyTable(["Date", "Time", "1", "X", "2", "Home", "Away"])

    for tr in find_all_elements:

        i = 0
        row = {}
        home = ""
        away = ""
        for td in tr.find_all("td"):

            if td["class"] == ["time", "coupon-scoreboard"]:
                row["Date"] = td.find('span', class_='date').text
                row["Time"] = td.find('span', class_='time').text

            if "seln" in td["class"]:

                if i == 0:
                    home = td.select_one("div button span span.seln-label span span.seln-name").text
                    row["1"] = td.select_one("div button span span.price.dec").text
                elif i == 1:
                    row["X"] = td.select_one("div button span span.price.dec").text
                elif i == 2:
                    away = td.select_one("div button span span.seln-label span span.seln-name").text
                    row["2"] = td.select_one("div button span span.price.dec").text

                i += 1

        row["Home"] = home
        row["Away"] = away

        if len(row) != len(table._field_names):
            continue
        else:
            table.add_row(row.values())

    print(table)
