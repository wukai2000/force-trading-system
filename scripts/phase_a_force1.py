#!/usr/bin/env python3
"""
Force 1 Phase A — prices + residual vs VOO + coherence scan.

Ticket group (2026-08-19):
  legs:     MAGS, SMH, SPMO
  control:  VOO
  secondary: DRAM (leading/confirmation only)

Outputs (under data/ and artifacts/):
  - data/state/force1_daily_residual.csv
  - data/state/force1_episodes.csv
  - artifacts/charts/force1_residual.png (if matplotlib available)

Run from repo root:
  PYTHONPATH=. python scripts/phase_a_force1.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from force_learning.data.fetch_prices import update_prices, DEFAULT_TICKERS
from force_learning.data.panel import (
    residual_vs,
    coherence,
    DEFAULT_LEGS,
    DEFAULT_CONTROLS,
)
from force_learning.data.cache import data_root, save_parquet

LEGS = list(DEFAULT_LEGS)          # MAGS, SMH, SPMO
CONTROL = DEFAULT_CONTROLS[0]      # VOO
SECONDARY = ["DRAM"]
COHERENCE_LB = 60
Z_WINDOW = 60
PHASE_MIN_DAYS = 10
JOINT_SHIFT_SIGMA = 1.75


def ensure_prices(period: str = "max") -> None:
    tickers = list(dict.fromkeys(LEGS + [CONTROL] + SECONDARY + ["SPY", "QQQ"]))
    print(f"[phase-a] fetching prices for {tickers} (period={period}) ...")
    update_prices(tickers=tickers, period=period, sleep_s=1.0)


def build_daily_series() -> pd.DataFrame:
    resid = residual_vs(CONTROL, legs=LEGS)
    if resid is None:
        raise RuntimeError("Could not build residual — run price fetch first")
    coh = coherence(legs=LEGS, lookback=COHERENCE_LB)
    df = pd.DataFrame({"resid_vs_VOO": resid})
    if coh is not None:
        df["coherence"] = coh
    # z-score of residual
    mu = df["resid_vs_VOO"].rolling(Z_WINDOW).mean()
    sd = df["resid_vs_VOO"].rolling(Z_WINDOW).std()
    df["resid_z"] = (df["resid_vs_VOO"] - mu) / sd.replace(0, np.nan)
    # cumulative residual (for visual)
    df["cum_resid"] = df["resid_vs_VOO"].cumsum()
    return df.dropna(how="all")


def simple_phase_scan(df: pd.DataFrame) -> pd.DataFrame:
    """
    Very lightweight 3-phase candidate detector (v0).
    Quiet dominance: positive rolling residual mean + rising/high coherence.
    Catch-up: joint residual acceleration > JOINT_SHIFT_SIGMA.
    Stabilization: residual mean reverts toward zero while still elevated.
    """
    episodes = []
    if "resid_z" not in df.columns or len(df) < Z_WINDOW + 20:
        return pd.DataFrame()

    z = df["resid_z"]
    coh = df.get("coherence", pd.Series(index=df.index, dtype=float))
    rolling_mean = df["resid_vs_VOO"].rolling(20).mean()

    # candidate quiet periods: z > 0.5 for sustained stretch + coherence high
    quiet_mask = (z > 0.4) & (coh.fillna(0) > 0.3)
    # acceleration mask
    accel = z.diff(5)
    catch_mask = accel > JOINT_SHIFT_SIGMA

    # crude contiguous-region finder
    in_quiet = False
    start = None
    for i, (idx, is_q) in enumerate(quiet_mask.items()):
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
                        "mean_z": float(z.loc[start:idx].mean()),
                        "mean_coh": float(coh.loc[start:idx].mean()) if coh is not None else np.nan,
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
                    "mean_z": float(z.loc[start:end].mean()),
                    "mean_coh": float(coh.loc[start:end].mean()) if coh is not None else np.nan,
                }
            )

    # catch-up spikes
    for idx, val in catch_mask.items():
        if val:
            episodes.append(
                {
                    "phase": "catch_up_disturbance",
                    "start": idx,
                    "end": idx,
                    "days": 1,
                    "mean_z": float(z.loc[idx]),
                    "mean_coh": float(coh.loc[idx]) if idx in coh.index else np.nan,
                }
            )

    return pd.DataFrame(episodes)


def maybe_plot(df: pd.DataFrame, out_path: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[phase-a] matplotlib not available — skip chart")
        return

    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
    ax0, ax1, ax2 = axes

    ax0.plot(df.index, df["cum_resid"], label="cum residual vs VOO", color="C0")
    ax0.set_ylabel("Cumulative residual")
    ax0.legend(loc="upper left")
    ax0.set_title("Force 1 Phase A — MAGS+SMH+SPMO residual vs VOO")

    ax1.plot(df.index, df["resid_z"], label="residual z (60d)", color="C1", alpha=0.8)
    ax1.axhline(0, color="k", lw=0.5)
    ax1.axhline(1.5, color="r", ls="--", lw=0.7)
    ax1.axhline(-1.5, color="r", ls="--", lw=0.7)
    ax1.set_ylabel("z-score")
    ax1.legend(loc="upper left")

    if "coherence" in df.columns:
        ax2.plot(df.index, df["coherence"], label="coherence (60d)", color="C2")
        ax2.set_ylabel("Coherence")
        ax2.legend(loc="upper left")
    ax2.set_xlabel("Date")

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    print(f"[phase-a] chart → {out_path}")


def main() -> None:
    print("=== Force 1 Phase A scanner ===")
    print(f"legs={LEGS}  control={CONTROL}  secondary={SECONDARY}")

    ensure_prices(period="max")

    df = build_daily_series()
    print(f"[phase-a] daily residual rows={len(df)}  range={df.index.min().date()} → {df.index.max().date()}")

    state_dir = data_root() / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    daily_csv = state_dir / "force1_daily_residual.csv"
    df.to_csv(daily_csv)
    print(f"[phase-a] wrote {daily_csv}")

    # also try parquet if available
    try:
        save_parquet(df, "state/force1_daily_residual.parquet")
    except Exception as e:
        print(f"[phase-a] parquet skip: {e}")

    episodes = simple_phase_scan(df)
    ep_csv = state_dir / "force1_episodes.csv"
    episodes.to_csv(ep_csv, index=False)
    print(f"[phase-a] episodes found={len(episodes)} → {ep_csv}")
    if not episodes.empty:
        print(episodes.groupby("phase").size().to_string())

    chart_path = ROOT / "artifacts" / "charts" / "force1_residual.png"
    maybe_plot(df, chart_path)

    print("=== Phase A complete ===")
    print("Next: review residual series + episodes, refine phase thresholds, then residualize more carefully.")


if __name__ == "__main__":
    main()
