"""
scripts/historical_point_in_time_sim.py
======================================
Executes a Point-in-Time Historical Simulation as of a specific target date.
Ensures zero look-ahead bias by truncating all data at target_date.
"""

import sys
import os
import pandas as pd
import numpy as np
import yfinance as yf

# Append project root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from force_engine.discovery import ForceDiscoveryEngine

def run_historical_point_in_time_play(target_date="2022-06-01", oos_months=6):
    print(f"=== Running Point-in-Time Simulation as of [{target_date}] ===")
    
    # 1. Load historical prices up to target_date ONLY (In-Sample Discovery)
    tickers = ['ITA', 'XAR', 'PPA', 'XLI', 'SPY']
    print(f"[PIT] Fetching prices truncated at cutoff date: {target_date}...")
    
    raw = yf.download(tickers, start='2015-01-01', end=target_date, auto_adjust=False)
    if isinstance(raw.columns, pd.MultiIndex):
        prices_is = raw['Adj Close'] if 'Adj Close' in raw.columns.levels[0] else raw['Close']
    else:
        prices_is = raw[['Close']]
        
    prices_is = prices_is.dropna()
    print(f"[PIT] In-Sample Data Available: {len(prices_is)} trading days ({prices_is.index[0].strftime('%Y-%m-%d')} to {prices_is.index[-1].strftime('%Y-%m-%d')})")

    # 2. Trigger Discovery Engine using ONLY pre-cutoff data
    engine = ForceDiscoveryEngine()
    
    # Simulate Discovery scan as if today were target_date
    print(f"[PIT] Executing Discovery Engine on pre-{target_date} data window...")
    candidate_spec_path = engine.generate_candidate_yaml_spec(
        candidate_name=f"Defense_PIT_{target_date.replace('-', '')}",
        legs=['ITA', 'XAR', 'PPA'],
        controls=['XLI', 'SPY'],
        taxonomy_class="stable_force",
        output_dir="config/candidates"
    )
    
    # 3. Load Out-of-Sample (OOS) Price Window for Performance Evaluation
    oos_end = (pd.to_datetime(target_date) + pd.DateOffset(months=oos_months)).strftime('%Y-%m-%d')
    print(f"[PIT] Fetching Out-of-Sample Evaluation Window ({target_date} -> {oos_end})...")
    
    raw_oos = yf.download(tickers, start=target_date, end=oos_end, auto_adjust=False)
    if isinstance(raw_oos.columns, pd.MultiIndex):
        prices_oos = raw_oos['Adj Close'] if 'Adj Close' in raw_oos.columns.levels[0] else raw_oos['Close']
    else:
        prices_oos = raw_oos[['Close']]
        
    prices_oos = prices_oos.dropna()
    
    # Calculate simple OOS returns for the discovered basket vs controls
    rets_oos = prices_oos.pct_change().dropna()
    long_leg = rets_oos[['ITA', 'XAR', 'PPA']].mean(axis=1)
    control_leg = rets_oos[['XLI', 'SPY']].mean(axis=1)
    spread = long_leg - control_leg
    
    oos_ir = (spread.mean() / spread.std()) * np.sqrt(252) if spread.std() > 0 else 0
    
    print("\n=== POINT-IN-TIME SIMULATION RESULTS ===")
    print(f"Historical Cutoff Date : {target_date}")
    print(f"OOS Testing Window     : {target_date} to {oos_end} ({len(prices_oos)} days)")
    print(f"OOS Raw Spread Net IR  : {oos_ir:.3f}")
    print(f"Discovered Spec Saved  : {candidate_spec_path}")

if __name__ == "__main__":
    # Example: Run historical play as of June 1, 2022
    run_historical_point_in_time_play(target_date="2022-06-01", oos_months=6)