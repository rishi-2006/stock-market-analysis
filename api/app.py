# api/app.py
# Flask API for Stock Market Analyzer Dashboard
# Run: python app.py  → http://localhost:5000
#
# Endpoints:
#   GET /api/stock-data?ticker=AAPL&period=2y
#   GET /api/predict?ticker=AAPL
#   GET /api/compare?stocks=AAPL,MSFT,TSLA
#   GET /api/lstm?ticker=AAPL
#   GET /api/health

import os, json
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
import joblib

app = Flask(__name__)
CORS(app)  # Allow dashboard (file://) to call the API

MODEL_FILE = os.path.join(os.path.dirname(__file__), "..", "rf_week6.joblib")
FEATURES   = ["Return", "SMA_5", "SMA_10", "EMA_10", "Vol_Change"]

# ── Helper: add technical indicators ──────────────────────────────────
def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close = df["Close"]
    df["Return"]     = close.pct_change()
    df["SMA_5"]      = close.rolling(5).mean()
    df["SMA_10"]     = close.rolling(10).mean()
    df["SMA_20"]     = close.rolling(20).mean()
    df["EMA_10"]     = close.ewm(span=10, adjust=False).mean()
    df["Vol_Change"] = df["Volume"].pct_change()
    df.dropna(inplace=True)
    return df

# ── Helper: trend summary ──────────────────────────────────────────────
def trend_summary(df: pd.DataFrame, lookback: int = 20) -> dict:
    recent = df["Close"].tail(lookback)
    sma_s  = float(df["Close"].rolling(5).mean().iloc[-1])
    sma_l  = float(df["Close"].rolling(20).mean().iloc[-1])
    slope  = float(recent.pct_change().mean())

    if sma_s > sma_l:
        direction = "Bullish"
        badge = "success"
    elif sma_s < sma_l:
        direction = "Bearish"
        badge = "danger"
    else:
        direction = "Neutral"
        badge = "warning"

    return {
        "direction": direction,
        "badge": badge,
        "sma_short": round(sma_s, 2),
        "sma_long":  round(sma_l, 2),
        "slope":     round(slope, 6),
    }

# ── Helper: load or train RF model ────────────────────────────────────
def get_model(df: pd.DataFrame, force_retrain: bool = False):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score

    data = df.copy()
    data["Target"] = (data["Close"].shift(-1) > data["Close"]).astype(int)
    data.dropna(inplace=True)
    X = data[FEATURES]
    y = data["Target"]

    if os.path.exists(MODEL_FILE) and not force_retrain:
        model = joblib.load(MODEL_FILE)
        return model, None

    split = int(len(X) * 0.8)
    X_tr, X_te = X.iloc[:split], X.iloc[split:]
    y_tr, y_te = y.iloc[:split], y.iloc[split:]
    model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
    model.fit(X_tr, y_tr)
    acc = accuracy_score(y_te, model.predict(X_te))
    joblib.dump(model, MODEL_FILE)
    return model, round(acc, 4)


# ══════════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


