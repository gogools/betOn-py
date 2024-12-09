from enum import Enum

# beautiful soup
from bs4 import BeautifulSoup  # pip install lxml in order to use the lxml parser
# util
from util import wait_til_filled, msg, get_table_data
# mine
from .AbstractCrawlerNavScrapper import AbstractCrawlerNavScrapper


class FBrefLeaguesScrapper(AbstractCrawlerNavScrapper):

    base_url = "https://fbref.com/en/"

    class Comps(Enum):
        CLUB_INTERNATIONAL_CUPS = 'comps_intl_club_cup'
        NATIONAL_TEAMS_COMPS = 'comps_intl_fa_nonqualifier_senior'
        BIG_5_EUROPEAN = 'comps_club'
        DOMESTIC_LEAGUES = 'comps_1_fa_club_league_senior'

    REGEX = "comps/.*"

    def __init__(self, hide_browser: bool = True, comp: Comps = Comps.BIG_5_EUROPEAN, league: str = None):
        super().__init__(hide_browser)
        self.comp = comp.value
        self.league = league

    def _validate_required_fields(self) -> bool:
        return True

    def _navigate(self):
        self.driver.get("https://fbref.com/en/comps/")
        msg(f"About to navigate page {self.driver.current_url}")

        title = self.driver.title  # Access the <title> element's text content
        msg(f"Page title: {title.strip()}")

        if not wait_til_filled(self.driver, "//table[@id='comps_1_fa_club_league_senior']"):
            raise Exception("I wasn't able to find the leagues and seasons")


    def _scrap(self) -> dict:

        url = self.driver.current_url
        self.soup = BeautifulSoup(self.driver.page_source, "html.parser")

        return {
            "current_url": url,
            "leagues": self.get_league_names()
        }


    def get_league_names(self) -> list:
        msg(f"Getting leagues from table id:{self.comp}")
        url = self.driver.current_url
        leagues_data = get_table_data(self.soup.find("table", id=f"{self.comp}"), url)

        results = []
        for league in leagues_data:
            l = {}
            if self.league is None:
                l["name"] = league["competition_name"]
                results.append(l)
            elif self.league == league["competition_name"]:
                l["name"] = league["competition_name"]
                l["seasons"] = self.get_seasons(league["competition_name_url"])
                results.append(l)
                break

        return results

    def get_seasons(self, url: str) -> list:
        msg(f"Getting seasons from {url}")

        self.driver.get(url)
        wait_til_filled(self.driver, f"//table[@id='seasons']")

        self.soup = BeautifulSoup(self.driver.page_source, "html.parser")

        seasons_data = get_table_data(self.soup.find("table", id=f"seasons"), url)
        return [x["season"] for x in seasons_data]