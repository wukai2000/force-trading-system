#!/usr/bin/env python3
"""
Honest point-in-time evaluation.

Uses force_engine.pipeline.evaluate_candidate (neutralize first).
Raw EW spread IR is printed only as a diagnostic.

A 6-month OOS window is a SCOUT. It cannot pass min_overlap_years or the
multi-regime gate. Scout numbers never allocate capital.

Default: research-only. Will refuse specs marked scannable=false for *new*
forces unless --research-only is set (default on).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
import os

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from force_engine.evaluate import annualized_ir, sign_placebo_ir
from force_engine.false_discovery import diagnose
from force_engine.neighbor import load_paused_residual_csv, orthogonalize_against_paused
from force_engine.neutralize import NeutralizationError, neutralize_prices
from force_engine.pipeline import evaluate_candidate, spec_from_yaml


def _load_prices_from_cache(tickers):
    """
    Loads price CSVs from data/prices/, deduplicates date indices to prevent 
    reindexing crashes, and returns a unified DataFrame.
    """
    cols = {}
    for ticker in tickers:
        p = os.path.join("data", "prices", f"{ticker}.csv")
        if not os.path.exists(p):
            raise FileNotFoundError(f"Missing cached price CSV for ticker: {ticker} at {p}")
            
        df = pd.read_csv(p, index_col=0, parse_dates=True)
        
        # Deduplicate date index (keep first occurrence)
        df = df[~df.index.duplicated(keep='first')]
        
        # Extract Close or Adj Close column safely
        if 'Adj Close' in df.columns:
            series = df['Adj Close']
        elif 'Close' in df.columns:
            series = df['Close']
        else:
            series = df.iloc[:, 0]
            
        cols[ticker] = series.rename(ticker)
        
    # Build combined DataFrame and sort cleanly by date
    out = pd.DataFrame(cols).sort_index()
    return out.dropna(how='all')


def _load_prices_yf(tickers, start: str, end: Optional[str]):
    import yfinance as yf

    raw = yf.download(list(tickers), start=start, end=end, auto_adjust=False, progress=False)
    if raw is None or raw.empty:
        raise RuntimeError("yfinance returned empty")
    if isinstance(raw.columns, pd.MultiIndex):
        px = raw["Adj Close"] if "Adj Close" in raw.columns.levels[0] else raw["Close"]
    else:
        px = raw
    px.columns = [str(c) for c in px.columns]
    return px


def raw_spread_ir(prices: pd.DataFrame, legs, controls) -> float:
    rets = prices.pct_change(fill_method=None).dropna(how="any")
    long_leg = rets[list(legs)].mean(axis=1)
    ctrl = rets[list(controls)].mean(axis=1)
    spread = long_leg - ctrl
    return annualized_ir(spread)


def window_metrics(resid: pd.Series) -> dict:
    s = resid.dropna()
    if s.empty:
        return {"n": 0, "ir": float("nan"), "placebo": float("nan")}
    return {
        "n": int(len(s)),
        "start": str(s.index.min().date()),
        "end": str(s.index.max().date()),
        "ir": annualized_ir(s),
        "placebo": sign_placebo_ir(s) if len(s) >= 60 else float("nan"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="YAML spec path")
    ap.add_argument("--as-of", dest="as_of", default=None, help="PIT cutoff YYYY-MM-DD")
    ap.add_argument("--oos-months", type=int, default=6)
    ap.add_argument("--start", default="2015-01-01")
    ap.add_argument("--research-only", action="store_true", default=True)
    ap.add_argument("--allow-yahoo", action="store_true", default=False)
    args = ap.parse_args()

    spec_path = Path(args.spec)
    if not spec_path.exists():
        spec_path = ROOT / args.spec
    spec = spec_from_yaml(spec_path)
    raw_yaml = {}
    try:
        import yaml

        raw_yaml = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}
    except Exception:
        raw_yaml = {}

    print("=== PIT evaluate (neutralized residual; capital=0) ===")
    print(f"spec={spec_path}  force_id={spec.force_id}")
    print(f"legs={spec.legs}  controls={spec.controls}")
    print(f"as_of={args.as_of}  oos_months={args.oos_months}  research_only={args.research_only}")
    if raw_yaml.get("scannable") is True and raw_yaml.get("lock_status") != "locked":
        print("NOTE: spec marked scannable but lock_status is not locked; treating as research.")

    tickers = list(dict.fromkeys(list(spec.legs) + list(spec.controls)))
    prices = _load_prices_from_cache(tickers)
    source = "cache"
    if prices is None:
        if not args.allow_yahoo:
            print("No cached prices and --allow-yahoo not set. Refusing live fetch.")
            print("Pass --allow-yahoo to use yfinance for a research scout.")
            return 2
        end = None
        prices = _load_prices_yf(tickers, args.start, end)
        source = "yfinance"
    prices = prices.dropna(how="any")
    print(f"prices source={source} rows={len(prices)} {prices.index.min().date()} → {prices.index.max().date()}")

    try:
        full = evaluate_candidate(spec, prices)
    except NeutralizationError as e:
        print(f"NEUTRALIZATION REFUSED: {e}")
        return 1

    resid = full.panel.residual.dropna()
    report = {
        "force_id": spec.force_id,
        "legs": spec.legs,
        "controls": spec.controls,
        "capital": 0,
        "research_only": True,
        "price_source": source,
        "full_sample": {
            "gate_verdict": full.gate.verdict,
            "failures": list(full.gate.failures),
            "metrics": full.gate.metrics,
            "raw_basket_ir_diagnostic_only": full.diagnostic.get("raw_basket_ir"),
        },
    }

    if args.as_of:
        t = pd.Timestamp(args.as_of)
        oos_end = t + pd.DateOffset(months=args.oos_months)
        is_m = window_metrics(resid.loc[:t])
        oos_m = window_metrics(resid.loc[t:oos_end])
        # raw diagnostic on OOS window only
        oos_px = prices.loc[t:oos_end]
        raw_oos = raw_spread_ir(oos_px, spec.legs, spec.controls) if len(oos_px) > 20 else float("nan")
        report["pit"] = {
            "as_of": args.as_of,
            "oos_end": str(oos_end.date()),
            "in_sample_neutralized": is_m,
            "oos_neutralized_scout": oos_m,
            "oos_raw_spread_ir_diagnostic_only": raw_oos,
            "scout_cannot_promote": True,
            "scout_reason": "window shorter than min_overlap_years and not a multi-regime gate",
        }
        print("\n--- PIT windows (neutralized) ---")
        print(f"  IS  ≤ {args.as_of}: n={is_m['n']} IR={is_m['ir']}")
        print(f"  OOS scout {args.as_of} → {oos_end.date()}: n={oos_m['n']} IR={oos_m['ir']}")
        print(f"  OOS raw spread IR (diagnostic only): {raw_oos}")

    fd = diagnose(resid, n_trials=1)
    report["false_discovery_diagnostic"] = {
        "observed_ir": fd.observed_ir,
        "time_shuffle_ir": fd.time_shuffle_ir,
        "deflated_sharpe": fd.deflated_sharpe,
        "note": fd.note,
    }

    paused = {}
    data_root = ROOT / "data"
    for fid, folder, col in (
        ("f1", "force1", None),
        ("f2", "force2", "resid_oos_hedged"),
        ("f3", "force3", None),
    ):
        for cand in (
            data_root / folder / f"{folder}_daily_residual.csv",
            data_root / folder / "force2_daily_residual.csv",
            data_root / folder / f"{fid}_resid.csv",
        ):
            s = load_paused_residual_csv(cand, col)
            if s is not None and not s.empty:
                paused[fid] = s
                break
    if paused:
        nb = orthogonalize_against_paused(resid, paused)
        report["neighbor"] = {
            "verdict": nb.verdict,
            "neighbor_ir": nb.neighbor_ir,
            "n_days": nb.n_days,
            "betas": nb.betas,
            "aligned_paused": nb.aligned_paused,
        }
        print(f"\n--- Neighbor vs paused {list(paused)} ---")
        print(f"  {nb.verdict}  neighbor_IR={nb.neighbor_ir:.3f}  n={nb.n_days}")
    else:
        report["neighbor"] = {"verdict": "NO_PAUSED_SERIES", "note": "cached paused residuals not found"}

    print("\n--- Full-sample gate (the only promotion-shaped object) ---")
    print(f"  verdict:  {full.gate.verdict}")
    print(f"  clean_IR: {full.gate.metrics.get('clean_ir')}")
    print(f"  placebo:  {full.gate.metrics.get('placebo_ir')}")
    print(f"  betas:    {full.gate.metrics.get('mean_betas')}")
    print(f"  failures: {full.gate.failures or 'none'}")
    print(f"  raw basket IR diagnostic: {full.diagnostic.get('raw_basket_ir')}")
    print("Capital: $0. Scout windows cannot promote. Force 4 remains wait.")

    out_dir = ROOT / "data" / "meta"
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = spec.force_id
    if args.as_of:
        tag += f"_asof_{args.as_of.replace('-', '')}"
    out = out_dir / f"pit_evaluate_{tag}.json"
    out.write_text(json.dumps(report, indent=2, default=str))
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
