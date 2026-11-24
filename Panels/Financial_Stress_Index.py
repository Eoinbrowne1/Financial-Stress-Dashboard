"""Financial Stress Index panel for the Financial Stress Dashboard.

Owner: Dara Quinn

Shows the St. Louis Fed Financial Stress Index (FRED series STLFSI4).
A value of 0 means normal stress in financial markets. Values above 0 mean more stress than normal, values below 0 mean less.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import gradio as gr

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

# --- Functions ---

def load_stress_index(path: str = DATA_FILE) -> pd.Series:
    """Load the weekly Financial Stress Index from a CSV file.

    Args:
        path (str): Location of the CSV file downloaded from FRED.

    Returns:
        pd.Series: Stress index values, with the dates as the index.
    """
    df = pd.read_csv(path)
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    df = df.set_index("observation_date")
    df = df.dropna()
    return df["STLFSI4"]

def calculate_sma(prices: list, k: int) -> list:
    """Calculate a k-period Simple Moving Average

    Args:
        prices (list): The values to average, oldest first.
        k (int) : How many values go into each average.
    
    Returns:
        list: The moving avergaes. This list is k - 1 items shorter than prices, because the first average needs k values.
    """

    sma_values = []
    for i in range(k - 1, len(prices)):
        window_sum = sum(prices[i - k + 1:i + 1])
        sma_values.append(window_sum / k)
    return sma_values

def smooth_stress_index(stress: pd.Series, weeks: int) -> pd.Series:
    """Smooth the stress index with a moving average.

    Args:
        stress (pd.Series): Weekly stress index values.
        weeks (int): Number of weeks to average. 1 means no smoothing.

    Returns:
        pd.Series: The smoothed values, with matching dates.
    """
    if weeks <= 1:
        return stress
    sma_values = calculate_sma(list(stress.values), weeks)
    # Each average belongs to the last date in its window
    return pd.Series(sma_values, index=stress.index[weeks - 1:])

def summarise_stress(stress: pd.Series) -> dict:
    """Work out the key numbers for the selected period.

    Args:
        stress (pd.Series): Stress index values for the period shown.

    Returns:
        dict: The latest value, the peak value, the date of the peak, and the percentage of weeks with above normal stress.
    """
    peak = stress.max()
    peak_date = stress[stress == peak].index[0]
    weeks_above_normal = len(stress[stress > 0])
    percent_above = weeks_above_normal / len(stress) * 100
    return {
        "latest": stress.iloc[-1],
        "peak": peak,
        "peak_date": peak_date,
        "percent_above": percent_above,
    }

def plot_stress_index(
    stress: pd.Series,
    start: str,
    end: str,
    crises_to_show: list = None,
    sma_weeks: int = 1,
) -> plt.Figure:
    """Draw the Financial Stress Index as a line chart.

    Args:
        stress (pd.Series): Weekly stress index values.
        start (str): First date to show, e.g. "2006-01-01".
        end (str): Last date to show, e.g. "2026-11-13".
        crises_to_show (list): Names of the crises to shade.
            None means shade all of them.
        sma_weeks (int): Weeks in the moving average. 1 means raw data.

    Returns:
        plt.Figure: The finished chart.
    """
    # Avoid the mutable default argument trap
    if crises_to_show is None:
        crises_to_show = list(CRISES.keys())

    smoothed = smooth_stress_index(stress, sma_weeks)
    visible = smoothed.loc[start:end]

    fig, ax = plt.subplots(figsize=(10, 4.5))

    # Stop here if the chosen dates contain no data
    if len(visible) == 0:
        ax.set_title("No data in this date range", loc="left")
        return fig

    ax.plot(visible.index, visible.values, color="#1f4e79", linewidth=1.5, label="Stress index")
    ax.axhline(0, color="grey", linestyle="--", linewidth=1, label="Normal stress (0)")

    for name, (crisis_start, crisis_end) in CRISES.items():
        if name in crises_to_show:
            ax.axvspan(pd.to_datetime(crisis_start), pd.to_datetime(crisis_end), color=CRISIS_COLOURS[name], alpha=0.15, label=name)

            # Label the highest point inside the crisis, if it is on screen
            crisis = visible.loc[crisis_start:crisis_end]
            if len(crisis) > 0:
                peak = crisis.max()
                peak_date = crisis[crisis == peak].index[0]
                ax.annotate(f"Peak {peak:.1f}\n{peak_date:%b %Y}",
                            xy=(peak_date, peak),
                            xytext=(15, -5),
                            textcoords="offset points",
                            fontsize=8,
                            arrowprops=dict(arrowstyle="-"))

    # Keep the x-axis to the dates the user chose
    ax.set_xlim(visible.index[0], visible.index[-1])

    # A title that tells the story of whatever period is on screen
    summary = summarise_stress(visible)
    ax.set_title(f"Stress peaked at {summary['peak']:.1f} in "
                 f"{summary['peak_date']:%B %Y}; "
                 f"{summary['percent_above']:.0f}% of weeks were above normal",
                 loc="left", fontweight="bold")
    ax.set_ylabel("Stress index (0 = normal)")
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.spines[["top", "right"]].set_visible(False)
    fig.autofmt_xdate()
    return fig


# --- Gradio controls ---

def update_stress_panel(
        start_year: int,
        end_year: int,
        crises: list,
        sma_weeks: int,
) -> tuple:
    """Redraw the chart and summary when the control changes.

    Args:
        start_year (int): Firsy year to show.
        end_year (int): Last year to show.
        crises (list): Names of the crises to shade.
        sma_weeks (int): Weeks in the moving average.

    Returns:
        tuple: The new chart (plt.Figure) and the summary text (str).
    """
    plt.close("all") # Free the memory used by old charts
    stress = load_stress_index()
    start = f"{int(start_year)}-01-01"
    end = f"{int(end_year)}-12-31"
    fig = plot_stress_index(stress, start, end, crises, int(sma_weeks))

    visible = stress.loc[start:end]
    if len(visible) == 0:
        return fig, "No data in this date range."

    summary = summarise_stress(visible)
    text = (
        f"**Latest reading:** {summary['latest']:.2f} | "
        f"**Peak in this period:** {summary['peak']:.1f} "
        f"({summary['peak_date']:%b %Y}) | "
        f"**Weeks above normal:** {summary['percent_above']:.0f}%"
    )
    return fig, text
                

# --- Quick test (only runs when this file is run directly) ---

if __name__ == "__main__":
    stress = load_stress_index()
    print(stress.head())
    print(stress.tail())
    print(summarise_stress(stress))
    fig = plot_stress_index(stress, "2006-01-01", "2026-12-31")
    Path("figures").mkdir(exist_ok=True)
    fig.savefig("figures/stress_index.png", dpi=200, bbox_inches="tight")
    plt.show()