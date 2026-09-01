"""
Multi-layer instruments for the tug-of-war taxonomy.

L1 = sector residual (already produced by neutralize / Phase A).
L2 = vol / credit / curve regime + optional extra residualization vs those series.
L3 = breadth pairs (RSP-SPY, IWM-SPY).
L4 = GPR veto clock (force_engine.clocks; real Iacoviello file; cannot promote).

These never promote a failing L1 residual. They condition and further-neutralize.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from .dates import as_naive_day_series, naive_day_index, pick_close_column

ROOT = Path(__file__).resolve().parents[1]


def _read_fred_csv(name: str) -> pd.Series:
    p = ROOT / "data" / "macro" / f"{name}.csv"
    df = pd.read_csv(p)
    date_col = df.columns[0]
    val_col = "value" if "value" in df.columns else df.columns[-1]
    s = pd.to_numeric(df[val_col], errors="coerce")
    idx = pd.DatetimeIndex(pd.to_datetime(df[date_col], errors="coerce")).tz_localize(None).normalize()
    out = pd.Series(s.values, index=idx, name=name)
    out = out[~out.index.duplicated(keep="last")].sort_index()
    return out.replace(".", np.nan).astype(float)


def _read_price_close(ticker: str) -> pd.Series:
    p = ROOT / "data" / "prices" / f"{ticker}.csv"
    df = pd.read_csv(p)
    date_col = df.columns[0]
    close_col = pick_close_column(df.columns)
    close = pd.to_numeric(df[close_col], errors="coerce")
    idx = naive_day_index(df[date_col])
    s = pd.Series(close.values, index=idx, name=ticker)
    return s[~s.index.duplicated(keep="last")].sort_index()


def load_l2_panel() -> pd.DataFrame:
    vix = _read_fred_csv("vix_cls").rename("vix")
    vxv = _read_fred_csv("vxv_cls").rename("vix3m")
    curve = _read_fred_csv("t10y2y").rename("t10y2y")
    real10 = _read_fred_csv("dfii10").rename("dfii10")
    baa = _read_fred_csv("baa10y").rename("baa10y")
    hy = _read_fred_csv("hy_oas").rename("hy_oas")
    nfci = _read_fred_csv("nfci").rename("nfci")
    panel = pd.concat([vix, vxv, curve, real10, baa, hy, nfci], axis=1).sort_index()
    panel["vix_term"] = panel["vix"] / panel["vix3m"]
    panel["dvix"] = panel["vix"].diff()
    panel["dbaa"] = panel["baa10y"].diff()
    panel["dcurve"] = panel["t10y2y"].diff()
    panel["dreal"] = panel["dfii10"].diff()
    # expanding percentile via rolling rank against expanding mean/std is biased;
    # use a 5y rolling rank (1260d) as a causal stress score.
    def rolling_pctile(s: pd.Series, win: int = 1260) -> pd.Series:
        return s.rolling(win, min_periods=252).rank(pct=True)

    panel["vix_pctile"] = rolling_pctile(panel["vix"])
    panel["baa_pctile"] = rolling_pctile(panel["baa10y"])
    return panel


def classify_regime(row: pd.Series) -> str:
    vix = row.get("vix")
    term = row.get("vix_term")
    baa_p = row.get("baa_pctile")
    if pd.isna(vix):
        return "unknown"
    stress = False
    if vix >= 20.0:
        stress = True
    if pd.notna(term) and term > 1.0:
        stress = True
    if pd.notna(baa_p) and baa_p >= 0.80:
        stress = True
    complacency = False
    if vix < 16.0 and (pd.isna(term) or term < 1.0) and (pd.isna(baa_p) or baa_p <= 0.40):
        complacency = True
    if stress and complacency:
        return "mixed"
    if stress:
        return "stress"
    if complacency:
        return "complacency"
    return "normal"


def attach_regimes(panel: pd.DataFrame) -> pd.DataFrame:
    out = panel.copy()
    out["regime"] = out.apply(classify_regime, axis=1)
    return out


def load_l3_breadth() -> pd.DataFrame:
    spy = _read_price_close("SPY")
    rsp = _read_price_close("RSP")
    iwm = _read_price_close("IWM")
    df = pd.concat(
        {
            "spy_ret": spy.pct_change(),
            "rsp_ret": rsp.pct_change(),
            "iwm_ret": iwm.pct_change(),
        },
        axis=1,
    ).sort_index()
    df["breadth_rsp_spy"] = df["rsp_ret"] - df["spy_ret"]
    df["breadth_iwm_spy"] = df["iwm_ret"] - df["spy_ret"]
    return df


def lagged_ols_residual(
    y: pd.Series,
    X: pd.DataFrame,
    lookback: int = 60,
) -> pd.DataFrame:
    """
    OOS residual: y_t - b_{t-1}' X_t.
    Betas from prior `lookback` days including intercept for estimation only.
    Intercept is NOT subtracted from traded residual.
    """
    y = y.dropna()
    y = as_naive_day_series(y, name=y.name or "y")
    X = X.copy()
    X.index = naive_day_index(X.index)
    X = X[~X.index.duplicated(keep="last")].sort_index()
    X = X.reindex(y.index).astype(float)
    cols = list(X.columns)
    idx = y.index
    resid = np.full(len(idx), np.nan)
    betas = np.full((len(idx), len(cols)), np.nan)
    yv = y.to_numpy(dtype=float)
    xv = X.to_numpy(dtype=float)
    for i in range(lookback + 1, len(idx)):
        sl = slice(i - lookback, i)  # prior window, excludes today
        Yw = yv[sl]
        Xw = xv[sl]
        mask = np.isfinite(Yw) & np.isfinite(Xw).all(axis=1)
        if mask.sum() < max(20, len(cols) + 5):
            continue
        Yw = Yw[mask]
        Xw = Xw[mask]
        ones = np.ones((len(Yw), 1))
        A = np.hstack([ones, Xw])
        try:
            coef, *_ = np.linalg.lstsq(A, Yw, rcond=None)
        except np.linalg.LinAlgError:
            continue
        b = coef[1:]
        xt = xv[i]
        if not np.isfinite(xt).all() or not np.isfinite(yv[i]):
            continue
        resid[i] = yv[i] - float(b @ xt)
        betas[i] = b
    out = pd.DataFrame({"resid_layer": resid}, index=idx)
    for j, c in enumerate(cols):
        out[f"beta_{c}"] = betas[:, j]
    return out


@dataclass
class LiveTape:
    asof: str
    vix: Optional[float]
    vix3m: Optional[float]
    vix_term: Optional[float]
    hy_oas: Optional[float]
    baa10y: Optional[float]
    t10y2y: Optional[float]
    dfii10: Optional[float]
    regime: str
    note: str


def live_tape(panel: pd.DataFrame) -> LiveTape:
    last = panel.dropna(subset=["vix"]).iloc[-1]
    term = last.get("vix_term")
    note = (
        f"VIX={last['vix']:.2f}, VIX3M={last.get('vix3m', float('nan')):.2f}, "
        f"term={term if pd.isna(term) else f'{term:.3f}'}, "
        f"HY_OAS={last.get('hy_oas', float('nan'))}, BAA10Y={last.get('baa10y', float('nan')):.2f}"
    )
    return LiveTape(
        asof=str(last.name.date()),
        vix=float(last["vix"]),
        vix3m=float(last["vix3m"]) if pd.notna(last.get("vix3m")) else None,
        vix_term=float(term) if pd.notna(term) else None,
        hy_oas=float(last["hy_oas"]) if pd.notna(last.get("hy_oas")) else None,
        baa10y=float(last["baa10y"]) if pd.notna(last.get("baa10y")) else None,
        t10y2y=float(last["t10y2y"]) if pd.notna(last.get("t10y2y")) else None,
        dfii10=float(last["dfii10"]) if pd.notna(last.get("dfii10")) else None,
        regime=str(last.get("regime", "unknown")),
        note=note,
    )


def l4_aigpr_stub() -> None:
    """AI-GPR narrative clock. Unwired. Cannot promote. May veto later."""
    return None
