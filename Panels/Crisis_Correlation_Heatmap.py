import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import gradio as gr
from pathlib import Path
from functools import lru_cache

# Load and prepare market data
BASE_DIR = Path(__file__).resolve().parents[1]
data = pd.read_csv(BASE_DIR / "Data" / "market_data_expanded.csv")
data["Date"] = pd.to_datetime(data["Date"])
data = data.sort_values("Date").reset_index(drop=True)
TICKERS = [ "SPY", "QQQ", "IWM", "EFA", "EEM","TLT", "IEF", "LQD", "HYG","GLD", "USO", "VNQ"]
EQUITY_TICKERS = ["SPY", "QQQ", "IWM", "EFA", "EEM"]
DIVERSIFIER_TICKERS = ["TLT", "IEF", "LQD", "HYG", "GLD", "USO", "VNQ"]
returns = np.log(data[TICKERS] / data[TICKERS].shift(1))
returns = returns.replace([np.inf, -np.inf], np.nan).dropna()
returns["Date"] = data.loc[returns.index, "Date"]

# Core correlation analysis
def crisis_correlation(start_date, end_date):
    """Calculate the correlation matrix for asset returns within a selected crisis period."""
    crisis_data = returns[
        (returns["Date"] >= start_date) &
        (returns["Date"] <= end_date)
    ]
    correlation_matrix = crisis_data[TICKERS].corr()
    return correlation_matrix

# Plotting functions
def plot_heatmap(correlation_matrix, title, average_abs_corr, normal_average_abs_corr, correlation_change, best_diversifier, best_diversifier_corr):
    """Create the main crisis correlation heatmap and supporting annotations."""
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
    if correlation_change > 0.01:
        impact_interpretation = "Cross-asset relationships strengthened"
    elif correlation_change < -0.01:
        impact_interpretation = "Cross-asset relationships weakened"
    else: 
        impact_interpretation = "Little change in cross-asset relationships"      
    impact_text = (
        "CRISIS IMPACT\n"
        f"Crisis avg |corr|: {average_abs_corr:.2f}\n"
        f"Normal avg |corr|: {normal_average_abs_corr:.2f}\n"
        f"Change: {correlation_change:+.2f}\n"
        f"Impact: {impact_interpretation}\n"
        f"Best diversifier: {best_diversifier} ({best_diversifier_corr:.2f})"
    )
    fig.text(0.83, 0.2, impact_text, fontsize=10, fontweight="bold", va="top", bbox=dict(boxstyle="round, pad=0.6", facecolor="#f2f2f2", edgecolor="#cccccc"))

    return fig     

# Correlation summary statistics
def correlation_summary(correlation_matrix):
    """Summarise pairwise correlations using average, absolute average, and extreme values."""
    mask = np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)

    pairs = correlation_matrix.where(mask).stack()

    average_corr = pairs.mean()
    average_abs_corr = pairs.abs().mean()
    strongest_pair = pairs.idxmax()
    weakest_pair = pairs.idxmin()
    strongest_value = pairs.max()
    weakest_value = pairs.min()

    return average_corr, average_abs_corr, strongest_pair, weakest_pair, strongest_value, weakest_value

# Crisis periods used throughout the dashboard
crises = {
    "2008 Financial Crisis": ("2007-10-01", "2009-03-31"),
    "COVID-19 Crash": ("2020-02-01", "2020-04-30"),
    "2022 Market Stress": ("2021-12-01", "2022-10-31")
}

# Diversification and normal-market benchmark analysis
def diversification_ranking(correlation_matrix):
    """Rank potential diversifiers by their average correlation with the selected equity group."""
    equities = EQUITY_TICKERS
    diversifiers = DIVERSIFIER_TICKERS
    scores = {}
    for asset in diversifiers:
        scores[asset] = correlation_matrix.loc[equities, asset].mean()
    ranking = pd.Series(scores).sort_values()
    return ranking  
@lru_cache(maxsize=1)
def normal_market_correlation():
    """Calculate the baseline correlation matrix after excluding the defined crisis periods."""
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

# Correlation change analysis
def correlation_change_matrix(crisis_matrix):
    """Compare crisis correlations with the normal-market baseline."""
    normal_matrix = normal_market_correlation()
    change_matrix = crisis_matrix - normal_matrix
    return change_matrix

