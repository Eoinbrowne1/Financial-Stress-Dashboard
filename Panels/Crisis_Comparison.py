import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

#Crises periods agreed by the team
CRISES = {
    "2008 Financial Crisis": ("2007-10-01", "2009-03-31"),
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
    """Worst percentage fall from a peak from start to end of the period, plus the peak and trough dates."""
    window = prices.loc[start:end]                          #Dates during the crisis
    drawdown = (window / running_peak(window) - 1) * 100    #Percentage below the peak each day   
    worst = drawdown.min()                                  #The worst drawdown day                                #Worst day

    trough_date = drawdown[drawdown == worst].index[0]

    before_trough = window.loc[:trough_date]                 #All the days before the trough
    peak_price = before_trough.max()
    peak_date = before_trough[before_trough == peak_price].index[0]

    return {"drawdown": worst, "peak_date": peak_date, "trough_date": trough_date}


def peak_volatility(prices, start, end, window=21):
    """Highest yearly volatility (%) during the period from start to end."""
    daily_returns = prices.pct_change()                #Percentage change from yesterday
    rolling_vol = daily_returns.rolling(window).std() * np.sqrt(252) * 100    
    return rolling_vol.loc[start:end].max()


def recovery_days(prices, peak_date, trough_date):
    """Trading days from the bottom until the price gets back to its old peak.
    Returns None if it never recovered."""
    peak_price = prices.loc[peak_date]
    after_trough = prices.loc[trough_date:]                     #from the bottom to the end of the data
    back_above = after_trough[after_trough >= peak_price]       #days at or above the old peak

    if len(back_above) == 0:                                    #no days found = never recovered
        return None
    else:
        recovery_date = back_above.index[0]                         #first day it got back
        return len(prices.loc[trough_date:recovery_date]) - 1 


def crisis_row(prices, ticker, crisis_name, start, end):
    """All the measures for one asset in one crisis, as one row of the table."""
    dd = max_drawdown(prices[ticker], start, end)
    vol = peak_volatility(prices[ticker], start, end)
    days = recovery_days(prices[ticker], dd["peak_date"], dd["trough_date"])
    return {
        "Crisis": crisis_name,
        "Asset": ASSET_NAMES[ticker],
        "Max drawdown (%)": round(dd["drawdown"], 2),
        "Peak yearly volatility (%)": round(vol, 2),
        "Recovery (trading days)": days,
        }


def compare_crises(prices):
    """Build the full comparison table: every asset in every crisis."""
    rows = []
    for crisis_name in CRISES:
        start, end = CRISES[crisis_name]
        for ticker in ASSET_NAMES:
            rows.append(crisis_row(prices, ticker, crisis_name, start, end))
    return pd.DataFrame(rows)       



prices = load_prices()
table = compare_crises(prices)
print(table)