"""
Neighbor / spanning test (Huberman-Kandel / Barillas-Shanken flavor).

A new residual that is a linear combination of paused F1/F2/F3 residuals
is not an independent force. Orthogonalize first; leftover IR must still
clear the locked neighbor floor (default 0.40) AND survive the same
concentration-placebo kill as the main gate.

Leftover IR of white-noise clones sits on the Gaussian sampling floor
(~0.44 at T≈900), so `leftover IR ≥ 0.40` alone cannot detect a clone.
span_r2 is recorded as a diagnostic; it is not a hard kill (a real overlay
drift on top of a paused force must still be allowed to show leftover IR).

This module never promotes and never allocates capital.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Mapping, Optional

import numpy as np
import pandas as pd

from .dates import as_naive_day_series, naive_day_index
from .evaluate import (
    DEFAULT_MAX_PLACEBO_FRAC,
    DEFAULT_MAX_PLACEBO_IR,
    annualized_ir,
    is_concentrated_placebo,
    null_abs_ir_floor,
    placebo_frac_of_observed,
    sign_placebo_ir,
)
from .layers import lagged_ols_residual


DEFAULT_NEIGHBOR_FLOOR = 0.40

_RESID_COLS = (
    "resid_oos_hedged",
    "resid_gross",
    "resid_l2",
    "resid_ols",
    "factor_clean_resid",
    "residual",
    "resid_layer",
    "resid",
)


@dataclass
class NeighborResult:
    neighbor_ir: float
    n_days: int
    betas: Dict[str, float]
    aligned_paused: int
    overlap_days: int
    verdict: str
    note: str
    span_r2: float = float("nan")
    placebo_abs_ir: float = float("nan")
    placebo_frac_of_observed: float = float("nan")


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
    Indexes are coerced to naive calendar days before alignment.
    """
    y = as_naive_day_series(candidate, name="cand")
    cols = {}
    for name, s in paused.items():
        if s is None:
            continue
        ss = as_naive_day_series(s, name=str(name))
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
            overlap_days=0,
            verdict="NO_PAUSED_SERIES",
            note="no paused residuals supplied; neighbor test not informative",
        )

    X = pd.DataFrame(cols).sort_index()
    y = y.reindex(y.index.union(X.index)).dropna()
    X = X.reindex(y.index)
    overlap = int(X.dropna(how="any").shape[0])
    panel = lagged_ols_residual(y, X, lookback=lookback)
    resid = panel["resid_layer"].dropna()
    ir = annualized_ir(resid)
    p_ir = sign_placebo_ir(resid) if len(resid) >= 60 else float("nan")
    p_frac = placebo_frac_of_observed(p_ir, ir)
    y_use = y.reindex(resid.index)
    var_y = float(np.nanvar(y_use.to_numpy())) if len(y_use) else float("nan")
    var_e = float(np.nanvar(resid.to_numpy())) if len(resid) else float("nan")
    if np.isfinite(var_y) and var_y > 1e-18 and np.isfinite(var_e):
        span_r2 = float(max(0.0, min(1.0, 1.0 - var_e / var_y)))
    else:
        span_r2 = float("nan")
    betas = {}
    for c in X.columns:
        key = f"beta_{c}"
        if key in panel.columns and panel[key].notna().any():
            betas[c] = float(panel[key].dropna().mean())

    concentrated = is_concentrated_placebo(
        p_ir, ir, max_placebo_ir=DEFAULT_MAX_PLACEBO_IR, max_frac=DEFAULT_MAX_PLACEBO_FRAC
    )
    n_floor = null_abs_ir_floor(len(resid))

    if overlap < lookback + 20:
        verdict = "INSUFFICIENT"
        note = (
            f"date overlap {overlap} after naive-day align; "
            "need lookback+20. not a promotion."
        )
    elif len(resid) < 60 or not np.isfinite(ir):
        verdict = "INSUFFICIENT"
        note = "leftover residual shorter than 60 days after lagged-β; not a promotion."
    elif ir >= floor and not concentrated:
        verdict = "NEIGHBOR_INDEPENDENT"
        note = (
            "leftover IR after lagged-β on paused residuals survives concentration "
            "placebo; not a promotion by itself"
        )
    else:
        verdict = "NEIGHBOR_SPANNED"
        why = []
        if not (ir >= floor):
            why.append(f"leftover IR {ir:.3f} < {floor}")
        if concentrated:
            why.append(
                f"placebo |IR| {p_ir:.3f} is {p_frac:.0%} of leftover IR "
                f"(sampling-floor / concentrated clone)"
            )
        note = (
            "; ".join(why)
            + f"; span_r2={span_r2:.2f} (diagnostic); null |IR| floor={n_floor:.3f}"
        )
    return NeighborResult(
        neighbor_ir=float(ir) if np.isfinite(ir) else float("nan"),
        n_days=int(len(resid)),
        betas=betas,
        aligned_paused=len(X.columns),
        overlap_days=overlap,
        verdict=verdict,
        note=note,
        span_r2=span_r2,
        placebo_abs_ir=float(p_ir) if np.isfinite(p_ir) else float("nan"),
        placebo_frac_of_observed=float(p_frac) if np.isfinite(p_frac) else float("nan"),
    )


