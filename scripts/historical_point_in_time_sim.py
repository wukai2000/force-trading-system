"""
scripts/historical_point_in_time_sim.py
======================================
Point-in-time *research* loop.

Default: do NOT scan the Defense sketch (WAIT). Literature hypotheses only.
A 6-month OOS window is a scout and cannot promote.

`--research-wait-sketch` is the only way to touch ITA/XAR/PPA, and it still
writes scannable=false. `--allow-yahoo` is required if those prices are not
cached (they should not be cached while WAIT holds).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from force_engine.discovery import ForceDiscoveryEngine
from force_engine.dates import naive_day_index, pick_close_column
from force_engine.evaluate import annualized_ir
from force_engine.freeze import FreezeError
from force_engine.guards import WAIT_TICKERS, WaitLockError, refuse_wait_scan
from force_engine.literature import run_all_simulators
from force_engine.neutralize import NeutralizationError
from force_engine.pipeline import CandidateSpec, evaluate_candidate


DEFAULT_CUTOFFS = ("2021-11-01", "2022-06-01", "2023-10-01")
SKETCH_LEGS = ["ITA", "XAR", "PPA"]
SKETCH_CONTROLS = ["XLI", "SPY"]


def _fetch(tickers, start, end):
    import yfinance as yf

    raw = yf.download(list(tickers), start=start, end=end, auto_adjust=False, progress=False)
    if raw is None or raw.empty:
        raise RuntimeError("empty yfinance")
    if isinstance(raw.columns, pd.MultiIndex):
        px = raw["Adj Close"] if "Adj Close" in raw.columns.levels[0] else raw["Close"]
    else:
        px = raw
    px.columns = [str(c) for c in px.columns]
    return px.dropna(how="any")


def _cache_or_yahoo(tickers, start, end, allow_yahoo: bool):
    cols = {}
    price_dir = ROOT / "data" / "prices"
    ok = True
    for t in tickers:
        p = price_dir / f"{t}.csv"
        if not p.exists():
            ok = False
            break
        df = pd.read_csv(p)
        date_col = df.columns[0]
        close_col = pick_close_column(df.columns)
        idx = naive_day_index(df[date_col])
        cols[t] = pd.Series(pd.to_numeric(df[close_col], errors="coerce").values, index=idx, name=t)
    if ok:
        px = pd.DataFrame(cols).sort_index().dropna(how="any")
        return px.loc[start:end], "cache"
    if not allow_yahoo:
        raise FileNotFoundError("no cached prices; pass allow_yahoo=True")
    return _fetch(tickers, start, end), "yfinance"


def run_one(target_date: str, oos_months: int = 6, allow_yahoo: bool = False) -> dict:
    refuse_wait_scan(SKETCH_LEGS + SKETCH_CONTROLS, allow_wait_sketch=True)
    print(f"\n=== PIT research as of [{target_date}] (WAIT sketch; not a Force 4 lock) ===")
    tickers = SKETCH_LEGS + SKETCH_CONTROLS
    prices_is, src = _cache_or_yahoo(tickers, "2015-01-01", target_date, allow_yahoo)
    print(f"[PIT] IS prices {src}: {len(prices_is)} days")

    engine = ForceDiscoveryEngine()
    rng = np.random.default_rng(abs(hash(target_date)) % (2**32))
    n = min(120, max(60, len(prices_is) // 15))
    idx = pd.date_range(end=pd.Timestamp(target_date), periods=n, freq="ME")
    terms = pd.DataFrame(
        {
            "under_noticed_widget": np.linspace(10, 20, n) + rng.normal(0, 0.5, n),
            "viral_headline": np.linspace(50, 160, n) + rng.normal(0, 6, n),
        },
        index=idx,
    )
    epu = pd.Series(100 + rng.normal(0, 8, n), index=idx)
    epu.iloc[-8:] += 30
    hyps = run_all_simulators(term_counts=terms, epu=epu)
    print(f"[PIT] literature hypotheses as-of {target_date}: {len(hyps)}")
    for h in hyps:
        print(f"      {h.model_id} → {h.theme} ({h.role}) map={h.map_key}")
        if h.map_key in ("defense_sovereign_capacity",):
            raise WaitLockError("literature must not auto-map to defense tickets")

    yaml_path = engine.generate_candidate_yaml_spec(
        candidate_name=f"Defense_PIT_{target_date.replace('-', '')}",
        legs=SKETCH_LEGS,
        controls=SKETCH_CONTROLS,
        taxonomy_class="stable_force",
        as_of=target_date,
        literature_models=[h.model_id for h in hyps],
        scannable=False,
    )

    oos_end = (pd.Timestamp(target_date) + pd.DateOffset(months=oos_months)).strftime("%Y-%m-%d")
    prices_all, src2 = _cache_or_yahoo(tickers, "2015-01-01", oos_end, allow_yahoo)
    spec = CandidateSpec(
        force_id=f"defense_pit_{target_date.replace('-', '')}",
        legs=SKETCH_LEGS,
        controls=SKETCH_CONTROLS,
        gate={
            "min_clean_ir": 0.40,
            "max_placebo_ir": 0.15,
            "min_overlap_years": 0,
        },
    )
    result = {
        "as_of": target_date,
        "oos_end": oos_end,
        "yaml": yaml_path,
        "hypotheses": [h.as_dict() for h in hyps],
        "scout_cannot_promote": True,
        "capital": 0,
        "lock_status": "wait",
        "scannable": False,
        "price_source": src2,
        "note": "raw spread IR is diagnostic only; 6-month scout cannot promote",
    }
    try:
        ev = evaluate_candidate(
            spec, prices_all, allow_wait_sketch=True, allow_unfrozen=True
        )
        resid = ev.panel.residual.dropna()
        t = pd.Timestamp(target_date)
        oos = resid.loc[t : pd.Timestamp(oos_end)]
        result["oos_neutralized_ir"] = annualized_ir(oos) if len(oos) else float("nan")
        result["oos_n"] = int(len(oos))
        result["full_gate_verdict_on_truncated_sample"] = ev.gate.verdict
        result["full_failures"] = list(ev.gate.failures)
        result["mean_betas"] = ev.gate.metrics.get("mean_betas")
        result["placebo_abs_ir"] = ev.gate.metrics.get("placebo_ir")
        result["raw_basket_ir_diagnostic_only"] = ev.diagnostic.get("raw_basket_ir")
        oos_px = prices_all.loc[t : pd.Timestamp(oos_end)]
        rets = oos_px.pct_change(fill_method=None).dropna()
        spread = rets[SKETCH_LEGS].mean(axis=1) - rets[SKETCH_CONTROLS].mean(axis=1)
        result["oos_raw_spread_ir_diagnostic_only"] = annualized_ir(spread) if len(spread) else float("nan")
    except (NeutralizationError, FreezeError, WaitLockError) as e:
        result["error"] = str(e)

    print("=== PIT scout (not a promotion) ===")
    print(f"  cutoff {target_date} → {oos_end}")
    print(f"  neutralized OOS IR: {result.get('oos_neutralized_ir')}")
    print(f"  raw spread OOS IR (diagnostic): {result.get('oos_raw_spread_ir_diagnostic_only')}")
    print(f"  betas: {result.get('mean_betas')}")
    print("  action: wait / no capital / Force 4 not locked")
    return result


def main():
    allow = "--allow-yahoo" in sys.argv
    wait_sketch = "--research-wait-sketch" in sys.argv
    if not wait_sketch:
        print("=== PIT default: WAIT. Not scanning ITA/XAR/PPA/XLI. ===")
        print("Literature hypotheses only. Pass --research-wait-sketch to score the")
        print("defense *sketch* (still scannable=false). Capital $0.")
        engine = ForceDiscoveryEngine()
        hyps = run_all_simulators()
        print(f"literature hypotheses with no series: {len(hyps)} (empty is correct)")
        for key, theme in (engine._theme_map.get("themes") or {}).items():
            print(f"  map {key}: status={theme.get('status')} scannable={theme.get('scannable', False)}")
        out = ROOT / "data" / "meta" / "pit_research_matrix.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(
                {
                    "capital": 0,
                    "lock_status": "wait",
                    "scannable": False,
                    "rows": [],
                    "note": "default PIT refuses WAIT tickers; no Force 4 scan",
                },
                indent=2,
            )
        )
        print(f"Wrote {out}")
        return
    if allow:
        print("WARNING: --allow-yahoo with wait sketch will fetch ITA/XAR/PPA/XLI.")
        print("This is research-only and cannot promote.")
    rows = []
    for t in DEFAULT_CUTOFFS:
        try:
            rows.append(run_one(t, allow_yahoo=allow))
        except FileNotFoundError as e:
            print(f"[PIT] skip {t}: {e}")
            print("Prices for WAIT tickers are not in cache (correct). Not fetching unless --allow-yahoo.")
            break
    out = ROOT / "data" / "meta" / "pit_research_matrix.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"capital": 0, "lock_status": "wait", "rows": rows}, indent=2, default=str))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
