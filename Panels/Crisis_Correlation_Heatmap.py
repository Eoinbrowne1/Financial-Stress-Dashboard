import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

data = pd.read_csv("Data/market_data_expanded.csv")
data["Date"] = pd.to_datetime(data["Date"])
TICKERS = [ "SPY", "QQQ", "IWM", "EFA", "EEM","TLT", "IEF", "LQD", "HYG","GLD", "USO", "VNQ"]
returns = np.log(data[TICKERS] / data[TICKERS].shift(1))
returns = returns.dropna()
returns["Date"] = data.loc[returns.index, "Date"]

def crisis_correlation(start_date, end_date):
    crisis_data = returns[
        (returns["Date"] >= start_date) &
        (returns["Date"] <= end_date)
    ]
    correlation_matrix = crisis_data[TICKERS].corr()
    return correlation_matrix

corr_2008 = crisis_correlation("2007-10-01", "2009-03-31")
corr_covid = crisis_correlation("2020-02-01", "2020-04-30")
corr_2022 = crisis_correlation("2021-12-01", "2022-10-31")

def plot_heatmap(correlation_matrix, title, average_abs_corr, normal_average_abs_corr, correlation_change, best_diversifier, best_diversifier_corr):
    fig, ax = plt.subplots(figsize=(13,8))
    ax.grid(False)
    mask = np.tril(
        np.ones(correlation_matrix.shape, dtype=bool)
    )
    sns.heatmap(
        correlation_matrix,
        annot=True,
        cmap="RdBu",
        vmin=-1 ,
        vmax=1 ,
        center=0 ,
        ax=ax ,
        mask=mask,
        fmt=".2f",
        annot_kws={"size": 9},
        cbar_kws={"label": "Correlation", "shrink": 0.85, "pad": 0.02}
        )
    equities_key = (
        "EQUITIES\n"
        "SPY: S&P 500\n"
        "QQQ: Nasdaq 100\n"
        "IWM: Russell 2000\n"
        "EFA: MSCI EAFE\n"
        "EEM: MSCI Emerging Markets\n"
    )
    bonds_key = (
        "BONDS\n"
        "TLT: 20+ Year Treasury Bond\n"
        "IEF: 7-10 Year Treasury Bond\n"
        "LQD: Investment Grade Corporate Bond\n"
        "HYG: High Yield Corporate Bond\n"
    )
    alternatives_key = (
        "ALTERNATIVES\n"
        "GLD: Gold\n"
        "USO: Crude Oil\n"
        "VNQ: Real Estate\n")
    fig.text(0.83, 0.88, "ASSET GUIDE", fontsize=12, fontweight="bold",va="top")
    fig.text(0.83, 0.78, equities_key, fontsize=9, va="top", linespacing= 1.5, bbox=dict(boxstyle="round, pad=0.5", facecolor="#f2f2f2", edgecolor="#cccccc"))
    fig.text(0.83, 0.58, bonds_key, fontsize=9, va="top", linespacing= 1.5, bbox=dict(boxstyle="round, pad=0.5", facecolor="#f2f2f2", edgecolor="#cccccc"))
    fig.text(0.83, 0.38, alternatives_key, fontsize=9, va="top", linespacing= 1.5, bbox=dict(boxstyle="round, pad=0.5", facecolor="#f2f2f2", edgecolor="#cccccc"))
    fig.subplots_adjust(right=0.80)      
    ax.set_title(f"{title} - Cross Asset Correlations", loc= "left", fontweight = "bold", fontsize=14, pad=12)
    if correlation_change > 0:
        impact_interpration = "Cross-asset relationships strengthened"
    elif correlation_change < 0:
        impact_interpration = "Cross-asset relationships weakened"
    else: 
        impact_interpration = "No major change in cross-asset relationships"      
    impact_text = (
        "CRISIS IMPACT\n"
        f"Crisis avg |corr|: {average_abs_corr:.2f}\n"
        f"Normal avg |corr|: {normal_average_abs_corr:.2f}\n"
        f"Change: {correlation_change:+.2f}\n"
        f"Impact: {impact_interpration}\n"
        f"Best diversifier: {best_diversifier} ({best_diversifier_corr:.2f})"
    )
    fig.text(0.83, 0.2, impact_text, fontsize=10, fontweight="bold", va="top", bbox=dict(boxstyle="round, pad=0.6", facecolor="#f2f2f2", edgecolor="#cccccc"))

    return fig     

def correlation_summary(correlation_matrix):
    mask = np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)

    pairs = correlation_matrix.where(mask).stack()

    average_corr = pairs.mean()
    average_abs_corr = pairs.abs().mean()
    strongest_pair = pairs.idxmax()
    weakest_pair = pairs.idxmin()
    strongest_value = pairs.max()
    weakest_value = pairs.min()

    return average_corr, average_abs_corr, strongest_pair, weakest_pair, strongest_value, weakest_value

crises = {
    "2008 Financial Crisis": ("2007-10-01", "2009-03-31"),
    "COVID-19 Crash": ("2020-02-01", "2020-04-30"),
    "2022 Market Stress": ("2021-12-01", "2022-10-31")
}

def diversification_ranking(correlation_matrix):
    equities = ["SPY", "QQQ", "IWM", "EFA", "EEM"]
    diversifiers = ["TLT", "IEF", "LQD", "HYG", "GLD", "USO", "VNQ"]
    scores= {}
    for asset in diversifiers:
        scores[asset] = correlation_matrix.loc[equities, asset].mean()
    ranking = pd.Series(scores).sort_values()
    return ranking  


def normal_market_correlation():
    normal_data = returns.copy()

    for start_date, end_date in crises.values():
        normal_data = normal_data[
            ~(
                (normal_data["Date"] >= start_date) &
                (normal_data["Date"] <= end_date)
            )
        ]
    normal_corr = normal_data[TICKERS].corr()   
    return normal_corr
  
 
def show_selected_crisis(selected_crisis):
    start_date, end_date = crises[selected_crisis]
    selected_corr = crisis_correlation(start_date, end_date)
    observation_count = returns["Date"].between(start_date, end_date).sum()
    ranking = diversification_ranking(selected_corr)
    best_diversifier = ranking.index[0]
    best_diversifier_corr = ranking.iloc[0]
    average_corr, average_abs_corr, strongest_pair, weakest_pair, strongest_value, weakest_value = correlation_summary(selected_corr)
    normal_corr = normal_market_correlation()
    normal_summary = correlation_summary(normal_corr)
    normal_average_abs_corr = normal_summary[1]
    correlation_change = average_abs_corr - normal_average_abs_corr
    fig = plot_heatmap(selected_corr, f"{selected_crisis} - {observation_count} trading days", average_abs_corr, normal_average_abs_corr, correlation_change, best_diversifier, best_diversifier_corr)
    return (
        fig,
        average_corr,
        average_abs_corr,
        strongest_pair,
        weakest_pair,
        strongest_value,
        weakest_value
    )

