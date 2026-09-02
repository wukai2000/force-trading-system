#!/usr/bin/env python3
"""
Phase B — validate the validator.

Runs Null A (sign-null), Null B (5/21/60 block bootstrap), and both
concentration stats against stored F1/F2/F3 residuals as
research_role=negative_control.

Cannot promote. Cannot scan Force 4. Cannot un-pause F2.
If F2 looks clean under the new reports, print DISTRUST_FRAMEWORK.

Writes data/meta/negative_control_audit.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_engine.dates import naive_day_index, pick_close_column  # noqa: E402
from force_engine.false_discovery import (  # noqa: E402
    DEFAULT_BLOCK_NULL_N,
    DEFAULT_SIGN_NULL_N,
    NegativeControlAudit,
    audit_residual,
    distrust_framework_if_f2_looks_clean,
)
from force_engine.guards import WAIT_TICKERS, WaitLockError  # noqa: E402
from force_engine.neighbor import load_paused_residual_csv  # noqa: E402
from force_engine.neutralize import NeutralizationError, neutralize_prices  # noqa: E402


PAUSED_SOURCES = {
    "f1": [
        (ROOT / "data" / "force1" / "force1_factor_residualized.csv", "factor_clean_resid"),
        (ROOT / "data" / "force1" / "force1_daily_residual.csv", None),
    ],
    "f2": [
        (ROOT / "data" / "force2" / "force2_walkforward_daily.csv", "resid_gross"),
        (ROOT / "data" / "meta" / "l2_force2_aligned.csv", "resid_l2"),
        (ROOT / "data" / "force2" / "force2_daily_residual.csv", "resid_ols"),
    ],
    "f3": [
        (ROOT / "data" / "force3" / "force3_daily_residual.csv", "resid_oos_hedged"),
        (ROOT / "data" / "meta" / "l2_force3_aligned.csv", "resid_l2"),
    ],
}

# Extra F2 families so the attractive-looking residual is not hidden
# behind a later walk-forward CSV with collapsed IR. Still negative controls.
EXTRA_SOURCES = {
    "f2_resid_l2": (ROOT / "data" / "meta" / "l2_force2_aligned.csv", "resid_l2"),
    "f2_resid_ols": (ROOT / "data" / "force2" / "force2_daily_residual.csv", "resid_ols"),
}

F2_OOS_LEGS = ["VST", "ETN", "PWR"]
F2_OOS_CONTROLS = ["XLU", "QQQ"]


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


def _f2_oos_from_cache():
    """Canonical tradable object for F2 (close, lagged-β). Research only."""
    cols = {}
    for t in F2_OOS_LEGS + F2_OOS_CONTROLS:
        s = _load_close(t)
        if s is None:
            return None
        cols[t] = s
    px = pd.DataFrame(cols).dropna(how="any")
    if px.empty:
        return None
    try:
        panel = neutralize_prices(px, F2_OOS_LEGS, F2_OOS_CONTROLS, lookback=60)
    except NeutralizationError:
        return None
    return panel.residual.dropna()


def _refuse_force4(args: argparse.Namespace) -> None:
    if getattr(args, "scan_force4", False) or getattr(args, "promote", False):
        raise WaitLockError(
            "Negative-control audit refuses --promote and Force 4. "
            f"WAIT tickers {sorted(WAIT_TICKERS)} stay unscannable. Capital $0."
        )


def _load_paused() -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for fid, cands in PAUSED_SOURCES.items():
        for path, col in cands:
            s = load_paused_residual_csv(path, col)
            if s is not None and len(s) >= 60:
                src = f"{path.relative_to(ROOT)}:{col or 'auto'}"
                out[fid] = {"series": s, "source": src}
                break
    for fid, (path, col) in EXTRA_SOURCES.items():
        s = load_paused_residual_csv(path, col)
        if s is not None and len(s) >= 60:
            out[fid] = {"series": s, "source": f"{path.relative_to(ROOT)}:{col}"}
    oos = _f2_oos_from_cache()
    if oos is not None and len(oos) >= 60:
        out["f2_oos_hedged"] = {
            "series": oos,
            "source": "data/prices/{VST,ETN,PWR,XLU,QQQ}.csv:close lagged-β OOS",
        }
    return out


def _print_audit(a: NegativeControlAudit) -> None:
    print(
        f"{a.force_id} role={a.research_role} n={a.n_days} IR={a.observed_ir:.3f} "
        f"labels={a.labels} Q1={a.audit_questions['Q1_statistical_null']} "
        f"Q2={a.audit_questions['Q2_dependence']} "
        f"Q3={a.audit_questions['Q3_concentration']} "
        f"Q4={a.audit_questions['Q4_mechanism']} "
        f"Q5={a.audit_questions['Q5_independence']}"
    )
    sn = a.sign_null
    print(
        f"  Null A: perc={sn.get('observed_percentile')} "
        f"p1={sn.get('empirical_p_value_one_sided')} "
        f"p2={sn.get('empirical_p_value_two_sided')} "
        f"null_std={sn.get('null_std_ir')}"
    )
    conc = a.concentration
    print(
        f"  Conc A persist={conc.get('ir_persistence_ratio')} "
        f"kill={conc.get('ir_persistence_kill')} "
        f"Conc B top5={conc.get('pnl_mass_top5')} top10={conc.get('pnl_mass_top10')}"
    )
    for blk in ("5", "21", "60"):
        b = a.block_bootstrap.get(blk, {})
        print(
            f"  Null B block={blk}: mean_ir={b.get('mean_ir')} "
            f"std={b.get('std_ir')} frac>=0.40={b.get('frac_ir_ge_gate')} "
            f"p5={b.get('p5')}"
        )


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="F1/F2/F3 negative-control audit. Cannot promote.")
    p.add_argument("--n-sign", type=int, default=DEFAULT_SIGN_NULL_N, help="Null A draws (computational sample)")
    p.add_argument("--n-block", type=int, default=DEFAULT_BLOCK_NULL_N, help="Null B draws per block length")
    p.add_argument("--out", type=Path, default=ROOT / "data" / "meta" / "negative_control_audit.json")
    p.add_argument("--promote", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--scan-force4", action="store_true", help=argparse.SUPPRESS)
    args = p.parse_args(argv)
    _refuse_force4(args)

    loaded = _load_paused()
    if not loaded:
        print("NO_RESIDUALS: no paused F1/F2/F3 residual CSVs found", file=sys.stderr)
        return 2

    audits: List[NegativeControlAudit] = []
    order = ["f1", "f2", "f2_oos_hedged", "f2_resid_l2", "f2_resid_ols", "f3"]
    for fid in order:
        if fid not in loaded:
            print(f"SKIP {fid}: no residual")
            continue
        item = loaded[fid]
        a = audit_residual(
            item["series"],
            force_id=fid,
            source=item["source"],
            n_sign=int(args.n_sign),
            n_block=int(args.n_block),
        )
        audits.append(a)
        _print_audit(a)

    distrust = distrust_framework_if_f2_looks_clean(audits)
    payload = {
        "as_of": datetime.now(timezone.utc).date().isoformat(),
        "protocol": "docs/RESEARCH_PROTOCOL.md",
        "cannot_promote": True,
        "capital": 0,
        "trump_account": "SPYM_passive_only",
        "force4_scanned": False,
        "n_sign": int(args.n_sign),
        "n_block": int(args.n_block),
        "n_sign_note": "computational sample, not proof of rigor",
        "research_role": "negative_control",
        "desired_result": (
            "methodology exposes why F1/F2/F3 must not be promoted; "
            "F2 PASS would mean distrust the framework, not revive F2"
        ),
        "distrust_framework": bool(distrust),
        "controls": [a.to_dict() for a in audits],
        "queued": {
            "Q4_mechanism": "frozen leading observables for a NEW hypothesis, not F2 after the fact",
            "Q5_independence": "geography / instrument / manifestation / market expression; not US equity cousins",
            "Phase_C": "freeze protocol before naming the next leftover",
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=False))
    print("wrote", args.out)
    if distrust:
        print("DISTRUST_FRAMEWORK: F2 looked clean under Null A and concentration. Do not revive F2.")
        return 3
    print("cannot_promote=true capital=0 force4_scanned=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
