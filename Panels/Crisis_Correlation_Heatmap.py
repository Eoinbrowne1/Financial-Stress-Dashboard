import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load shared market data
data = pd.read_csv("Data/market_data.csv")

# Convert Date column to proper dates
data["Date"] = pd.to_datetime(data["Date"])

# Calculate daily percentage returns
returns = data[["SPY", "GLD", "TLT", "USO"]].pct_change()

# Calculate correlations between asset returns
correlation_matrix = returns.corr()

print(correlation_matrix)

# Create heatmap
sns.heatmap(
    correlation_matrix,
    annot=True,
    cmap="coolwarm",
    vmin=-1,
    vmax=1
)

plt.title("Asset Return Correlation Heatmap")
plt.tight_layout()
plt.show()