def load_paused_residual_csv(path, column: Optional[str] = None) -> Optional[pd.Series]:
    p = Path(path)
    if not p.exists():
        return None
    df = pd.read_csv(p)
    date_col = df.columns[0]
    idx = naive_day_index(df[date_col])
    if column and column in df.columns:
        val = df[column]
    else:
        val = None
        for c in _RESID_COLS:
            if c in df.columns:
                val = df[c]
                break
        if val is None:
            val = df.iloc[:, -1]
    s = pd.Series(pd.to_numeric(val, errors="coerce").values, index=idx)
    return s[~s.index.duplicated(keep="last")].dropna().sort_index()


def load_default_paused(root: Optional[Path] = None) -> Dict[str, pd.Series]:
    """Best available cached paused residuals (OOS object preferred)."""
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1] / "data"
    out: Dict[str, pd.Series] = {}
    searches = {
        "f1": [
            (root / "force1" / "force1_factor_residualized.csv", "factor_clean_resid"),
            (root / "force1" / "force1_daily_residual.csv", None),
        ],
        "f2": [
            (root / "force2" / "force2_walkforward_daily.csv", "resid_gross"),
            (root / "meta" / "l2_force2_aligned.csv", "resid_l2"),
            (root / "force2" / "force2_daily_residual.csv", "resid_ols"),
        ],
        "f3": [
            (root / "force3" / "force3_daily_residual.csv", "resid_oos_hedged"),
            (root / "meta" / "l2_force3_aligned.csv", "resid_l2"),
        ],
    }
    for fid, cands in searches.items():
        for path, col in cands:
            s = load_paused_residual_csv(path, col)
            if s is not None and len(s) >= 60:
                out[fid] = s
                break
    return out


# Ticket groups of paused forces — used so a force is not neighbored against itself.
_PAUSED_LEGS = {
    "f1": {"MAGS", "SMH", "SPMO"},
    "f2": {"VST", "ETN", "PWR"},
    "f3": {"IHF", "IHI", "XHS"},
}


def paused_excluding_legs(
    legs: Optional[Iterable[str]] = None,
    paused: Optional[Mapping[str, pd.Series]] = None,
    root: Optional[Path] = None,
) -> Dict[str, pd.Series]:
    """Drop the paused residual whose tickets overlap `legs` (no self-neighbor)."""
    paused = dict(paused) if paused is not None else load_default_paused(root)
    if not legs:
        return paused
    up = {str(t).upper() for t in legs}
    for fid, fl in _PAUSED_LEGS.items():
        if up & fl:
            paused.pop(fid, None)
    return paused

