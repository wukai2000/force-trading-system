#!/usr/bin/env python3
"""
Force 2 Phase A — Energy × AI power coupling.

Ticket group (locked 2026-08-24, BEFORE this scan):
  legs:      VST, ETN, PWR
  OLS ctrls: XLU, QQQ
  secondary: CEG (leading only)
  diagnostic: XLE (energy-cycle contamination flag)

Promotion residual = rolling 60d OLS of equal-weight legs on [XLU, QQQ].
Pre-registered gate (do not move after seeing results):
  clean IR ≥ 0.40
  placebo (time-shuffle) IR < 0.15
  |mean β_QQQ| < 0.80
  overlapping history ≥ 8 years

Phase detector: Force-1 Aug-22 style, scale-invariant
  z(resid_slope_20d) and vol_z — NOT the v0 absolute z>0.4 detector.

Run from repo root:
  PYTHONPATH=. python scripts/phase_a_force2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from force_learning.data.cache import data_root, save_parquet
from force_learning.data.fetch_prices import update_prices
from force_learning.data.panel import (
    FORCE2_CONTROLS,
    FORCE2_LEGS,
    annualized_ir,
    coherence,
    residual_ols,
    residual_vs,
)

LEGS = list(FORCE2_LEGS)
CONTROLS = list(FORCE2_CONTROLS)
SECONDARY = ["CEG"]
DIAGNOSTIC = ["XLE", "SPY", "VOO"]
OLS_LB = 60
COH_LB = 60
SLOPE_W = 20
VOL_W = 20
Z_W = 60
PHASE_MIN_DAYS = 10
GATE_IR = 0.40
GATE_PLACEBO_IR = 0.15
GATE_ABS_BETA_QQQ = 0.80
GATE_YEARS = 8


def ensure_prices(period: str = "max") -> None:
    tickers = list(dict.fromkeys(LEGS + CONTROLS + SECONDARY + DIAGNOSTIC))
    print(f"[force2] fetching {tickers} period={period}")
    update_prices(tickers=tickers, period=period, sleep_s=1.0)


def _z(s: pd.Series, window: int) -> pd.Series:
    mu = s.rolling(window).mean()
    sd = s.rolling(window).std()
    return (s - mu) / sd.replace(0, np.nan)


def build_daily_series() -> pd.DataFrame:
    ols = residual_ols(LEGS, CONTROLS, lookback=OLS_LB)
    if ols is None:
        raise RuntimeError("OLS residual failed — fetch prices first")
    df = ols.copy()
    df = df.rename(columns={"resid": "resid_ols"})
    coh = coherence(legs=LEGS, lookback=COH_LB)
    if coh is not None:
        df["coherence"] = coh
    vs_xlu = residual_vs("XLU", legs=LEGS)
    if vs_xlu is not None:
        df["resid_vs_XLU"] = vs_xlu
    vs_xle = residual_vs("XLE", legs=LEGS)
    if vs_xle is not None:
        df["resid_vs_XLE"] = vs_xle

    df["resid_slope_20d"] = df["resid_ols"].rolling(SLOPE_W).mean()
    df["vol"] = df["resid_ols"].rolling(VOL_W).std()
    df["slope_z"] = _z(df["resid_slope_20d"], Z_W)
    df["vol_z"] = _z(df["vol"], Z_W)
    df["resid_z"] = _z(df["resid_ols"], Z_W)
    df["cum_resid"] = df["resid_ols"].cumsum()
    return df.dropna(how="all")


def simple_phase_scan(df: pd.DataFrame) -> pd.DataFrame:
    """
    Scale-invariant 3-phase detector (Aug-22, transferred to Force 2).
    Quiet dominance: slope_z > 0.4 and vol_z < 0.3, sustained.
    Catch-up: slope_z acceleration > 1.5.
    Stabilization: slope_z decaying toward 0 while cum residual still elevated.
    """
    if "slope_z" not in df.columns or len(df) < Z_W + 20:
        return pd.DataFrame()

    slope_z = df["slope_z"]
    vol_z = df.get("vol_z", pd.Series(0.0, index=df.index))
    quiet_mask = (slope_z > 0.4) & (vol_z < 0.3)
    accel = slope_z.diff(5)
    catch_mask = accel > 1.5

    episodes = []
    in_quiet = False
    start = None
    for idx, is_q in quiet_mask.items():
        if is_q and not in_quiet:
            in_quiet = True
            start = idx
        elif not is_q and in_quiet:
            in_quiet = False
            if start is not None and (idx - start).days >= PHASE_MIN_DAYS:
                episodes.append(
                    {
                        "phase": "quiet_dominance",
                        "start": start,
                        "end": idx,
                        "days": (idx - start).days,
                        "mean_slope_z": float(slope_z.loc[start:idx].mean()),
                    }
                )
            start = None
    if in_quiet and start is not None:
        end = quiet_mask.index[-1]
        if (end - start).days >= PHASE_MIN_DAYS:
            episodes.append(
                {
                    "phase": "quiet_dominance",
                    "start": start,
                    "end": end,
                    "days": (end - start).days,
                    "mean_slope_z": float(slope_z.loc[start:end].mean()),
                }
            )

    for idx, val in catch_mask.items():
        if val:
            episodes.append(
                {
                    "phase": "catch_up_disturbance",
                    "start": idx,
                    "end": idx,
                    "days": 1,
                    "mean_slope_z": float(slope_z.loc[idx]),
                }
            )

    # Stabilization: previously elevated slope_z now decaying through 0
    decay = (slope_z.shift(10) > 0.6) & (slope_z < 0.2) & (slope_z > -0.4)
    in_st = False
    st_start = None
    for idx, is_s in decay.items():
        if is_s and not in_st:
            in_st = True
            st_start = idx
        elif not is_s and in_st:
            in_st = False
            if st_start is not None and (idx - st_start).days >= PHASE_MIN_DAYS:
                episodes.append(
                    {
                        "phase": "residual_stabilization",
                        "start": st_start,
                        "end": idx,
                        "days": (idx - st_start).days,
                        "mean_slope_z": float(slope_z.loc[st_start:idx].mean()),
                    }
                )
            st_start = None
    return pd.DataFrame(episodes)


def placebo_ir(resid: pd.Series, n: int = 50, seed: int = 24) -> float:
    """Sign-randomization placebo. A time-shuffle would leave mean/std (hence IR) unchanged."""
    rng = np.random.default_rng(seed)
    vals = resid.dropna().values
    if len(vals) < 60:
        return float("nan")
    irs = []
    for _ in range(n):
        signs = rng.choice(np.array([-1.0, 1.0]), size=len(vals))
        irs.append(annualized_ir(pd.Series(vals * signs)))
    return float(np.nanmean(irs))


def evaluate_gate(df: pd.DataFrame) -> dict:
    resid = df["resid_ols"].dropna()
    years = (resid.index.max() - resid.index.min()).days / 365.25
    ir = annualized_ir(resid)
    p_ir = placebo_ir(resid)
    mean_b_qqq = float(df["beta_QQQ"].mean()) if "beta_QQQ" in df.columns else float("nan")
    mean_b_xlu = float(df["beta_XLU"].mean()) if "beta_XLU" in df.columns else float("nan")
    ir_vs_xle = (
        annualized_ir(df["resid_vs_XLE"]) if "resid_vs_XLE" in df.columns else float("nan")
    )
    fail = []
    if years < GATE_YEARS:
        fail.append(f"overlap {years:.1f}y < {GATE_YEARS}y")
    if not (ir >= GATE_IR):
        fail.append(f"IR {ir:.3f} < {GATE_IR}")
    if not (p_ir < GATE_PLACEBO_IR):
        fail.append(f"placebo IR {p_ir:.3f} ≥ {GATE_PLACEBO_IR}")
    if abs(mean_b_qqq) >= GATE_ABS_BETA_QQQ:
        fail.append(f"|β_QQQ| {abs(mean_b_qqq):.3f} ≥ {GATE_ABS_BETA_QQQ} (stealth tech beta)")
    verdict = "PROMOTE_CANDIDATE" if not fail else "FAIL_GATE"
    return {
        "verdict": verdict,
        "years": years,
        "n_days": int(len(resid)),
        "clean_ir": ir,
        "placebo_ir": p_ir,
        "mean_beta_QQQ": mean_b_qqq,
        "mean_beta_XLU": mean_b_xlu,
        "ir_vs_XLE_diagnostic": ir_vs_xle,
        "failures": fail,
    }


def maybe_plot(df: pd.DataFrame, out_path: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[force2] matplotlib missing — skip chart")
        return
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
    ax0, ax1, ax2 = axes
    ax0.plot(df.index, df["cum_resid"], color="C0", label="cum OLS residual vs XLU+QQQ")
    ax0.set_ylabel("Cumulative residual")
    ax0.set_title("Force 2 Phase A — VST+ETN+PWR residual vs XLU+QQQ")
    ax0.legend(loc="upper left")
    ax1.plot(df.index, df["slope_z"], color="C1", alpha=0.85, label="slope_z 20d")
    ax1.axhline(0, color="k", lw=0.5)
    ax1.axhline(0.4, color="r", ls="--", lw=0.7)
    ax1.set_ylabel("slope z")
    ax1.legend(loc="upper left")
    if "coherence" in df.columns:
        ax2.plot(df.index, df["coherence"], color="C2", label="coherence 60d")
        ax2.legend(loc="upper left")
    ax2.set_xlabel("Date")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    print(f"[force2] chart → {out_path}")


def main() -> None:
    print("=== Force 2 Phase A scanner ===")
    print(f"legs={LEGS}  ols_controls={CONTROLS}  secondary={SECONDARY}")
    print(
        f"GATE: IR≥{GATE_IR}  placebo_IR<{GATE_PLACEBO_IR}  "
        f"|β_QQQ|<{GATE_ABS_BETA_QQQ}  years≥{GATE_YEARS}"
    )

    ensure_prices(period="max")
    df = build_daily_series()
    print(
        f"[force2] rows={len(df)}  range={df.index.min().date()} → {df.index.max().date()}"
    )

    state_dir = data_root() / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    f2_dir = data_root() / "force2"
    f2_dir.mkdir(parents=True, exist_ok=True)

    daily_csv = f2_dir / "force2_daily_residual.csv"
    df.to_csv(daily_csv)
    print(f"[force2] wrote {daily_csv}")
    try:
        save_parquet(df, "state/force2_daily_residual.parquet")
    except Exception as e:
        print(f"[force2] parquet skip: {e}")

    episodes = simple_phase_scan(df)
    ep_csv = f2_dir / "force2_episodes.csv"
    episodes.to_csv(ep_csv, index=False)
    print(f"[force2] episodes={len(episodes)} → {ep_csv}")
    if not episodes.empty:
        print(episodes.groupby("phase").size().to_string())

    gate = evaluate_gate(df)
    print("=== PRE-REGISTERED GATE ===")
    for k, v in gate.items():
        print(f"  {k}: {v}")
    print("=== verdict:", gate["verdict"], "===")
    pd.Series({k: str(v) for k, v in gate.items()}).to_csv(
        f2_dir / "force2_gate.json", header=False
    )

    chart_path = ROOT / "artifacts" / "charts" / "force2_residual.png"
    maybe_plot(df, chart_path)
    print("=== Force 2 Phase A complete (no capital; python_sim only) ===")


if __name__ == "__main__":
    main()
