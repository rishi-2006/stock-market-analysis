from collections import deque
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

symbol = "AAPL"
period = "2y"
df = yf.download(symbol, period=period, interval="1d", progress=False)

# --- deque for sliding window (size 5) ---
window = deque(maxlen=5)
for price in df["Close"].head(10):
    window.append(price)
    print("Current window:", list(window))

# --- dict mapping names to dataframes ---
companies = {
    "Apple": df,
    "Microsoft": yf.download("MSFT", period=period, interval="1d", progress=False)
}

# --- indicators ---
df["SMA_20"] = df["Close"].rolling(window=20).mean()
df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
df["Daily_Return"] = df["Close"].pct_change()
daily_vol = df["Daily_Return"].std()
annual_vol = daily_vol * (252 ** 0.5)
print(f"Daily vol: {daily_vol:.4f} | Annualized vol: {annual_vol:.4f}")

# --- plot close + MAs ---
ax = df[["Close","SMA_20","EMA_20"]].plot(title=f"{symbol} – Close, SMA20, EMA20")
ax.set_xlabel("Date"); ax.set_ylabel("Price")
plt.tight_layout(); plt.show()
#python week2_indicators.py
