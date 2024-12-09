import re

# beautiful soup
from bs4 import BeautifulSoup  # pip install lxml in order to use the lxml parser
# fuzzywuzzy
from fuzzywuzzy import fuzz  # needs pip install python-Levenshtein
# selenium
from selenium.webdriver.common.by import By

from crawler_scrapper import AbstractCrawlerNavScrapper
# util
from util import click_element_xpath_by_script, click_element_by_script, wait_til_filled, msg, get_whole_table, url_id


class FBrefLeaguesStatsScrapper(AbstractCrawlerNavScrapper):

    base_url = "https://fbref.com/en/"
    REGEX = "comps/.*"

    def __init__(self, hide_browser: bool = True, tournament: str = None, season: str = None):
        super().__init__(hide_browser)
        self.tournament = tournament
        self.season = season

    def _validate_required_fields(self) -> bool:
        if self.base_url == self.driver.current_url:
            return self.tournament is not None and self.season is not None
        else:
            return True

    def _navigate(self):
        msg(f"About to navigate page {self.driver.current_url}")

        title = self.driver.title  # Access the <title> element's text content
        msg(f"Page title: {title.strip()}")

        # click on "Competitions" link
        msg(f"Clicking {self.driver.find_element(By.XPATH, '//li[@id="header_comps"]//a').text}")
        click_element_xpath_by_script(self.driver, "//li[@id='header_comps']//a")

        wait_til_filled(self.driver, "//table[@id='comps_1_fa_club_league_senior']")

        a_domestic_list_xpath = "//table[@id='comps_1_fa_club_league_senior']//tbody//tr//th//a"
        a_list = self.driver.find_elements(By.XPATH, a_domestic_list_xpath)

        msg(f"Found {len(a_list)} tournaments")
        for a in a_list:
            # print(f"ratio:{fuzz.ratio(self.tournament, a.text)}, <a>: {a.get_attribute("outerHTML")}")
            if fuzz.ratio(self.tournament.lower(), a.text.lower()) > 90:
                msg(f"Clicking on {a.text}")
                click_element_by_script(self.driver, a)
                break

        wait_til_filled(self.driver, "//table[@id='seasons']")

        a_seasons_list_xpath = "//table[@id='seasons']//tbody//tr//th//a"
        a_season_list = self.driver.find_elements(By.XPATH, a_seasons_list_xpath)

        msg(f"Found {len(a_season_list)} seasons for {self.tournament}")
        for a in a_season_list:
            # print(f"ratio:{fuzz.ratio(self.season, a.text)}, <a>: {a.get_attribute("outerHTML")}")
            if fuzz.ratio(self.season.lower(), a.text.lower()) > 90:
                msg(f"Clicking on {a.text}")
                click_element_by_script(self.driver, a, wait_after=3)
                return  # we found the tournament and season, so we can return

        raise Exception(f"There was no match for tournament:{self.tournament} "
                        f"and season:{self.season}")

    def _scrap(self) -> dict:

        page_source = self.driver.page_source
        self.soup = BeautifulSoup(page_source, "html.parser")

        season = None
        meta_tag = self.soup.find("meta", attrs={'name': 'Description'})
        if meta_tag is not None:
            search = re.search(r"\d{4}-\d{4}", meta_tag['content'])
            if search is not None:
                season = search.group(0)

        msg(f"Scraping url:{self.driver.current_url}")
        last_char_index = self.driver.current_url.rfind('/')
        msg(f"Tournament: {self.tournament if last_char_index < 0 else self.driver.current_url[last_char_index + 1:]}")
        msg(f"Season: {season}")

        url = self.driver.current_url
        return {
            "current_url": url,
            "scores_fixtures_url": f"{self.driver.find_element(By.XPATH, "//li//div//section//p//a[text()='Scores & Fixtures']").get_attribute("href")}",
            "regular_season_overall": get_whole_table(self.soup.find("table", id=f"results{season}{url_id(self.driver.current_url)}1_overall"), url),
            "regular_season_home_away": get_whole_table(self.soup.find("table", id=f"results{season}{url_id(self.driver.current_url)}1_home_away"), url),
            "squad_standard_stats": get_whole_table(self.soup.find("table", id=f"stats_squads_standard_for"), url),
            "opponent_standard_stats": get_whole_table(self.soup.find("table", id=f"stats_squads_standard_against"), url),
            "squad_goalkeeping": get_whole_table(self.soup.find("table", id=f"stats_squads_keeper_for"), url),
            "opponent_goalkeeping": get_whole_table(self.soup.find("table", id=f"stats_squads_keeper_against"), url),
            "squad_advanced_goalkeeping": get_whole_table(self.soup.find("table", id=f"stats_squads_keeper_adv_for"), url),
            "opponent_advanced_goalkeeping": get_whole_table(self.soup.find("table", id=f"stats_squads_keeper_adv_against"), url),
            "squad_shooting": get_whole_table(self.soup.find("table", id=f"stats_squads_shooting_for"), url),
            "opponent_shooting": get_whole_table(self.soup.find("table", id=f"stats_squads_shooting_against"), url),
            "squad_possession": get_whole_table(self.soup.find("table", id=f"stats_squads_possession_for"), url),
            "opponent_possession": get_whole_table(self.soup.find("table", id=f"stats_squads_possession_against"), url)
        }
