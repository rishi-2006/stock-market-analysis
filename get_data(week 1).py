import argparse
import sys
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("symbol", nargs="?", default="AAPL", help="Stock ticker, e.g., AAPL")
    parser.add_argument("--period", default="2y", help="e.g., 1y, 2y, 6mo")
    args = parser.parse_args()

    print(f"Downloading {args.symbol} for {args.period} ...")
    df = yf.download(args.symbol, period=args.period, interval="1d", progress=False)
    if df.empty:
        print("No data received. Check ticker or network.")
        sys.exit(1)

    csv_name = f"data_{args.symbol}_{args.period}.csv"
    df.to_csv(csv_name)
    print(f"Saved CSV: {csv_name}")

    ax = df["Close"].plot(title=f"{args.symbol} Close ({args.period})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
#pip install yfinance pandas matplotlib
#python get_data.py AAPL

