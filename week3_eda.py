import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf

symbol = "AAPL"
period = "2y"
df = yf.download(symbol, period=period, interval="1d", progress=False)
 
# --- simple support/resistance (min/max over entire period) ---
support = df["Close"].min().item()
resistance = df["Close"].max().item()
print(f"Support ~ {support:.2f}, Resistance ~ {resistance:.2f}")


# --- detect price spikes ---
df["Return"] = df["Close"].pct_change()
df["Ret_z"] = (df["Return"] - df["Return"].mean()) / df["Return"].std()
spikes = df[df["Ret_z"].abs() > 2]
print("Spike dates:\n", spikes.index.date[:10])

# --- trend ---
ax = df["Close"].plot(title=f"{symbol} Trend (Close + SMA50)")
df["Close"].rolling(50).mean().plot(ax=ax)
ax.set_xlabel("Date"); ax.set_ylabel("Price")
plt.tight_layout(); plt.show()

# --- volume bar chart ---
plt.bar(df.index, df["Volume"].to_numpy())
plt.title(f"{symbol} Trading Volume")
plt.xlabel("Date"); plt.ylabel("Volume")
plt.tight_layout(); plt.show()


# --- candlesticks ---
mpf.plot(df.tail(80), type="candle", volume=True, mav=(20,50), title=f"{symbol} – Candles (last 80)")

# --- correlation ---
peers = ["MSFT","GOOGL","TSLA"]
panel = {t: yf.download(t, period="1y", interval="1d", progress=False)["Close"].pct_change()
         for t in [symbol]+peers}
corr_df = pd.DataFrame(panel).corr()
print("\nReturn Correlations (1y):\n", corr_df)
#pip install mplfinance
#python week3_eda.py
