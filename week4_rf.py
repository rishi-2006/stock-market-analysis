import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, classification_report

symbol = "AAPL"
period = "2y"
df = yf.download(symbol, period=period, interval="1d", progress=False)

# --- features ---
df["Return"] = df["Close"].pct_change()
df["SMA_5"] = df["Close"].rolling(5).mean()
df["SMA_10"] = df["Close"].rolling(10).mean()
df["EMA_10"] = df["Close"].ewm(span=10, adjust=False).mean()
df["Vol_Change"] = df["Volume"].pct_change()

# target
df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)

features = ["Return","SMA_5","SMA_10","EMA_10","Vol_Change"]
data = df.dropna().copy()
X = data[features]
y = data["Target"]

split = int(len(X) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]

model = RandomForestClassifier(n_estimators=300, max_depth=5, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Accuracy :", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall   :", recall_score(y_test, y_pred))
print("\nConfusion matrix:\n", confusion_matrix(y_test, y_pred))
print("\nReport:\n", classification_report(y_test, y_pred, digits=4))
#pip install scikit-learn

#python week4_rf.py
