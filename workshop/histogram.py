import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

import numpy as np

def plot_plotly():

    # Generate random data
    data = np.random.randn(1000)

    # Create a histogram using Plotly
    fig = go.Figure(go.Histogram(x=data))

    # Show the plot
    fig.show()

def plot_seaborn():

    # Generate random data
    data = [0,1,2,3,4,5,5,5,5,5]

    # Create a histogram using Seaborn
    sns.histplot(data, stat="density", kde=True, bins=10)

    # Show the plot
    plt.show()

def plot_matplot():
    # Generate random data
    data = np.random.randn(10)

    num_bins = int(np.log2(len(data)) + 1)

    # Create a histogram
    hist, bin_edges, patches = plt.hist(data, bins = num_bins, density = False)

    # Add labels and title
    plt.xlabel("Data")
    plt.ylabel("Density")
    plt.title("Histogram of Random Data")

    print(f"Data: {data}")
    print(f"num_bins: {num_bins}")
    print(f"hist: {hist}, sum: {sum(hist)}")
    print(f"bin_edges: {bin_edges}")
    print(f"patches: {patches}")

    # Show the plot
    plt.show()


def scatter_matplot():
    # Data sets
    x1 = [1, 2, 3, 4, 5]
    y1 = [2, 4, 5, 3, 6]

    x2 = [2, 3, 4, 5, 6]
    y2 = [3, 5, 6, 4, 7]

    x3 = [3, 4, 5, 6, 7]
    y3 = [4, 5, 6, 7, 8]

    # Create the plot
    plt.scatter(x1, y1, color='blue', label='Data Set 1')
    plt.scatter(x2, y2, color='red', label='Data Set 2')
    plt.scatter(x3, y3, color='green', label='Data Set 3')

    # Add labels and title
    plt.xlabel("X-axis Label")
    plt.ylabel("Y-axis Label")
    plt.title("Scatter Plot with Multiple Data Sets")

    # Show the legend
    plt.legend()

    # Show the plot
    plt.show()
