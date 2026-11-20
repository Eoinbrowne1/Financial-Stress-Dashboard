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
def drawdown1(x, y, z):
       if y in crisis_periods:
              if crisis_periods[y][0] <= x <= crisis_periods[y][1]:
                     trading_date = z.index.asof(pd.Timestamp(x))
                     dates = z.loc[crisis_periods[y][0]:trading_date]
                     dateprice = z.loc[trading_date, "Close"].copy()
                     peak = dates["Close"].max()
                     drawdown = round((((dateprice - peak) / peak) * 100), 2)

   
#x for date y for crisis
def drawdownsp(x, y):
       return(drawdown1(x, y, spdata))
def drawdownnd(x, y):
       return(drawdown1(x, y, nasddata))
def drawdownrus(x, y):
       return(drawdown1(x, y, russdata))

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