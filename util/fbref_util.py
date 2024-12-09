import numbers
import re

from fuzzywuzzy import fuzz
from selenium.webdriver.common.by import By

from util import msg, wait_til_filled, click_element_by_script, click_element_xpath_by_script


def who_win(score: str):
    if score.split("–")[0] > score.split("–")[1]:
        return "h" # home
    elif score.split("–")[0] < score.split("–")[1]:
        return "a" # away
    else:
        return "d" # draw


def get_team_name_from_url(url: str) -> str:
    url = url[url.rfind("/") + 1:]
    return url[:url.rfind("-")].replace("-", " ").title()


def url_id(url: str) -> str:
    match = re.search(r"(?<=https://fbref\.com/en/comps/)\d+(?=/\w+)", url)
    if match:
        return match.group(0)
    return ""


def stats_by_team(team: str, fixtures: list) -> dict:

    result = {  'mp': 0,
                'goals': 0,
                'goals_against': 0,
                'xg': 0,
                'xg_home': 0,
                'xg_away': 0,
                'xga': 0,
                'xga_home': 0,
                'xga_away': 0,
                'points': 0,
                'xg_points': 0
            }

    mp = 0
    for row in fixtures:
        if row["score"] == "":
            break
        if row["home"] == team:
            result['goals'] += int(row["score"].split("–")[0])
            result['goals_against'] += int(row["score"].split("–")[1])
            result['xg'] += row["xg"] if isinstance(row["xg"], numbers.Number) else 0
            result['xg_home'] += row["xg"] if isinstance(row["xg"], numbers.Number) else 0
            result['xga'] += row["xg1"] if isinstance(row["xg1"], numbers.Number) else 0
            result['xga_home'] += row["xg1"] if isinstance(row["xg1"], numbers.Number) else 0
            result['points'] += 3 if who_win(row["score"]) == "h" else 1 if who_win(row["score"]) == "d" else 0
            result['xg_points'] += 3 if row["xg"] > row["xg1"] else 1 if row["xg"] == row["xg1"] else 0
            mp += 1
        if row["away"] == team:
            result['goals'] += int(row["score"].split("–")[1])
            result['goals_against'] += int(row["score"].split("–")[0])
            result['xg'] += row["xg1"] if isinstance(row["xg1"], numbers.Number) else 0
            result['xg_away'] += row["xg1"] if isinstance(row["xg1"], numbers.Number) else 0
            result['xga'] += row["xg"] if isinstance(row["xg"], numbers.Number) else 0
            result['xga_away'] += row["xg"] if isinstance(row["xg"], numbers.Number) else 0
            result['points'] += 3 if who_win(row["score"]) == "a" else 1 if who_win(row["score"]) == "d" else 0
            result['xg_points'] += 3 if row["xg1"] > row["xg"] else 1 if row["xg1"] == row["xg"] else 0
            mp += 1

    result['mp'] = mp

    return result


def navigate_to_league_stats_page(driver, tournament: str, season: str) -> str:

    msg(f"About to navigate page {driver.current_url}")

    title = driver.title  # Access the <title> element's text content
    msg(f"Page title: {title.strip()}")

    # click on "Competitions" link
    msg(f"Clicking {driver.find_element(By.XPATH, '//li[@id="header_comps"]//a').text}")
    click_element_xpath_by_script(driver, "//li[@id='header_comps']//a")

    wait_til_filled(driver, "//table[@id='comps_1_fa_club_league_senior']")

    a_domestic_list_xpath = "//table[@id='comps_1_fa_club_league_senior']//tbody//tr//th//a"
    a_list = driver.find_elements(By.XPATH, a_domestic_list_xpath)

    msg(f"Found {len(a_list)} tournaments")
    for a in a_list:
        if fuzz.ratio(tournament.lower(), a.text.lower()) > 80:
            msg(f"Clicking on {a.text}")
            click_element_by_script(driver, a)
            break

    wait_til_filled(driver, "//table[@id='seasons']")

    a_seasons_list_xpath = "//table[@id='seasons']//tbody//tr//th//a"
    a_season_list = driver.find_elements(By.XPATH, a_seasons_list_xpath)

    msg(f"Found {len(a_season_list)} seasons for {tournament}")
    current_season = ""
    if len(a_season_list) > 0:
        current_season = a_season_list[0].text

    for a in a_season_list:
        if fuzz.ratio(season.lower(), a.text.lower()) > 90:
            msg(f"Clicking on {a.text}")
            click_element_by_script(driver, a, wait_after=3)
            break

    wait_til_filled(driver, f"//table[@id='results{season.lower()}{url_id(driver.current_url)}1_overall']")

    return current_season