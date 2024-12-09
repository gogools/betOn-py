# my python files to tests
import time

from crawler_scrapper import FBrefLeaguesStatsScrapper


# this test is to test the scrapper with the default url and specific tournament and season
def test_fbref_league_season_stats_scrapper_1():
    tournament = "Premier League"
    season = "2023-2024"

    start_time = time.time()
    scrapper = FBrefLeaguesStatsScrapper(True, tournament, season)
    result = scrapper.scrap(FBrefLeaguesStatsScrapper.base_url)

    assert len(result) > 0
    assert len(result["regular_season_overall"]) > 0
    assert len(result["regular_season_home_away"]) > 0
    assert len(result["squad_standard_stats"]) > 0
    assert len(result["opponent_standard_stats"]) > 0
    assert len(result["squad_advanced_goalkeeping"]) > 0
    assert len(result["opponent_advanced_goalkeeping"]) > 0
    assert len(result["squad_shooting"]) > 0
    assert len(result["opponent_shooting"]) > 0
    assert len(result["squad_possession"]) > 0
    assert len(result["opponent_possession"]) > 0

    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"test test_fbref_league_season_stats_scrapper_1() elapsed time: {elapsed_time}")


# this test is to test the scrapper with a specific url
def test_fbref_league_season_stats_scrapper_2():
    start_time = time.time()
    scrapper = FBrefLeaguesStatsScrapper()
    result = scrapper.scrap("https://fbref.com/en/comps/9/Premier-League-Stats")

    assert len(result) > 0
    assert len(result["regular_season_overall"]) > 0
    assert len(result["regular_season_home_away"]) > 0
    assert len(result["squad_standard_stats"]) > 0
    assert len(result["opponent_standard_stats"]) > 0
    assert len(result["squad_advanced_goalkeeping"]) > 0
    assert len(result["opponent_advanced_goalkeeping"]) > 0
    assert len(result["squad_shooting"]) > 0
    assert len(result["opponent_shooting"]) > 0
    assert len(result["squad_possession"]) > 0
    assert len(result["opponent_possession"]) > 0

    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"test test_fbref_league_season_stats_scrapper_2() elapsed time: {elapsed_time}")
