import statistics

import numpy as np
from fastapi import FastAPI

from util import build_histogram

app = FastAPI()


@app.get("/simulation/poisson/match")
async def poisson_simulation_match(sims: int, h_lambda: float, a_lambda: float):
    """
    Simulate a poisson match between two teams
    """
    h_goals_list = []
    a_goals_list = []
    scores_list = []

    response = {}
    histograms = {}
    stats = {}
    results = {}

    h_wins = 0
    a_wins = 0
    draws = 0

    for _ in range(sims):
        home_goals = np.random.poisson(h_lambda)
        away_goals = np.random.poisson(a_lambda)

        h_goals_list.append(home_goals)
        a_goals_list.append(away_goals)
        scores_list.append(f"{home_goals}-{away_goals}")

        if home_goals > away_goals:
            h_wins += 1
        elif home_goals < away_goals:
            a_wins += 1
        else:
            draws += 1

    histograms["scores"] = build_histogram(scores_list)
    histograms["home_goals"] = build_histogram(h_goals_list)
    histograms["away_goals"] = build_histogram(a_goals_list)
    response["histograms"] = histograms

    stats["home_goals_avg"] = statistics.mean(h_goals_list)
    stats["away_goals_avg"] = statistics.mean(a_goals_list)
    stats["home_goals_median"] = statistics.median(h_goals_list)
    stats["away_goals_median"] = statistics.median(a_goals_list)
    stats["home_goals_mode"] = statistics.mode(h_goals_list)
    stats["away_goals_mode"] = statistics.mode(a_goals_list)
    response["stats"] = stats

    results["home_wins"] = h_wins
    results["away_wins"] = a_wins
    results["draws"] = draws
    response["results"] = results

    return response


@app.get("/simulation/poisson/goals")
async def poisson_simulation_goals(sims: int, lambda_: float):
    """
    Simulate a poisson tournament goals
    """
    goals_list = np.random.poisson(lambda_, sims).tolist()

    return build_histogram(goals_list)
