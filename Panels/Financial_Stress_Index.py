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

# --- Quick test (only runs when this file is run directly) ---

if __name__ == "__main__":
    stress = load_stress_index()
    print(stress.head())
    print(stress.tail())
    