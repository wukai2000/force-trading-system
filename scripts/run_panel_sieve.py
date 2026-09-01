#!/usr/bin/env python3
"""
Panel sieve: leftover residuals after market + paused F1/F2/F3 spanning.

Does not scan Force 4. WAIT tickers are skipped. Paused legs are skipped.
Cannot promote. Capital $0.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from force_engine.dates import naive_day_index, pick_close_column
from force_engine.guards import HARD_EXCLUDED_LEGS, NON_CANDIDATE_TICKERS, WAIT_TICKERS
from force_engine.neighbor import load_default_paused
from force_engine.sieve import sieve_from_prices, sieve_panel


def _load_cached_prices() -> pd.DataFrame:
    cols = {}
    price_dir = ROOT / "data" / "prices"
    for p in sorted(price_dir.glob("*.csv")):
        if p.name.startswith("."):
            continue
        ticker = p.stem
        if ticker.upper() in NON_CANDIDATE_TICKERS:
            continue
        df = pd.read_csv(p)
        date_col = df.columns[0]
        close_col = pick_close_column(df.columns)
        idx = naive_day_index(df[date_col])
        s = pd.Series(pd.to_numeric(df[close_col], errors="coerce").values, index=idx, name=ticker)
        cols[ticker] = s[~s.index.duplicated(keep="last")].sort_index()
    if not cols:
        return pd.DataFrame()
    return pd.DataFrame(cols).sort_index()


def _synthetic_demo() -> list:
    """Planted leftover vs a spanned combo. No market data required."""
    rng = np.random.default_rng(7)
    idx = pd.bdate_range("2018-01-02", periods=1500)
    mkt = pd.Series(rng.normal(0.0003, 0.011, len(idx)), index=idx, name="SPY")
    f2 = pd.Series(0.0004 + rng.normal(0, 0.008, len(idx)), index=idx, name="f2")
    leftover = pd.Series(0.0009 + rng.normal(0, 0.004, len(idx)), index=idx, name="PLANT")
    spanned = (0.8 * f2 + rng.normal(0, 0.001, len(idx)))
    spanned = pd.Series(spanned, index=idx, name="CLONE")
    wait = pd.Series(0.001 + rng.normal(0, 0.004, len(idx)), index=idx, name="ITA")
    cands = pd.DataFrame({"PLANT": leftover, "CLONE": spanned, "ITA": wait, "VST": f2})
    paused = {"f2": f2}
    return sieve_panel(cands, mkt, paused)


def main() -> int:
    print("=== Panel sieve (cannot promote, capital=0, Force 4 = WAIT) ===")
    paused = load_default_paused()
    print(f"paused residuals loaded: {list(paused)}")
    prices = _load_cached_prices()
    if prices.empty or "SPY" not in prices.columns:
        print("No cached SPY panel — running synthetic planted/spanned/WAIT demo.")
        hits = _synthetic_demo()
        source = "synthetic_demo"
    else:
        print(f"cached prices: {list(prices.columns)} rows={len(prices)}")
        hits = sieve_from_prices(prices, market="SPY", paused=paused, allow_wait=False)
        source = "cache"
    rows = [h.as_dict() for h in hits]
    keep = [r for r in rows if r["verdict"] == "SIEVE_KEEP"]
    print(f"source={source}  candidates={len(rows)}  SIEVE_KEEP={len(keep)}")
    for r in rows:
        print(
            f"  {r['verdict']:16s} {r['name']:8s} IR={r['leftover_ir']}  "
            f"placebo|IR|={r['placebo_abs_ir']}  neighbor={r['neighbor_verdict']}"
        )
        if r["name"] in WAIT_TICKERS:
            assert r["verdict"] == "SKIP_WAIT"
        if r["name"] in HARD_EXCLUDED_LEGS:
            assert r["verdict"] == "SKIP_EXCLUDED"
    out = ROOT / "data" / "meta" / "panel_sieve.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "capital": 0,
        "force4_lock_status": "wait",
        "source": source,
        "n_keep": len(keep),
        "hits": rows,
        "note": "SIEVE_KEEP is not a promotion. pipeline.evaluate_candidate is the only gate.",
    }
    out.write_text(json.dumps(payload, indent=2, default=str))
    print(f"Wrote {out}")
    print("No tickets locked. No ITA/XAR/PPA scan. No capital.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
