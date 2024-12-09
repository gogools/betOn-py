import os
import json
import shutil
import time
import fitz

from crawler_scrapper import FBrefTeamStatsScrapper
from crawler_scrapper.FBrefLeaguesScoresFixturesScrapper import FBrefLeaguesScoresFixturesScrapper
from simulator.fbref.soccer_match_simulation import SoccerMatchSimulation
from util import msg, today_date, delete_files_in_folder, format_file_name, err


def simulate_with_h_a_seasons_stats(league: str, season: str, seasons_back: int):
    start_time = time.time()

    all_scores_fixtures = []
    lsf_season_data = {}
    for i in range(seasons_back,-1,-1):

        aux_season = f"{int(season.split("-")[0])-i}-{int(season.split("-")[1])-i}"
        prepare_folder_structure(league, aux_season)

        lsf_data = get_league_scores_fixtures_data(league, aux_season)

        if aux_season == season:
            lsf_season_data = lsf_data

        all_scores_fixtures.extend(lsf_data["scores_fixtures"]["data"])

    lsf_season_data["past_seasons_fixtures"] = all_scores_fixtures

    if len(lsf_season_data["fixtures_2_sim"]) == 0 and lsf_season_data["current_season"] == season:
        print(f"No fixtures to simulate for league: {league}, season: {season}")
    else:
        for fixture_2_sim in lsf_season_data["fixtures_2_sim"]:
            print(f"\n=== Simulating week:{fixture_2_sim['week']} - {fixture_2_sim['local']} vs {fixture_2_sim['away']}, "
                  f"{fixture_2_sim['date']} in {fixture_2_sim['venue']} ===")

            sim = SoccerMatchSimulation(fixture_2_sim['local'], fixture_2_sim['away'], lsf_season_data)
            results = sim.simulation_with_home_away_performance()

            older_season = f"{int(season.split("-")[0]) - seasons_back}-{int(season.split("-")[1]) - seasons_back}"
            for key, value in results.items():
                merge_pdfs(key, f"{league}_{older_season}_to_{season}_({today_date()})")

    print(f"\nSimulation elapsed time: {time.time() - start_time}")


def simulate_with_season_stats(league: str, season: str):
    start_time = time.time()

    prepare_folder_structure(league, season)

    lsf_data = get_league_scores_fixtures_data(league, season)
    print("\n=== Data loaded, starting simulation ===")

    if len(lsf_data["fixtures_2_sim"]) == 0:
        print("No fixtures to simulate")
    else:
        for fixture_2_sim in lsf_data["fixtures_2_sim"]:
            print(f"\n=== Simulating week:{fixture_2_sim['week']} - {fixture_2_sim['local']} vs {fixture_2_sim['away']}, {fixture_2_sim['date']} in {fixture_2_sim['venue']} ===")

            sim = SoccerMatchSimulation(fixture_2_sim['local'], fixture_2_sim['away'], lsf_data)
            results = sim.simulation_with_season_performance()
            for key, value in results.items():
                merge_pdfs(key, f"{league}_{season}_({today_date()})")

    # print(json.dumps(lsf_data, indent=4, ensure_ascii=False))
    print(f"\nSimulation elapsed time: {time.time()-start_time}")


