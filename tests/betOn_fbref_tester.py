# my python files to tests
import json
import time

from crawler_scrapper import FBrefTeamStatsScrapper, FBrefLeaguesStatsScrapper, FBrefInternationalCompsStatsScrapper, FBrefTeamAllMatchesStatsScrapper
from crawler_scrapper.FBrefLeaguesScoresFixturesScrapper import FBrefLeaguesScoresFixturesScrapper
from crawler_scrapper.FBrefLeaguesScrapper import FBrefLeaguesScrapper
from util import val


def test_fbref_team_all_performance_stats_scrapper():

    #country = "england"
    #tournament = "Premier League"
    #season = "2024-2025"
    #squad = "Machester City"

    start_time = time.time()
    scrapper = FBrefTeamAllMatchesStatsScrapper(True)#, country, tournament, season, squad)
    result = scrapper.scrap_and_print("https://fbref.com/en/squads/b8fd03ef/2024-2025/Manchester-City-Stats")
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"scrap result: {json.dumps(result, indent=4, ensure_ascii=False)}")
    print(f"test test_fbref_team_all_performance_stats_scrapper() elapsed time: {elapsed_time}")


def test_fbref_team_stats_scrapper():

    country = "england"
    tournament = "Premier League"
    season = "2024-2025"
    squad = "Machester City"

    start_time = time.time()
    scrapper = FBrefTeamStatsScrapper(True, tournament, season, squad)
    result = scrapper.scrap_and_print(FBrefTeamStatsScrapper.base_url)
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"scrap result: {json.dumps(result, indent=4, ensure_ascii=False)}")
    print(f"test test_fbref_team_stats_scrapper() elapsed time: {elapsed_time}")


def test_fbref_league_season_stats_scrapper_1():
    tournament = "Premier League"
    season = "2023-2024"

    start_time = time.time()
    scrapper = FBrefLeaguesStatsScrapper(True, tournament, season)
    result = scrapper.scrap_and_print(FBrefLeaguesStatsScrapper.base_url)
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"scrap result: {json.dumps(result, indent=4, ensure_ascii=False)}")
    print(f"test test_fbref_league_season_stats_scrapper_1() elapsed time: {elapsed_time}")


def test_fbref_league_season_stats_scrapper_2():
    start_time = time.time()
    scrapper = FBrefLeaguesStatsScrapper(True)
    result = scrapper.scrap_and_print("https://fbref.com/en/comps/9/Premier-League-Stats")
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"scrap result: {json.dumps(result, indent=4, ensure_ascii=False)}")
    print(f"test test_fbref_league_season_stats_scrapper_2() elapsed time: {elapsed_time}")


def test_fbref_national_comps_stats_scrapper():
    competition = "UEFA European Football Championship"
    year = "2024"

    start_time = time.time()
    scrapper = FBrefInternationalCompsStatsScrapper(True, competition, year)
    scrapper.scrap_and_print(FBrefInternationalCompsStatsScrapper.base_url)
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"test test_fbref_national_comps_stats_scrapper() elapsed time: {elapsed_time}")


def test_fbref_league_season_scores_fixtures_scrapper_1():
    tournament = "Premier League"
    season = "2024-2025"

    start_time = time.time()
    scrapper = FBrefLeaguesScoresFixturesScrapper(True, tournament, season)
    result = scrapper.scrap_and_print(FBrefLeaguesStatsScrapper.base_url)
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"scrap result: {json.dumps(result, indent=4, ensure_ascii=False)}")
    print(f"test test_fbref_league_season_scores_fixtures_scrapper_1() elapsed time: {elapsed_time}")

def test_fbref_league_season_scores_fixtures_scrapper_2():
    start_time = time.time()
    scrapper = FBrefLeaguesScoresFixturesScrapper(True)
    result = scrapper.scrap_and_print("https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures")
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"scrap result: {json.dumps(result, indent=4, ensure_ascii=False)}")
    print(f"test test_fbref_league_season_stats_scrapper_2() elapsed time: {elapsed_time}")

def test_fbref_leagues_scrapper_1():
    start_time = time.time()
    scrapper = FBrefLeaguesScrapper(True)
    result = scrapper.scrap_and_print()
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"scrap result: {json.dumps(result, indent=4, ensure_ascii=False)}")
    print(f"test test_fbref_league_season_stats_scrapper_2() elapsed time: {elapsed_time}")


def test_fbref_leagues_scrapper_2():
    start_time = time.time()
    scrapper = FBrefLeaguesScrapper(True,FBrefLeaguesScrapper.Comps.DOMESTIC_LEAGUES, "Premier League")
    result = scrapper.scrap_and_print()
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"scrap result: {json.dumps(result, indent=4, ensure_ascii=False)}")
    print(f"test test_fbref_league_season_stats_scrapper_2() elapsed time: {elapsed_time}")


def test_convert_to_number():
    print(f"convert 1 to {val('1')} type: {type(val('1'))}")
    print(f"convert 1.0 to {val('1.0')} type: {type(val('1.0'))}")
    print(f"convert 1h to {val('1h')} type: {type(val('1h'))}")

if __name__ == "__main__":
    # test_fbref_league_season_stats_scrapper_1()
    # test_fbref_league_season_stats_scrapper_2()
    # test_fbref_team_stats_scrapper()
    # test_fbref_team_all_performance_stats_scrapper()
    # test_fbref_national_comps_stats_scrapper()
    # test_convert_to_number()
    # test_fbref_league_season_scores_fixtures_scrapper_1()
    test_fbref_league_season_scores_fixtures_scrapper_2()
    # test_fbref_leagues_scrapper_1()
    # test_fbref_leagues_scrapper_2()
