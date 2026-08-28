import os
import yfinance as yf
import pandas as pd

def fetch_breadth_tickers():
    os.makedirs("data/prices", exist_ok=True)
    tickers = ['RSP', 'IWM']
    
    print("=== Fetching Missing Layer 3 Breadth Series (RSP, IWM) ===")
    
    for ticker in tickers:
        print(f"[fetch] Downloading {ticker}...")
        raw = yf.download(ticker, start='2010-01-01', auto_adjust=False)
        
        # Extract Adj Close / Close safely regardless of yfinance MultiIndex output
        if isinstance(raw.columns, pd.MultiIndex):
            if 'Adj Close' in raw.columns.levels[0]:
                df = raw['Adj Close'][[ticker]].rename(columns={ticker: 'Close'})
            else:
                df = raw['Close'][[ticker]].rename(columns={ticker: 'Close'})
        else:
            if 'Adj Close' in raw.columns:
                df = raw[['Adj Close']].rename(columns={'Adj Close': 'Close'})
            else:
                df = raw[['Close']].rename(columns={'Close': 'Close'})
                
        df = df.dropna()
        out_path = f"data/prices/{ticker}.csv"
        df.to_csv(out_path)
        print(f"[saved] {ticker} -> {out_path} ({len(df)} rows, last date: {df.index[-1].strftime('%Y-%m-%d')})")

if __name__ == "__main__":
    fetch_breadth_tickers()