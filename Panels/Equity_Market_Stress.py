import yfinance as yf
import seaborn as sns
import fredapi as fpi
import matplotlib as plt
import numpy as np
import pandas as pd


#How the data was imported and coverted to csv files
vix = yf.Ticker("^VIX")
sp = yf.Ticker("^GSPC")
fsetf = yf.Ticker("XLF")
nasd = yf.Ticker("^NDX")
russ = yf.Ticker("^RUT")

dfvix = yf.download("^VIX", start = "2007-01-01", end = "2026-01-01")
outputfile1 = "vix.csv"
dfvix.to_csv(outputfile1)

dfsp = yf.download("^GSPC", start = "2007-01-01", end = "2026-01-01")
outputfile2 = "sp.csv"
dfsp.to_csv(outputfile2)

dffsetf = yf.download("XLF", start = "2007-01-01", end = "2026-01-01")
outputfile3 = "fsetf.csv"
dffsetf.to_csv(outputfile3)

dfnasd = yf.download("^NDX", start = "2007-01-01", end = "2026-01-01")
outputfile4 = "nasd.csv"
dfnasd.to_csv(outputfile4)

dfruss = yf.download("^RUT", start = "2007-01-01", end = "2026-01-01")
outputfile5 = "russ.csv"
dfruss.to_csv(outputfile5)

#List of tickers and their full name
tickers = {"^VIX":"CBOE Volatility Index", "^GSPC":"S&P 500 Index", "XLF":"Financial Sector ETF",
            "^NDX":"Nasdaq 100 Index", "^RUT":"Russell 2000 Index"}

#Crisis periods as agreed on
crisis_periods = {"2008 Financial Crisis":("2007-10-1", "2009-03-31"),
                  "COVID-19 Crash":("2020-02-01", "2020-04-30"),
                  "Market Sress":("2021-12-01", "2022-10-31")}
