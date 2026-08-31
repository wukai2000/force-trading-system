"""
scripts/test_l4_wire.py
=======================
Diagnostic test for L4-WIRE Geopolitical Risk Veto Clock alignment.
"""

import sys
import os
import pandas as pd

# Append project root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from force_engine.clocks import GPRVetoClock

def main():
    print("=== Testing L4-WIRE (Caldara GPR Veto Clock) ===")
    clock = GPRVetoClock(z_threshold=2.0)
    
    # Load mock/cached prices to get trading calendar
    price_cache_sample = os.path.join("data", "prices", "SPY.csv")
    if os.path.exists(price_cache_sample):
        trading_calendar = pd.read_csv(price_cache_sample, index_col=0, parse_dates=True).index
    else:
        trading_calendar = pd.date_range("2016-01-01", "2026-08-27", freq="B")

    # Fetch data and align veto series
    gpr_df = clock.fetch_and_cache_gpr_data()
    veto_aligned = clock.compute_veto_series(target_index=trading_calendar)
    
    # Analyze historical veto triggers
    veto_days = veto_aligned[veto_aligned['veto_active'] == True]
    print(f"\nTotal Trading Days Analyzed : {len(veto_aligned)}")
    print(f"Total Veto Days Triggered   : {len(veto_days)} ({len(veto_days)/len(veto_aligned)*100:.2f}%)")
    
    print("\nRecent Sample Veto Spikes (GPR Z-Score >= 2.0):")
    print(veto_aligned[veto_aligned['veto_active'] == True].tail(10)[['gpr_index', 'gpr_zscore', 'veto_active']])

if __name__ == "__main__":
    main()