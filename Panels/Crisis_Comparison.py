import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
#Crises periods agreed by the team
CRISES = {
    "2008 Financial Crises": ("2007-10-01", "2009-03-31"),
    "COVID-19 Crash": ("2020-02-01", "2020-04-30"),
    "2022 Market Stress": ("2021-12-01", "2022-10-31")
}
#Full names for each ticker
ASSET_NAMES = {
    "SPY": "US Stocks",
    "GLD": "Gold",
    "TLT": "US Government Bonds",
    "USO": "Oil"
}


def load_prices():
    """Load daily prices from market_data.csv with the dates as the index."""
    prices = pd.read_csv("Data/market_data.csv", index_col="Date", parse_dates=True)
    return prices


def running_peak(prices):
    """For each day, the highest price seen so far."""
    peaks=[]
    highest = prices.iloc[0]    #Starting with the first price as highest
    for price in prices:
        if price > highest:
            highest = price
        peaks.append(highest)
    return pd.Series(peaks, index=prices.index)


def max_drawdown(prices, start, end):
    """Worst percentage fall from a peak from start to end of the period."""
    window = prices.loc[start:end]                          #Dates during the crisis
    drawdown = (window / running_peak(window) - 1) * 100    #Percentage below the peak each day   
    worst = drawdown.min()                                  #The worst drawdown day                                #Worst day
    return worst

prices = load_prices()
start, end = CRISES["2008 Financial Crises"]

results = {}
for ticker in ASSET_NAMES:
    worst = max_drawdown(prices[ticker], start, end)
    results[ticker] = worst
    print(f"The worst drawdown for {ASSET_NAMES[ticker]} was {worst:.2f}%")

hardest = min(results, key=results.get)
safest = max(results, key=results.get)
print(f"\nThe hardest hit asset was {ASSET_NAMES[hardest]} with a drawdown of {results[hardest]:.2f}%")
print(f"The asset that held up the best was {ASSET_NAMES[safest]} with a drawdown of {results[safest]:.2f}%")