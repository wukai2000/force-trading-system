"""
Weekly panel: residual vs SPY/EFA, coherence, placeholder clock flags.

Consumable state for force_engine / dashboard.
"""

from __future__ import annotations

from typing import List, Optional, Sequence

import numpy as np
import pandas as pd

from .cache import load_parquet, save_parquet

DEFAULT_LEGS = ["MAGS", "SMH", "SPMO"]
DEFAULT_CONTROLS = ["VOO"]


def _load_close(ticker: str) -> Optional[pd.Series]:
    rel = f"prices/{ticker.replace('/', '_')}.parquet"
    df = load_parquet(rel)
    if df is None or "close" not in df.columns:
        return None
    s = df["close"].copy()
    s.index = pd.to_datetime(s.index).tz_localize(None)
    s.name = ticker
    return s.sort_index()


def _equal_weight_returns(tickers: Sequence[str]) -> Optional[pd.Series]:
    frames = []
    for t in tickers:
        s = _load_close(t)
        if s is None or s.empty:
            print(f"[panel] missing price: {t}")
            return None
        frames.append(s.pct_change())
    rets = pd.concat(frames, axis=1).dropna(how="any")
    return rets.mean(axis=1)


def residual_vs(control: str, legs: Sequence[str] = DEFAULT_LEGS) -> Optional[pd.Series]:
    basket = _equal_weight_returns(legs)
    ctrl = _load_close(control)
    if basket is None or ctrl is None:
        return None
    ctrl_ret = ctrl.pct_change()
    aligned = pd.concat([basket, ctrl_ret], axis=1, keys=["basket", "ctrl"]).dropna()
    # simple residual: basket - control (not beta-adjusted yet — Phase F will residualize)
    resid = aligned["basket"] - aligned["ctrl"]
    resid.name = f"resid_vs_{control}"
    return resid


def coherence(legs: Sequence[str] = DEFAULT_LEGS, lookback: int = 60) -> Optional[pd.Series]:
    """Mean pairwise correlation of daily returns over rolling window."""
    rets = []
    for t in legs:
        s = _load_close(t)
        if s is None:
            return None
        rets.append(s.pct_change())
    df = pd.concat(rets, axis=1).dropna()
    if len(df) < lookback:
        return None

    def _mean_corr(window: pd.DataFrame) -> float:
        c = window.corr().values
        n = c.shape[0]
        if n < 2:
            return np.nan
        # upper triangle
        iu = np.triu_indices(n, k=1)
        return float(np.nanmean(c[iu]))

    out = df.rolling(lookback).apply(lambda x: np.nan, raw=False)  # placeholder structure
    # proper rolling pairwise mean
    vals = []
    idx = []
    for i in range(lookback - 1, len(df)):
        window = df.iloc[i - lookback + 1 : i + 1]
        vals.append(_mean_corr(window))
        idx.append(df.index[i])
    return pd.Series(vals, index=idx, name="coherence")


def build_weekly_panel(
    legs: Sequence[str] = DEFAULT_LEGS,
    controls: Sequence[str] = DEFAULT_CONTROLS,
    coherence_lookback: int = 60,
) -> Optional[pd.DataFrame]:
    """
    Build weekly panel and save to data/state/force1_weekly.parquet.

    Columns:
      resid_vs_SPY, resid_vs_EFA (weekly sum of daily residual)
      coherence (last daily value in week)
      naming_score, cot_joint_flag, flow_proxy_flag  (placeholders until streams wired)
    """
    pieces = {}
    for c in controls:
        r = residual_vs(c, legs=legs)
        if r is not None:
            weekly = r.resample("W-FRI").sum()
            pieces[f"resid_vs_{c}"] = weekly

    coh = coherence(legs=legs, lookback=coherence_lookback)
    if coh is not None:
        pieces["coherence"] = coh.resample("W-FRI").last()

    if not pieces:
        print("[panel] no data — run price fetch first")
        return None

    panel = pd.DataFrame(pieces).sort_index()
    # placeholders for other clocks
    panel["naming_score"] = np.nan
    panel["cot_joint_flag"] = 0
    panel["flow_proxy_flag"] = 0
    panel["phase_label"] = "unknown"

    save_parquet(panel, "state/force1_weekly.parquet")
    print(f"[panel] weekly rows={len(panel)} last={panel.index.max().date()}")
    return panel


if __name__ == "__main__":
    build_weekly_panel()
