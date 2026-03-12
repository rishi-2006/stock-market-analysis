# 📈 Stock Market Analyzer

The Stock Market Analyzer is a Python-based project designed to explore and understand stock market trends using historical data and machine learning techniques. The goal of this project is to fetch real market data, analyze patterns in stock prices, visualize trends, and predict the next-day movement of a stock using an AI model.

This project was built as part of a structured learning process in data structures, data analysis, and machine learning. It combines financial data analysis with predictive modeling to demonstrate how AI can assist in understanding market behavior.

---

# 🚀 Project Goal

The main objective of this project is to build a tool that can:

- Fetch historical stock market data
- Analyze trends and patterns in stock prices
- Visualize historical performance
- Predict the next-day price movement using a machine learning model

Instead of just plotting charts, this project also explores how data structures and AI models can work together to generate insights from stock market data.

---

# 🛠 Tech Stack

This project is built using Python and several widely used data science libraries.

### Programming Language
- Python

### Libraries Used
- `yfinance` – Fetch stock market data
- `pandas` – Data manipulation and analysis
- `numpy` – Numerical computations
- `matplotlib` – Data visualization
- `seaborn` – Statistical data visualization
- `scikit-learn` – Machine learning models
- `tensorflow / keras` – LSTM neural network model (optional)

---

# 🧠 Data Structures Used

The project also demonstrates the use of basic data structures for handling time-series financial data.

### Time Series Storage
A list or deque is used to store historical stock prices efficiently and analyze sliding windows of price history.

### HashMap (Dictionary)
Python dictionaries are used to map stock symbols to their datasets and metadata. This helps manage multiple companies easily.

Example:

```python
stock_data = {
    "AAPL": apple_data,
    "TSLA": tesla_data
}
```
📊 Key Features
Historical Data Visualization

The system downloads stock data and visualizes closing prices over time. This helps identify long-term trends and market behavior.

Pattern Analysis

The project analyzes stock patterns using technical indicators such as:

Moving averages

Daily returns

Volatility

Trend direction

These indicators help understand the behavior of the stock market over time.

AI-Based Prediction

A Random Forest model is used to predict the next-day movement of the stock price.

The model learns patterns from historical data such as:

Past prices

Returns

Moving averages

Volume

The prediction output is usually a classification:

UP
or
DOWN

This gives a basic idea of possible market movement.

Multi-Company Comparison

The system allows analyzing multiple companies and comparing their performance.

This includes:

Price trend comparison

Volatility comparison

Correlation between companies

Exporting Results

Charts and analysis results can be saved for future reference.

Examples:

Export charts as images

Save processed data to CSV files

Generate analysis reports

Development Timeline:
The project was developed over an 8-week period. In Week 1, the required libraries were installed and stock market data was collected using the yfinance API, downloading one to two years of historical price data and plotting basic closing price trends. In Week 2, time-series data structures such as lists and deques were used to store stock price history, and dictionaries were used to map company symbols to their data while calculating moving averages and volatility. Week 3 focused on exploratory data analysis, identifying trends, price spikes, support and resistance levels, and performing volume analysis through visualizations. In Week 4, a Random Forest machine learning model was developed by creating features from historical data and training the model to predict next-day price movement while evaluating its accuracy and performance. Week 5 explored an advanced approach using an LSTM neural network for time-series prediction and evaluating prediction errors. In Week 6, a simple user interface was integrated to allow users to enter stock tickers and view analysis charts and predictions. Week 7 introduced multi-stock comparison, enabling analysis of multiple companies and generating correlation matrices. Finally, Week 8 focused on refining visualizations, completing documentation, and preparing the project for demonstration. 

The system works in the following steps:

User enters stock ticker
        ↓
Fetch data using yfinance
        ↓
Analyze historical patterns
        ↓
Generate visualizations
        ↓
Train ML model
        ↓
Predict next-day movement
