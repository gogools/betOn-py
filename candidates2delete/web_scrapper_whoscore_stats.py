import re

# beautiful soup
from bs4 import BeautifulSoup  # pip install lxml in order to use the lxml parser
# selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

# mine
from util import close_whoscore_cover_div, click_select_option, click_element_xpath, wait_til_filled


def get_all_teams_stats(tournament_url: str, year: str) -> dict:
    """
        This script is a web crawler_scrapper that gets the team stats from whoscored.com
    """

    # preparing options to avoid opening the browser
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')  # Last I checked this was necessary.
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 "
        "Safari/537.36")

    try:
        with webdriver.Chrome(options=options) as driver:

            url = tournament_url
            driver.get(url)

            title = driver.title  # Access the <title> element's text content
            print(f"Page title: {title.strip()}")

            close_whoscore_cover_div(driver)

            click_select_option(driver, "seasons", f".*{year}$", True)

            click_element_xpath(driver, "//div[@id='sub-navigation']//a[text()='Team Statistics']", wait_after=2)

            click_element_xpath(driver, "//div[@id='stage-team-stats']//a[text()='Detailed']", wait_after=2)

            click_select_option(driver, "statsAccumulationType", "Total")

            click_element_xpath(driver, "//div[@id='filter-options']//button[text()='Search']", wait_after=3)

            wait_til_filled(driver, "//div[@id='statistics-team-table-detailed']")

            # let's get the statistics table
            # Locate the table element and then use beautiful soup to parse it
            table_element = driver.find_element(By.CSS_SELECTOR,"table#top-team-stats-summary-grid")
            soup = BeautifulSoup(table_element.get_attribute("outerHTML"), "lxml")
            stats = []
            for row in soup.find("table").find("tbody").find_all("tr"):
                cells = row.find_all("td") # currently: Team, Total, OutOfBox, SixYardBox,PenaltyArea, Rating
                row_data = {"rank": cells[0].text.strip().split(". ")[0],
                            "team": cells[0].text.strip().split(". ")[1],
                            "total": cells[1].text.strip(),
                            "outOfBox": cells[2].text.strip(),
                            "sixYardBox": cells[3].text.strip(),
                            "penaltyArea": cells[4].text.strip(),
                            "rating": cells[5].text.strip()}
                stats.append(row_data)

            # now let's get the legend info
            legend_div = driver.find_element(By.CSS_SELECTOR, "div.table-column-legend.info")
            soup = BeautifulSoup(legend_div.get_attribute("outerHTML"), "lxml")
            legends = []
            for l_div in soup.find("div").find_all("div"):
                l_div.text.strip()
                div_text = re.sub(r"<strong>|</strong>", "", l_div.text.strip())
                legends.append(div_text)

            return {"stats": stats, "legends": legends}

    except NoSuchElementException as e:
        print(f"<EXC---[Element not found] : {str(e)}]--->")
