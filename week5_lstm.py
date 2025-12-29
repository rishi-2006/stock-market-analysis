import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

# ✅ Use Keras 3 instead of tensorflow.keras
import keras
from keras import layers

# -----------------------------
# Download Stock Data
# -----------------------------
symbol = "AAPL"
period = "2y"
df = yf.download(symbol, period=period, interval="1d", progress=False)

close = df[["Close"]].dropna()

# -----------------------------
# Scale Data 0–1
# -----------------------------
scaler = MinMaxScaler()
scaled = scaler.fit_transform(close.values)

def make_sequences(arr, seq_len=60):
    X, y = [], []
    for i in range(len(arr) - seq_len):
        X.append(arr[i:i+seq_len])
        y.append(arr[i+seq_len])
    return np.array(X), np.array(y)

SEQ_LEN = 60
X, y = make_sequences(scaled, SEQ_LEN)

split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# -----------------------------
# Build LSTM Model
# -----------------------------
model = keras.Sequential([
    layers.LSTM(64, return_sequences=True, input_shape=(SEQ_LEN, 1)),
    layers.LSTM(32),
    layers.Dense(1)
])
model.compile(optimizer="adam", loss="mse")

history = model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=1)

# -----------------------------
# Predictions
# -----------------------------
pred = model.predict(X_test)
y_test_inv = scaler.inverse_transform(y_test)
pred_inv = scaler.inverse_transform(pred)

mae = mean_absolute_error(y_test_inv, pred_inv)
rmse = mean_squared_error(y_test_inv, pred_inv, squared=False)
print(f"MAE: {mae:.4f}, RMSE: {rmse:.4f}")

plt.plot(y_test_inv, label="Actual")
plt.plot(pred_inv, label="Predicted")
plt.title(f"{symbol} – LSTM Test Predictions")
plt.xlabel("Time Step")
plt.ylabel("Price")
plt.legend()
plt.tight_layout()
plt.show()
# for output this will help 
#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass # venv311\Scripts\activate  
# pip install tensorflow==2.15 keras==2.15 scikit-learn pandas matplotlib yfinance
#python week5_lstm.py
