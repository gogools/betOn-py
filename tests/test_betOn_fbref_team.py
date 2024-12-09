# my python files to tests
import time

from crawler_scrapper import FBrefTeamStatsScrapper


# this test is to test the scrapper with the default url and specific tournament and season
def test_fbref_team_stats_scrapper_1():
    country = "england"
    tournament = "Premier League"
    squad = "Machester City"
    season = "2024-2025"

    start_time = time.time()
    scrapper = FBrefTeamStatsScrapper(True, country, tournament, squad, season)
    result = scrapper.scrap(FBrefTeamStatsScrapper.base_url)

    assert len(result) > 0
    assert len(result["summary"]) > 0
    assert len(result["standard_stats"]) > 0
    assert len(result["scores_fixtures"]) > 0
    assert len(result["goalkeeping"]) > 0
    assert len(result["advance_goalkeeping"]) > 0
    assert len(result["shooting"]) > 0
    assert len(result["passing"]) > 0
    assert len(result["possession"]) > 0
    assert len(result["playing_time"]) > 0

    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"test test_fbref_team_stats_scrapper_1() elapsed time: {elapsed_time}")


def test_fbref_team_stats_scrapper_2():

    start_time = time.time()
    scrapper = FBrefTeamStatsScrapper()
    result = scrapper.scrap("https://fbref.com/en/squads/b8fd03ef/Manchester-City-Stats")

    assert len(result) > 0
    assert len(result["summary"]) > 0
    assert len(result["standard_stats"]) >= 0
    assert len(result["scores_fixtures"]) >= 0
    assert len(result["goalkeeping"]) >= 0
    assert len(result["advance_goalkeeping"]) >= 0
    assert len(result["shooting"]) >= 0
    assert len(result["passing"]) >= 0
    assert len(result["possession"]) >= 0
    assert len(result["playing_time"]) >= 0

    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"test test_fbref_team_stats_scrapper_2() elapsed time: {elapsed_time}")
