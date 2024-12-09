import plotly.graph_objects as go

def plot(self, method: str, scores_sim_list: list, img: bool = False):
    print(f"\n=== Simulating: {self.home_team} vs {self.away_team} ===")
    print(f" Method: {method}")
    print("This are the first 5 most probable scores:")
    for i in range(5):
        print(f"{scores_sim_list[i]['score']} with a probability of {scores_sim_list[i]['prob'] * 100}")

    score_list = [e['score'] for e in scores_sim_list]
    score_prob_list = [e['prob'] * 100 for e in scores_sim_list]

    print("score_list", score_list[:10])
    print("score_prob_list", score_prob_list[:10])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=score_list[:10], y=score_prob_list[:10], mode='lines+markers'))
    fig.update_layout(
        title=f'Poisson Distribution {self.home_team} vs {self.away_team}',
        xaxis_title="Scores",
        yaxis_title="Probability",
    )
    if img:
        fig.write_image("my_plot.png")
    else:
        fig.show()