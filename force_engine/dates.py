"""Naive calendar-day indexes + price close picker.

Paused residual CSVs store Yahoo timestamps (14:30). Neutralized residuals
often use midnight or tz-aware stamps. Neighbor OLS reindex then yields
n_days=0. Always compare on UTC-naive normalized dates.
"""
from __future__ import annotations

from typing import Iterable

import pandas as pd


def naive_day_index(idx) -> pd.DatetimeIndex:
    dt = pd.DatetimeIndex(pd.to_datetime(idx, errors="coerce"))
    if dt.tz is not None:
        dt = dt.tz_convert("UTC").tz_localize(None)
    return dt.normalize()


def as_naive_day_series(s: pd.Series, name=None) -> pd.Series:
    s = pd.Series(s).dropna().astype(float)
    out = pd.Series(s.to_numpy(), index=naive_day_index(s.index), name=name or s.name)
    return out[~out.index.duplicated(keep="last")].sort_index()


def pick_close_column(columns: Iterable[str]) -> str:
    """Never fall back to open/volume. Prefer close / adj close, any case."""
    lower = {str(c).strip().lower().replace(" ", "_"): c for c in columns}
    for key in ("close", "adj_close", "adjclose"):
        if key in lower:
            return lower[key]
    raise ValueError(f"no close/adj-close column in {list(columns)}")
