"""
Daily/weekly panel helpers: equal-weight residual, rolling OLS residual, coherence.

Force 1 defaults (MAGS/SMH/SPMO vs VOO) are archived — Force 1 is falsified/paused.
Force 2 Phase A uses residual_ols() with legs/controls passed explicitly.
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
    resid = aligned["basket"] - aligned["ctrl"]
    resid.name = f"resid_vs_{control}"
    return resid


def residual_ols(
    legs: Sequence[str],
    controls: Sequence[str],
    lookback: int = 60,
) -> Optional[pd.DataFrame]:
    """
    Rolling OLS: basket_ret ~ 1 + controls. Residual is the promotion series.

    Returns DataFrame with columns:
      basket, resid, plus beta_<ctrl> for each control.
    """
    basket = _equal_weight_returns(legs)
    if basket is None:
        return None
    ctrl_cols = {}
    for c in controls:
        s = _load_close(c)
        if s is None or s.empty:
            print(f"[panel] missing control: {c}")
            return None
        ctrl_cols[c] = s.pct_change()
    X = pd.DataFrame(ctrl_cols)
    df = pd.concat([basket.rename("basket"), X], axis=1).dropna()
    if len(df) < lookback + 5:
        print(f"[panel] OLS too short: {len(df)} rows")
        return None

    n_ctrl = len(controls)
    betas = {c: [] for c in controls}
    resid = []
    idx = []
    y_all = df["basket"].values
    X_all = np.column_stack([np.ones(len(df))] + [df[c].values for c in controls])

    for i in range(lookback - 1, len(df)):
        sl = slice(i - lookback + 1, i + 1)
        y = y_all[sl]
        x = X_all[sl]
        try:
            coef, *_ = np.linalg.lstsq(x, y, rcond=None)
        except np.linalg.LinAlgError:
            resid.append(np.nan)
            for c in controls:
                betas[c].append(np.nan)
            idx.append(df.index[i])
            continue
        yhat = float(x[-1] @ coef)
        resid.append(float(y_all[i] - yhat))
        for j, c in enumerate(controls):
            betas[c].append(float(coef[j + 1]))
        idx.append(df.index[i])

    out = pd.DataFrame({"resid": resid, "basket": df["basket"].loc[idx].values}, index=idx)
    for c in controls:
        out[f"beta_{c}"] = betas[c]
    out.index.name = "date"
    return out


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
