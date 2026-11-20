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

#Team colours: same colour for all four panels too
ASSET_COLOURS = {
    "US Stocks": "#c0392b",          #Red (SPY)
    "Gold": "#d4a017",               #Gold (GLD)
    "US Government Bonds": "#3a9a5b", #green (TLT)
    "Oil": "#2e6fbf",                  #blue (USO)
}

#Short names for labelling bubbles
CRISIS_SHORT = {
    "2008 Financial Crisis": "2008",
    "COVID-19 Crash": "COVID",
    "2022 Market Stress": "2022",
}

#House style for every chart
INK, MUTED = "#0b0b0b", "#52514e"
plt.rcParams.update({
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid":True, "grid.color": "#e4e3df",
    "axes.edgecolor": MUTED,
    "axes.labelcolor":MUTED,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "font.size":11,
})

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
    Returns (days, True) if it has recovered, or (days so far, False) if it hasn't yet."""
    peak_price = prices.loc[peak_date]
    after_trough = prices.loc[trough_date:]                     #from the bottom to the end of the data
    back_above = after_trough[after_trough >= peak_price]       #days at or above the old peak

    if len(back_above) == 0:                                    #never recovered
        return len(after_trough) - 1, False                     #days so far, and "not recovered"
    else:
        recovery_date = back_above.index[0]                         #first day it got back
        return len(prices.loc[trough_date:recovery_date]) - 1, True


def crisis_row(prices, ticker, crisis_name, start, end):
    """All the measures for one asset in one crisis, as one row of the table."""
    dd = max_drawdown(prices[ticker], start, end)
    vol = peak_volatility(prices[ticker], start, end)
    days, recovered = recovery_days(prices[ticker], dd["peak_date"], dd["trough_date"])

    if recovered:
        recovered_text = "Yes"
    else:
        recovered_text = "No"
    return {
        "Crisis": crisis_name,
        "Asset": ASSET_NAMES[ticker],
        "Max drawdown (%)": round(dd["drawdown"], 2),
        "Peak yearly volatility (%)": round(vol, 2),
        "Recovery (trading days)": days,
        "Recovery (years)": round(days / 252,1),
        "Recovered": recovered_text,
        }


def compare_crises(prices):
    """Build the full comparison table: every asset in every crisis."""
    rows = []
    for crisis_name in CRISES:
        start, end = CRISES[crisis_name]
        for ticker in ASSET_NAMES:
            rows.append(crisis_row(prices, ticker, crisis_name, start, end))
    return pd.DataFrame(rows)       


def plot_comparison(table, measure="Max drawdown (%)"):
    """Grouped bar chart: one group of bars per crisis, one bar per asset."""
    # Find the worst row, so the title can state the finding
    if measure == "Max drawdown (%)":
        ranked = table.sort_values(measure)
    else:
        ranked = table.sort_values(measure, ascending= False)
    worst = ranked.iloc[0]

    fig, ax = plt.subplots(figsize=(11, 5), layout="constrained")
    sns.barplot(data=table, x="Crisis", y=measure, hue="Asset",
                palette=ASSET_COLOURS, errorbar=None, ax=ax)
    ax.axhline(0, color="grey")
    ax.set_title(f"{worst['Asset']} was hit hardest: {worst[measure]:.1f}% in the {worst['Crisis']}",
                 loc="left", fontweight="bold", color=INK)
    ax.set_xlabel("Source: Yahoo Finance daily prices (SPY, GLD, TLT, USO), 2007 onwards.",
                  loc="left", fontsize=9)
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1, 1), title="Asset")
    return fig


def plot_bubbles(table):
   """Bubble chart: how far each asset fell, how long it took to recover,
    and how wild it got (bubble size)."""
   slowest = table.sort_values("Recovery (trading days)", ascending=False).loc[0]
   if slowest["Recovered"] == "No":
       headline = f"{slowest['Asset']} has still not recovered from the {slowest['Crisis']}"
   else:
       headline = f"{slowest['Asset']} look longest to recover, after the {slowest['Crisis']}"
   fig, ax = plt.subplots(figsize=(11, 6), layout="constrained")
   sns.scatterplot(data=table,
                   x="Max drawdown (%)",
                   y="Recovery (years)",
                   hue="Asset",
                   size="Peak yearly volatility (%)",
                   sizes=(100, 1500),
                   palette=ASSET_COLOURS, alpha=0.7, ax=ax)
   ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1, 1))
   ax.set_title(headline, loc="left", fontweight="bold", color=INK)
   ax.axhline(1, color=MUTED, linestyle=":", linewidth=1)
   ax.text(table["Max drawdown (%)"].min(), 1.2, "1 year", color=MUTED, fontsize=9)
   for i, row in table.iterrows():                       # one row = one bubble
        label = CRISIS_SHORT[row["Crisis"]]
        if row["Recovered"] == "No":
            label = label + " (not yet recovered)"
        ax.annotate(label,
                    (row["Max drawdown (%)"], row["Recovery (years)"]),
                    xytext=(10, 10), textcoords="offset points",
                    fontsize=9, color=MUTED)
   return fig
   
                                


prices = load_prices()
table = compare_crises(prices)
plot_bubbles(table)
plt.show()
