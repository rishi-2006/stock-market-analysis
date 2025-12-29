import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Pick multiple companies
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
data = yf.download(tickers, period="1y")["Close"]
data.head()
plt.figure(figsize=(12,6))
for ticker in tickers:
    plt.plot(data.index, data[ticker], label=ticker)

plt.title("Stock Closing Prices (1 Year)")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.show()
normed = data / data.iloc[0] * 100  # all start at 100

plt.figure(figsize=(12,6))
for ticker in tickers:
    plt.plot(normed.index, normed[ticker], label=ticker)

plt.title("Relative Performance (Base = 100)")
plt.xlabel("Date")
plt.ylabel("Normalized Price")
plt.legend()
plt.show()
corr = data.pct_change().corr()

plt.figure(figsize=(8,6))
sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
plt.title("Correlation of Daily Returns")
plt.show()
#pip install yfinance pandas matplotlib seaborn
#python week7_multi_compy.py