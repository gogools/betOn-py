import json
import shutil
import time

from crawler_scrapper import FBrefTeamStatsScrapper
from crawler_scrapper.FBrefLeaguesScoresFixturesScrapper import FBrefLeaguesScoresFixturesScrapper
from util import today_date, msg, err
from util.util_file import format_file_name, verify_if_file_exists, save_dict_2_file, delete_24h_old_files


def get_league_scores_fixtures_data(league: str, season: str) -> dict:

    start_time = time.time()

    # checking if the season is the current one p.e. 2024-2025 and today is 2024
    # current season creates a folder with the current date, older seasons don't
    if today_date("%Y") in season.split("-"):
        lsf_filename = format_file_name(f"output/{league}_stats/{league}_{season}_({today_date()}).json", True)
    else:
        lsf_filename = format_file_name(f"output/{league}_stats/{league}_{season}.json", True)

    if verify_if_file_exists(f"{lsf_filename}"):
        lsf = get_data_from_file(f"{lsf_filename}")
        msg(f"Data loaded from {lsf_filename}")
    else:

        # here we get the league scores fixtures data for the league and season
        lsf = FBrefLeaguesScoresFixturesScrapper(True, league, season).scrap_and_print()

        if len(lsf) == 0 or lsf == "{}":
            err("There's no Leagues Scores Fixtures data to continue, exiting...")
            try:
                path = format_file_name(f"output/{league}_stats/{season}")
                shutil.rmtree(f"{path}")
                print(f"Folder '{path}' deleted successfully.")
            except OSError as e:
                print(f"Error: {e.strerror}")
            exit()

        for team in lsf["teams"]:

            # here we get the team stats for the league and season
            team_stats = get_teams_stats(league, team, season, lsf["current_season"])

            if len(team_stats) == 0 or team_stats == "{}":
                err(f"Theres no {team} data to continue, exiting...")
                exit()

            # this is the where we gather the data from the team stats to the league scores fixtures data and play with it
            copy_data_from_teams_to_lsf(team_stats, lsf["teams_stats"][team])
            extract_xg_psxg_from_lineups(lsf, team_stats)

        # gk ranking
        teams_stats_list = [{**{"team": key}, **value} for key, value in lsf["teams_stats"].items()]
        # here I compare the post-shot expected goals divided by the number of goalkeepers used by the team until the current available data
        teams_gk_list_sorted = sorted(teams_stats_list, key=lambda x: (x['psxg+/-_total']/x['gk_num']), reverse=True)
        for i, t in enumerate(teams_gk_list_sorted):
            lsf["teams_stats"][t['team']]['gk_position'] = i + 1

        lsf["teams_gk_rank"] = [t['team'] for t in teams_gk_list_sorted]

        msg(f"Data scrapped, saving to {lsf_filename}")
        save_dict_2_file(lsf, f"{lsf_filename}")

    print(f"Creating file '{lsf_filename}' elapsed time: {time.time()-start_time}")
    return lsf


def get_data_from_file(file_name: str) -> dict:
    with open(f"{format_file_name(file_name)}", "r") as f:
        return json.loads(f.read())


def get_teams_stats(league:str, team:str, season:str, current_season:str ) -> dict:

    delete_24h_old_files(format_file_name(f"{league}_stats/{current_season}"))
    if current_season == season:
        ts_filename = format_file_name(f"output/{league}_stats/{season}/{team}_{league}_{season}_({today_date()}).json")
    else:
        ts_filename = format_file_name(f"output/{league}_stats/{season}/{team}_{league}_{season}.json")

    if verify_if_file_exists(f"{ts_filename}"):
        team_stats = get_data_from_file(f"{ts_filename}")
        msg(f"Data loaded from {ts_filename}")
    else:
        # here we go to get the team stats for the league and season
        team_stats = FBrefTeamStatsScrapper(True, league, season, team).scrap_and_print()
        msg(f"Data scrapped, saving to {ts_filename}")
        save_dict_2_file(team_stats, f"{ts_filename}")
        msg("Wait for 7 seconds, simulating a human behavior")
        time.sleep(7)

    return team_stats


def copy_data_from_teams_to_lsf(team_stats: dict, lsf_team_stats: dict):

    advance_goalkeeping_total = {}
    for ag_total in team_stats["advance_goalkeeping"]["total"]:
        if ag_total["player"] == "Squad Total":
            advance_goalkeeping_total = ag_total
            break

    lsf_team_stats["psxg_total"] = advance_goalkeeping_total["expected_psxg"]
    lsf_team_stats["psxg/sot_total"] = advance_goalkeeping_total["expected_psxg/sot"]
    lsf_team_stats["psxg+/-_total"] = advance_goalkeeping_total["expected_psxg+/-"]
    lsf_team_stats["gk_num"] = len(team_stats["advance_goalkeeping"]["data"])


def extract_xg_psxg_from_lineups(lsf: dict, team_stats:dict):

    team_name = team_stats["summary"]["team_short"]

    xg = 0
    xga = 0
    if len(lsf["last_week_lineups"][team_name]["lineup"]) >= 11:
        for player in lsf["last_week_lineups"][team_name]["lineup"][:11]:
            for p_stats in team_stats["standard_stats"]["data"]:
                if player["player"] == p_stats["player"]:
                    #p_stats
                    xg += p_stats["expected_xg"]
                    xga += p_stats["expected_xag"]

    psxg = 0
    if len(lsf["last_week_lineups"][team_name]["lineup"]) > 0:
        gk = lsf["last_week_lineups"][team_name]["lineup"][0]
        for p_stats in team_stats["advance_goalkeeping"]["data"]:
            if gk["player"] == p_stats["player"]:
                psxg += p_stats["expected_psxg+/-"]

    # mp = lsf["teams_stats"][team_name]["mp"]
    # xg = xg / mp if mp > 0 else 1
    # xga = xga / mp if mp > 0 else 1
    # psxg = psxg / mp if mp > 0 else 1