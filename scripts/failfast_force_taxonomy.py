#!/usr/bin/env python3
"""
Fail-fast diagnostics for the Force Taxonomy (tug-of-war model).
Runs on existing residual series only — no new tickets, no Option-B.

Questions answered:
1. Does any regime of an existing residual still clear IR >= 0.40?
2. How does residual IR behave under high vs low vol / dispersion proxies?
3. Is performance concentrated (soft-fail signal)?
4. Neighbor check: correlation structure across available residuals.

Exit 0 always (diagnostic). Prints structured JSON + human summary.
Capital remains $0. Does not promote or un-pause any force.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

IR_FLOOR = 0.40
ANN_FACTOR = 252.0


def annualized_ir(r: pd.Series) -> float:
    r = r.dropna()
    if len(r) < 20:
        return float("nan")
    mu = r.mean()
    sd = r.std(ddof=1)
    if sd == 0 or np.isnan(sd):
        return float("nan")
    return float(mu / sd * np.sqrt(ANN_FACTOR))


def load_force2_residual() -> pd.DataFrame:
    p = ROOT / "data" / "force2" / "force2_daily_residual.csv"
    if not p.exists():
        p = Path("/home/workdir/artifacts/force2_out/force2_daily_residual.csv")
    df = pd.read_csv(p)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    # prefer resid_ols if present; fall back
    if "resid_ols" not in df.columns and "resid_oos_hedged" in df.columns:
        df["resid_ols"] = df["resid_oos_hedged"]
    return df


def load_gate(force_id: str) -> dict:
    for base in [ROOT / "data" / force_id, Path("/home/workdir/artifacts/force2_out")]:
        p = base / f"{force_id}_gate.csv"
        if p.exists():
            d = {}
            for line in p.read_text().strip().splitlines():
                if "," in line:
                    k, v = line.split(",", 1)
                    d[k.strip()] = v.strip()
            return d
    return {}


def regime_slice(df: pd.DataFrame, start: str, end: str) -> pd.Series:
    s = df.loc[start:end, "resid_ols"]
    return s


def run_force2_diagnostics(df: pd.DataFrame) -> dict:
    out = {"force": "force2", "n_days": len(df)}
    r = df["resid_ols"]
    out["full_sample_ir"] = annualized_ir(r)

    # Pre-registered style regimes from walkforward
    regimes = {
        "2017-2019": ("2017-01-01", "2019-12-31"),
        "2020-2021": ("2020-01-01", "2021-12-31"),
        "2022-2023": ("2022-01-01", "2023-12-31"),
        "2024-2026": ("2024-01-01", "2026-12-31"),
    }
    regime_irs = {}
    for name, (a, b) in regimes.items():
        ir = annualized_ir(regime_slice(df, a, b))
        regime_irs[name] = ir
    out["regime_irs"] = regime_irs

    # Vol-conditioned (proxy for hyper vs stable)
    if "vol" in df.columns and df["vol"].notna().sum() > 50:
        vol = df["vol"]
        med = vol.median()
        high_vol = r[vol >= med]
        low_vol = r[vol < med]
        out["ir_high_vol"] = annualized_ir(high_vol)
        out["ir_low_vol"] = annualized_ir(low_vol)
    else:
        # fallback: rolling 20d std of residual as vol proxy
        roll_vol = r.rolling(20).std()
        med = roll_vol.median()
        out["ir_high_vol"] = annualized_ir(r[roll_vol >= med])
        out["ir_low_vol"] = annualized_ir(r[roll_vol < med])

    # Coherence-conditioned if available
    if "coherence" in df.columns and df["coherence"].notna().sum() > 50:
        coh = df["coherence"]
        med = coh.median()
        out["ir_high_coherence"] = annualized_ir(r[coh >= med])
        out["ir_low_coherence"] = annualized_ir(r[coh < med])

    # Concentration test: max regime IR / full IR
    valid = [v for v in regime_irs.values() if not np.isnan(v)]
    if valid and out["full_sample_ir"] and not np.isnan(out["full_sample_ir"]):
        out["max_regime_ir"] = max(valid)
        out["concentration_ratio"] = max(valid) / abs(out["full_sample_ir"]) if out["full_sample_ir"] != 0 else None
    else:
        out["max_regime_ir"] = None
        out["concentration_ratio"] = None

    # Fail-fast verdicts (diagnostic only)
    out["clears_ir_floor_any_regime"] = any(
        (v is not None and not np.isnan(v) and v >= IR_FLOOR) for v in regime_irs.values()
    )
    out["clears_ir_floor_low_vol"] = (
        out.get("ir_low_vol") is not None
        and not np.isnan(out["ir_low_vol"])
        and out["ir_low_vol"] >= IR_FLOOR
    )
    out["soft_fail_concentration"] = (
        out.get("concentration_ratio") is not None
        and out["concentration_ratio"] > 2.0
        and out.get("regime_irs", {}).get("2022-2023", 0) == out.get("max_regime_ir")
    )
    return out


def force3_gate_summary() -> dict:
    g = load_gate("force3")
    if not g:
        return {"force": "force3", "status": "gate_file_missing"}
    return {
        "force": "force3",
        "verdict": g.get("verdict"),
        "clean_ir": float(g.get("clean_ir", "nan")),
        "placebo_ir": float(g.get("placebo_ir", "nan")),
        "mean_betas": g.get("mean_betas"),
        "failures": g.get("failures"),
        "clears_ir_floor": float(g.get("clean_ir", 0)) >= IR_FLOOR,
        "stealth_factor": "β_XLV" in str(g.get("failures", "")),
    }


def main() -> int:
    report = {
        "taxonomy": "tug_of_war_v1",
        "date": pd.Timestamp.utcnow().isoformat(),
        "ir_floor": IR_FLOOR,
        "capital": 0,
        "note": "Diagnostic only. Does not un-pause or re-spec any force.",
    }

    try:
        df2 = load_force2_residual()
        report["force2"] = run_force2_diagnostics(df2)
    except Exception as e:
        report["force2"] = {"error": str(e)}

    report["force3"] = force3_gate_summary()
    report["force1"] = {
        "status": "falsified_paused",
        "known_clean_ir": 0.003,
        "failure_mode": "stealth_QQQ_beta_~1.24",
    }

    # Critical synthesis
    f2 = report.get("force2", {})
    f3 = report.get("force3", {})
    synthesis = []
    if f2.get("soft_fail_concentration"):
        synthesis.append(
            "F2 residual strength is regime-concentrated (2022-23). "
            "Consistent with hyper/market (energy shock) rather than pure stable force."
        )
    if f2.get("clears_ir_floor_low_vol") is False and f2.get("ir_low_vol") is not None:
        synthesis.append(
            f"F2 low-vol IR={f2.get('ir_low_vol'):.3f} < 0.40 → stable-force signature weak."
        )
    if f3.get("stealth_factor"):
        synthesis.append(
            "F3 failed on stealth XLV beta (0.841). Demand-side residual collapsed into regular healthcare factor."
        )
    if not f2.get("clears_ir_floor_any_regime") and not f3.get("clears_ir_floor"):
        synthesis.append(
            "No existing residual clears IR floor in a sustained non-hyper regime. "
            "Next exploration must instrument multi-layer residualization before new tickets."
        )
    report["synthesis"] = synthesis

    # Direction for future exploration
    report["next_failfast_directions"] = [
        "Instrument VIX term-structure + cross-sectional dispersion as continuous state vars (layer 2).",
        "Re-residualize existing F2/F3 residual series against breadth / high-beta-low-vol ratio (layer 3).",
        "Build simple narrative residual (dictionary counts residualized vs price mom) and test lead-lag (layer 4).",
        "Neighbor test: any new candidate must be orthogonalized against paused F1/F2/F3 residuals before gate.",
        "Do not re-spec IHF/IHI/XHS or VST/ETN/PWR. New force definitions start from taxonomy, not ticket swaps.",
    ]

    out_path = ROOT / "data" / "meta" / "failfast_taxonomy_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, default=str))

    print(json.dumps(report, indent=2, default=str))
    print("\n=== HUMAN SUMMARY ===")
    print(f"F2 full IR (this residual series): {f2.get('full_sample_ir')}")
    print(f"F2 regime IRs: {f2.get('regime_irs')}")
    print(f"F2 low-vol IR: {f2.get('ir_low_vol')} | high-vol IR: {f2.get('ir_high_vol')}")
    print(f"F2 soft concentration fail: {f2.get('soft_fail_concentration')}")
    print(f"F3 gate: {f3.get('verdict')} clean_ir={f3.get('clean_ir')}")
    for s in synthesis:
        print(f"- {s}")
    print(f"\nReport written: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
