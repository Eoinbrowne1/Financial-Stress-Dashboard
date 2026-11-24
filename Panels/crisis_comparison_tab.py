"""
Gradio tab for the Crisis Comparison panel (Sean O'Neill).

The calculations and charts all live in Crisis_Comparison.py. This file only
builds the controls and connects them to those functions, so the analysis does
not depend on which dashboard tool is used.
"""

import matplotlib
matplotlib.use("Agg")
import pandas as pd
import gradio as gr
from Panels.Crisis_Comparison import (load_prices, load_stress, compare_crises,
                                      plot_comparison, plot_bubbles, CRISES,
                                      ASSET_COLOURS)

CHART_TYPES = ["Compare one measure", "Overall severity (bubbles)"]
MEASURES = ["Max drawdown (%)", "Peak yearly volatility (%)", "Recovery (years)"]

EXPLANATION = (
    "**Max drawdown:** the worst % fall from a peak to a low during the period. "
    "**Peak yearly volatility:** how wildly prices swung at the most turbulent point, as a yearly figure. "
    "**Recovery:** years from the low until the price got back to its old peak (or years so far, if it hasn't). "
    "Oil is measured with the USO fund, which tracks oil futures and loses value over time, "
    "so it can make oil's recovery look slower than the oil price itself."
)

# Load the data once when the dashboard starts, not on every click
PRICES = load_prices()
STRESS = load_stress()
FIRST_DAY = PRICES.index.min() + pd.Timedelta(days=30)   
LAST_DAY = PRICES.index.max()

def check_custom_dates(start_text, end_text):
    """Check the user's custom dates. Returns (start, end, message):
    start and end are None if the dates can't be used."""
    try:
        start = pd.to_datetime(start_text, format="%Y-%m-%d")
        end = pd.to_datetime(end_text, format="%Y-%m-%d")
    except ValueError:
        return None, None, "Type the custom dates as YYYY-MM-DD, e.g. 2018-10-01."

    if start >= end:
        return None, None, "The custom start date must be before the end date."
    if start < FIRST_DAY or end > LAST_DAY:
        return None, None, (f"Custom dates must be between {FIRST_DAY.date()} "
                            f"and {LAST_DAY.date()}.")
    return str(start.date()), str(end.date()), ""

def stress_summary(table, chosen_crises):
    """The stress index peak for each chosen period, as a short Markdown table."""
    if STRESS is None:
        return "Stress index not available (no saved copy and no FRED key)."
    lines = ["**Financial Stress Index peak**: the highest weekly stress reading in each period "
             "(St. Louis Fed). 0 = normal, above 0 = more stress than normal.",
             "",
             "| Period | Stress index peak |",
             "|---|---|"]
    for name in chosen_crises:
        crisis_rows = table[table["Crisis"] == name]           # this period's rows
        peak = crisis_rows["Stress index peak"].iloc[0]
        lines.append(f"| {name} | {peak:.2f} |")
    return "\n".join(lines)