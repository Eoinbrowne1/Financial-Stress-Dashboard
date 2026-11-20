import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

data = pd.read_csv("Data/market_data.csv")
data["Date"] = pd.to_datetime(data["Date"])

returns = np.log(data[["GLD" , "SPY", "TLT", "USO"]] / data[["GLD" , "SPY", "TLT", "USO"]].shift(1))
returns = returns.dropna()
returns["Date"] = data.loc[returns.index, "Date"]

def crisis_correlation(start_date, end_date):
    crisis_data = returns[
        (returns["Date"] >= start_date) &
        (returns["Date"] <= end_date)
    ]
    correlation_matrix = crisis_data[["GLD" , "SPY", "TLT", "USO"]].corr()
    return correlation_matrix

corr_2008 = crisis_correlation("2007-10-01", "2009-03-31")
corr_covid = crisis_correlation("2020-02-01", "2020-04-30")
corr_2022 = crisis_correlation("2021-12-01", "2022-10-31")

def plot_heatmap(correlation_matrix, title):
    fig, ax = plt.subplots(figsize=(7,6))
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
        mask=mask
    )
               
    ax.set_title(title)
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

def show_selected_crisis(selected_crisis):
    start_date, end_date = crises[selected_crisis]
    selected_corr = crisis_correlation(start_date, end_date)
    average_corr, average_abs_corr, strongest_pair, weakest_pair, strongest_value, weakest_value = correlation_summary(selected_corr)
    fig = plot_heatmap(selected_corr, selected_crisis)
    return (
        fig,
        average_corr,
        average_abs_corr,
        strongest_pair,
        weakest_pair,
        strongest_value,
        weakest_value
    )

