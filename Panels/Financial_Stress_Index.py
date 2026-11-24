"""Financial Stress Index panel for the Financial Stress Dashboard.

Owner: Dara Quinn

Shows the St. Louis Fed Financial Stress Index (FRED series STLFSI4).
A value of 0 means normal stress in financial markets. Values above 0 mean more stress than normal, values below 0 mean less.
"""

import pandas as pd
import matplotlib.pyplot as plt

# --- Settings ---

# Where the data file lives (relative to main project folder)
DATA_FILE = "Data/stlfsi.csv"

# Crisis periods agreed by group : name -> (start date, end date)
CRISES = {
    "2008 Financial Crisis": ("2007-10-01", "2009-03-31"),
    "COVID-19 Crash": ("2020-02-01", "2020-04-30"),
    "2022 Market Stress": ("2021-12-01", "2022-10-31"),
}

# One colour per crisis, so each shaded area looks different
CRISIS_COLOURS = {
    "2008 Financial Crisis": "#c0392b",
    "COVID-19 Crash": "#8e44ad",
    "2022 Market Stress": "#d68910",
}

# --- Functions ---

def load_stress_index(path: str = DATA_FILE) -> pd.Series:
    """Load the weekly Financial Stress Index from a CSV file.

    Args:
        path (str): Location of the CSV file downloaded from FRED.

    Returns:
        pd.Series: Stress index values, with the dates as the index.
    """
    df = pd.read_csv(path)
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    df = df.set_index("observation_date")
    df = df.dropna()
    return df["STLFSI4"]

def calculate_sma(prices: list, k: int) -> list:
    """Calculate a k-period Simple Moving Average

    Args:
        prices (list): The values to average, oldest first.
        k (int) : How many values go into each average.
    
    Returns:
        list: The moving avergaes. This list is k - 1 items shorter than prices, because the first average needs k values.
    """

    sma_values = []
    for i in range(k - 1, len(prices)):
        window_sum = sum(prices[i - k + 1:i + 1])
        sma_values.append(window_sum / k)
    return sma_values

def smooth_stress_index(stress: pd.Series, weeks: int) -> pd.Series:
    """Smooth the stress index with a moving average.

    Args:
        stress (pd.Series): Weekly stress index values.
        weeks (int): Number of weeks to average. 1 means no smoothing.

    Returns:
        pd.Series: The smoothed values, with matching dates.
    """
    if weeks <= 1:
        return stress
    sma_values = calculate_sma(list(stress.values), weeks)
    # Each average belongs to the last date in its window
    return pd.Series(sma_values, index=stress.index[weeks - 1:])

# --- Quick test (only runs when this file is run directly) ---

if __name__ == "__main__":
    stress = load_stress_index()
    print(stress.head())
    print(stress.tail())
