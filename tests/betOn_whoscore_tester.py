import json
import time
from pprint import pprint

from crawler_scrapper.WhoScoredLeagueFixturesStatsScrapper import WhoScoredLeaguesScoresFixturesScrapper


def test_whoscored_tournament_stats_scrapper():
    start_time = time.time()

    tournament = "Premier League"
    country = "England"
    season = "2023/2024"

    scrapper = WhoScoredLeaguesScoresFixturesScrapper(hide_browser=True, country=country, tournament=tournament, season=season)
    result = scrapper.scrap_and_print()
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"scrap result: {json.dumps(result, indent=4, ensure_ascii=False)}")
    print(f"test test_whoscored_tournament_stats_scrapper() elapsed time: {elapsed_time}")


def test_whoscored_tournament_stats_scrapper_url():
    start_time = time.time()

    scrapper = WhoScoredLeaguesScoresFixturesScrapper()
    result = scrapper.scrap_and_print("https://www.whoscored.com/Regions/252/Tournaments/2/Seasons/9618/Stages/22076/Show/England-Premier-League-2023-2024")
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"scrap result: {json.dumps(result, indent=4, ensure_ascii=False)}")
    print(f"test test_whoscored_tournament_stats_scrapper_url() elapsed time: {elapsed_time}")


if __name__ == "__main__":
    # test_whoscored_tournament_stats_scrapper()
    test_whoscored_tournament_stats_scrapper_url()
