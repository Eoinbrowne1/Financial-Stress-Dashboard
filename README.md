# Financial Stress Dashboard

An interactive Streamlit dashboard exploring how financial crises affect markets.
Four panels, one per team member, each answering a different question about the
2008 Financial Crisis, the COVID-19 crash and the 2022 market stress.

## How to run

1. Install the packages:
   pip install -r requirements.txt
2. From the main folder, start the dashboard:
   streamlit run shared_app.py
3. It opens in your browser at http://localhost:8501

No API key is needed: the FRED data is saved in the `Data` folder.
(Optional: to download fresh FRED data, set an environment variable `FRED_API_KEY`
and delete `Data/fred_STLFSI4.csv`.)

## Data

| Data | Source | File | Used by |
|---|---|---|---|
| Daily prices: SPY (US stocks), GLD (gold), TLT (US government bonds), USO (oil), from January 2007 | Yahoo Finance via yfinance (`download_data.py`) | `Data/market_data.csv` | Crisis Comparison |
| St. Louis Fed Financial Stress Index (STLFSI4, weekly, 0 = normal stress) | FRED API, downloaded once and saved by `load_stress()` | `Data/fred_STLFSI4.csv` | Crisis Comparison |
|csv` |

## Crisis periods (shared by all panels)

| Crisis | Start | End |
|---|---|---|
| 2008 Financial Crisis | 2007-10-01 | 2009-03-31 |
| COVID-19 Crash | 2020-02-01 | 2020-04-30 |
| 2022 Market Stress | 2021-12-01 | 2022-10-31 |

Each window starts just before the US stock market peak and ends just after its low.

## Panels

### 1. Equity Market Stress (Ruairi)
(Ruairi to fill in)

### 2. Crisis Comparison (Sean)
**Question:** Which financial crisis was most severe, and how did the crises differ?

For each asset in each crisis, the panel calculates from the raw daily prices:
- **Max drawdown**: the worst % fall from a peak
- **Peak yearly volatility**: the most turbulent point (rolling standard deviation of daily returns × √252)
- **Recovery time**: how long it took to get back to the old peak, or how long so far if it hasn't
- **Stress index peak**: the highest reading of the St. Louis Fed Financial Stress Index

No statistics are typed in manually, so adding a crisis to `CRISES` updates everything automatically.

**Controls**
- **Chart:** a bar chart comparing one measure, or a bubble chart showing all measures at once
- **Crises to include:** tick which crises to compare
- **Measure:** drawdown, volatility or recovery (bar chart only)
- **Volatility window:** 5 to 63 trading days (shown when volatility is on screen)

**Key findings**
- Oil fell about 80% in both 2008 and COVID, and has still not recovered from 2008.
- COVID falls were deep but short: most assets recovered within about a year.
- In 2022 the stress index barely rose above normal (0.63, against 9.68 in 2008),
  yet US government bonds fell 39% and have not recovered. Rising interest rates,
  not a system-wide panic.

**Checks:** `check_crisis_comparison.py` tests the functions on made-up prices
with known answers (run it with `python check_crisis_comparison.py`).

### 3. Crisis Correlation Heatmap (Eoin)
(Eoin to fill in)

### 4. Financial Stress Index (Dara)
(Dara to fill in)

## Use of AI tools

As permitted by the module lecturer, team members used AI assistants
(e.g. Claude, Copilot, Gemini, ChatGPT) to explain concepts, help find and fix errors,
and suggest code, which we then adapted, tested and checked against the data.
Each member's use of AI is described in their individual learning journal.

## Contributions

| Member | Panel | Files |
|---|---|---|
| Ruairi | Equity Market Stress | `Panels/Equity_Market_Stress.py` |
| Sean | Crisis Comparison | `Panels/Crisis_Comparison.py`, `check_crisis_comparison.py`
 `Data/fred_STLFSI4.csv` |
| Eoin | Crisis Correlation Heatmap | `Panels/Crisis_Correlation_Heatmap.py` |
| Dara | Financial Stress Index | `Panels/Financial_Stress_Index.py` |
| Shared | Dashboard app | `shared_app.py` (set up by Eoin) |