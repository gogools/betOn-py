# beautiful soup
from bs4 import BeautifulSoup  # pip install lxml in order to use the lxml parser
# fuzzywuzzy
from fuzzywuzzy import fuzz  # needs pip install python-Levenshtein
# selenium
from selenium.webdriver.common.by import By

# util
from util import click_element_xpath_by_script, click_element_by_script, build_url, wait_til_filled, msg, val
# mine
from .AbstractCrawlerNavScrapper import AbstractCrawlerNavScrapper


class FBrefInternationalCompsStatsScrapper(AbstractCrawlerNavScrapper):

    base_url = "https://fbref.com/en/"
    REGEX = "comps/.*"

    def __init__(self, hide_browser: bool = True, competition: str = None, year: str = None):
        super().__init__(hide_browser)
        self.competition = competition
        self.year = year

    def _validate_required_fields(self) -> bool:
        return self.competition is not None and self.year is not None

    def _navigate(self):
        msg(f"About to navigate page {self.driver.current_url}")

        title = self.driver.title
        msg(f"Page title: {title.strip()}")

        # click on "Competitions" link
        click_element_xpath_by_script(self.driver, "//li[@id='header_comps']//a")

        wait_til_filled(self.driver, "//table[@id='comps_intl_fa_nonqualifier_senior']")

        a_domestic_list_xpath = "//table[@id='comps_intl_fa_nonqualifier_senior']//tbody//tr//th//a"
        c_list = self.driver.find_elements(By.XPATH, a_domestic_list_xpath)

        msg(f"Found {len(c_list)} competitions")
        for c in c_list:
            msg(f"Competition ratio: {fuzz.ratio(self.competition.lower(), c.text.lower())}, <a>: {c.text}")
            if fuzz.ratio(self.competition.lower(), c.text.lower()) > 90:
                msg(f"Clicking on {c.text}")
                click_element_by_script(self.driver, c)
                break

        wait_til_filled(self.driver, "//table[@id='seasons']")

        a_year_list_xpath = "//table[@id='seasons']//tbody//tr//th//a"
        a_year_list = self.driver.find_elements(By.XPATH, a_year_list_xpath)

        msg(f"Found {len(a_year_list)} years for {self.competition}")
        for y in a_year_list:
            msg(f"ratio:{fuzz.ratio(self.year.lower(), y.text.lower())}, <a>: {y.text}")
            if fuzz.ratio(self.year.lower(), y.text.lower()) > 90:
                msg(f"Clicking on {y.text}")
                click_element_by_script(self.driver, y, wait_after=3)
                break

        wait_til_filled(self.driver, "//div[@id='all_Group stage']")

    def _scrap(self) -> dict:

        page_source = self.driver.page_source
        self.soup = BeautifulSoup(page_source, "html.parser")

        msg(f"Scraping url:{self.driver.current_url}")
        msg(f"Competition: {self.competition}")
        msg(f"Season: {self.year}")

        return {
            "current_url": self.driver.current_url,
            "group_stage": self.fetch_group_stage_data(),
            "leaders": self.fetch_leaders_tables()
        }

    def fetch_group_stage_data(self) -> list:
        msg(f"fetch_group_stage_data()")

        group_stage_xpath = "//div[@id='div_Group stage']//div[contains(@class,'table_wrapper')]"
        group_stage_list = self.driver.find_elements(By.XPATH, group_stage_xpath)

        if group_stage_list is None or len(group_stage_list) == 0:
            return []

        stats = []

        for group_stage in group_stage_list:
            group_stage_id = group_stage.get_attribute("id")
            gs_div = self.soup.find("div", id=group_stage_id)

            group_name = gs_div.find("div", class_="section_heading").find("h3").text

            group = {}
            teams = []
            for row in gs_div.find("table", class_="stats_table").find("tbody").find_all("tr"):
                first_cell = row.find("th")
                tds = row.find_all("td")

                if len(tds) < 14:
                    continue

                team_data = {
                    "rk": int(0 if len(first_cell.text) == 0 else first_cell.text),
                    "squad": tds[0].find("a").text,
                    "squad_url": build_url(self.driver.current_url, tds[0].find("a")["href"]),
                    "MP": int(0 if len(tds[1].text) == 0 else tds[1].text),
                    "W": int(0 if len(tds[2].text) == 0 else tds[2].text),
                    "D": int(0 if len(tds[3].text) == 0 else tds[3].text),
                    "L": int(0 if len(tds[4].text) == 0 else tds[4].text),
                    "GF": int(0 if len(tds[5].text) == 0 else tds[5].text),
                    "GA": int(0 if len(tds[6].text) == 0 else tds[6].text),
                    "GD": int(0 if len(tds[7].text) == 0 else tds[7].text),
                    "Pts": int(0 if len(tds[8].text) == 0 else tds[8].text),
                    "xG": float(0 if len(tds[9].text) == 0 else tds[9].text),
                    "xGA": float(0 if len(tds[10].text) == 0 else tds[10].text),
                    "xGD": float(0 if len(tds[11].text) == 0 else tds[11].text),
                    "xGD/90": float(0 if len(tds[12].text) == 0 else tds[12].text),
                    "notes": tds[13].text
                }

                teams.append(team_data)

            group["group_name"] = group_name
            group["teams"] = teams
            stats.append(group)

        return stats

    def fetch_leaders_tables(self) -> dict:
        msg(f"fetch_leaders_tables()")

        leader_divs_xpath = "//div[@id='div_leaders']//div[contains(@class,'data_grid_box')]"
        leader_div_list = self.driver.find_elements(By.XPATH, leader_divs_xpath)

        results = {}

        for div in leader_div_list:
            table = self.soup.find("div", id=div.get_attribute("id")).find("table")

            caption = table.find("caption").text
            table_list = []
            rank = 0
            for tr in table.find("tbody").find_all("tr"):
                rank += 1
                who = tr.find("td", class_="who").find("a").text
                who_url = self.base_url[0: self.base_url.find("/en/")] + tr.find("td", class_="who").find("a")["href"]
                value = val(tr.find("td", class_="value").text)
                table_list.append({"rank": rank, "who": who, "who_url": who_url, "value": value})

            results[caption] = table_list

        return results
