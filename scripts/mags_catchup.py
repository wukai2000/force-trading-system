import yfinance as yf
import pandas as pd
import os

# 1. Full universe required by phase_a_force1.py
mag7_constituents = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA']
other_legs = ['SMH', 'SPMO', 'VOO', 'SPY', 'QQQ', 'MAGS']

all_tickers = list(set(mag7_constituents + other_legs))

print(f"Downloading full price panel for: {all_tickers}")
raw_data = yf.download(all_tickers, start='2020-01-01', auto_adjust=False)

# Extract Close/Adj Close safely
if 'Adj Close' in raw_data.columns.levels[0]:
    data = raw_data['Adj Close'].copy()
else:
    data = raw_data['Close'].copy()

# 2. Build equal-weighted Mag-7 synthetic return for pre-MAGS dates
synth_returns = data[mag7_constituents].pct_change().mean(axis=1)
synth_mags_price = (1 + synth_returns).cumprod() * 100

# 3. Patch MAGS column
if 'MAGS' in data.columns:
    data['MAGS'] = data['MAGS'].combine_first(synth_mags_price)
else:
    data['MAGS'] = synth_mags_price

# 4. Save full panel to data/force1/prices_patched.csv
os.makedirs('data/force1', exist_ok=True)
data.to_csv('data/force1/prices_patched.csv')
print(f"Full price panel saved successfully to data/force1/prices_patched.csv. Columns: {list(data.columns)}")