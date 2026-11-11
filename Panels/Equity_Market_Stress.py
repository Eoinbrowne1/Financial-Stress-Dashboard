import yfinance as yf
import seaborn as sns
import fredapi as fpi
import matplotlib as plt
import numpy as np
import pandas as pd
tickers = yf.Tickers("^VIX ^GSPC XLF ^NDX ^RUT")

def csvfile(x):
     for x in tickers.tickers:
        df = yf.download(tickers.tickers[x], start="2007-01-01", end="2024-01-01")
        output_file = str(x) + "data.csv"
        df.to_csv(output_file)
        print(f"File saved as")