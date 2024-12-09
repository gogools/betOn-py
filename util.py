# Description: Utility functions for the project

def build_histogram(data: list, default: int = 0):
    """
    Build a histogram from a list of data
    """
    histogram = {}

    for item in data:
        histogram.setdefault(item, default)
        histogram[item] += 1

    return histogram
