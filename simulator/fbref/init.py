import os
import time
import fitz

from simulator.fbref.scrap_logic import get_league_scores_fixtures_data
from simulator.fbref.soccer_match_simulation import SoccerMatchSimulation
from util import msg, today_date
from util.util_file import format_file_name, delete_files_in_folder


def simulate_with_h_a_seasons_stats(league: str, season: str, seasons_back: int):
    start_time = time.time()

    all_scores_fixtures = []
    lsf_season_data = {}
    for i in range(seasons_back,-1,-1): # taking the current season into account and go down to the past seasons

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
                merge_pdfs(key, f"output/{league}_{older_season}_to_{season}_({today_date()})")

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
                merge_pdfs(key, f"output/{league}_{season}_({today_date()})")

    # print(json.dumps(lsf_data, indent=4, ensure_ascii=False))
    print(f"\nSimulation elapsed time: {time.time()-start_time}")


def merge_pdfs(subfolder: str, output_file: str):

    print(f"Simulation: Merging PDFs for method {subfolder} to file {output_file}_{subfolder}.pdf")

    pdf_merger = fitz.open()

    for file in sorted(os.listdir(f"output/temp/{subfolder}")):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(f"output/temp/{subfolder}", file)
            pdf_doc = fitz.open(pdf_path)
            pdf_merger.insert_pdf(pdf_doc)

    pdf_merger.save(format_file_name(f"{output_file}_{subfolder}.pdf", True))
    pdf_merger.close()


def prepare_folder_structure(league: str, season: str):
    msg(f"Preparing folder structure for league: {league}, season: {season}")

    teams_stats_folder = format_file_name(f"output/{league}_stats/{season}")
    if not os.path.exists(teams_stats_folder):
        os.makedirs(teams_stats_folder)

    temp_stats_folder = format_file_name("output/temp/imgs")
    if not os.path.exists(temp_stats_folder):
        os.makedirs(temp_stats_folder)

    delete_files_in_folder("output/temp")


if __name__ == "__main__":
    # Change the working directory
    work_dir = os.path.join(os.getcwd(), "simulator", "fbref")
    os.chdir(work_dir)

    simulate_with_season_stats("Premier League", "2024-2025")
    # simulate_with_h_a_seasons_stats("Premier League", "2024-2025", 5)