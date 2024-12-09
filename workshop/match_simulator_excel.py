import numpy as np
import pandas as pd

filename = '/Users/dan/pet projects/bets/data/EPL Test 2019-2023.xlsx'

def sim_by_season(home: str, away: str, season: int, sims: int) -> dict:

    print(f"\nSimulating {sims} games between {home} and {away} for season {season}")

    result = {}

    g_avg = get_goals_avg(home, away, season)

    if len(g_avg) == 0:
        return result

    home_goals = np.random.poisson(g_avg['avg_home_goals'],sims)
    away_goals = np.random.poisson(g_avg['avg_away_goals'],sims)

    pair_counts = {}
    for i in range(len(home_goals)):
        pair = f"{home_goals[i]}-{away_goals[i]}"
        if pair in pair_counts:
            pair_counts[pair]['sim'] += 1
        else:
            pair_counts[pair] = {'sim': 1}

    for key, value in pair_counts.items():
        pair_counts[key]['prob'] = round(pair_counts[key]['sim'] / sims, 5)

    result['scores'] = pair_counts
    result['avg_home_goals'] = g_avg['avg_home_goals']
    result['avg_away_goals'] = g_avg['avg_away_goals']

    return result

def sim_by_seasons(home: str, away: str, seasons: list, sims: int) -> dict:

    print(f"\nSimulating {sims} games between {home} and {away} for season {seasons}")

    result = {}

    avg_h_goals = 0
    avg_a_goals = 0
    g_avg = {}
    for season in seasons:
        g_avg = get_goals_avg(home, away, season)

        if len(g_avg) == 0:
            continue

        avg_h_goals += g_avg['avg_home_goals']
        avg_a_goals += g_avg['avg_away_goals']

    avg_h_goals = avg_h_goals / len(seasons)
    avg_a_goals = avg_a_goals / len(seasons)

    home_goals = np.random.poisson(avg_h_goals,sims)
    away_goals = np.random.poisson(avg_a_goals,sims)

    pair_counts = {}
    for i in range(len(home_goals)):
        pair = f"{home_goals[i]}-{away_goals[i]}"
        if pair in pair_counts:
            pair_counts[pair]['sim'] += 1
        else:
            pair_counts[pair] = {'sim': 1}

    for key, value in pair_counts.items():
        pair_counts[key]['prob'] = round(pair_counts[key]['sim'] / sims, 5)

    result['scores'] = pair_counts
    result['avg_home_goals'] = g_avg['avg_home_goals']
    result['avg_away_goals'] = g_avg['avg_away_goals']

    return result

def get_data_by_season(home: str, away: str, season: int) -> dict:

    data = {}
    sheet = f'EPL{season}-stats'

    try:
        df = pd.read_excel(filename, sheet)

        for index, row in df.iterrows():
            # print(f"Squad: {row['Squad']}")
            if row['Squad'] == home:
                data['home'] = row
            if row['Squad'] == away:
                data['away'] = row

        if 'home' not in data or 'away' not in data:
            print(f"Warning: Team <{away if 'home' in data else home}> not found in the data year {season}")
            return {}

        return data

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return {}


def get_goals_avg(home: str, away: str, season: int) -> dict:

    result = {}
    data = get_data_by_season(home, away, season)

    if len(data) == 0:
        return result

    result['avg_home_goals'] = data['home']['H_GF'] / data['home']['H_MP']
    result['avg_away_goals'] = data['away']['A_GF'] / data['away']['A_MP']

    return result