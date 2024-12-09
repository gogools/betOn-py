from fuzzywuzzy import fuzz  # needs pip install python-Levenshtein
from selenium import webdriver
from selenium.webdriver.common.by import By

from util import close_whoscore_cover_div, print_table, sort_and_get_row  # my util functions


def get_whoscore_popular_tournament_url(tournament_name: str, country: str) -> str:
    """
        This script is a web crawler that gets the urls of the popular tournaments in whoscored.com
    """

    # preparing options to avoid opening the browser
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')  # Last I checked this was necessary.

    with webdriver.Chrome(options=options) as driver:

        url = 'https://www.whoscored.com/'
        driver.get(url)

        title = driver.title  # Access the <title> element's text content
        print(f"<MSG : Page title: {title.strip()} >")

        close_whoscore_cover_div(driver)

        popular_tournaments_div = driver.find_element(By.CSS_SELECTOR, "div#popular")
        lis = popular_tournaments_div.find_elements(By.CSS_SELECTOR, "li")
        print(f"<MSG : Number of popular tournaments: {len(lis)} >")

        table_data = list()

        print(f"<MSG : Input tournament name: {tournament_name} >")
        for li in lis:
            li_a_text = li.find_element(By.CSS_SELECTOR, "a").text
            li_a_href = li.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

            country_is_there = country in li_a_href
            ratio = fuzz.ratio(tournament_name, li_a_text)
            table_data.append([li_a_text, li_a_href, country_is_there, ratio])

        sort_by_columns = [2, 3]
        reverse = True

        print_table(["Tournament", "Url", "Country Match","Ratio",], table_data, sort_by_columns, reverse)

        return sort_and_get_row(table_data, sort_by_columns, reverse, 0)[1]  # return the url of the first row
