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

def stat_card(label, value, detail, colour):
    """One headline card: a small label, a big number and a line of detail."""
    return (f'<div style="flex:1; min-width:180px; padding:16px 18px; border-radius:14px; '
            f'background:rgba(127,127,127,0.08); border-left:5px solid {colour};">'
            f'<div style="font-size:13px; opacity:0.75;">{label}</div>'
            f'<div style="font-size:30px; font-weight:700; margin:4px 0; color:{colour};">{value}</div>'
            f'<div style="font-size:13px; opacity:0.8;">{detail}</div></div>')


def headline_cards(table):
    """A row of headline cards worked out from the table, so they change with the controls."""
    hardest = table.sort_values("Max drawdown (%)").iloc[0]
    wildest = table.sort_values("Peak yearly volatility (%)", ascending=False).iloc[0]
    slowest = table.sort_values("Recovery (trading days)", ascending=False).iloc[0]

    if slowest["Recovered"] == "No":
        slow_detail = f"{slowest['Asset']}, {slowest['Crisis']} (not yet recovered)"
    else:
        slow_detail = f"{slowest['Asset']}, {slowest['Crisis']}"

    cards = [
        stat_card("Deepest fall", f"{hardest['Max drawdown (%)']:.1f}%",
                  f"{hardest['Asset']}, {hardest['Crisis']}", ASSET_COLOURS[hardest["Asset"]]),
        stat_card("Wildest swings", f"{wildest['Peak yearly volatility (%)']:.0f}%",
                  f"{wildest['Asset']}, {wildest['Crisis']}", ASSET_COLOURS[wildest["Asset"]]),
        stat_card("Slowest recovery", f"{slowest['Recovery (years)']:.1f} yrs",
                  slow_detail, ASSET_COLOURS[slowest["Asset"]]),
    ]

    if STRESS is not None:
        most_stress = table.sort_values("Stress index peak", ascending=False).iloc[0]
        cards.append(stat_card("Peak system stress", f"{most_stress['Stress index peak']:.1f}",
                               f"{most_stress['Crisis']} (0 = normal)", "#7f7f7f"))

    return '<div style="display:flex; gap:12px; flex-wrap:wrap;">' + "".join(cards) + "</div>"

def update_panel(chart_type, chosen_names, measure, window, add_custom, custom_start, custom_end):
    """Gradio calls this whenever a control changes.
    Returns the headline cards, the chart and the text below it."""
    # Build a smaller dictionary with only the chosen crises
    chosen_crises = {}
    for name in chosen_names:
        chosen_crises[name] = CRISES[name]

    message = ""
    if add_custom:
        start, end, message = check_custom_dates(custom_start, custom_end)
        if start is not None:
            chosen_crises["Custom period"] = (start, end)

    if len(chosen_crises) == 0:
        return "", None, "Pick at least one crisis."

    table = compare_crises(PRICES, STRESS, chosen_crises, int(window))

    if chart_type == "Compare one measure":
        fig = plot_comparison(table, measure)
    else:
        fig = plot_bubbles(table)

    text = EXPLANATION + "\n\n" + stress_summary(table, chosen_crises)
    if message != "":
        text = "**" + message + "**\n\n" + text
    return headline_cards(table), fig, text