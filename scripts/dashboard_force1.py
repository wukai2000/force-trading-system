#!/usr/bin/env python3
"""
Quick Force 1 status dashboard (terminal + optional PNG).

Usage:
  python scripts/dashboard_force1.py
  python scripts/dashboard_force1.py --png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from force_learning.data.cache import LastFetch, load_parquet


def load_panel() -> pd.DataFrame | None:
    return load_parquet("state/force1_weekly.parquet")


def print_status(panel: pd.DataFrame) -> None:
    lf = LastFetch()
    print("=" * 60)
    print("FORCE 1 STATUS")
    print("=" * 60)
    print("Last fetch keys:")
    for k, v in sorted(lf.all().items()):
        print(f"  {k}: {v}")
    print("-" * 60)
    if panel is None or panel.empty:
        print("No weekly panel. Run: python scripts/fetch_all.py")
        return

    last = panel.iloc[-1]
    print(f"Panel weeks: {len(panel)}  last week: {panel.index.max().date()}")
    for col in panel.columns:
        val = last[col]
        if pd.isna(val):
            print(f"  {col}: n/a")
        elif isinstance(val, float):
            print(f"  {col}: {val:.4f}")
        else:
            print(f"  {col}: {val}")

    # trailing residual sums
    for w in (4, 12):
        for col in ("resid_vs_SPY", "resid_vs_EFA"):
            if col in panel.columns and len(panel) >= w:
                s = panel[col].tail(w).sum()
                print(f"  {col} sum last {w}w: {s:.4f}")
    print("=" * 60)


def maybe_png(panel: pd.DataFrame, out: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[dashboard] matplotlib not installed; skip PNG")
        return

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    if "resid_vs_SPY" in panel.columns:
        panel["resid_vs_SPY"].cumsum().plot(ax=axes[0], title="Cumulative residual vs SPY")
    if "resid_vs_EFA" in panel.columns:
        panel["resid_vs_EFA"].cumsum().plot(ax=axes[1], title="Cumulative residual vs EFA")
    if "coherence" in panel.columns:
        panel["coherence"].plot(ax=axes[2], title="Coherence (rolling pairwise corr)")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"[dashboard] wrote {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", action="store_true", help="Write artifacts/force1_status.png")
    args = ap.parse_args()

    panel = load_panel()
    print_status(panel if panel is not None else pd.DataFrame())
    if args.png and panel is not None and not panel.empty:
        maybe_png(panel, ROOT / "artifacts" / "force1_status.png")


if __name__ == "__main__":
    main()
