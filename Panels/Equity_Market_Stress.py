import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.widgets import Button, RadioButtons, TextBox
from pathlib import Path

#List of tickers and their full name
tickers = {"^VIX":"CBOE Volatility Index", "^GSPC":"S&P 500 Index", "XLF":"Financial Sector ETF",
            "^NDX":"Nasdaq 100 Index", "^RUT":"Russell 2000 Index"}

#Crisis periods as agreed on
crisis_periods = {"2008 Financial Crisis":("2007-10-1", "2009-03-31"),
                  "COVID-19 Crash":("2020-02-01", "2020-04-30"),
                  "2022 Market Stress":("2021-12-01", "2022-10-31")}

#Default dates before any are selected
default_dates = {"2008 Financial Crisis":"2008-07-02",
                 "COVID-19 Crash":"2020-03-03",
                 "2022 Market Stress":"2022-05-09"}
#axis limits for drawdown bar chart
dd_axis_limits = {"2008 Financial Crisis": -90,
                  "COVID-19 Crash": -50,
                  "2022 Market Stress": -45}
# Key events for each crisis
crisis_events = {
    "2008 Financial Crisis": {"2007-10-09": "S&P pre-crisis peak",
                              "2008-03-16": "Bear Stearns rescued",
                              "2008-09-15": "Lehman collapses",
                              "2008-09-29": "Congress rejects TARP",
                              "2008-10-03": "TARP signed",
                              "2008-11-25": "Fed launches QE1",
                              "2009-03-09": "Market bottom"},
    "COVID-19 Crash": {"2020-02-19": "S&P pre-COVID peak",
                       "2020-03-03": "Fed emergency cut",
                       "2020-03-09": "1st circuit breaker",
                       "2020-03-11": "WHO declares pandemic",
                       "2020-03-16": "Fed cuts to zero",
                       "2020-03-23": "Market bottom / unlimited QE",
                       "2020-03-27": "CARES Act signed"},
    "2022 Market Stress": {"2022-01-03": "S&P record high",
                           "2022-02-24": "Russia invades Ukraine",
                           "2022-03-16": "Fed's first hike",
                           "2022-06-15": "Fed hikes 75bp",
                           "2022-08-26": "Powell Jackson Hole",
                           "2022-09-13": "Hot CPI print",
                           "2022-10-12": "Market bottom"},}

DATA_DIR = Path(__file__).parent.parent / "data"

def load_prices(filename: str) -> pd.DataFrame:
    try:
        data = pd.read_csv(DATA_DIR / filename, index_col=0, parse_dates=True, skiprows=[1, 2])
    except FileNotFoundError:
        raise SystemExit(f"Data file not found: {DATA_DIR / filename}\n"
                         f"Make sure {filename} is in the same folder as this script.")
    return data[~data.index.duplicated(keep="last")].sort_index()

vixdata = load_prices("vix.csv")
spdata = load_prices("sp.csv")
fsetfdata = load_prices("fsetf.csv")
nasddata = load_prices("nasd.csv")
russdata = load_prices("russ.csv")
  
#function for calculating drawdowns, x is date y is crisis z is data
def drawdown(x, y, z):
       if y in crisis_periods:
              if z.index.asof(pd.Timestamp(crisis_periods[y][0])) <= pd.Timestamp(x) <= z.index.asof(pd.Timestamp(crisis_periods[y][1])):
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
              if vixdata.index.asof(pd.Timestamp(crisis_periods[y][0])) <= pd.Timestamp(x) <= vixdata.index.asof(pd.Timestamp(crisis_periods[y][1])):
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
              if vixdata.index.asof(pd.Timestamp(crisis_periods[y][0])) <= pd.Timestamp(x) <= vixdata.index.asof(pd.Timestamp(crisis_periods[y][1])):
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
              if fsetfdata.index.asof(pd.Timestamp(crisis_periods[y][0])) <= pd.Timestamp(x) <= fsetfdata.index.asof(pd.Timestamp(crisis_periods[y][1])):
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
         "Zoom After":pd.Timedelta(days=30), 
         "Syncing":False}

plt.rcParams["font.sans-serif"] = "Segoe UI"
fig = plt.figure(figsize = (14, 8.5), facecolor= "#f8fafc")
fig.canvas.manager.set_window_title("Financial Stress Dashboard")
gs = fig.add_gridspec(2, 2, width_ratios=[3,1], left=0.07, right=0.97, top=0.76, bottom=0.09, hspace=0.35, wspace=0.2)
ax_sp = fig.add_subplot(gs[0,0])
ax_vix = fig.add_subplot(gs[1,0], sharex=ax_sp)
ax_dd = fig.add_subplot(gs[:, 1])
status_text = fig.text(0.43, 0.87, "", fontsize=9, color="#475569", wrap=True)

