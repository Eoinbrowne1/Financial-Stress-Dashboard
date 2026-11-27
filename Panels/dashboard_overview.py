import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import gradio as gr
from pathlib import Path

from Panels.Crisis_Correlation_Heatmap import (
    data, crises, crisis_correlation
)

BASE_DIR = Path(__file__).resolve().parents[1]


def plot_overview():

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))

    start, end = crises["2008 Financial Crisis"]
    crisis_data = data[data["Date"].between(start, end)]

    # 1. Equity Market Stress
    prices = crisis_data.set_index("Date")["SPY"]
    drawdown = (prices / prices.cummax() - 1) * 100

    axes[0, 0].plot(drawdown, color="#dc2626")
    axes[0, 0].fill_between(
        drawdown.index, drawdown, 0,
        color="#dc2626", alpha=0.15
    )
    axes[0, 0].set_title(
        "Equity Market Stress - 2008",
        fontweight="bold"
    )
    axes[0, 0].set_ylabel("SPY Drawdown (%)")

    # 2. Crisis Correlation
    corr = crisis_correlation(start, end)

    sns.heatmap(
        corr,
        mask=np.tril(np.ones(corr.shape, dtype=bool)),
        cmap="RdBu",
        vmin=-1,
        vmax=1,
        center=0,
        ax=axes[0, 1],
        cbar_kws={"label": "Correlation"}
    )
    axes[0, 1].set_title(
        "Crisis Correlation - 2008",
        fontweight="bold"
    )

    # 3. Crisis Comparison
    drawdowns = []

    for start_date, end_date in crises.values():
        prices = data.loc[
            data["Date"].between(start_date, end_date),
            "SPY"
        ]
        maximum_drawdown = (
            prices / prices.cummax() - 1
        ).min() * 100

        drawdowns.append(maximum_drawdown)

    bars = axes[1, 0].bar(
        ["2008", "COVID-19", "2022"],
        drawdowns,
        color=["#6366f1", "#0ea5e9", "#14b8a6"]
    )

    axes[1, 0].bar_label(bars, fmt="%.1f%%")
    axes[1, 0].set_title(
        "Crisis Comparison",
        fontweight="bold"
    )
    axes[1, 0].set_ylabel("SPY Maximum Drawdown (%)")

    # 4. Financial Stress Index
    stress = pd.read_csv(
        BASE_DIR / "Data" / "fred_STLFSI4.csv"
    )

    stress.columns = stress.columns.str.strip().str.lower()

    date_col = next(
        col for col in stress.columns if "date" in col
    )

    value_col = next(
        col for col in stress.columns
        if col in ["stlfsi4", "value"]
    )

    stress[date_col] = pd.to_datetime(stress[date_col])
    stress[value_col] = pd.to_numeric(
        stress[value_col], errors="coerce"
    )
    stress = stress.sort_values(date_col)

    axes[1, 1].plot(
        stress[date_col],
        stress[value_col],
        color="#6366f1",
        linewidth=1.3
    )

    for start_date, end_date in crises.values():
        axes[1, 1].axvspan(
            pd.Timestamp(start_date),
            pd.Timestamp(end_date),
            color="red",
            alpha=0.12
        )

    axes[1, 1].axhline(
        0, color="grey", linestyle="--"
    )

    axes[1, 1].set_title(
        "Financial Stress Index",
        fontweight="bold"
    )
    axes[1, 1].set_ylabel("STLFSI4")

    for ax in axes.flat:
        ax.tick_params(axis="both", labelsize=9)

    fig.tight_layout(pad=3)
    plt.close(fig)

    return fig


def build_overview():
    gr.Markdown("## Dashboard Overview")

    gr.Markdown(
        "Explore three major financial crises through four "
        "complementary perspectives. Select the individual "
        "tabs above for detailed interactive analysis."
    )

    gr.Plot(value=plot_overview(), show_label=False)