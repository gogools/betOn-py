import os

from fpdf import FPDF
import numpy as np
import plotly.graph_objects as go

from util import today_date, format_file_name, stats_by_team


class SoccerMatchSimulationMixin:

    # sims num constant
    SIMS = 161803

    home_team = ""
    away_team = ""
    data = {}

    output_temp = "output/temp"


    def __init__(self, home_team: str, away_team: str, data: dict):
        self.home_team = home_team
        self.away_team = away_team
        self.data = data


    def simulation_with_season_performance(self) -> dict:

        results = { "xG": self.pure_xg("xG"),
                    "xG_GK": self.pure_xg_gk("xG_GK"),
                    "ha_xG": self.home_away_xg("ha_xG")}

        return results


    def simulation_with_home_away_performance(self):

        results = {"xG": self.pure_xg("xG", "past_seasons_fixtures"),
                   "xG_GK": self.pure_xg_gk("xG_GK", "past_seasons_fixtures")
        }

        return results


    def pure_xg(self, subfolder: str, data_kind: str = "team_stats") -> str:

        if not os.path.exists(format_file_name(f"{self.output_temp}/{subfolder}")):
            os.makedirs(f"{self.output_temp}/{subfolder}")

        home = self.get_team_stats(self.home_team, data_kind)
        h_xg = home["xg"] / home["mp"] # home_xg_per_game: season xG / matches played
        h_xg_a = home["xga"] / home["mp"] # home_xg_against_per_game: season xG against / matches played

        away = self.get_team_stats(self.away_team, data_kind)
        a_xg = away["xg"] / away["mp"] # away_xg_per_game: season xG / matches played
        a_xg_a = away["xga"] / away["mp"] # away_xg_against_per_game: season xG against / matches played

        h_eff = (h_xg + a_xg_a) / 2
        a_eff = (a_xg + h_xg_a) / 2

        # eff_data = self.poisson_orderby_prob(h_eff, a_eff)
        sim = self.poisson(h_eff, a_eff, self.SIMS)

        return self.write_2_pdf(subfolder, sim, self.plot(subfolder, sim, img=True), top=5)


    def pure_xg_gk(self, subfolder: str, data_kind: str = "team_stats") -> str:

        if not os.path.exists(format_file_name(f"{self.output_temp}/{subfolder}")):
            os.makedirs(f"{self.output_temp}/{subfolder}")

        home = self.get_team_stats(self.home_team, data_kind)
        h_xg_eff = home["xg"] / home["mp"] # team xG per game
        h_xga_eff = home["xga"] / home["mp"] # team xG against per game
        h_gk_eff = (home["psxg+/-_total"] / home["gk_num"]) / home["mp"] # team post-shot xG +/- per game

        away = self.get_team_stats(self.away_team, data_kind)
        a_xg_eff = away["xg"] / away["mp"] # team xG per game
        a_xga_eff = away["xga"] / away["mp"] # team xG against per game
        a_gk_eff = (away["psxg+/-_total"] / away["gk_num"]) / away["mp"] # team post-shot xG +/- per game

        h_eff = (h_xg_eff + a_xga_eff)/2 - a_gk_eff
        a_eff = (a_xg_eff + h_xga_eff)/2 - h_gk_eff

        print(f"xG - GK Simulation: {self.home_team} vs {self.away_team}")
        print(f"Home team: {self.home_team} xG: {h_xg_eff} - GK: {h_gk_eff}, eff: {h_eff}")
        print(f"Away team: {self.away_team} xG: {a_xg_eff} - GK: {a_gk_eff}, eff: {a_eff}")

        # eff_data = self.poisson_orderby_prob(h_eff, a_eff)
        sim = self.poisson(h_eff, a_eff, self.SIMS)

        return self.write_2_pdf(subfolder, sim, self.plot(subfolder, sim, img=True), top=5)


    def home_away_xg(self, subfolder: str, data_kind: str = "team_stats") -> str:

        if not os.path.exists(format_file_name(f"{self.output_temp}/{subfolder}")):
            os.makedirs(f"{self.output_temp}/{subfolder}")

        home = self.get_team_stats(self.home_team, data_kind)
        h_xg_eff = home["xg_home"] / home["mp"]  # home team xG per game at home
        h_xga_eff = home["xga_home"] / home["mp"]  # home team xG against per game at home

        away = self.get_team_stats(self.away_team, data_kind)
        a_xg_eff = away["xg_away"] / away["mp"]  # away team xG per game away
        a_xga_eff = away["xga_away"] / away["mp"]  # away team xG against per game away

        h_eff = (h_xg_eff + a_xga_eff) / 2
        a_eff = (a_xg_eff + h_xga_eff) / 2

        print(f"Home Away xG Simulation: {self.home_team} vs {self.away_team}")
        print(f"Home team: {self.home_team} xG: {h_xg_eff} - xGa: {h_xga_eff}, eff: {h_eff}")
        print(f"Away team: {self.away_team} xG: {a_xg_eff} - xGa: {a_xga_eff}, eff: {a_eff}")

        # eff_data = self.poisson_orderby_prob(h_eff, a_eff)
        sim = self.poisson(h_eff, a_eff, self.SIMS)

        return self.write_2_pdf(subfolder, sim, self.plot(subfolder, sim, img=True), top=5)


    def home_away_xg_gk(self) -> list:
        pass


    def get_team_stats(self, team:str, data_kind: str) -> dict:
        pass


    def add_prep_data_2_teams_stats(self, team:str, result: dict):
        pass

    def poisson(self, home_eff: float, away_eff: float, sims: int) -> dict:

        sim_h_goals = np.random.poisson(home_eff, sims)
        sim_a_goals = np.random.poisson(away_eff, sims)

        scores = {}
        local = 0
        draw = 0
        away = 0
        for i in range(len(sim_h_goals)):
            score = f"{sim_h_goals[i]}-{sim_a_goals[i]}"
            if score in scores:
                scores[score]['count'] += 1
            else:
                scores[score] = {'count': 1}

            if sim_h_goals[i] > sim_a_goals[i]:
                local += 1
            elif sim_h_goals[i] < sim_a_goals[i]:
                away += 1
            else:
                draw += 1

        for key, value in scores.items():
            scores[key]['prob'] = round(scores[key]['count'] / sims, 3)

        return {'scores': scores,
                'home_team': self.home_team,
                'away_team': self.away_team,
                'local_win_prob': local / sims,
                'draw_prob': draw / sims,
                'away_win_prob': away / sims,
                'home_eff': home_eff,
                'away_eff': away_eff}


    def poisson_orderby_prob(self, home_eff: float, away_eff: float) -> list:

        poisson = self.poisson(home_eff, away_eff, self.SIMS)
        return sorted([{**{"score": key}, **value} for key, value in poisson["scores"].items()], key=lambda x: (x['prob']), reverse=True)


    def plot(self, method:str, sim: dict, img: bool = False, sort: bool = True, top: int = 10 ) -> str:
        print(f"Plotting: {self.home_team} vs {self.away_team}")
        print(f" Method: {method}")
        print("This are the first 5 most probable scores:")

        sim_list = [{**{"score": key}, **value} for key, value in sim["scores"].items() if value['prob'] > 0]
        for s in sorted(sim_list, key=lambda x: (x['prob']), reverse=True)[:5]:
            print(f"{s['score']} with a probability of {s['prob'] * 100}")

        sim_list = (sorted(sim_list, key=lambda x: (x['prob']), reverse=True) if sort else sim_list)[:top if top > 0 else len(sim_list)]
        score_list = [e['score'] for e in sim_list]
        score_prob_list = [e['prob'] * 100 for e in sim_list]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=score_list, y=score_prob_list, mode='lines+markers'))
        fig.update_layout(
            title=f'{self.home_team} vs {self.away_team} - Top {top} scores by probability',
            xaxis_title="Scores",
            yaxis_title="Probability")
        if img:
            img_name = format_file_name(f"{self.output_temp}/imgs/{self.home_team}_VS_{self.away_team}_{today_date()}_{method}.png")
            fig.write_image(img_name)
            return img_name
        else:
            fig.show()


    def write_2_pdf(self, method:str, sim: dict, image_name: str, sort: bool = True, top: int = 10 ) -> str:
        # Create a PDF object
        pdf = FPDF()
        pdf.add_page()

        pew = pdf.w - (pdf.l_margin + pdf.r_margin)

        # Add title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(pew, 10, f"=== Simulating: {self.home_team} vs {self.away_team} ===", ln=1, align='C')
        pdf.cell(pew, 10, f" Method: {method}", ln=1, align='C')

        pdf.set_font("Arial", "B", 14)
        pdf.cell(pew, 10, "Local-Draw-Away Probabilities:", ln=1)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(pew, 8, f"Local: {round(sim['local_win_prob'] * 100, 2)}% - "
                         f"Draw: {round(sim['draw_prob'] * 100, 2)}% - "
                         f"Away: {round(sim['away_win_prob'] * 100, 2)}%", ln=1, align='C')

        # Add text
        pdf.set_font("Arial", "B", 14)
        pdf.cell(pew, 10, "This are the first 5 most probable scores:", ln=1)

        # Add a table header
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(pew/4, 8, '', 1, 0, 'C')
        pdf.cell(pew/4, 8, self.home_team, 1, 0, 'C')
        pdf.cell(pew/4, 8, self.away_team, 1, 0, 'C')
        pdf.cell(pew/4, 8, "Probability", 1, 1, 'C')

        # Add table rows
        pdf.set_font('Arial', '', 10)
        sim_list = [{**{"score": key}, **value} for key, value in sim["scores"].items() if value['prob'] > 0]
        sim_list = (sorted(sim_list, key=lambda x: (x['prob']), reverse=True) if sort else sim_list)[:top if top > 0 else len(sim_list)]
        for i in range(len(sim_list)):
            pdf.cell(pew/4, 8, f"#{i+1}", 1, 0, 'C')
            pdf.cell(pew/4, 8, f"{sim_list[i]['score'].split('-')[0]}", 1, 0, 'C')
            pdf.cell(pew/4, 8, f"{sim_list[i]['score'].split('-')[1]}", 1, 0, 'C')
            pdf.cell(pew/4, 8, f"{round(sim_list[i]['prob'] * 100,2)}%", 1, 1, 'C')

        pdf.cell(pew, 4, "", 0, 1, 'C')

        # Add image in the center X axis of the page but just below the table
        pdf.image(f"{image_name}", x=pew/5, w=pew*.75)

        pdf_name = format_file_name(f"{self.output_temp}/{method}/{image_name[image_name.rfind("/") + 1: image_name.rfind(".")]}.pdf")
        pdf.output(pdf_name)

        return pdf_name