def get_league_scores_fixtures_data(league: str, season: str) -> dict:

    start_time = time.time()

    if today_date("%Y") not in season: #TODO I need to improve this
        lsf_filename = format_file_name(f"{league}_stats/{league}_{season}.json", True)
    else:
        lsf_filename = format_file_name(f"{league}_stats/{league}_{season}_({today_date()}).json", True)

    if verify_if_file_exists(f"{lsf_filename}"):
        lsf = get_data_from_file(f"{lsf_filename}")
        msg(f"Data loaded from {lsf_filename}")
    else:
        lsf = FBrefLeaguesScoresFixturesScrapper(True, league, season).scrap_and_print(FBrefLeaguesScoresFixturesScrapper.base_url)

        if len(lsf) == 0:
            err("Theres no Leagues Scores Fixtures data to continue, exiting...")
            try:
                path = format_file_name(f"{league}_stats/{season}")
                shutil.rmtree(f"{path}")
                print(f"Folder '{path}' deleted successfully.")
            except OSError as e:
                print(f"Error: {e.strerror}")
            exit()

        for team in lsf["teams"]:

            team_stats = get_teams_stats(league, team, season, lsf["current_season"])

            if len(team_stats) == 0:
                err(f"Theres no {team} data to continue, exiting...")
                exit()

            pass_data_from_teams_to_lsf(team_stats, lsf["teams_stats"][team])
            extract_xg_psxg_from_lineups(lsf, team_stats)

        # gk ranking
        teams_stats_list = [{**{"team": key}, **value} for key, value in lsf["teams_stats"].items()]
        # here I compare the post-shot expected goals divided by the number of goalkeepers used by the team until the current available data
        teams_gk_list_sorted = sorted(teams_stats_list, key=lambda x: (x['psxg+/-_total']/x['gk_num']), reverse=True)
        for i, t in enumerate(teams_gk_list_sorted):
            lsf["teams_stats"][t['team']]['gk_position'] = i + 1

        lsf["teams_gk_rank"] = [t['team'] for t in teams_gk_list_sorted]

        msg(f"Data scrapped, saving to {lsf_filename}")
        save_data_2_file(lsf, f"{lsf_filename}")

    print(f"Creating file '{lsf_filename}' elapsed time: {time.time()-start_time}")
    return lsf


def get_teams_stats(league:str, team:str, season:str, current_season:str ) -> dict:

    delete_old_files(format_file_name(f"{league}_stats/{current_season}"))
    if current_season == season:
        ts_filename = format_file_name(f"{league}_stats/{season}/{team}_{league}_{season}_({today_date()}).json")
    else:
        ts_filename = format_file_name(f"{league}_stats/{season}/{team}_{league}_{season}.json")

    if verify_if_file_exists(f"{ts_filename}"):
        team_stats = get_data_from_file(f"{ts_filename}")
        msg(f"Data loaded from {ts_filename}")
    else:
        team_stats = FBrefTeamStatsScrapper(True, league, season, team).scrap_and_print(FBrefTeamStatsScrapper.base_url)
        msg(f"Data scrapped, saving to {ts_filename}")
        save_data_2_file(team_stats, f"{ts_filename}")
        msg("Wait for 7 seconds, simulating a human behavior")
        time.sleep(7)

    return team_stats


def save_data_2_file(data: dict, file_name: str):
    with open(f"{file_name}", "w") as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))
        msg(f"Data saved to {file_name}")


def get_data_from_file(file_name: str) -> dict:
    with open(f"{format_file_name(file_name)}", "r") as f:
        return json.loads(f.read())


def verify_if_file_exists(file_name: str) -> bool:
    try:
        with open(f"{format_file_name(file_name)}", "r") as f:
            content = f.read().strip()
            if content == "" or content == "{}":
                return False
            return True
    except FileNotFoundError:
        return False


def merge_pdfs(subfolder: str, output_file: str):

    print(f"Simulation: Merging PDFs for method {subfolder} to file {output_file}_{subfolder}.pdf")

    pdf_merger = fitz.open()

    for file in sorted(os.listdir(f"temp/{subfolder}")):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(f"temp/{subfolder}", file)
            pdf_doc = fitz.open(pdf_path)
            pdf_merger.insert_pdf(pdf_doc)

    pdf_merger.save(format_file_name(f"{output_file}_{subfolder}.pdf", True))
    pdf_merger.close()


def prepare_folder_structure(league: str, season: str):
    msg(f"Preparing folder structure for league: {league}, season: {season}")
    teams_stats_folder = format_file_name(f"{league}_stats/{season}")
    if not os.path.exists(teams_stats_folder):
        os.makedirs(teams_stats_folder)

    delete_files_in_folder("temp")


def delete_old_files(directory):
    msg(f"Trying to delete old files in {directory}")
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_mtime = os.path.getmtime(file_path)
            if file_mtime < time.time() - 24 * 60 * 60:
                os.remove(file_path)
                print(f"Deleted {file_path}")


def pass_data_from_teams_to_lsf(team_stats: dict, lsf_team_stats: dict):

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

    mp = lsf["teams_stats"][team_name]["mp"]
    xg = xg / mp if mp > 0 else 1
    xga = xga / mp if mp > 0 else 1
    psxg = psxg / mp if mp > 0 else 1


if __name__ == "__main__":
    simulate_with_season_stats("Premier League", "2024-2025")
    # simulate_with_h_a_seasons_stats("Premier League", "2024-2025", 5)