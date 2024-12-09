def pass_data_from_teams_to_lsf(team_stats: dict, lsf_team_stats: dict):

    advance_goalkeeping_total = {}
    for ag_total in team_stats["advance_goalkeeping"]["total"]:
        if ag_total["player"] == "Squad Total":
            advance_goalkeeping_total = ag_total
            break

    lsf_team_stats["psxg_total"] = advance_goalkeeping_total["expected_psxg"]
    lsf_team_stats["psxg/sot_total"] = advance_goalkeeping_total["expected_psxg/sot"]
    lsf_team_stats["psxg+/-_total"] = advance_goalkeeping_total["expected_psxg+/-"]
    lsf_team_stats["gk_num"] = len(advance_goalkeeping_total["advance_goalkeeping"]["data"])