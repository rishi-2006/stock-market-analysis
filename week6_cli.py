# week6_cli.py
import argparse, os
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
from datetime import datetime

MODEL_FILE = "rf_week6.joblib"

def fetch_data(ticker, period="2y"):
    try:
        df = yf.download(ticker, period=period, interval="1d", progress=False, auto_adjust=False)
        if df.empty:
            raise ValueError(f"No data for ticker {ticker}. Check symbol or network.")
        return df
    except Exception as e:
        print("⚠️ Error while fetching data:", e)
        raise

def add_indicators(df):
    df = df.copy()
    df["Return"] = df["Close"].pct_change()
    df["SMA_5"] = df["Close"].rolling(5).mean()
    df["SMA_10"] = df["Close"].rolling(10).mean()
    df["EMA_10"] = df["Close"].ewm(span=10, adjust=False).mean()
    df["Vol_Change"] = df["Volume"].pct_change()
    df.dropna(inplace=True)
    return df

def train_or_load_model(df, force_retrain=False):
    features = ["Return","SMA_5","SMA_10","EMA_10","Vol_Change"]
    data = df.copy()
    data["Target"] = (data["Close"].shift(-1) > data["Close"]).astype(int)
    data.dropna(inplace=True)
    X = data[features]
    y = data["Target"]

    if os.path.exists(MODEL_FILE) and not force_retrain:
        print("Loading existing model:", MODEL_FILE)
        model = joblib.load(MODEL_FILE)
        return model, None  # no metrics when loading
    print("Training a new RandomForest model (this may take a few seconds)...")
    split = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]
    model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    joblib.dump(model, MODEL_FILE)
    print(f"Model trained and saved to {MODEL_FILE} | Test Accuracy: {acc:.3f}")
    return model, acc
def summarize_trend(df, lookback=20):
    recent = df["Close"].tail(lookback)

    # force scalars
    sma_short = df["Close"].rolling(5).mean().iloc[-1].item()
    sma_long = df["Close"].rolling(20).mean().iloc[-1].item()

    # Fallback if dataset is too short
    if pd.isna(sma_short) or pd.isna(sma_long):
        return "Not enough data to compute SMA trend (need at least 20 rows)."

    slope = recent.pct_change().mean()

    if sma_short > sma_long:
        direction = "up"
    elif sma_short < sma_long:
        direction = "down"
    else:
        direction = "sideways"

    summary = (
        f"Recent (last {lookback} days) average return ≈ {slope:.4f}. "
        f"Short SMA(5) is {sma_short:.2f}, long SMA(20) is {sma_long:.2f} → trend: {direction}."
    )
    return summary


def plot_and_save(df, ticker, save=False):
    plt.figure(figsize=(10,5))
    plt.plot(df.index, df["Close"], label="Close")
    if "SMA_5" in df.columns: plt.plot(df.index, df["SMA_5"], label="SMA5")
    if "SMA_10" in df.columns: plt.plot(df.index, df["SMA_10"], label="SMA10")
    plt.title(f"{ticker} Close Price")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()
    if save:
        fname = f"{ticker}_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(fname)
        print("Chart saved to", fname)
    plt.show()

def make_report_text(ticker, trend_summary, prediction, model_acc=None, filename=None):
    lines = [
        f"Stock Analysis Report - {ticker}",
        f"Generated: {datetime.now()}",
        "",
        "1) Current Trend Summary:",
        trend_summary,
        "",
        "2) Predicted Movement (next trading day):",
        prediction,
        "",
    ]
    if model_acc is not None:
        lines += [f"Model test accuracy: {model_acc:.3f}", ""]
    content = "\n".join(lines)
    if filename:
        with open(filename, "w") as f:
            f.write(content)
        print("Report saved to", filename)
    return content

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", required=True, help="Stock ticker (e.g., AAPL)")
    parser.add_argument("--period", default="2y")
    parser.add_argument("--save", action="store_true", help="Save chart and text report")
    parser.add_argument("--retrain", action="store_true", help="Force retrain model")
    args = parser.parse_args()

    df = fetch_data(args.ticker, period=args.period)
    df = add_indicators(df)
    model, acc = train_or_load_model(df, force_retrain=args.retrain)

    # build input for last row
    last_row = df.iloc[-1]
    X_last = last_row[["Return","SMA_5","SMA_10","EMA_10","Vol_Change"]].values.reshape(1, -1)
    pred = model.predict(X_last)[0]
    pred_label = "UP" if pred == 1 else "DOWN"

    trend_summary = summarize_trend(df)
    print("\n=== Current Trend Summary ===")
    print(trend_summary)
    print("\n=== Predicted Movement (next trading day) ===")
    print(pred_label)

    if args.save:
        plot_and_save(df, args.ticker, save=True)
        report_file = f"{args.ticker}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        make_report_text(args.ticker, trend_summary, pred_label, acc, filename=report_file)

if __name__ == "__main__":
  main()