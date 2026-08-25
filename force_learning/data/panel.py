"""
Daily/weekly panel helpers.

Promotion residuals live in force_engine.neutralize (OOS hedged, intercept
not subtracted). residual_ols() is a compatibility wrapper that delegates
there — the old in-sample intercept residual is how F1/F2 zeroed alpha.
"""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np
import pandas as pd

from .cache import load_parquet, save_parquet

# Archived Force 1 defaults — do not use for new experiments.
DEFAULT_LEGS = ["MAGS", "SMH", "SPMO"]
DEFAULT_CONTROLS = ["VOO"]

# Force 2 Phase A (2026-08-24)
FORCE2_LEGS = ["VST", "ETN", "PWR"]
FORCE2_CONTROLS = ["XLU", "QQQ"]

FORCE3_LEGS = ["IHF", "IHI", "XHS"]
FORCE3_CONTROLS = ["XLV", "XBI"]


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
        frames.append(s.pct_change(fill_method=None))
    rets = pd.concat(frames, axis=1).dropna(how="any")
    return rets.mean(axis=1)


def residual_vs(control: str, legs: Sequence[str] = DEFAULT_LEGS) -> Optional[pd.Series]:
    """Diagnostic only — not a promotion series."""
    basket = _equal_weight_returns(legs)
    ctrl = _load_close(control)
    if basket is None or ctrl is None:
        return None
    ctrl_ret = ctrl.pct_change(fill_method=None)
    aligned = pd.concat([basket, ctrl_ret], axis=1, keys=["basket", "ctrl"]).dropna()
    resid = aligned["basket"] - aligned["ctrl"]
    resid.name = f"resid_vs_{control}"
    return resid


def residual_ols(
    legs: Sequence[str],
    controls: Sequence[str],
    lookback: int = 60,
) -> Optional[pd.DataFrame]:
    """
    Compatibility wrapper. Delegates to force_engine.neutralize so a re-run
    of old Phase A scripts cannot silently use the in-sample intercept residual.
    """
    from force_engine.neutralize import NeutralizationError, neutralize_prices

    if not controls:
        print("[panel] residual_ols refuses empty controls")
        return None
    cols = {}
    for t in list(dict.fromkeys(list(legs) + list(controls))):
        s = _load_close(t)
        if s is None or s.empty:
            print(f"[panel] missing price: {t}")
            return None
        cols[t] = s
    prices = pd.DataFrame(cols)
    try:
        panel = neutralize_prices(prices, legs, controls, lookback=lookback)
    except NeutralizationError as e:
        print(f"[panel] neutralize failed: {e}")
        return None
    out = pd.DataFrame({"resid": panel.residual, "basket": panel.basket})
    for c in panel.controls:
        col = f"beta_{c}"
        if col in panel.betas.columns:
            out[col] = panel.betas[col]
    out.index.name = "date"
    print("[panel] residual_ols delegated to force_engine.neutralize (OOS hedged)")
    return out


def coherence(legs: Sequence[str] = DEFAULT_LEGS, lookback: int = 60) -> Optional[pd.Series]:
    """Mean pairwise correlation of daily returns over rolling window."""
    rets = []
    for t in legs:
        s = _load_close(t)
        if s is None:
            return None
        rets.append(s.pct_change(fill_method=None))
    df = pd.concat(rets, axis=1).dropna()
    if len(df) < lookback:
        return None

    def _mean_corr(window: pd.DataFrame) -> float:
        c = window.corr().values
        n = c.shape[0]
        if n < 2:
            return np.nan
        iu = np.triu_indices(n, k=1)
        return float(np.nanmean(c[iu]))

    vals = []
    idx = []
    for i in range(lookback - 1, len(df)):
        window = df.iloc[i - lookback + 1 : i + 1]
        vals.append(_mean_corr(window))
        idx.append(df.index[i])
    return pd.Series(vals, index=idx, name="coherence")


def annualized_ir(resid: pd.Series, periods_per_year: int = 252) -> float:
    s = resid.dropna()
    if len(s) < 60 or s.std() == 0:
        return float("nan")
    return float(s.mean() / s.std() * np.sqrt(periods_per_year))


def build_weekly_panel(
    legs: Sequence[str] = FORCE2_LEGS,
    controls: Sequence[str] = FORCE2_CONTROLS,
    coherence_lookback: int = 60,
) -> Optional[pd.DataFrame]:
    ols = residual_ols(legs, controls, lookback=coherence_lookback)
    coh = coherence(legs=legs, lookback=coherence_lookback)
    if ols is None:
        print("[panel] no OLS residual — run price fetch first")
        return None
    pieces = {"resid_ols": ols["resid"].resample("W-FRI").sum()}
    for c in controls:
        col = f"beta_{c}"
        if col in ols.columns:
            pieces[col] = ols[col].resample("W-FRI").last()
    if coh is not None:
        pieces["coherence"] = coh.resample("W-FRI").last()
    panel = pd.DataFrame(pieces).sort_index()
    panel["naming_score"] = np.nan
    panel["cot_joint_flag"] = 0
    panel["flow_proxy_flag"] = 0
    panel["phase_label"] = "unknown"
    save_parquet(panel, "state/force2_weekly.parquet")
    print(f"[panel] weekly rows={len(panel)} last={panel.index.max().date()}")
    return panel


if __name__ == "__main__":
    build_weekly_panel()
