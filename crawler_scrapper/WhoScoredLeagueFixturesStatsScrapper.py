import re

# beautiful soup
from bs4 import BeautifulSoup  # pip install lxml in order to use the lxml parser
from fuzzywuzzy import fuzz
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

# mine
from util import wait_til_filled, msg, get_whole_table, click_element_by_script_wait_4_element, click_element_by_script, \
    click_and_wait, click_select, get_select_current_text, warn, click_and_wait_inner, click_element_xpath, \
    get_select_by_index_text
from .AbstractCrawlerNavScrapper import AbstractCrawlerNavScrapper


class WhoScoredLeaguesScoresFixturesScrapper(AbstractCrawlerNavScrapper):
    base_url = "https://www.whoscored.com/"
    REGEX = "Regions/.*"

    def __init__(self, hide_browser: bool = True, country: str = None, tournament: str = None, season: str = None, t_event: str = None):
        super().__init__(hide_browser)
        self.country = country
        self.tournament = tournament
        self.season = season
        self.t_event = t_event
        self.current_season = None


    def _validate_required_fields(self) -> bool:
        if self.base_url == self.driver.current_url:
            return self.country is not None and self.tournament is not None and self.season is not None
        else:
            return True

    def _navigate(self):

        msg(f"About to navigate page {self.driver.current_url}")

        title = self.driver.title  # Access the <title> element's text content
        msg(f"Page title: {title.strip()}")

        # click on "All Tournaments drop down"
        all_tournaments = '//button[@id="All-Tournaments-btn"]'
        countries_container = "//div[contains(@class, 'MainNavigation-module_tournamentsDropdownMenus__SEMU2')]"
        msg(f"Clicking: [{self.driver.find_element(By.XPATH, all_tournaments).text}]")
        click_and_wait(self.driver, all_tournaments, countries_container)

        all_country_alpha = "//div[@class='AlphabetSearch-module_lettersContainer__o1pBK']//button"
        countries_container = '//div[@class="TournamentsDropdownMenu-module_allTournamentsGrid__Wn4T6"]'
        country_buttons = self.driver.find_elements(By.XPATH, all_country_alpha)
        msg(f"Found {len(country_buttons)} countries buttons")
        for b in country_buttons:
            if (fuzz.ratio(self.country[0].lower(), b.text.lower()) == 100 or
                    (b.text.lower() == "International" and fuzz.ratio(self.country.lower(), b.text.lower()) == 100)):
                msg(f"Clicking {b.text}")
                click_element_by_script_wait_4_element(self.driver, b, countries_container)
                break

        countries_xpath = "//div[contains(@class, 'TournamentsDropdownMenu-module_allTournamentsButton__GahzG')]"
        countries_list = self.driver.find_elements(By.XPATH, countries_xpath)
        msg(f"Found {len(countries_list)} countries")
        comps_list = []
        for c in countries_list:
            if fuzz.ratio(self.country.lower(), c.text.lower()) == 100:
                msg(f"Clicking {c.text}")
                to_click = ".//div[starts-with(@class, 'TournamentsDropdownMenu-module_countryDropdown') and @id]"
                to_wait = ".//div[starts-with(@class, 'TournamentsDropdownMenu-module_children')]"
                click_and_wait_inner(self.driver, c, to_click, to_wait)
                comps_list = c.find_element(By.XPATH, to_wait).find_elements(By.XPATH, ".//a")
                break

        msg(f"Found {len(comps_list)} tournaments")
        for comp in comps_list:
            if fuzz.ratio(self.tournament.lower(), comp.text.lower()) > 80:
                msg(f"Clicking {comp.text}")
                click_element_by_script(self.driver, comp)
                break

        wait_til_filled(self.driver, f"//table[starts-with(@id, 'standings')]")

        season_select_path = "//select[@id='seasons']"
        self.current_season = get_select_current_text(self.driver.find_element(By.XPATH, season_select_path))
        if self.current_season != self.season:
            # get the current season data
            if click_select(self.driver.find_element(By.XPATH, season_select_path), self.season):
                wait_til_filled(self.driver, f"//table[starts-with(@id, 'standings')]")
                return
            else:
                raise Exception(
                    f"There was no match for country:{self.country} and tournament:{self.tournament} and season:{self.season}")
        else:
            msg(f"Season already selected, it's the current season, let's continue")


    def _scrap(self) -> dict:

        page_source = self.driver.page_source
        self.soup = BeautifulSoup(page_source, "html.parser")

        season = self.soup.find("select", id="seasons").find("option", selected=True).text

        msg(f"Scraping url:{self.driver.current_url}")
        msg(f"Tournament: {self.soup.find('h1', class_='tournament-header').text}")
        msg(f"Season: {season}")

        url = self.driver.current_url
        result = {
            "current_url": url,
            "summary": self.fetch_summary()
        }

        self.get_league_tables(result)
        self.get_team_statistics(result)
        self.get_player_statistics(result)

        return self.format_data(result)

    def fetch_summary(self) -> dict:
        msg(f"fetch_summary")

        summary = {"country": self.soup.find("div", id="breadcrumb-nav").find("span").text,
                   "tournament": get_select_current_text(self.driver.find_element(By.XPATH, "//select[@id='tournaments']")),
                   "season": get_select_current_text(self.driver.find_element(By.XPATH, "//select[@id='seasons']")),
                   "current_season": self.current_season if self.current_season is not None \
                       else get_select_by_index_text(self.driver.find_element(By.XPATH, "//select[@id='seasons']"), 0)}

        best_xi_list = ["overall-formation-weekly-content",
                        "overall-formation-monthly-content",
                        "overall-formation-seasonal-content"]

        for bxi in best_xi_list:
            best_xi = {}
            best_xi_div = self.soup.find("div", id=f"{bxi}")
            best_xi["dates"] = best_xi_div.find("div", id="overall-formation-dates-header").text

            #then each player is in a <ul> inside a <div> with class='team-pitch-formation'
            best_xi["players"] = []
            for player in best_xi_div.find("div", class_="team-pitch-formation").findAll("ul"):
                player_data = [p.text for p in player.findAll("li") if p.text != ""]
                player_dic = {"player_team": player_data[0], "player_name": player_data[1], "player_rating": player_data[2]} \
                    if len(player_data) >= 3 else {}
                best_xi["players"].append(player_dic)

            summary[f"{bxi}"] = best_xi

        return summary


    def get_league_tables(self, scrapped_data: dict) -> None:
        msg(f"get_league_tables, for {self.driver.current_url}")

        for link in ["Standings", "Form", "Streaks", "Progress"]:
            msg(f"Clicking on {link}")

            try:
                l_to_click = f"//ul[starts-with(@id, 'tournament-tables')]//a[text()='{link}']"
                if link == "Standings": # initial state is standings, it doesn't change the div
                    click_element_xpath(self.driver, l_to_click)
                else:
                    link = link.lower() if link != "Progress" else "History" # link text doesn't match the elements name
                    l_to_wait = f"//div[starts-with(@id, '{link.lower()}') and @style]"
                    click_and_wait(self.driver, l_to_click, l_to_wait)
                # self.driver.find_element(By.XPATH, f"//ul[starts-with(@id, 'tournament-tables')]//a[text()='{link}']").click()
                # wait for the sub menu to be filled half a second
                #time.sleep(0.5)
            except NoSuchElementException as nse:
                warn(f"Element not found: {nse}")
                continue

            for btn in ["Overall", "Home", "Away"]:
                msg(f"Clicking on {btn}")

                try:
                    to_click = f"//dl[@id='tournament-filter-{link.lower()}']//a[text()='{btn}']"
                    if btn == "Overall": # initial state is overall, it doesn't change the table
                        click_element_xpath(self.driver, to_click)
                    else:
                        to_wait = f"//table[starts-with(@id, '{link.lower()}')]"
                        click_and_wait(self.driver, to_click, to_wait)
                    # self.driver.find_element(By.XPATH, f"//dl[@id='tournament-filter-{filter_id}']//a[text()='{btn}']").click()
                        # wait for the table to be filled half a second
                        # time.sleep(0.5)
                except NoSuchElementException as nse:
                    warn(f"Element not found: {nse}")
                    continue

                self.soup = BeautifulSoup(self.driver.page_source, "html.parser")
                table_tag = self.soup.find("table", id=re.compile(rf"{link.lower()}"))
                scrapped_data[f"league_{link.lower()}_{btn.lower()}"] = get_whole_table(table_tag, self.driver.current_url)


    def format_data(self, scrapped_data: dict) -> dict:
        msg(f"format_data for {self.driver.current_url}")

        #get keys and values from scrapped_data and iterate over them
        for key, value in scrapped_data.items():
            #if the key contains the word history
            if "history" in key:
                #iterate over the values
                for val in value['data']:
                    #if the key contains the word 'date'
                    if "h1" in val:
                        val['h1'] = [self.match_class_result(v) for v in val['h1'].split(', ')]

        return scrapped_data


    def match_class_result(self, c: str):
        if c == "r1":
            return "draw"
        elif c == "r0":
            return "lose"
        elif c == "r3":
            return "win"
        else:
            return c


    def get_team_statistics(self, scrapped_data: dict) -> None:
        msg(f"get_team_statistics, for {self.driver.current_url}")

        click_element_by_script(self.driver, self.driver.find_element(By.XPATH, f"//div[@id='sub-navigation']//a[text()='Team Statistics']"))
        wait_til_filled(self.driver, f"//div[@id='stage-team-stats']")

        for link in ["Summary", "Defensive", "Offensive", "xG"]:
            msg(f"Clicking on {link}")

            try:
                l_to_click = f"//ul[starts-with(@id, 'stage-team-stats-options')]//a[text()='{link}']"
                if link == "Summary": # initial state is summary, it doesn't change the div
                    click_element_xpath(self.driver, l_to_click)
                else:
                    # link = link.lower() if link != "Progress" else "History"
                    l_to_wait = f"//div[substring(@id, string-length(@id)-{len(link.lower())-1}) = '{link.lower()}' and @style]"
                    click_and_wait(self.driver, l_to_click, l_to_wait)
            except NoSuchElementException as nse:
                warn(f"Element not found: {nse}")
                continue

            for btn in ["Overall", "Home", "Away"]:
                msg(f"Clicking on {btn}")

                try:
                    # to_click = f"//dl[@id='field']//a[text()='{btn}']"
                    to_click = f"//div[substring(@id, string-length(@id)-{len(link.lower())-1}) = '{link.lower()}' and @style]//dl[@id='field']//a[text()='{btn}']"
                    if btn == "Overall": # initial state is overall, it doesn't change the table
                        click_element_xpath(self.driver, to_click)
                    else:
                        to_wait = f"//div[substring(@id, string-length(@id)-{len(link.lower())-1}) = '{link.lower()}' and @style]//table"
                        click_and_wait(self.driver, to_click, to_wait)
                except NoSuchElementException as nse:
                    warn(f"Element not found: {nse}")
                    continue

                self.soup = BeautifulSoup(self.driver.page_source, "html.parser")
                table_tag = self.soup.find("div", id=re.compile(rf"{link.lower()}$")).find("table")
                scrapped_data[f"Summary_{link.lower()}_{btn.lower()}"] = get_whole_table(table_tag, self.driver.current_url)


    def get_player_statistics(self, scrapped_data: dict) -> None:
        msg(f"get_player_statistics, for {self.driver.current_url}")

        click_element_by_script(self.driver, self.driver.find_element(By.XPATH, f"//div[@id='sub-navigation']//a[text()='Player Statistics']"))
        wait_til_filled(self.driver, f"//div[@id='stage-top-player-stats']")

