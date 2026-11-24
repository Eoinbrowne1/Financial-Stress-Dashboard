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