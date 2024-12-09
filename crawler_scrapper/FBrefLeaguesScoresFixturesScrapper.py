import re
import time

# beautiful soup
from bs4 import BeautifulSoup  # pip install lxml in order to use the lxml parser
# util
from util import click_element_xpath_by_script, wait_til_filled, msg, get_whole_table, val, \
    get_table_data, url_id, stats_by_team, build_url, navigate_to_league_stats_page
# mine
from .AbstractCrawlerNavScrapper import AbstractCrawlerNavScrapper


class FBrefLeaguesScoresFixturesScrapper(AbstractCrawlerNavScrapper):
    base_url = "https://fbref.com/en/"
    REGEX = "comps/.*"

    def __init__(self, hide_browser: bool = True, tournament: str = None, season: str = None):
        super().__init__(hide_browser)
        self.tournament = tournament
        self.season = season
        self.current_season = None


    def _validate_required_fields(self) -> bool:
        if self.base_url == self.driver.current_url:
            return self.tournament is not None and self.season is not None
        else:
            return True

    def _navigate(self):

        self.current_season = navigate_to_league_stats_page(self.driver, self.tournament, self.season)

        # then we click the Scores & Fixtures tab
        click_element_xpath_by_script(self.driver, "//li//div//section//p//a[text()='Scores & Fixtures']", wait_after=3)

        if not wait_til_filled(self.driver, f"//table[@id='sched_{self.season.lower()}_{url_id(self.driver.current_url)}_1']"):
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
        result = {
            "current_url": url,
            "current_season": self.current_season,
            "summary": self.fetch_summary(),
            "scores_fixtures": get_whole_table(self.soup.find("table", id=f"sched_{season}_{url_id(self.driver.current_url)}_1"), url)
        }

        # set the most common team names
        fixtures_raw_data = get_table_data(self.soup.find("table", id=f"sched_{season}_{url_id(self.driver.current_url)}_1"))
        #for t in fixtures_raw_data:
        #    for row in result["scores_fixtures"]["data"]:
        #        if row["home"] == t["home"]:
        #            row["home"] = get_team_name_from_url(t["home_url"])
        #        if row["away"] == t["away"]:
        #            row["away"] = get_team_name_from_url(t["away_url"])

        # fetch the teams that compete in the league
        teams = []
        week = 0
        for row in result["scores_fixtures"]["data"]:
            if row["wk"] == 1:
                teams.append(row["home"])
                teams.append(row["away"])
            elif len(row["score"]) == 0:
                week = row["wk"]-1
                break
        result["teams"] = teams

        lineups = {}
        for t in fixtures_raw_data:
            if "match_report_url" in t and t["wk"] == week:
                msg(f"Fetching lineup for {t['home']} vs {t['away']}, url:{t['match_report_url']}")
                lineup = self.get_lineup(t["match_report_url"])
                for row in result["scores_fixtures"]["data"]:
                    #if row["home"] == get_team_name_from_url(t["home_url"]) and row["away"] == get_team_name_from_url(t["away_url"]):
                    if row["home"] == t["home"] and row["away"] == t["away"]:
                        lineups[f"{row["home"]}"] = {"lineup": lineup["home"]}
                        lineups[f"{row["away"]}"] = {"lineup": lineup["away"]}
        result["last_week_lineups"] = lineups

        fixtures = []
        current_round = 0
        for row in result["scores_fixtures"]["data"]:
            if len(row["score"]) == 0:
                if current_round == 0:
                    current_round = row["wk"]
                elif current_round != row["wk"]:
                    break

                fixtures.append({
                            "week": row["wk"],
                            "day": row["day"],
                            "date": row["date"],
                            "time": row["time"],
                            "local": row["home"],
                            "away": row["away"],
                            "venue": row["venue"]
                            })

        result["fixtures_2_sim"] = fixtures

        result["teams_stats"] = {}
        for team in teams:
            result["teams_stats"][team] = stats_by_team(team, result["scores_fixtures"]["data"])

        teams_list = [{**{"team": key}, **value} for key, value in result["teams_stats"].items()]

        teams_list_sorted = sorted(teams_list, key=lambda x: (x['points'], x['goals']-x['goals_against'], x['goals']), reverse=True)
        for i, t in enumerate(teams_list_sorted):
            result["teams_stats"][t['team']]['position'] = i + 1

        result["teams_rank"] = [t['team'] for t in teams_list_sorted]

        teams_xg_list_sorted = sorted(teams_list, key=lambda x: (x['xg_points'], x['xg'] - x['xga'], x['xg']), reverse=True)
        for i, t in enumerate(teams_xg_list_sorted):
            result["teams_stats"][t['team']]['xg_position'] = i + 1

        result["teams_xg_rank"] = [t['team'] for t in teams_xg_list_sorted]

        return result

    def fetch_summary(self) -> dict:
        msg(f"fetch_summary")

        summary = {}

        meta_div = self.soup.find('div', id='meta')
        summary_data = meta_div.findAll("p")
        summary["country"] = summary_data[0].find("a").text

        gender = summary_data[2].text
        summary["gender"] = gender[gender.find(' '):].strip()

        theres_a_champion = False
        if summary_data[3].find("strong").text == "Champion":
            theres_a_champion = True
            summary["champion"] = val(", ".join([link.text.strip() for link in summary_data[3].findAll("a")]))

        summary["most_goals_player"] = val(", ".join([link.text.strip() for link in summary_data[4 if theres_a_champion else 3].findAll("a")]))
        summary["most_goals_team"] = val(", ".join(re.findall(r"\((.*?)\)", summary_data[4 if theres_a_champion else 3].text)))
        summary["most_goals"] = val(summary_data[4 if theres_a_champion else 3].find("span").text)

        summary["most_assists_player"] = val(", ".join([link.text.strip() for link in summary_data[5 if theres_a_champion else 4].findAll("a")]))
        summary["most_assists_team"] = val(", ".join(re.findall(r"\((.*?)\)", summary_data[5 if theres_a_champion else 4].text)))
        summary["most_assists"] = val(summary_data[5 if theres_a_champion else 4].find("span").text)

        summary["most_clean_sheets_player"] = val(", ".join([link.text.strip() for link in summary_data[6 if theres_a_champion else 5].findAll("a")]))
        summary["most_clean_sheets_team"] = val(", ".join(re.findall(r"\((.*?)\)", summary_data[6 if theres_a_champion else 5].text)))
        summary["most_clean_sheets"] = val(summary_data[6 if theres_a_champion else 5].find("span").text)

        return summary


    def get_lineup(self, match_url:str) -> dict:
        msg(f"get_lineup for match_url:{match_url}")
        match_url = build_url(self.driver.current_url, match_url)
        self.driver.get(match_url)
        self.soup = BeautifulSoup(self.driver.page_source, "html.parser")

        start_time = time.time()
        wait_til_filled(self.driver, f"//div[@id='field_wrap']")
        wait_time = start_time - time.time()
        if wait_time < 5:
            msg(f"Wait for {5-wait_time} seconds, simulating a human behavior")
            time.sleep(5-wait_time)

        result = {}
        for t in ['a','b']:
            lineup = []
            lineup_div = self.soup.find("div", id=f"{t}",attrs={'class': 'lineup'})
            if lineup_div is not None:
                for row in lineup_div.findAll("tr"):
                    if row.findAll("td") is not None and len(row.findAll("td")) == 2:
                        lineup.append({
                            "number": row.findAll("td")[0].text,
                            "player": row.findAll("td")[1].text
                        })
            result["home" if t == 'a' else "away"] = lineup
        return result