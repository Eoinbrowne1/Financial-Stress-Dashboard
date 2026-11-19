import yfinance as yf
import seaborn as sns
import fredapi as fpi
import matplotlib as plt
import numpy as np
import pandas as pd




#List of tickers and their full name
tickers = {"^VIX":"CBOE Volatility Index", "^GSPC":"S&P 500 Index", "XLF":"Financial Sector ETF",
            "^NDX":"Nasdaq 100 Index", "^RUT":"Russell 2000 Index"}

#Crisis periods as agreed on
crisis_periods = {"2008 Financial Crisis":("2007-10-1", "2009-03-31"),
                  "COVID-19 Crash":("2020-02-01", "2020-04-30"),
                  "2022 Market Sress":("2021-12-01", "2022-10-31")}

#prepping data for use in date calling functions
vixdata = pd.read_csv("vix.csv", index_col= 0, parse_dates= True, skiprows=[1,2])
spdata = pd.read_csv("sp.csv", index_col= 0, parse_dates= True, skiprows=[1,2])
fsetfdata = pd.read_csv("fsetf.csv", index_col= 0, parse_dates= True, skiprows=[1,2])
nasddata = pd.read_csv("nasd.csv", index_col= 0, parse_dates= True, skiprows=[1,2])
russdata = pd.read_csv("russ.csv", index_col= 0, parse_dates= True, skiprows=[1,2])

#function for calculating drawdowns
def drawdown(x, y, z):
    if y == "2008 Financial Crisis" and x in z.loc["2007-10-01":"2009-03-31"].index:
            dates1 = z.loc["2007-10-01":x].copy()
            peak1 = dates1["Close"].max()
            dateprice1 = z.loc[x, "Close"]
            drawdown1 = round((((dateprice1 - peak1) / peak1) * 100), 2)
            return(drawdown1)
    elif y == "COVID-19 Crash" and x in z.loc["2020-02-01":"2020-04-30"].index:
            dates2 = z.loc["2020-02-01":x].copy()
            peak2 = dates2["Close"].max()
            dateprice2 = z.loc[x, "Close"]
            drawdown2 = round((((dateprice2 - peak2) / peak2) * 100), 2)
            return(drawdown2)
    elif y == "2022 Market Stress" and x in z.loc["2021-12-01":"2022-10-31"].index:
            dates3 = z.loc["2021-12-01":x].copy()
            peak3 = dates3["Close"].max()
            dateprice3 = z.loc[x, "Close"]
            drawdown3 = round((((dateprice3 - peak3) / peak3) * 100), 2)
            return(drawdown3)
    elif y in crisis_periods: 
            trading_date = z.index.asof(pd.Timestamp(x))
            dates4 = z.loc[crisis_periods[y][0]:trading_date]
            dateprice4 = z.loc[trading_date, "Close"].copy()
            peak4 = dates4["Close"].max()
            drawdown4 = round((((dateprice4 - peak4) / peak4) * 100), 2)
            return(drawdown4)
    
#x for date y for crisis
def drawdownsp(x, y):
       return(drawdown(x, y, spdata))
def drawdownnd(x, y):
       return(drawdown(x, y, nasddata))
def drawdownrus(x, y):
       return(drawdown(x, y, russdata))

def vixfear(x, y):
       if y in crisis_periods:
              if x >= crisis_periods[y][0] and x<= crisis_periods[y][1]:
                date = vixdata.index.asof(pd.Timestamp(x))             
                vix_level = round(float(vixdata.loc[date, "Close"]), 2)
                if vix_level >= 40:
                       return("EXTREME PANIC (>=40)")
                if 30 <= vix_level < 40:
                       return("HIGH STRESS (30-40)")
                if 20 <= vix_level < 30:
                       return("ELEVATED (20-30)")
                if vix_level < 20:
                       return("CALM (<20)")

well = vixfear("2008-02-07", "2008 Financial Crisis")              
print(well)