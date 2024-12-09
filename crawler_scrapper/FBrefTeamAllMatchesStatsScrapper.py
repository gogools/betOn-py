import time

# beautiful soup
from bs4 import BeautifulSoup  # pip install lxml in order to use the lxml parser
# fuzzywuzzy
from fuzzywuzzy import fuzz  # needs pip install python-Levenshtein
from selenium.webdriver.common.by import By

from util import click_element_xpath_by_script, click_element_by_script, wait_til_filled, CELL_404, get_table_data, \
    get_whole_table
# mine
from util import msg
from .AbstractCrawlerNavScrapper import AbstractCrawlerNavScrapper


class FBrefTeamAllMatchesStatsScrapper(AbstractCrawlerNavScrapper):
    base_url = "https://fbref.com/en/"
    REGEX = "squads/.*"

    def __init__(self, hide_browser: bool = True, country: str = None, tournament: str = None, season: str = None, squad: str = None,):
        super().__init__(hide_browser)
        self.country = country
        self.tournament = tournament
        self.season = season
        self.squad = squad

    def _validate_required_fields(self) -> bool:

        if self.base_url == self.driver.current_url:
            return (self.country is not None and
                    self.tournament is not None and
                    self.squad is not None and
                    self.season is not None)
        else:
            return self.tournament is not None

    def _navigate(self):
        msg(f"About to navigate page {self.driver.current_url}")

        title = self.driver.title  # Access the <title> element's text content
        msg(f"Page title: {title.strip()}")

        # click on "Clubs" link
        click_element_xpath_by_script(self.driver, "//li[@id='header_clubs']//a", 7)

        wait_til_filled(self.driver, "//table[@id='countries']")

        country_list_xpath = "//table[@id='countries']//tbody//tr//th//strong//a"
        country_list = self.driver.find_elements(By.XPATH, country_list_xpath)

        msg(f"Found {len(country_list)} countries")
        country_fc = self.country + " Football Clubs"
        for c in country_list:
            msg(f"country ratio:{fuzz.ratio(country_fc.lower(), c.text.lower())}, <a>: {c.text}")
            if fuzz.ratio(country_fc.lower(), c.text.lower()) > 85:
                msg(f"Clicking {c.text}")
                click_element_by_script(self.driver, c, 7)
                break

        wait_til_filled(self.driver, "//table[@id='clubs']")

        squad_list_xpath = "//table[@id='clubs']//tbody//tr[not(@class='thead')]"
        squad_list = self.driver.find_elements(By.XPATH, squad_list_xpath)

        msg(f"Found {len(squad_list)} squads in {country_fc}")
        for s in squad_list:
            row_t = s.find_element(By.XPATH, ".//td[@data-stat='comp']")  # tournament

            if len(row_t.text) == 0:
                continue

            msg(f"tournament ratio:{fuzz.ratio(self.tournament.lower(), row_t.text.lower())}, <a>: {row_t.text}")
            if fuzz.ratio(self.tournament, row_t.text) > 85:
                row_squad = s.find_element(By.XPATH, ".//th[@data-stat='team']//a")  # squad
                msg(f"squad ratio:{fuzz.ratio(self.squad.lower(), row_squad.text.lower())}, <a>: {row_squad.text}")
                if fuzz.ratio(self.squad.lower(), row_squad.text.lower()) > 85:
                    msg(f"Clicking {row_squad.text}")
                    msg(f"Clicking {row_squad.get_attribute('href')}")
                    click_element_by_script(self.driver, row_squad, wait_after=7)
                    break

        wait_til_filled(self.driver, "//table[@id='comps_fa_club_league']")

        seasons_list_xpath = "//table[@id='comps_fa_club_league']//tbody//tr[not(@class='thead')]"
        seasons_list = self.driver.find_elements(By.XPATH, seasons_list_xpath)

        msg(f"Found {len(seasons_list)} seasons for {self.squad}")
        for s in seasons_list:
            row_squad = s.find_element(By.XPATH, ".//td[@data-stat='team']")  # squad
            msg(f"squad ratio:{fuzz.ratio(self.squad.lower(), row_squad.text.lower())}, <a>: {row_squad.text}")
            if fuzz.ratio(self.squad.lower(), row_squad.text.lower()) > 85:
                squad_link = s.find_element(By.XPATH, ".//td[@data-stat='team']//a")  # squad link
                row_season = s.find_element(By.XPATH, ".//th[@data-stat='year_id']")  # season
                msg(f"season ratio:{fuzz.ratio(self.season.lower(), row_season.text.lower())}, <a>: {row_season.text}")
                if fuzz.ratio(self.season.lower(), row_season.text.lower()) == 100:
                    msg(f"Clicking {row_squad.text}")
                    msg(f"Clicking {squad_link.get_attribute('href')}")
                    click_element_by_script(self.driver, squad_link, wait_after=7)
                    return

        raise Exception(f"There was no match for squad:{self.squad} "
                        f"in tournament:{self.tournament} "
                        f"in country:{self.country} "
                        f"in season:{self.season}")

    def _scrap(self) -> dict:

        page_source = self.driver.page_source
        self.soup = BeautifulSoup(page_source, "html.parser")

        msg(f"Scraping url:{self.driver.current_url}")

        result = {
            "current_url": self.driver.current_url
        }

        for match_url_date in self.fetch_all_competition_matches_url_and_date():
            if len(match_url_date['url']) == 0:
                continue
            result[f"match_{match_url_date['date']}"] = self.get_matches_data(match_url_date['url'])
            msg("Wait for 7 seconds, simulating a human behavior")
            time.sleep(7)

        return result


    def get_matches_data(self, match_url: str) -> {}:
        msg(f"get_matches_data, match_url:{match_url}")

        self.driver.get(match_url)
        self.soup = BeautifulSoup(self.driver.page_source, "html.parser")

        match_data = {
            "match_report": self.get_match_report(),
        }

        local_team_summary_tbl = f"stats_{match_data["match_report"]["local_team_id"]}_summary"
        match_data["local_team_summary"] = get_whole_table(self.soup.find("table", id=local_team_summary_tbl), match_url)

        away_team_summary_tbl = f"stats_{match_data["match_report"]["away_team_id"]}_summary"
        match_data["away_team_summary"] = get_whole_table(self.soup.find("table", id=away_team_summary_tbl), match_url)

        local_team_passing_tbl = f"stats_{match_data["match_report"]["local_team_id"]}_passing"
        match_data["local_team_passing"] = get_whole_table(self.soup.find("table", id=local_team_passing_tbl), match_url)

        away_team_passing_tbl = f"stats_{match_data["match_report"]["away_team_id"]}_passing"
        match_data["away_team_passing"] = get_whole_table(self.soup.find("table", id=away_team_passing_tbl), match_url)

        local_team_goalkeeping_tbl = f"keeper_stats_{match_data["match_report"]["local_team_id"]}"
        match_data["local_team_goalkeeping"] = get_whole_table(self.soup.find("table", id=local_team_goalkeeping_tbl), match_url)

        away_team_goalkeeping_tbl = f"keeper_stats_{match_data["match_report"]["away_team_id"]}"
        match_data["away_team_goalkeeping"] = get_whole_table(self.soup.find("table", id=away_team_goalkeeping_tbl), match_url)

        return match_data


    def get_match_report(self):
        print(f"get_match_report")

        match_report = {}

        match_teams_xpath = "//div[@class='scorebox']//div//div//strong//a"
        match_teams = self.driver.find_elements(By.XPATH, match_teams_xpath)

        if len(match_teams) >= 3:
            match_report["local_team"] = match_teams[0].text
            match_report["away_team"] = match_teams[1].text
            match_report["date"] = match_teams[2].text

            local_team_href = match_teams[0].get_attribute("href")
            local_team_href = local_team_href[local_team_href.find("/en/squads/") + len("/en/squads/"):]
            match_report["local_team_id"] = local_team_href[0:local_team_href.find("/")]

            away_team_href = match_teams[1].get_attribute("href")
            away_team_href = away_team_href[away_team_href.find("/en/squads/") + len("/en/squads/"):]
            match_report["away_team_id"] = away_team_href[0:away_team_href.find("/")]

        match_score_xpath = "//div[@class='scorebox']//div//div[@class='scores']//div[@class='score']"
        match_score = self.driver.find_elements(By.XPATH, match_score_xpath)
        match_report["local_score"] = int(match_score[0].text)
        match_report["away_score"] = int(match_score[1].text)

        match_xg_xpath = "//div[@class='scorebox']//div//div[@class='scores']//div[@class='score_xg']"
        match_xg = self.driver.find_elements(By.XPATH, match_xg_xpath)
        match_report["local_xg"] = float(match_xg[0].text)
        match_report["away_xg"] = float(match_xg[1].text)

        venue_time = self.driver.find_element(By.XPATH, "//span[@class='venuetime']").text
        match_report["venue_time"] = venue_time[0:venue_time.find(" ")]

        return match_report


    def fetch_all_competition_matches_url_and_date(self) -> list :
        msg(f"fetch_all_competition_matches_url_and_date")

        table_element = self.soup.find("table", id="matchlogs_for")

        if table_element is None:
            return []

        urls = []
        for row in get_table_data(table_element, self.driver.current_url):
            print(f"row: {row}")
            if "comp" in row and fuzz.ratio(self.tournament, row['comp']) > 85:
                urls.append({
                    'date': row["date"],
                    'url': row["match_report_url"] if "match_report_url" in row else CELL_404
                })

        return urls
