import yfinance as yf
tickers = ["SPY" , "GLD" , "TLT" , "USO"]
data = yf.download(
    tickers,
    start = "2007-01-01",
    end = "2026-11-11" ,
    interval = "1d" ,
    auto_adjust = True,
    progress = False
)

prices = data["Close"]

prices.to_csv("Data/market_data.csv")

print(prices.head())
print("Market data saved successfully.")
