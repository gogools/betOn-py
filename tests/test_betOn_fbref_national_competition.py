# my python files to tests
import time

from crawler_scrapper import FBrefInternationalCompsStatsScrapper


def test_fbref_national_competition_stats_scrapper_1():
    competition = "UEFA European Football Championship"
    year = "2024"

    start_time = time.time()
    scrapper = FBrefInternationalCompsStatsScrapper(True, competition, year)
    result = scrapper.scrap(FBrefInternationalCompsStatsScrapper.base_url)

    assert len(result) > 0
    assert len(result["group_stage"]) > 0
    assert len(result["leaders"]) > 0

    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"test test_fbref_team_stats_scrapper_1() elapsed time: {elapsed_time}")


def test_fbref_national_competition_stats_scrapper_2():

    start_time = time.time()
    scrapper = FBrefInternationalCompsStatsScrapper()
    result = scrapper.scrap("https://fbref.com/en/comps/676/UEFA-Euro-Stats")

    assert len(result) > 0
    assert len(result["group_stage"]) > 0
    assert len(result["leaders"]) > 0

    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"test test_fbref_team_stats_scrapper_1() elapsed time: {elapsed_time}")
