#!/usr/bin/env python3
"""
Null 1 — regime-label permutation + dwell/hysteresis sensitivity.

Locked 2026-08-27 L2 labels stay the classifier. This script asks whether
IR_complacency − IR_stress on paused residuals is unusual given occupancy
or dwell. Hysteresis is a sensitivity, not a replacement.

Cannot promote. Cannot scan Force 4. Cannot feed labels into position_scale.
HMM / GMM / REGIME_CONTROL_MAP are refused.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_engine.dates import naive_day_index, pick_close_column  # noqa: E402
from force_engine.false_discovery import (  # noqa: E402
    DEFAULT_REGIME_NULL_N,
    hysteresis_sensitivity,
    regime_dwell_report,
    regime_ir_table,
    regime_label_permutation,
)
from force_engine.guards import WAIT_TICKERS, WaitLockError  # noqa: E402
from force_engine.neutralize import NeutralizationError, neutralize_prices  # noqa: E402




ALIGNED = {
    "f2_l1": (ROOT / "data" / "meta" / "l2_force2_aligned.csv", "resid"),
    "f2_l2": (ROOT / "data" / "meta" / "l2_force2_aligned.csv", "resid_l2"),
    "f3_l1": (ROOT / "data" / "meta" / "l2_force3_aligned.csv", "resid"),
    "f3_l2": (ROOT / "data" / "meta" / "l2_force3_aligned.csv", "resid_l2"),
}

# Attractive F2 object: align OOS hedged residual to locked labels by day.



def _refuse(args: argparse.Namespace) -> None:
    if getattr(args, "promote", False) or getattr(args, "scan_force4", False):
        raise WaitLockError(
            "Null 1 refuses --promote, Force 4, HMM, and position_scale. "
            f"WAIT tickers {sorted(WAIT_TICKERS)} stay unscannable. Capital $0."
        )


def _read_aligned(path: Path, col: str) -> Optional[pd.DataFrame]:
    if not path.exists():
        return None
    df = pd.read_csv(path)
    date_col = df.columns[0]
    idx = naive_day_index(df[date_col])
    if col not in df.columns or "regime" not in df.columns:
        return None
    out = pd.DataFrame(
        {
            "r": pd.to_numeric(df[col], errors="coerce").to_numpy(),
            "g": df["regime"].astype(str).to_numpy(),
        },
        index=idx,
    )
    out = out[~out.index.duplicated(keep="last")].sort_index()
    return out.dropna(subset=["r"])


def _load_close(ticker: str):
    p = ROOT / "data" / "prices" / f"{ticker}.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    date_col = df.columns[0]
    close_col = pick_close_column(df.columns)
    idx = naive_day_index(df[date_col])
    s = pd.Series(pd.to_numeric(df[close_col], errors="coerce").values, index=idx, name=ticker)
    return s[~s.index.duplicated(keep="last")].sort_index()


def _f2_oos_hedged_on_labels() -> Optional[pd.DataFrame]:
    """Attractive F2 object (close lagged-β) on locked L2 labels. Still a negative control."""
    aligned = _read_aligned(ROOT / "data" / "meta" / "l2_force2_aligned.csv", "resid")
    if aligned is None:
        return None
    cols = {}
    for t in ("VST", "ETN", "PWR", "XLU", "QQQ"):
        s = _load_close(t)
        if s is None:
            return None
        cols[t] = s
    px = pd.DataFrame(cols).dropna(how="any")
    if px.empty:
        return None
    try:
        panel = neutralize_prices(px, ["VST", "ETN", "PWR"], ["XLU", "QQQ"], lookback=60)
    except NeutralizationError:
        return None
    resid = panel.residual.dropna()
    resid.index = naive_day_index(resid.index)
    df = pd.concat([resid.rename("r"), aligned["g"]], axis=1, join="inner").dropna()
    return df



def _evaluate_one(fid: str, r: pd.Series, g: pd.Series, n: int) -> Dict[str, Any]:
    occ = regime_label_permutation(r, g, n=n, seed=31, mode="occupancy")
    run = regime_label_permutation(r, g, n=n, seed=32, mode="run_length")
    return {
        "force_id": fid,
        "research_role": "negative_control",
        "cannot_promote": True,
        "n_days": int(len(pd.concat([r.rename("r"), g.rename("g")], axis=1, join="inner").dropna())),
        "ir_by_regime": regime_ir_table(r, g),
        "dwell": regime_dwell_report(g),
        "occupancy_null": occ.to_dict(),
        "run_length_null": run.to_dict(),
        "hysteresis_dwell2": hysteresis_sensitivity(r, g, min_dwell=2),
        "hysteresis_dwell3": hysteresis_sensitivity(r, g, min_dwell=3),
    }


def _print_one(row: Dict[str, Any]) -> None:
    ir = row.get("ir_by_regime") or {}
    occ = row.get("occupancy_null") or {}
    run = row.get("run_length_null") or {}
    dwell = row.get("dwell") or {}
    print(
        f"{row['force_id']} n={row.get('n_days')} "
        f"IR_c={ir.get('complacency', {}).get('ir')} "
        f"IR_s={ir.get('stress', {}).get('ir')} "
        f"delta={occ.get('observed_delta')} "
        f"occ_p1={occ.get('empirical_p_value_one_sided')} "
        f"run_p1={run.get('empirical_p_value_one_sided')} "
        f"frac_1day={dwell.get('frac_1day_runs')}"
    )


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Null 1 regime-label permutation. Cannot promote.")
    p.add_argument("--n", type=int, default=DEFAULT_REGIME_NULL_N, help="permutation draws (computational sample)")
    p.add_argument("--out", type=Path, default=ROOT / "data" / "meta" / "regime_label_null.json")
    p.add_argument("--promote", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--scan-force4", action="store_true", help=argparse.SUPPRESS)
    args = p.parse_args(argv)
    _refuse(args)

    rows: List[Dict[str, Any]] = []
    for fid, (path, col) in ALIGNED.items():
        df = _read_aligned(path, col)
        if df is None or len(df) < 120:
            print(f"SKIP {fid}: no aligned residual")
            continue
        if df["r"].notna().sum() < 120:
            print(f"SKIP {fid}: residual too short / empty")
            continue
        row = _evaluate_one(fid, df["r"], df["g"], n=int(args.n))
        rows.append(row)
        _print_one(row)

    oos = _f2_oos_hedged_on_labels()
    if oos is not None and len(oos) >= 120:
        row = _evaluate_one("f2_oos_hedged_on_l2_labels", oos["r"], oos["g"], n=int(args.n))
        rows.append(row)
        _print_one(row)


    if not rows:
        print("NO_RESIDUALS: no aligned L2 residuals", file=sys.stderr)
        return 2

    payload = {
        "as_of": datetime.now(timezone.utc).date().isoformat(),
        "protocol": "docs/RESEARCH_PROTOCOL.md",
        "cannot_promote": True,
        "capital": 0,
        "trump_account": "SPYM_passive_only",
        "force4_scanned": False,
        "n": int(args.n),
        "n_note": "computational sample, not proof of rigor",
        "classifier": "locked 2026-08-27 classify_regime {complacency, normal, stress}",
        "refused": [
            "HMM/GMM hidden states as L2",
            "REGIME_CONTROL_MAP position_scale/leverage/active_strategies",
            "IR(s_t, r_t) with s_t = regime",
            "Force 4 scan",
            "unpause F1/F2/F3",
        ],
        "desired_result": (
            "If occupancy/run-length p is not small, the complacency/stress IR "
            "split is an occupancy artifact — do not treat L2 labels as identification. "
            "If p is small, still cannot promote; calendar non-shock windows remain "
            "the locked REGIME_FAIL partitions."
        ),
        "objects": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=False))
    print("wrote", args.out)
    print("cannot_promote=true capital=0 force4_scanned=false hmm_refused=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
