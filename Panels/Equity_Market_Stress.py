import yfinance as yf
import seaborn as sns
import fredapi as fpi
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.widgets import Button, RadioButtons, TextBox

#List of tickers and their full name
tickers = {"^VIX":"CBOE Volatility Index", "^GSPC":"S&P 500 Index", "XLF":"Financial Sector ETF",
            "^NDX":"Nasdaq 100 Index", "^RUT":"Russell 2000 Index"}

#Crisis periods as agreed on
crisis_periods = {"2008 Financial Crisis":("2007-10-1", "2009-03-31"),
                  "COVID-19 Crash":("2020-02-01", "2020-04-30"),
                  "2022 Market Sress":("2021-12-01", "2022-10-31")}

#Default dates before any are selected
default_dates = {"2008 Financial Crisis":"2008-07-02",
                 "COVID-19 Crash":"2020-03-03",
                 "2022 Market Stress":"2022-05-09"}

#prepping data for use in date calling functions
vixdata = pd.read_csv("vix.csv", index_col= 0, parse_dates= True, skiprows=[1,2])
spdata = pd.read_csv("sp.csv", index_col= 0, parse_dates= True, skiprows=[1,2])
fsetfdata = pd.read_csv("fsetf.csv", index_col= 0, parse_dates= True, skiprows=[1,2])
nasddata = pd.read_csv("nasd.csv", index_col= 0, parse_dates= True, skiprows=[1,2])
russdata = pd.read_csv("russ.csv", index_col= 0, parse_dates= True, skiprows=[1,2])

#function for calculating drawdowns, x is date y is crisis z is data
def drawdown(x, y, z):
       if y in crisis_periods:
              if z.index.asof(pd.Timestamp(crisis_periods[y][0])) <= x <= z.index.asof(pd.Timestamp(crisis_periods[y][1])):
                     trading_date = z.index.asof(pd.Timestamp(x))
                     dates = z.loc[z.index.asof(pd.Timestamp(crisis_periods[y][0])):trading_date]
                     dateprice = z.loc[trading_date, "Close"].copy()
                     peak = dates["Close"].max()
                     drawdown = round((((dateprice - peak) / peak) * 100), 2)
                     return(drawdown)
              else:
                     raise ValueError(f"Please select a date between {crisis_periods[y][0]} and {crisis_periods[y][1]}")
       if y not in crisis_periods:
             raise ValueError(f"Unknown crisis regime: {y}") 

   
#x for date y for crisis
def drawdownsp(x, y):
       return(drawdown(x, y, spdata))
def drawdownnd(x, y):
       return(drawdown(x, y, nasddata))
def drawdownrus(x, y):
       return(drawdown(x, y, russdata))

def vixfear(x, y):
       if y in crisis_periods:
              if vixdata.index.asof(pd.Timestamp(crisis_periods[y][0])) <= x <= vixdata.index.asof(pd.Timestamp(crisis_periods[y][1])):
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
              else:
                     raise ValueError(f"Please select a date between {crisis_periods[y][0]} and {crisis_periods[y][1]}")
       if y not in crisis_periods:
             raise ValueError(f"Unknown crisis regime: {y}")

#21 day annualized realized volatility log returns
def realizedvol(x, y):
       if y in crisis_periods:
              if vixdata.index.asof(pd.Timestamp(crisis_periods[y][0])) <= x <= vixdata.index.asof(pd.Timestamp(crisis_periods[y][1])):
                     date = vixdata.index.asof(pd.Timestamp(x))
                     vix_level = float(vixdata.loc[date, "Close"])
                     log_ret = np.log(spdata["Close"] / spdata["Close"].shift(1))
                     realvolseries = log_ret.rolling(window = 21).std() * np.sqrt(252) * 100
                     vol_21d = round(float(realvolseries.loc[date]), 2)
                     vix_spread = round(vix_level - vol_21d, 2)
                     return(vix_spread)
              else:
                raise ValueError(f"Please select a date between {crisis_periods[y][0]} and {crisis_periods[y][1]}")
       if y not in crisis_periods:
              raise ValueError(f"Unknown crisis regime: {y}")      

#Banking/Financial Sector relative performance from crisis start to date 
def finperformce(x, y):
       if y in crisis_periods:
              if fsetfdata.index.asof(pd.Timestamp(crisis_periods[y][0])) <= x <= fsetfdata.index.asof(pd.Timestamp(crisis_periods[y][1])):
                     trading_date = fsetfdata.index.asof(pd.Timestamp(x))
                     startdate = fsetfdata.index.asof(pd.Timestamp(crisis_periods[y][0]))
                     startratio = fsetfdata.loc[startdate, "Close"] / spdata.loc[startdate, "Close"]
                     currentratio = fsetfdata.loc[trading_date, "Close"] / spdata.loc[trading_date, "Close"]
                     change_in_relperf_todate = round(((currentratio / startratio) - 1) * 100 , 2)
                     return(change_in_relperf_todate)
              else:
                raise ValueError(f"Please select a date between {crisis_periods[y][0]} and {crisis_periods[y][1]}")
       if y not in crisis_periods:
              raise ValueError(f"Unknown crisis regime: {y}") 


                     
#Initializing plots and prepping data selection
state = {"Crisis":"2008 Financial Crisis", 
         "Date":default_dates["2008 Financial Crisis"],
         "Zoom Before":pd.Timedelta(days=30),
         "Zoom After":pd.Timedelta(days=30)}

plt.rcParams["font.sans-serif"] = "Segoe UI"
fig = plt.figure(figsize = (14, 8.5), facecolor= "#f8fafc")
fig.canvas.manager.set_window_title("Financial Stress Dashboard")
gs = fig.add_gridspec(2, 1, left=0.25, right=0.96, top=0.77, bottom=0.09, hspace=0.16)
ax_sp = fig.add_subplot(gs[0])
ax_vix = fig.add_subplot(gs[1], sharex=ax_sp)

kpi_text = fig.text(0.25, 0.81, "", fontsize=10, family="Consolas", va="bottom", ha="left",
                    bbox=dict(boxstyle = "round,pad=0.65", facecolor = "#ffffff", edgecolor = "#cbd5e1", linewidth = 1.2,),)
status_text = fig.text(0.03, 0.28, "", fontsize=9, color="#475569", wrap=True)

#function for updating dashboard
def update(target_date: str, crisis: str):
       try:
              figures = (drawdownsp(target_date, crisis), drawdownnd(target_date, crisis), drawdownrus(target_date, crisis),
                         vixfear(target_date, crisis), realizedvol(target_date, crisis), finperformce(target_date, crisis))
       except Exception as exc:
             
             
             