@app.route("/api/stock-data")
def stock_data():
    """
    GET /api/stock-data?ticker=AAPL&period=2y
    Returns OHLCV + technical indicators as JSON.
    """
    ticker = request.args.get("ticker", "AAPL").upper()
    period = request.args.get("period", "2y")

    try:
        raw = yf.download(ticker, period=period, interval="1d",
                          progress=False, auto_adjust=False)
        if raw.empty:
            return jsonify({"error": f"No data for {ticker}"}), 404

        df = add_indicators(raw)

        # Last 252 rows for the chart (1 year)
        chart_df = df.tail(252).copy()

        # Flatten MultiIndex columns (yfinance sometimes returns them)
        if isinstance(chart_df.columns, pd.MultiIndex):
            chart_df.columns = ["_".join(c).strip() for c in chart_df.columns]

        # Build chart series
        dates  = chart_df.index.strftime("%Y-%m-%d").tolist()
        close  = [round(float(v), 2) for v in chart_df["Close"]]
        sma5   = [round(float(v), 2) if not pd.isna(v) else None for v in chart_df["SMA_5"]]
        sma20  = [round(float(v), 2) if not pd.isna(v) else None for v in chart_df["SMA_20"]]
        ema10  = [round(float(v), 2) if not pd.isna(v) else None for v in chart_df["EMA_10"]]
        volume = [int(v) for v in chart_df["Volume"]]

        # Latest stats
        last = df.iloc[-1]
        prev = df.iloc[-2]
        cur_price  = round(float(last["Close"]), 2)
        prev_price = round(float(prev["Close"]), 2)
        daily_chg  = round((cur_price - prev_price) / prev_price * 100, 2)
        daily_vol  = round(float(df["Return"].std()), 6)
        ann_vol    = round(daily_vol * (252 ** 0.5) * 100, 2)

        trend = trend_summary(df)

        # Support / resistance (simple rolling min/max over 20 days)
        support    = round(float(df["Close"].tail(20).min()), 2)
        resistance = round(float(df["Close"].tail(20).max()), 2)

        return jsonify({
            "ticker":     ticker,
            "period":     period,
            "company":    ticker + " Inc.",
            "price":      cur_price,
            "daily_change_pct": daily_chg,
            "volume_today":    int(last["Volume"]),
            "sma_5":     round(float(last["SMA_5"]), 2),
            "sma_10":    round(float(last["SMA_10"]), 2),
            "sma_20":    round(float(last["SMA_20"]), 2),
            "ema_10":    round(float(last["EMA_10"]), 2),
            "daily_vol":  daily_vol,
            "ann_vol_pct": ann_vol,
            "trend":      trend,
            "support":    support,
            "resistance": resistance,
            "chart": {
                "dates":  dates,
                "close":  close,
                "sma_5":  sma5,
                "sma_20": sma20,
                "ema_10": ema10,
                "volume": volume,
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/predict")
def predict():
    """
    GET /api/predict?ticker=AAPL&retrain=false
    Returns next-day prediction (UP/DOWN) + confidence + feature importance.
    """
    ticker   = request.args.get("ticker", "AAPL").upper()
    retrain  = request.args.get("retrain", "false").lower() == "true"

    try:
        from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix

        raw = yf.download(ticker, period="2y", interval="1d",
                          progress=False, auto_adjust=False)
        if raw.empty:
            return jsonify({"error": f"No data for {ticker}"}), 404

        df    = add_indicators(raw)
        model, acc = get_model(df, force_retrain=retrain)

        # Predict last row
        last_row = df.iloc[-1][FEATURES].values.reshape(1, -1)
        pred     = model.predict(last_row)[0]
        proba    = model.predict_proba(last_row)[0]
        conf     = round(float(max(proba)) * 100, 1)

        label    = "UP" if pred == 1 else "DOWN"

        # Feature importance
        fi = {f: round(float(imp), 4)
              for f, imp in zip(FEATURES, model.feature_importances_)}

        # Test-set metrics (time-ordered split for display)
        data = df.copy()
        data["Target"] = (data["Close"].shift(-1) > data["Close"]).astype(int)
        data.dropna(inplace=True)
        split = int(len(data) * 0.8)
        X_te  = data[FEATURES].iloc[split:]
        y_te  = data["Target"].iloc[split:]
        y_pred = model.predict(X_te)

        cm = confusion_matrix(y_te, y_pred).tolist()

        return jsonify({
            "ticker":     ticker,
            "prediction": label,
            "confidence": conf,
            "probabilities": {
                "DOWN": round(float(proba[0]) * 100, 1),
                "UP":   round(float(proba[1]) * 100, 1)
            },
            "feature_importance": fi,
            "model_metrics": {
                "accuracy":  round(float(accuracy_score(y_te, y_pred)), 4),
                "precision": round(float(precision_score(y_te, y_pred, zero_division=0)), 4),
                "recall":    round(float(recall_score(y_te, y_pred, zero_division=0)), 4),
                "confusion_matrix": cm
            },
            "model_file": MODEL_FILE if os.path.exists(MODEL_FILE) else "not saved",
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/compare")
def compare():
    """
    GET /api/compare?stocks=AAPL,MSFT,TSLA&period=1y
    Returns normalized price series (base=100) + metrics for multiple tickers.
    """
    stocks_raw = request.args.get("stocks", "AAPL,MSFT,TSLA")
    tickers    = [t.strip().upper() for t in stocks_raw.split(",") if t.strip()]
    period     = request.args.get("period", "1y")

    try:
        data = yf.download(tickers, period=period, interval="1d",
                           progress=False, auto_adjust=False)["Close"]

        if data.empty:
            return jsonify({"error": "No data returned"}), 404

        data.dropna(inplace=True)
        dates  = data.index.strftime("%Y-%m-%d").tolist()

        series = {}
        metrics = {}
        for t in tickers:
            if t not in data.columns:
                continue
            prices  = data[t]
            normed  = (prices / prices.iloc[0] * 100).round(2).tolist()
            rets    = prices.pct_change().dropna()
            series[t]  = normed
            metrics[t] = {
                "ytd_return":   round(float((prices.iloc[-1] / prices.iloc[0] - 1) * 100), 2),
                "volatility":   round(float(rets.std() * (252**0.5) * 100), 2),
                "avg_daily_vol": round(float(rets.mean() * 100), 4),
            }

        # Correlation matrix
        rets_df = data.pct_change().dropna()
        corr = rets_df.corr().round(3).to_dict()

        return jsonify({
            "tickers": tickers,
            "period":  period,
            "dates":   dates,
            "series":  series,
            "metrics": metrics,
            "correlation": corr,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/lstm")
def lstm_stub():
    """
    GET /api/lstm?ticker=AAPL
    Returns LSTM metrics (stub if Keras not installed, full if it is).
    """
    ticker = request.args.get("ticker", "AAPL").upper()

    # Try to load and run LSTM
    try:
        import keras
        from keras import layers
        from sklearn.preprocessing import MinMaxScaler
        from sklearn.metrics import mean_absolute_error, mean_squared_error

        raw   = yf.download(ticker, period="2y", interval="1d", progress=False)
        close = raw[["Close"]].dropna()

        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(close.values)

        SEQ_LEN = 60
        X, y = [], []
        for i in range(len(scaled) - SEQ_LEN):
            X.append(scaled[i:i+SEQ_LEN])
            y.append(scaled[i+SEQ_LEN])
        X, y = np.array(X), np.array(y)

        split = int(0.8 * len(X))
        X_tr, X_te = X[:split], X[split:]
        y_tr, y_te = y[:split], y[split:]

        model = keras.Sequential([
            layers.LSTM(64, return_sequences=True, input_shape=(SEQ_LEN, 1)),
            layers.LSTM(32),
            layers.Dense(1)
        ])
        model.compile(optimizer="adam", loss="mse")
        model.fit(X_tr, y_tr, epochs=5, batch_size=32, verbose=0)

        pred      = model.predict(X_te, verbose=0)
        y_te_inv  = scaler.inverse_transform(y_te)
        pred_inv  = scaler.inverse_transform(pred)

        mae  = round(float(mean_absolute_error(y_te_inv, pred_inv)), 4)
        rmse = round(float(np.sqrt(mean_squared_error(y_te_inv, pred_inv))), 4)

        dates_all = close.index.strftime("%Y-%m-%d").tolist()
        actual_vals = [round(float(v), 2) for v in y_te_inv.flatten()]
        pred_vals   = [round(float(v), 2) for v in pred_inv.flatten()]

        return jsonify({
            "ticker":  ticker,
            "model":   "LSTM (64 → 32 → Dense 1)",
            "mae":     mae,
            "rmse":    rmse,
            "seq_len": SEQ_LEN,
            "epochs":  5,
            "chart": {
                "actual":    actual_vals[-80:],
                "predicted": pred_vals[-80:],
            }
        })

    except ImportError:
        # Keras not installed – return stub data
        return jsonify({
            "ticker":  ticker,
            "model":   "LSTM (stub – Keras not installed)",
            "mae":     4.23,
            "rmse":    5.87,
            "seq_len": 60,
            "epochs":  10,
            "note":    "Install tensorflow/keras to get real predictions",
            "chart":   {"actual": [], "predicted": []}
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  StockAI Flask API  –  Starting on http://localhost:5000")
    print("  Dashboard: open dashboard/index.html in your browser")
    print("=" * 55)
    app.run(debug=True, port=5000)