def plot_change_heatmap(change_matrix, title):
    """Create a heatmap showing correlation changes relative to normal-market conditions."""
    fig, ax = plt.subplots(figsize=(13, 8))
    mask = np.tril(
        np.ones(change_matrix.shape, dtype=bool)
    )
    sns.heatmap(
        change_matrix,
        annot=True,
        cmap="RdBu",
        vmin=-2,
        vmax=2,
        center=0,
        ax=ax,
        mask=mask,
        fmt=".2f",
        annot_kws={"size":9},
        cbar_kws={"label": "Change in Correlation", "shrink": 0.85, "pad": 0.02}
    )
    ax.grid(False)
    ax.set_title(
        f"{title} - Change vs Normal Market",
        loc="left",
        fontweight ="bold",
        fontsize=14,
        pad=12
    )
    return fig

def show_selected_crisis(selected_crisis):
    """Run the selected crisis analysis and return the figure and summary statistics."""
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
        weakest_value,
        ranking
    )

# Gradio output and interface functions
def gradio_correlation_output(selected_crisis):
    """Format the crisis correlation figure and summary for Gradio output."""
    results = show_selected_crisis(selected_crisis)
    fig = results[0]
    average_corr = results[1]
    average_abs_corr = results[2]
    strongest_pair = results[3]
    weakest_pair = results[4]
    strongest_value = results[5]
    weakest_value = results[6]
    ranking=results[7]
    summary = (f"### Correlation Summary\n"
               f"**Average Correlation:** {average_corr:.2f} \n"
               f"**Average Absolute Correlation:** {average_abs_corr:.2f} \n"
               f"**Highest Positive Correlation:** {strongest_pair} ({strongest_value:.2f}) \n"
               f"**Most Negative Correlation:** {weakest_pair} ({weakest_value:.2f})"
    )
    summary += "\n\n### Diversification Ranking\n"
    summary += "Lower average correlation with equities suggests greater diversification potential.\n\n"
    summary += "| Rank | Asset | Average Correlation |\n"
    summary += "|---|---|---|\n"
    for position, (asset, score) in enumerate(ranking.items(), start=1):
        summary += f"| {position} | {asset} | {score:.2f} |\n"
    return fig, summary

def gradio_analysis_output(selected_crisis, analysis_view):
    """Return the selected correlation analysis view and matching Gradio summary."""
    if analysis_view == "Crisis Correlation":
        return gradio_correlation_output(selected_crisis)

    start_date, end_date = crises[selected_crisis]
    crisis_matrix = crisis_correlation(start_date, end_date)
    change_matrix = correlation_change_matrix(crisis_matrix)

    observation_count = returns["Date"].between(start_date, end_date).sum()

    fig = plot_change_heatmap(
        change_matrix,
        f"{selected_crisis} — {observation_count} trading days"
    )

    average_change, average_abs_change, highest_pair, lowest_pair, highest_value, lowest_value = correlation_summary(change_matrix)

    summary = (
        "### Change vs Normal Market\n"
        f"**Average Correlation Change:** {average_change:+.2f}\n\n"
        f"**Average Absolute Change:** {average_abs_change:.2f}\n\n"
        f"**Highest Correlation Change:** {highest_pair[0]} & {highest_pair[1]} ({highest_value:+.2f})\n\n"
        f"**Lowest Correlation Change:** {lowest_pair[0]} & {lowest_pair[1]} ({lowest_value:+.2f})\n\n"
        "Positive values indicate increased correlation during the crisis, while negative values indicate decreased correlation."
    )

    return fig, summary

def build_correlation_panel():
    """Build the interactive Gradio controls and outputs for the correlation panel."""
    gr.Markdown(
        "Explore correlations across 12 ETFs during major financial crises. "
        "The normal-market benchmark excludes all three defined crisis periods."
    )
    crisis_dropdown = gr.Dropdown(
        choices=list(crises.keys()),
        value="2008 Financial Crisis",
        label="Select crisis period"
    )
    analysis_view = gr.Radio(
                choices=["Crisis Correlation", "Change vs Normal Market"],
                value="Crisis Correlation",
                label="Analysis view"
            )
    initial_figure, initial_summary = gradio_correlation_output("2008 Financial Crisis")
    correlation_plot = gr.Plot(value=initial_figure)
    summary_output = gr.Markdown(value=initial_summary)
    crisis_dropdown.change(
        fn=gradio_analysis_output, 
        inputs=[crisis_dropdown, analysis_view],
        outputs=[correlation_plot, summary_output]
    )
    analysis_view.change(
        fn=gradio_analysis_output,
        inputs=[crisis_dropdown, analysis_view],
        outputs=[correlation_plot, summary_output]
    )