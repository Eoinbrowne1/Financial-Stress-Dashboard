"""Checks for the Crisis Comparison panel: made-up prices where the right answer is known."""
import pandas as pd
from Panels.Crisis_Comparison import running_peak, max_drawdown, peak_volatility, recovery_days


def check(description, got, expected):
    """Print PASS if the function gave the expected answer, otherwise FAIL."""
    if got == expected:
        print(f"PASS  {description}")
    else:
        print(f"FAIL  {description}: expected {expected}, got {got}")


dates = pd.date_range("2020-01-01", periods=8)

# Price falls from 100 to 50, then climbs back to 110
crash = pd.Series([100, 90, 70, 50, 60, 80, 100, 110], index=dates)

check("running peak only goes up",
      list(running_peak(crash)), [100, 100, 100, 100, 100, 100, 100, 110])

result = max_drawdown(crash, "2020-01-01", "2020-01-08")
check("drawdown is the % fall from 100 to 50", round(result["drawdown"], 2), -50)
check("peak is on day 1", result["peak_date"], dates[0])
check("bottom is on day 4", result["trough_date"], dates[3])

check("back to 100 three days after the bottom",
      recovery_days(crash, dates[0], dates[3]), (3, True))

# Price falls and never gets back to 100
never_back = pd.Series([100, 80, 60, 70, 75], index=dates[:5])
check("never recovers: reported, not a crash",
      recovery_days(never_back, dates[0], dates[2]), (2, False))

# Price never moves, so there's no volatility
flat = pd.Series([100.0] * 8, index=dates)
check("flat prices have zero volatility",
      peak_volatility(flat, "2020-01-01", "2020-01-08", window=3), 0)