import time

from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz  # needs pip install python-Levenshtein
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from util import print_table, sort_and_get_row  # my util functions


def get_codere_caliente_tournament_url(base_url: str, section_url: str, p_tournament_name: str, p_country: str) -> str:
    """
        This script is a web crawler that gets the urls of the tournaments in codere.mx and caliente.mx
    """
    # preparing options to avoid opening the browser
    options = Options()
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')  # Last I checked this was necessary.

    with webdriver.Firefox(options=options) as driver:
        wait = WebDriverWait(driver, 5)

        url = base_url + section_url

        driver.get(url)
        time.sleep(3)
        source = driver.page_source
        soup = BeautifulSoup(source, 'html.parser')

        title = soup.title.text  # Access the <title> element's text content
        print(f"Page title: {title.strip()}")

        leagues = []

        data_container = soup.select_one("ul.classes")
        print(f"\ndata_container children: {len(data_container.contents)}")

        table_data = list()

        for country in data_container.find_all("li", class_="expander"):

            zone = country.select_one("h4.expander-button").text.replace("\n", "")

            country_leagues = []
            for li in country.select_one("ul.types.expander-content").find_all("li"):
                cl = {"name": li.select_one("div a").text.replace("\n", ""), "url": li.select_one("div a")["href"]}
                country_leagues.append(cl)

            for league in country_leagues:
                country_match = p_country in league["name"]
                ratio_name = fuzz.ratio(p_tournament_name, league["name"])
                table_data.append([zone, league["name"], league["url"], country_match, ratio_name])

        sort_by_columns = [3, 4]
        reverse = True

        print_table(["Zone", "Tournament", "Url", "Country Match", "Ratio Name"], table_data, sort_by_columns, reverse)

        return base_url + sort_and_get_row(table_data, sort_by_columns, reverse, 0)[2]  # return the url of the first row
