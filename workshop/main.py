# This is a sample Python script.
from matplotlib import pyplot as plt
from scipy.stats import poisson

from histogram import plot_plotly, plot_matplot, plot_seaborn, scatter_matplot
from read_xlsx import *
from match_simulator_excel import *
from util import print_table

filename = '/Users/dan/pet projects/bets/data/EPL Test 2019-2023.xlsx'

def excel_playground():

    print(f"Columns: {read_excel_sheet_columns(filename, 'EPL2019-stats')}")
    print(f"Index: {read_excel_sheet_index(filename, 'EPL2019-stats')}")
    print(f"Cell (1,1): {read_excel_sheet_cell(filename, 'EPL2019-stats', 1, 1)}")
    print(f"Row 0: {read_excel_sheet_row(filename, 'EPL2019-stats', 0)}")
    print(f"Col H_GD: {read_excel_sheet_col(filename, 'EPL2019-stats', 'H_GD')}")


def play_individual_seasons():

    print(f"\n\n=== Play individual seasons ===")

    years = [2019, 2020, 2021, 2022, 2023, 2024]
    home = 'Manchester City'
    away = 'Fulham'

    for year in years:
        simulation = sim_by_season(home, away, year, 161803)

        if len(simulation) == 0:
            continue

        # print_table(simulation['scores'], f'{home} vs {away}')

        # Find the key with the highest x value
        max_x_key = max(simulation['scores'], key=lambda k: simulation['scores'][k]["sim"])
        print(f"Most common score: {max_x_key} appear: {simulation['scores'][max_x_key]['sim']} times "
              f"with a prob: {simulation['scores'][max_x_key]['prob']*100}% ")

def play_by_seasons():

    print(f"\n\n=== Play by seasons ===")

    years = [2019, 2020, 2021, 2022, 2023, 2024]
    home = 'Manchester City'
    away = 'Fulham'

    simulation = sim_by_seasons(home, away, years, 161803)

    if len(simulation) == 0:
        return

    # print_table(simulation['scores'], f'{home} vs {away}')

    # Find the key with the highest x value
    max_x_key = max(simulation['scores'], key=lambda k: simulation['scores'][k]["sim"])
    print(f"Most common score: {max_x_key} appear: {simulation['scores'][max_x_key]['sim']} times "
          f"with a prob: {simulation['scores'][max_x_key]['prob']*100}% ")

    print("\nTop 3 scores:")
    for key in sorted(simulation['scores'], key=lambda k: simulation['scores'][k]['sim'], reverse=True)[:3]:
        print(f"Score: {key} appear: {simulation['scores'][key]['sim']} times with a prob: {simulation['scores'][key]['prob']*100}% ")

def play_histogram():
    plot_plotly()
    plot_matplot()
    plot_seaborn()
    scatter_matplot()


def testing_poisson():
    # Define the rate parameter (lambda)
    lam = 1.99

    # Calculate the PMF for different values of k
    x = range(9)
    probs = poisson.pmf(x, lam)

    # Plot the Poisson distribution
    plt.bar(x, probs)
    plt.xlabel('Goals')
    plt.ylabel('Probability')
    plt.title(f'Poisson Distribution (λ={lam})')
    plt.show()

    # Generate 10000 random samples from a Poisson distribution with λ=5
    samples = np.random.poisson(lam, 10000)

    # Plot the histogram of the samples
    plt.hist(samples, bins=20, density=True)
    plt.xlabel('Number of Events')
    plt.ylabel('Probability')
    plt.title(f'Poisson Distribution (λ={lam})')
    plt.show()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    play_individual_seasons()
    # play_by_seasons()
    play_histogram()
    # testing_poisson()

