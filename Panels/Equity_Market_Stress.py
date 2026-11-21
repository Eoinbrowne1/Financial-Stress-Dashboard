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
def finperformance(x, y):
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
              metrics = (drawdownsp(target_date, crisis), drawdownnd(target_date, crisis), drawdownrus(target_date, crisis),
                         vixfear(target_date, crisis), realizedvol(target_date, crisis), finperformance(target_date, crisis))
       except Exception as exc:
             status_text.set_text(f"Input error:\n{exc}")
             status_text.set_color("#dc2626")
             fig.canvas.draw_idle()
             return
       
       t_date = spdata.index.asof(pd.Timestamp(target_date))
       state["Date"] = t_date.strftime("%Y-%M-%D")
#message if date had to be snapped to valid trading day 
       if pd.Timestamp(target_date) != t_date:
        status_text.set_text(f"Snapped {target_date} to valid\ntrading day: {state['date']}")
        status_text.set_color("#0369a1")
       else:
        status_text.set_text(f"Showing trading session:\n{state['date']}")
        status_text.set_color("#15803d")
#calculate regquired metrics 
        sp_dd, nd_dd, rus_dd, vix_regime, vix_spread, fin_perf = metrics
       sp_close = round(float(spdata.loc[t_date, "Close"]), 2)
       vix_date = vixdata.index.asof(t_date)
       vix_level = round(float(vixdata.loc[vix_date, "Close"]), 2)

       log_ret = np.log(spdata["Close"] / spdata["Close"].shift(1))
       rvol_series = log_ret.rolling(window=21).std() * np.sqrt(252) * 100
       vol_21d = round(float(rvol_series.loc[t_date]), 2)
#set the kpi metrics to update 
       kpi_lines = (
        f"REGIME: {crisis.upper()}   |   TRADING DATE: {state['Date']}\n"
        f"S&P 500: {sp_close:,.2f}  (Drawdown: -{sp_dd:.2f}%)   |   "
        f"XLF/SPX Rel. Perf: {fin_perf:+.2f}%\n"
        f"VIX Fear: {vix_level:.2f} [{vix_regime}]   |   "
        f"21D Realized Vol: {vol_21d:.2f}% (Spread: {vix_spread:+.2f})   |   "
        f"NDX DD: -{nd_dd:.2f}%  |  RUT DD: -{rus_dd:.2f}%")
        
       kpi_text.set_text(kpi_lines)
#setting the window to be displayed on the graphs 
       win_start = max(spdata.index.min(), t_date - state["Zoom Before"])
       win_end = min(spdata.index.max(), t_date + state["Zoom After"])

       sp_win = spdata.loc[win_start:win_end, "Close"].copy()
       vix_win = vixdata.loc[win_start:win_end, "Close"].copy()
       rvol_win = rvol_series.loc[win_start:win_end].copy()
#getting the peak for the window selected to calculate drawdowns 
       crisis_start = spdata.index.asof(pd.Timestamp(crisis_periods[crisis][0]))
       anchor_start = min(crisis_start, win_start)
       running_peak = spdata.loc[anchor_start:win_end, "Close"].cummax().loc[win_start:win_end]   
#sp 500 panel and drawdown shading
       ax_sp.clear()
       ax_sp.plot(sp_win.index, sp_win.values, color="#0f172a", linewidth=1.8, label="S&P 500 Close")  
       ax_sp.plot(running_peak.index, running_peak.values, color="#64748b", linestyle="--", linewidth=1.0, label="Regime Peak")
       ax_sp.fill_between(sp_win.index, sp_win.values, running_peak.values, where=(sp_win.values < running_peak.values),
        color="#ef4444", alpha=0.18, interpolate=True, label="Peak-to-Trough Drawdown")  
#line and dot to highlight selected date and drawdown
       ax_sp.axvline(t_date, color="#2563eb", linestyle="--", linewidth=1.6)
       ax_sp.scatter([t_date], [sp_close], color="#2563eb", zorder=5, s=45)
       ax_sp.annotate(f" {state['Date']}\n DD: -{sp_dd:.2f}%", xy=(t_date, sp_close), xytext=(8, -14), textcoords="offset points",
        fontsize=9, fontweight="bold", color="#1d4ed8", bbox=dict(boxstyle="round,pad=0.25", facecolor="#eff6ff", edgecolor="#93c5fd"))
 #Add label grid and legend      
       ax_sp.set_ylabel("S&P 500 Index", fontweight="bold", color="#1e293b")
       ax_sp.grid(True, linestyle=":", alpha=0.5)
       ax_sp.legend(loc="upper right", fontsize=8.5, framealpha=0.9)       
       plt.setp(ax_sp.get_xticklabels(), visible=False)
 #set up vix plot 
       ax_vix.clear()
       ax_vix.plot(vix_win.index, vix_win.values, color="#d97706", linewidth=1.8, label="CBOE VIX")
       ax_vix.plot(rvol_win.index, rvol_win.values, color="#475569", linestyle="-.", linewidth=1.2, label="21D Realized Vol (%)")      
 #shade between daily values and high stress value (30)
       ax_vix.axhline(30, color="#dc2626", linestyle=":", linewidth=1.5, label="VIX = 30 Stress Threshold")
       ax_vix.fill_between(vix_win.index, 30, vix_win.values, where=(vix_win.values >= 30), color="#dc2626", alpha=0.16, interpolate=True)
#add vertical line to highlight selected date
       ax_vix.axvline(t_date, color="#2563eb", linestyle="--", linewidth=1.6)
       ax_vix.scatter([t_date], [vix_level], color="#d97706", edgecolor="#1e293b", zorder=5, s=45)
       ax_vix.annotate(f" VIX: {vix_level:.2f}", xy=(t_date, vix_level), xytext=(8, 6), textcoords="offset points",
                        fontsize=9, fontweight="bold", color="#b45309", bbox=dict(boxstyle="round,pad=0.25", facecolor="#fffbeb", edgecolor="#fcd34d"))

    
             
             
             