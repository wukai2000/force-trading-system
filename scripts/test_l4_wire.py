"""
scripts/test_l4_wire.py
=======================
L4-WIRE Caldara–Iacoviello GPR veto clock.

Real fetch only. Synthetic series require FORCE_GPR_SYNTHETIC=1 and are
never labeled as a Caldara fact.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from force_engine.clocks import GPRVetoClock, GPR_DAILY_XLS


def main() -> int:
    print("=== Testing L4-WIRE (Caldara GPR Veto Clock) ===")
    print(f"source URL: {GPR_DAILY_XLS}")
    print("role: veto-only; cannot promote; cannot scan Force 4")
    clock = GPRVetoClock(z_threshold=2.0)
    price_cache_sample = ROOT / "data" / "prices" / "SPY.csv"
    if price_cache_sample.exists():
        trading_calendar = pd.read_csv(price_cache_sample, index_col=0, parse_dates=True).index
    else:
        trading_calendar = pd.bdate_range("2016-01-01", "2026-08-27")

    try:
        gpr_df = clock.fetch_and_cache_gpr_data()
    except Exception as exc:
        print(f"UNWIRED: real GPR fetch failed ({exc})")
        print("Not writing synthetic data to production cache.")
        return 0

    print(f"source={clock.source}  rows={len(gpr_df)}  {gpr_df.index.min().date()} → {gpr_df.index.max().date()}")
    if clock.source == "synthetic-test":
        print("WARNING: this is FORCE_GPR_SYNTHETIC, not a Caldara series.")
    veto_aligned = clock.compute_veto_series(target_index=trading_calendar)
    veto_days = veto_aligned[veto_aligned["veto_active"] == True]
    print(f"Total Trading Days Analyzed : {len(veto_aligned)}")
    print(f"Total Veto Days Triggered   : {len(veto_days)} ({len(veto_days)/max(1,len(veto_aligned))*100:.2f}%)")
    print("Recent Sample Veto Spikes (GPR Z-Score >= 2.0):")
    cols = [c for c in ("gpr_index", "gpr_zscore", "veto_active") if c in veto_aligned.columns]
    print(veto_aligned[veto_aligned["veto_active"] == True].tail(10)[cols])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
