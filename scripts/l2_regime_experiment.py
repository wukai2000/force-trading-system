#!/usr/bin/env python3
"""
L2-REGIME experiment (default).

Condition existing F2 / F3 residuals on stress vs complacency using L2
vol/credit instruments. Optionally extra-neutralize vs L2 deltas and L3
breadth. L4 AI-GPR remains a stub.

Does NOT un-pause or re-spec tickets. Capital stays $0.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_engine.layers import (  # noqa: E402
    attach_regimes,
    l4_aigpr_stub,
    lagged_ols_residual,
    live_tape,
    load_l2_panel,
    load_l3_breadth,
)

ANN = 252.0
IR_FLOOR = 0.40
NONSHOCK_IR = 0.35
PLACEBO_MAX = 0.15


def ir(s: pd.Series) -> float:
    r = s.dropna()
    if len(r) < 20:
        return float("nan")
    sd = r.std(ddof=1)
    if sd == 0 or not np.isfinite(sd):
        return float("nan")
    return float(r.mean() / sd * np.sqrt(ANN))


def placebo_ir(s: pd.Series, seed: int = 7) -> float:
    r = s.dropna().to_numpy()
    if len(r) < 20:
        return float("nan")
    rng = np.random.default_rng(seed)
    signs = rng.choice([-1.0, 1.0], size=len(r))
    shuf = pd.Series(r * signs)
    return ir(shuf)


def load_f2() -> pd.Series:
    p = ROOT / "data" / "force2" / "force2_walkforward_daily.csv"
    df = pd.read_csv(p)
    dt = pd.to_datetime(df.iloc[:, 0], errors="coerce")
    s = pd.Series(df["resid_gross"].values, index=dt, name="f2_resid")
    return s[~s.index.duplicated(keep="first")].sort_index()


def load_f3() -> pd.Series:
    p = ROOT / "data" / "force3" / "force3_daily_residual.csv"
    df = pd.read_csv(p)
    dt = pd.to_datetime(df.iloc[:, 0], errors="coerce")
    col = "resid_oos_hedged" if "resid_oos_hedged" in df.columns else df.columns[1]
    s = pd.Series(df[col].values, index=dt, name="f3_resid")
    return s[~s.index.duplicated(keep="first")].sort_index()


def regime_table(resid: pd.Series, regimes: pd.Series) -> dict:
    out = {}
    aligned = pd.concat([resid.rename("r"), regimes.rename("g")], axis=1).dropna()
    for g, sl in aligned.groupby("g"):
        out[str(g)] = {
            "n": int(len(sl)),
            "ir": ir(sl["r"]),
            "mean": float(sl["r"].mean()),
        }
    out["full"] = {"n": int(len(aligned)), "ir": ir(aligned["r"])}
    return out


def calendar_regimes(resid: pd.Series) -> dict:
    windows = {
        "2017-2019": ("2017-01-01", "2019-12-31"),
        "2020-2021": ("2020-01-01", "2021-12-31"),
        "2022-2023": ("2022-01-01", "2023-12-31"),
        "2024-2026": ("2024-01-01", "2026-12-31"),
    }
    out = {}
    for name, (a, b) in windows.items():
        sl = resid.loc[a:b]
        out[name] = {"n": int(sl.dropna().shape[0]), "ir": ir(sl)}
    # non-shock = exclude 2022-2023 (energy/war shock) as a predefined hyper window
    nonshock = pd.concat(
        [resid.loc["2017-01-01":"2019-12-31"], resid.loc["2024-01-01":"2026-12-31"]]
    )
    out["nonshock_17-19_plus_24-26"] = {"n": int(nonshock.dropna().shape[0]), "ir": ir(nonshock)}
    shock = resid.loc["2022-01-01":"2023-12-31"]
    out["shock_22-23"] = {"n": int(shock.dropna().shape[0]), "ir": ir(shock)}
    return out


def neighbor_orthogonalize(a: pd.Series, b: pd.Series, lookback: int = 60) -> pd.Series:
    X = pd.DataFrame({"nbr": b})
    layer = lagged_ols_residual(a, X, lookback=lookback)
    return layer["resid_layer"]


def evaluate_force(name: str, resid: pd.Series, l2: pd.DataFrame, l3: pd.DataFrame) -> dict:
    cal = pd.DatetimeIndex(resid.index).normalize()
    aligned = resid.to_frame("resid")
    aligned["cal"] = cal
    l2c = l2.copy()
    l2c.index = pd.DatetimeIndex(l2c.index).normalize()
    l2c = l2c[~l2c.index.duplicated(keep="last")]
    l3c = l3.copy()
    l3c.index = pd.DatetimeIndex(l3c.index).normalize()
    l3c = l3c[~l3c.index.duplicated(keep="last")]
    aligned = aligned.join(l2c, on="cal", how="inner")
    aligned = aligned.join(l3c[["breadth_rsp_spy", "breadth_iwm_spy"]], on="cal", how="left")
    aligned = aligned.dropna(subset=["resid", "vix"])

    # L2 extra-neutralize vs dVIX, dBAA, dcurve (lagged β, no intercept in PnL)
    X2 = aligned[["dvix", "dbaa", "dcurve"]].copy()
    layer2 = lagged_ols_residual(aligned["resid"], X2, lookback=60)
    aligned["resid_l2"] = layer2["resid_layer"]
    for c in ["beta_dvix", "beta_dbaa", "beta_dcurve"]:
        if c in layer2.columns:
            aligned[c] = layer2[c]

    # L2+L3
    X23 = aligned[["dvix", "dbaa", "dcurve", "breadth_rsp_spy", "breadth_iwm_spy"]].copy()
    layer23 = lagged_ols_residual(aligned["resid"], X23, lookback=60)
    aligned["resid_l2l3"] = layer23["resid_layer"]

    regimes = aligned["regime"]
    report = {
        "force": name,
        "n": int(len(aligned)),
        "start": str(aligned.index.min().date()),
        "end": str(aligned.index.max().date()),
        "l1_ir": ir(aligned["resid"]),
        "l2_ir": ir(aligned["resid_l2"]),
        "l2l3_ir": ir(aligned["resid_l2l3"]),
        "l1_placebo": placebo_ir(aligned["resid"]),
        "l2_placebo": placebo_ir(aligned["resid_l2"]),
        "mean_beta_l2": {
            "dvix": float(np.nanmean(aligned.get("beta_dvix"))),
            "dbaa": float(np.nanmean(aligned.get("beta_dbaa"))),
            "dcurve": float(np.nanmean(aligned.get("beta_dcurve"))),
        },
        "ir_by_l2_regime_l1": regime_table(aligned["resid"], regimes),
        "ir_by_l2_regime_l2": regime_table(aligned["resid_l2"], regimes),
        "calendar_l1": calendar_regimes(aligned["resid"]),
        "calendar_l2": calendar_regimes(aligned["resid_l2"]),
    }

    # Gate evaluation on L2 residual (primary experiment object)
    l2ir = report["l2_ir"]
    cal = report["calendar_l2"]
    nonshock_hits = []
    for label in ("2017-2019", "2020-2021", "2024-2026"):
        v = cal.get(label, {}).get("ir", float("nan"))
        if np.isfinite(v) and v >= NONSHOCK_IR:
            nonshock_hits.append((label, v))
    report["gate"] = {
        "multilayer_ir_ge_0.40": bool(np.isfinite(l2ir) and l2ir >= IR_FLOOR),
        "nonshock_regimes_ge_0.35_count": len(nonshock_hits),
        "nonshock_hits": nonshock_hits,
        "nonshock_pass": len(nonshock_hits) >= 2,
        "placebo_lt_0.15": bool(report["l2_placebo"] < PLACEBO_MAX),
        "l4_stub": l4_aigpr_stub(),
        "verdict": None,
    }
    g = report["gate"]
    fails = []
    if not g["multilayer_ir_ge_0.40"]:
        fails.append(f"L2 IR {l2ir:.3f} < 0.40")
    if not g["nonshock_pass"]:
        fails.append(f"non-shock regimes passing 0.35: {len(nonshock_hits)} < 2")
    if not g["placebo_lt_0.15"]:
        fails.append(f"placebo {report['l2_placebo']:.3f} >= 0.15")
    g["failures"] = fails
    g["verdict"] = "FAIL_GATE" if fails else "PASS_DIAGNOSTIC_ONLY_STILL_PAUSED"
    return report, aligned


def main() -> int:
    l2 = attach_regimes(load_l2_panel())
    l3 = load_l3_breadth()
    tape = live_tape(l2)

    f2 = load_f2()
    f3 = load_f3()

    f2_rep, f2_al = evaluate_force("force2", f2, l2, l3)
    f3_rep, f3_al = evaluate_force("force3", f3, l2, l3)

    # Neighbor: F3 residual orthogonalized vs F2 residual (paused-neighbor test)
    nbr = neighbor_orthogonalize(f3, f2, lookback=60)
    f3_rep["neighbor_vs_f2_ir"] = ir(nbr)
    f3_rep["neighbor_vs_f2_clears_0.40"] = bool(
        np.isfinite(f3_rep["neighbor_vs_f2_ir"]) and f3_rep["neighbor_vs_f2_ir"] >= IR_FLOOR
    )
    # and F2 vs F3
    nbr2 = neighbor_orthogonalize(f2, f3, lookback=60)
    f2_rep["neighbor_vs_f3_ir"] = ir(nbr2)
    f2_rep["neighbor_vs_f3_clears_0.40"] = bool(
        np.isfinite(f2_rep["neighbor_vs_f3_ir"]) and f2_rep["neighbor_vs_f3_ir"] >= IR_FLOOR
    )

    # Complacency-window snapshot (matches live tape class)
    def window_ir(aligned: pd.DataFrame, key: str) -> dict:
        sl = aligned[aligned["regime"] == "complacency"]
        last60 = aligned.tail(60)
        return {
            "complacency_share": float((aligned["regime"] == "complacency").mean()),
            "stress_share": float((aligned["regime"] == "stress").mean()),
            "last60_regime_counts": last60["regime"].value_counts().to_dict(),
            "last60_l1_ir": ir(last60["resid"]),
            "last60_l2_ir": ir(last60["resid_l2"]),
            "complacency_l1_ir": ir(sl["resid"]) if len(sl) else float("nan"),
            "complacency_l2_ir": ir(sl["resid_l2"]) if len(sl) else float("nan"),
        }

    report = {
        "experiment": "L2-REGIME",
        "locked_gate": {
            "min_multilayer_ir": 0.40,
            "min_nonshock_regime_ir": 0.35,
            "min_nonshock_regimes": 2,
            "max_placebo_ir": 0.15,
            "max_abs_sector_beta": 0.80,
            "min_neighbor_ir": 0.40,
            "clocks": "veto_only",
        },
        "live_tape": tape.__dict__,
        "l4": "AI-GPR stub unwired",
        "capital": 0,
        "note": "Diagnostic on paused residuals only. Does not un-pause F1/F2/F3.",
        "force2": f2_rep,
        "force3": f3_rep,
        "live_window": {
            "force2": window_ir(f2_al, "f2"),
            "force3": window_ir(f3_al, "f3"),
        },
    }

    # synthesis
    syn = []
    syn.append(
        f"Live tape {tape.asof}: regime={tape.regime} VIX={tape.vix} "
        f"VIX3M={tape.vix3m} term={tape.vix_term} HY_OAS={tape.hy_oas} BAA10Y={tape.baa10y}."
    )
    syn.append(
        f"F2 L1 IR={f2_rep['l1_ir']:.3f} → L2 IR={f2_rep['l2_ir']:.3f} → L2+L3 IR={f2_rep['l2l3_ir']:.3f} "
        f"verdict={f2_rep['gate']['verdict']}"
    )
    syn.append(
        f"F3 L1 IR={f3_rep['l1_ir']:.3f} → L2 IR={f3_rep['l2_ir']:.3f} → L2+L3 IR={f3_rep['l2l3_ir']:.3f} "
        f"verdict={f3_rep['gate']['verdict']}"
    )
    syn.append(
        f"Neighbor: F3⊥F2 IR={f3_rep['neighbor_vs_f2_ir']:.3f}; F2⊥F3 IR={f2_rep['neighbor_vs_f3_ir']:.3f}."
    )
    # interpretation
    if f2_rep["l2_ir"] < f2_rep["l1_ir"] - 0.05:
        syn.append("F2 loses IR after stripping vol/credit deltas → part of the residual was L2 (hyper/market) exposure.")
    if f2_rep["ir_by_l2_regime_l1"].get("complacency", {}).get("ir", 0) < NONSHOCK_IR:
        syn.append("F2 complacency-window IR below 0.35 → weak stable-force signature on today's tape class.")
    if f3_rep["l2_ir"] < IR_FLOOR:
        syn.append("F3 remains below multilayer IR floor after L2. Demand residual is not a stable force vs vol/credit.")
    report["synthesis"] = syn

    out_json = ROOT / "data" / "meta" / "l2_regime_report.json"
    out_json.write_text(json.dumps(report, indent=2, default=str))

    # compact daily panel for inspection
    keep = ["resid", "resid_l2", "resid_l2l3", "regime", "vix", "vix3m", "vix_term", "baa10y", "hy_oas", "t10y2y"]
    f2_al[keep].to_csv(ROOT / "data" / "meta" / "l2_force2_aligned.csv")
    f3_al[keep].to_csv(ROOT / "data" / "meta" / "l2_force3_aligned.csv")

    print(json.dumps(report, indent=2, default=str))
    print("\n=== L2-REGIME HUMAN SUMMARY ===")
    print("LIVE:", tape.note, "regime=", tape.regime)
    for line in syn:
        print("-", line)
    print("Wrote", out_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
