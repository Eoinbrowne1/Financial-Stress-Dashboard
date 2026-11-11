import yfinance as yf
import pandas as pd

tickers = ["SPY", "GLD", "TLT", "USO"]

series_list = []

for ticker in tickers:
    data = yf.download(
        ticker,
        start="2007-01-01",
        end="2026-11-11",
        auto_adjust=True,
        progress=False
    )

    close = data["Close"]

    # Handles yfinance returning either a Series or one-column DataFrame
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    close.name = ticker
    series_list.append(close)

prices = pd.concat(series_list, axis=1)

prices.index.name = "Date"

prices.to_csv("Data/market_data.csv")

print(prices.head())
print()
print("Missing values:")
print(prices.isna().sum())

print("\nMarket data saved successfully.")