#function for updating dashboard
def update(target_date: str, crisis: str):
       try:
            metrics = (drawdownsp(target_date, crisis), drawdownnd(target_date, crisis), drawdownrus(target_date, crisis),
                         vixfear(target_date, crisis), realizedvol(target_date, crisis), finperformance(target_date, crisis),
                         drawdown(target_date, crisis, fsetfdata))
            t_date = spdata.index.asof(pd.Timestamp(target_date))
            state["Date"] = t_date.strftime("%Y-%m-%d")
            state["Syncing"] = True
            text_date.set_val(state["Date"])
            state["Syncing"] = False
            
            #message if date had to be snapped to valid trading day 
            if pd.Timestamp(target_date) != t_date:
                    status_text.set_text(f"Snapped {target_date} to valid\ntrading day: {state['Date']}")
                    status_text.set_color("#0369a1")
            else:
                    status_text.set_text(f"Showing trading session:\n{state['Date']}")
                    status_text.set_color("#15803d")
            #calculate required metrics 
                    sp_dd, nd_dd, rus_dd, vix_regime, vix_spread, fin_perf, xlf_dd = metrics
            sp_close = round(float(spdata.loc[t_date, "Close"]), 2)
            vix_date = vixdata.index.asof(t_date)
            vix_level = round(float(vixdata.loc[vix_date, "Close"]), 2)
            
            log_ret = np.log(spdata["Close"] / spdata["Close"].shift(1))
            rvol_series = log_ret.rolling(window=21).std() * np.sqrt(252) * 100
            vol_21d = round(float(rvol_series.loc[t_date]), 2)
           
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
            ax_sp.annotate(f" {state['Date']}\n S&P: {sp_close:,.2f}\n DD: {sp_dd:.2f}%",
               xy=(t_date, sp_close), xytext=(8, -14), textcoords="offset points", fontsize=9, 
               fontweight="bold", color="#1d4ed8", bbox=dict(boxstyle="round,pad=0.25", facecolor="#eff6ff", edgecolor="#93c5fd"))
            ax_sp.set_title(f"{crisis.upper()}  |  S&P 500 on {state['Date']}",
                fontsize=11, fontweight="bold", color="#1e293b", loc="left")
            ax_sp.text(0.01, 0.95, f"Financials (XLF) vs S&P since crisis start: {fin_perf:+.2f}%",
                transform=ax_sp.transAxes, va="top", fontsize=8.5, color="#1e293b",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#ffffff", edgecolor="#cbd5e1"))
            ax_sp.set_ylabel("S&P 500 Index", fontweight="bold", color="#1e293b")
            ax_sp.grid(True, linestyle=":", alpha=0.5)
            ax_sp.legend(loc="upper right", fontsize=8.5, framealpha=0.9)       
            plt.setp(ax_sp.get_xticklabels(), rotation=25, ha="right")
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
            if vol_21d > vix_level:
                vix_offset, vix_va = (8, -6), "top"      
                rv_offset, rv_va = (8, 6), "bottom"      
            else:
                vix_offset, vix_va = (8, 6), "bottom"
                rv_offset, rv_va = (8, -6), "top"
            ax_vix.annotate(f" VIX: {vix_level:.2f}\n {vix_regime}", xy=(t_date, vix_level),
                xytext=vix_offset, va=vix_va, textcoords="offset points",
                fontsize=9, fontweight="bold", color="#b45309",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#fffbeb", edgecolor="#fcd34d"))
            ax_vix.scatter([t_date], [vol_21d], color="#475569", zorder=5, s=35)
            ax_vix.annotate(f" 21D RV: {vol_21d:.2f}%\n Spread: {vix_spread:+.2f}", xy=(t_date, vol_21d),
                xytext=rv_offset, va=rv_va, textcoords="offset points",
                fontsize=9, fontweight="bold", color="#334155",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#f8fafc", edgecolor="#cbd5e1"))
            #add grid labels legend and date formatting
            ax_vix.set_ylabel("Volatility (%)", fontweight="bold", color="#1e293b")
            ax_vix.set_xlabel("Date", fontweight="bold", color="#1e293b")
            ax_vix.grid(True, linestyle=":", alpha=0.5)
            ax_vix.legend(loc="upper right", fontsize=8.5, framealpha=0.9)
            ax_vix.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            plt.setp(ax_vix.get_xticklabels(), rotation=25, ha="right")

            # Event markers: only draw events that fall inside the visible window
            for event_date, event_name in crisis_events[crisis].items():
                e_date = spdata.loc[event_date:].index[0]   # first trading day on/after the event
                if win_start <= e_date <= win_end:
                    ax_sp.axvline(e_date, color="#7c3aed", linestyle=":", linewidth=1.2)
                    ax_vix.axvline(e_date, color="#7c3aed", linestyle=":", linewidth=1.2)
                    ax_sp.text(e_date, 0.04, f" {event_name}", transform=ax_sp.get_xaxis_transform(),
                               rotation=90, ha="right", va="bottom", fontsize=8, color="#5b21b6",
                               bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff",
                               edgecolor="none", alpha=0.8))

            #bar chart comparing drawdowns across markets
            dd_values = {"S&P 500": sp_dd, "Nasdaq 100": nd_dd, "Russell 2000": rus_dd, "Financials (XLF)": xlf_dd}
            names = list(dd_values.keys())
            values = list(dd_values.values())
            worst = min(values)
            colours = ["#dc2626" if v == worst else "#94a3b8" for v in values]

            ax_dd.clear()
            ax_dd.barh(names, values, color=colours)
            for name, value in dd_values.items():
                if value <= -20:      # long bar: white label inside the bar
                    ax_dd.text(value, name, f" {value:.1f}%", va="center", ha="left",
                    fontsize=8.5, fontweight="bold", color="#ffffff")
                else:                 # short bar: dark label just outside the bar
                    ax_dd.text(value, name, f"{value:.1f}% ", va="center", ha="right",
                    fontsize=8.5, fontweight="bold", color="#1e293b")
            ax_dd.axvline(0, color="#1e293b", linewidth=0.8)
            ax_dd.set_xlim(dd_axis_limits[crisis], 0)
            ax_dd.invert_yaxis()                     # S&P 500 at the top
            ax_dd.set_title("Drawdown from Crisis Peak (%)", fontsize=10,
                fontweight="bold", color="#1e293b")
            ax_dd.grid(True, axis="x", linestyle=":", alpha=0.5)
            fig.canvas.draw()       

       except Exception as exc:
             status_text.set_text(f"Input error:\n{exc}")
             status_text.set_color("#dc2626")
             fig.canvas.draw_idle()
             return            

# function for interactive controls to update plotting function
def on_crisis_change(label: str):
    state["Crisis"] = label
    update(default_dates[label], label)
#functions for changing date
def on_date_submit(text: str):
    if state["Syncing"]:
          return
    cleaned = text.strip()
    if cleaned:
          update(cleaned, state["Crisis"])

def step_days(delta_days: int):
    start, end = crisis_periods[state["Crisis"]]
    trading_days = list(spdata.loc[start:end].index)
    current = spdata.index.asof(pd.Timestamp(state["Date"]))
    pos = trading_days.index(current)
    new_pos = max(0, min(pos + delta_days, len(trading_days) - 1))
    new_dt = trading_days[new_pos].strftime("%Y-%m-%d")

    update(new_dt, state["Crisis"])
#button to select crisis period
fig.text(0.03, 0.955, "1. Select Crisis Regime", fontweight="bold", fontsize=10.5, color="#1e293b")
ax_radio = fig.add_axes([0.03, 0.81, 0.16, 0.13], facecolor="#ffffff")
radio_crisis = RadioButtons(ax_radio, list(crisis_periods.keys()), active=0)
radio_crisis.on_clicked(on_crisis_change)    
#button for selecting date
fig.text(0.22, 0.955, "2. Inspect Date (YYYY-MM-DD)", fontweight="bold", fontsize=10.5, color="#1e293b")
ax_textbox = fig.add_axes([0.22, 0.89, 0.18, 0.045])
text_date = TextBox(ax_textbox, "", initial=state["Date"])
text_date.on_submit(on_date_submit)

ax_prev = fig.add_axes([0.22, 0.825, 0.085, 0.045])
ax_next = fig.add_axes([0.315, 0.825, 0.085, 0.045])
btn_prev = Button(ax_prev, "-5 Trading Days", color="#e2e8f0", hovercolor="#cbd5e1")
btn_next = Button(ax_next, "+5 Trading Days", color="#e2e8f0", hovercolor="#cbd5e1")
btn_prev.on_clicked(lambda _: step_days(-5))
btn_next.on_clicked(lambda _: step_days(5))

# Draw initial view and launch dashboard window
update(state["Date"], state["Crisis"])
plt.show()