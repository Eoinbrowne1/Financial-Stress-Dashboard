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