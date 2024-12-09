import re

# beautiful soup
from bs4 import BeautifulSoup  # pip install lxml in order to use the lxml parser

# fuzzywuzzy
from fuzzywuzzy import fuzz  # needs pip install python-Levenshtein
from selenium.webdriver.common.by import By

from util import click_element_by_script, get_whole_table, build_url, navigate_to_league_stats_page

# mine
from util import get_just_numbers, get_value_from_key, msg
from . import url_id
from .AbstractCrawlerNavScrapper import AbstractCrawlerNavScrapper


class FBrefTeamStatsScrapper(AbstractCrawlerNavScrapper):
    base_url = "https://fbref.com/en/"
    REGEX = "squads/.*"

    def __init__(self, hide_browser: bool = True, tournament: str = None, season: str = None, team: str = None, ):
        super().__init__(hide_browser)
        self.tournament = tournament
        self.season = season
        self.team = team
        self.league_url = ""

    def _validate_required_fields(self) -> bool:
        return (self.tournament is not None and
                self.team is not None and
                self.season is not None)

    def _navigate(self):

        navigate_to_league_stats_page(self.driver, self.tournament, self.season)

        team_overall_id = f"results{self.season.lower()}{url_id(self.driver.current_url)}1_overall"
        a_teams_list_xpath = f"//table[@id='{team_overall_id}']//tbody//tr//td[@data-stat='team']//a"
        a_teams_list = self.driver.find_elements(By.XPATH, a_teams_list_xpath)

        msg(f"Found {len(a_teams_list)} teams for {self.season}")
        for a in a_teams_list:
            if fuzz.ratio(self.team.lower(), a.text.lower()) > 80:
                msg(f"Clicking on {a.text}")
                click_element_by_script(self.driver, a, wait_after=3)
                return

        raise Exception(f"There was no match for squad:{self.team} "
                        f"in tournament:{self.tournament} "
                        f"in season:{self.season}")

    def _scrap(self) -> dict:

        page_source = self.driver.page_source
        self.soup = BeautifulSoup(page_source, "html.parser")

        msg(f"Scraping url:{self.driver.current_url}")

        result = {
            "current_url": self.driver.current_url,
            "summary": self.fetch_summary(),
            "standard_stats": get_whole_table(self.soup.find("table", id=f"stats_standard_{url_id(self.league_url)}"), self.driver.current_url),
            "scores_fixtures": get_whole_table(self.soup.find("table", id="matchlogs_for"), self.driver.current_url),
            "goalkeeping": get_whole_table(self.soup.find("table", id=f"stats_keeper_{url_id(self.league_url)}"), self.driver.current_url),
            "advance_goalkeeping": get_whole_table(self.soup.find("table", id=f"stats_keeper_adv_{url_id(self.league_url)}"), self.driver.current_url),
            "shooting": get_whole_table(self.soup.find("table", id=f"stats_shooting_{url_id(self.league_url)}"), self.driver.current_url),
            "passing": get_whole_table(self.soup.find("table", id=f"stats_passing_{url_id(self.league_url)}"), self.driver.current_url),
            "possession": get_whole_table(self.soup.find("table", id=f"stats_possession_{url_id(self.league_url)}"), self.driver.current_url),
            "playing_time": get_whole_table(self.soup.find("table", id=f"stats_playing_time_{url_id(self.league_url)}"), self.driver.current_url),
        }

        return result

    def fetch_summary(self) -> dict:
        msg(f"fetch_summary")

        summary = {}

        team_info_div = self.soup.find('div', {'data-template': 'Partials/Teams/Summary'})
        season_team = team_info_div.find("h1").find_all("span")[0].text
        summary["team"] = season_team[season_team.find(" ") + 1:season_team.find("Stats")].strip()
        summary["team_short"] = self.team
        summary["season"] = "-".join(str(i) for i in get_just_numbers(season_team))
        summary["league"] = team_info_div.find("h1").find_all("span")[1].text.replace("(", "").replace(")", "").strip()
        self.league_url = build_url(self.driver.current_url, team_info_div.find("p").find("a")["href"])


        for p in team_info_div.find_all("p"):

            r = "".join(item.strip() + " " for item in p.text.split("\n")).strip()

            if re.search("Record:", r):

                if r.count("Record:") == 1:
                    fetch_summary_record(summary, get_just_numbers(r))

                elif r.count("Record:") > 1:
                    fetch_summary_home_away_rec(summary, get_just_numbers(r))

            if re.search("Goals:", r) and re.search("Goals Against:", r):
                fetch_summary_goals(summary, get_just_numbers(r))

            if re.search("xG:", r) and re.search("xGA:", r) and re.search("Diff:", r):
                fetch_summary_xg(summary, get_just_numbers(r))

            if re.search("Last Match:", r):
                summary["last_match"] = get_value_from_key(r, "Last Match:")

            if re.search("Next Match:", r):
                summary["next_match"] = get_value_from_key(r, "Next Match:")

            if re.search("Manager:", r):
                summary["manager"] = get_value_from_key(r, "Manager:")

            if re.search("Governing Country:", r):
                country = get_value_from_key(r, "Governing Country:")
                summary["country"] = country[:country.find(" ")+1]

            if re.search("Gender:", r):
                summary["gender"] = get_value_from_key(r, "Gender:")

        return summary


def separate_goals_from_pk(score: str) -> str:
    if re.search("^\\d+\\s+.*$", score):
        return score[:score.find(" ")]
    else:
        return score


def fetch_summary_record(summary: dict, record: list):
    if len(record) >= 6:
        summary["win"] = record[0]
        summary["draw"] = record[1]
        summary["lose"] = record[2]
        summary["games"] = record[0] + record[1] + record[2]
        summary["points"] = record[3]
        summary["pts_per_game"] = 0 if summary["points"] == 0 else record[4]
        summary["place"] = record[4] if summary["points"] == 0 else record[5]
        summary["tier"] = record[5] if summary["points"] == 0 else record[6]


def fetch_summary_home_away_rec(summary: dict, home_away_rec: list):
    if len(home_away_rec) == 8:
        summary["record_home_w_d_l_p"] = '-'.join(str(x) for x in home_away_rec[:4])
        summary["record_away_w_d_l_p"] = '-'.join(str(x) for x in home_away_rec[4:8])


def fetch_summary_goals(summary: dict, goals: list):
    if len(goals) == 5:
        summary["goals"] = goals[0]
        summary["goals_per_game"] = goals[1]
        summary["goals_against"] = goals[2]
        summary["goals_against_per_game"] = goals[3]
        summary["goals_diff"] = goals[4]


def fetch_summary_xg(summary: dict, xg: list):
    if len(xg) == 3:
        summary["xg"] = xg[0]
        summary["xga"] = xg[1]
        summary["xg_diff"] = xg[2]
