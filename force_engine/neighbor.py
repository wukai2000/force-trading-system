"""
Neighbor / spanning test (Huberman-Kandel / Barillas-Shanken flavor).

A new residual that is a linear combination of paused F1/F2/F3 residuals
is not an independent force. Orthogonalize first; leftover IR must still
clear the locked neighbor floor (default 0.40).

This module never promotes and never allocates capital.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Optional

import numpy as np
import pandas as pd

from .evaluate import annualized_ir
from .layers import lagged_ols_residual


DEFAULT_NEIGHBOR_FLOOR = 0.40


@dataclass
class NeighborResult:
    neighbor_ir: float
    n_days: int
    betas: Dict[str, float]
    aligned_paused: int
    verdict: str
    note: str


def orthogonalize_against_paused(
    candidate: pd.Series,
    paused: Mapping[str, pd.Series],
    *,
    lookback: int = 60,
    floor: float = DEFAULT_NEIGHBOR_FLOOR,
) -> NeighborResult:
    """
    OOS residual of `candidate` on paused force residuals.
    Betas lagged; intercept used only in estimation.
    """
    y = pd.Series(candidate).dropna().astype(float).rename("cand")
    cols = {}
    for name, s in paused.items():
        if s is None:
            continue
        ss = pd.Series(s).dropna().astype(float)
        if ss.empty:
            continue
        cols[name] = ss
    if not cols:
        ir = annualized_ir(y)
        return NeighborResult(
            neighbor_ir=ir,
            n_days=int(len(y)),
            betas={},
            aligned_paused=0,
            verdict="NO_PAUSED_SERIES",
            note="no paused residuals supplied; neighbor test not informative",
        )

    X = pd.DataFrame(cols).sort_index()
    panel = lagged_ols_residual(y, X, lookback=lookback)
    resid = panel["resid_layer"].dropna()
    ir = annualized_ir(resid)
    betas = {}
    for c in X.columns:
        key = f"beta_{c}"
        if key in panel.columns and panel[key].notna().any():
            betas[c] = float(panel[key].dropna().mean())

    if len(resid) < 60 or not np.isfinite(ir):
        verdict = "INSUFFICIENT"
    elif ir >= floor:
        verdict = "NEIGHBOR_INDEPENDENT"
    else:
        verdict = "NEIGHBOR_SPANNED"
    return NeighborResult(
        neighbor_ir=float(ir) if np.isfinite(ir) else float("nan"),
        n_days=int(len(resid)),
        betas=betas,
        aligned_paused=len(X.columns),
        verdict=verdict,
        note="leftover IR after lagged-β on paused residuals; not a promotion by itself",
    )


def load_paused_residual_csv(path, column: Optional[str] = None) -> Optional[pd.Series]:
    from pathlib import Path

    p = Path(path)
    if not p.exists():
        return None
    df = pd.read_csv(p)
    date_col = df.columns[0]
    idx = pd.to_datetime(df[date_col], errors="coerce")
    if column and column in df.columns:
        val = df[column]
    else:
        for c in ("resid_oos_hedged", "resid_ols", "residual", "resid_layer"):
            if c in df.columns:
                val = df[c]
                break
        else:
            val = df.iloc[:, -1]
    s = pd.Series(pd.to_numeric(val, errors="coerce").values, index=pd.DatetimeIndex(idx).tz_localize(None).normalize())
    return s[~s.index.duplicated(keep="last")].dropna().sort_index()
