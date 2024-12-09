
from simulator.soccer_match_simulation_mixin import SoccerMatchSimulationMixin
from util import stats_by_team


class SoccerMatchSimulation(SoccerMatchSimulationMixin):


    def get_team_stats(self, team:str, data_kind: str) -> dict:
        if data_kind == "last_week_lineups" and "last_week_lineups" in self.data:
            pass
            #home_lu = self.data['last_week_lineups'][f"{self.home_team}"]
            #away_lu = self.data['last_week_lineups'][f"{self.away_team}"]
            #for player in [p for p in home_lu] if len(home_lu) >= 11 else []:
            #    for p_stat in self.data

            # for player in [p for p in away_lu] if len(away_lu) >= 11 else []

        if data_kind == "past_seasons_fixtures" and "past_seasons_fixtures" in self.data:
            hw_stats = [d for d in self.data['past_seasons_fixtures'] if d['home'] == self.home_team and d['away'] == self.away_team]
            result = stats_by_team(team, hw_stats)
            self.add_prep_data_2_teams_stats(team, result)
            return result if result["mp"] != 0 else []
        elif data_kind == "team_stats":
            return self.data["teams_stats"][team] if self.data["teams_stats"][team]["mp"] != 0 else []


    def add_prep_data_2_teams_stats(self, team:str, result: dict):
        result["psxg_total"] = self.data["teams_stats"][team]["psxg_total"]
        result["psxg/sot_total"] = self.data["teams_stats"][team]["psxg/sot_total"]
        result["psxg+/-_total"] = self.data["teams_stats"][team]["psxg+/-_total"]
        result["gk_num"] = self.data["teams_stats"][team]["gk_num"]

