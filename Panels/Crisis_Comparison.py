import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
def load_prices():
    """Load daily prices from market_data.csv with the dates as the index."""
    prices = pd.read_csv("Data/market_data.csv", index_col="Date", parse_dates=True)
    return prices

prices = load_prices()
print(prices.head())