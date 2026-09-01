"""
Panel sieve — invert discovery.

A unique force is a leftover residual NOT spanned by:
  market + optional extra controls + paused F1/F2/F3 residuals.

Literature models do not pick tickets. This module does not write a
scannable YAML and cannot allocate capital.

WAIT tickers (ITA/XAR/PPA/XLI) are refused as candidates.
Paused F1/F2/F3 legs are refused as candidates.
SIEVE_KEEP cannot promote.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence

import numpy as np
import pandas as pd

from .dates import as_naive_day_series, naive_day_index
from .evaluate import (
    DEFAULT_MAX_PLACEBO_FRAC,
    DEFAULT_MAX_PLACEBO_IR,
    annualized_ir,
    is_concentrated_placebo,
    placebo_frac_of_observed,
    sign_placebo_ir,
)
from .guards import HARD_EXCLUDED_LEGS, NON_CANDIDATE_TICKERS, WAIT_TICKERS, wait_hits
from .layers import lagged_ols_residual
from .neighbor import NeighborResult, load_default_paused, orthogonalize_against_paused


@dataclass
class SieveHit:
    name: str
    leftover_ir: float
    placebo_abs_ir: float
    neighbor_ir: float
    neighbor_verdict: str
    n_days: int
    mean_betas: Dict[str, float]
    verdict: str
    notes: List[str] = field(default_factory=list)
    span_r2: float = float("nan")
    placebo_frac_of_observed: float = float("nan")

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "leftover_ir": self.leftover_ir,
            "placebo_abs_ir": self.placebo_abs_ir,
            "placebo_frac_of_observed": self.placebo_frac_of_observed,
            "neighbor_ir": self.neighbor_ir,
            "neighbor_verdict": self.neighbor_verdict,
            "span_r2": self.span_r2,
            "n_days": self.n_days,
            "mean_betas": self.mean_betas,
            "verdict": self.verdict,
            "notes": list(self.notes),
            "cannot_promote": True,
            "capital": 0,
        }


def _align_returns(prices: pd.DataFrame) -> pd.DataFrame:
    px = prices.copy()
    px.index = naive_day_index(px.index)
    px = px[~px.index.duplicated(keep="last")].sort_index()
    return px.pct_change(fill_method=None)


def sieve_one(
    y: pd.Series,
    controls: pd.DataFrame,
    paused: Mapping[str, pd.Series],
    *,
    name: str,
    lookback: int = 60,
    min_ir: float = 0.40,
    max_placebo: float = DEFAULT_MAX_PLACEBO_IR,
    min_neighbor_ir: float = 0.40,
    max_abs_beta: float = 0.80,
    max_placebo_frac: float = DEFAULT_MAX_PLACEBO_FRAC,
) -> SieveHit:
    y = as_naive_day_series(y, name=name)
    X = pd.DataFrame({c: as_naive_day_series(controls[c], name=c) for c in controls.columns})
    X = X.reindex(y.index)
    panel = lagged_ols_residual(y, X, lookback=lookback)
    resid = panel["resid_layer"].dropna()
    betas = {}
    for c in X.columns:
        key = f"beta_{c}"
        if key in panel.columns and panel[key].notna().any():
            betas[c] = float(panel[key].dropna().mean())
    notes: List[str] = []
    if len(resid) < 60:
        return SieveHit(
            name=name,
            leftover_ir=float("nan"),
            placebo_abs_ir=float("nan"),
            neighbor_ir=float("nan"),
            neighbor_verdict="INSUFFICIENT",
            n_days=int(len(resid)),
            mean_betas=betas,
            verdict="INSUFFICIENT",
            notes=["residual shorter than 60 days"],
        )
    ir = annualized_ir(resid)
    p_ir = sign_placebo_ir(resid)
    p_frac = placebo_frac_of_observed(p_ir, ir)
    nb: NeighborResult = orthogonalize_against_paused(resid, paused, lookback=lookback)
    steal = [c for c, b in betas.items() if abs(b) >= max_abs_beta]
    if steal:
        notes.append(f"stealth beta {steal}")
    verdict = "SIEVE_KEEP"
    if not np.isfinite(ir) or ir < min_ir:
        verdict = "SIEVE_DROP"
        notes.append(f"IR {ir:.3f} < {min_ir}")
    if is_concentrated_placebo(p_ir, ir, max_placebo_ir=max_placebo, max_frac=max_placebo_frac):
        verdict = "SIEVE_DROP"
        notes.append(f"placebo |IR| {p_ir:.3f} is {p_frac:.0%} of observed (concentration)")
    if steal:
        verdict = "SIEVE_DROP"
    if nb.verdict == "NEIGHBOR_SPANNED":
        verdict = "SIEVE_DROP"
        notes.append(f"neighbor spanned IR={nb.neighbor_ir:.3f} span_r2={nb.span_r2:.2f}")
    elif nb.verdict == "INSUFFICIENT":
        notes.append("neighbor insufficient (kept as diagnostic, not a promote)")
        if verdict == "SIEVE_KEEP":
            verdict = "SIEVE_DROP"
            notes.append("cannot keep without a working neighbor test")
    elif nb.verdict == "NO_PAUSED_SERIES":
        notes.append("no paused residuals; neighbor not informative")
    elif np.isfinite(nb.neighbor_ir) and nb.neighbor_ir < min_neighbor_ir:
        verdict = "SIEVE_DROP"
        notes.append(f"neighbor IR {nb.neighbor_ir:.3f} < {min_neighbor_ir}")
    notes.append("cannot_promote; pipeline.evaluate_candidate is the only gate")
    return SieveHit(
        name=name,
        leftover_ir=float(ir) if np.isfinite(ir) else float("nan"),
        placebo_abs_ir=float(p_ir) if np.isfinite(p_ir) else float("nan"),
        neighbor_ir=float(nb.neighbor_ir) if np.isfinite(nb.neighbor_ir) else float("nan"),
        neighbor_verdict=nb.verdict,
        n_days=int(len(resid)),
        mean_betas=betas,
        verdict=verdict,
        notes=notes,
        span_r2=float(nb.span_r2) if np.isfinite(nb.span_r2) else float("nan"),
        placebo_frac_of_observed=float(p_frac) if np.isfinite(p_frac) else float("nan"),
    )


def sieve_panel(
    candidate_returns: pd.DataFrame,
    market: pd.Series,
    paused: Optional[Mapping[str, pd.Series]] = None,
    extra_controls: Optional[pd.DataFrame] = None,
    *,
    lookback: int = 60,
    allow_wait: bool = False,
) -> List[SieveHit]:
    """Residualize each candidate vs market (+ extra), then neighbor vs paused."""
    if candidate_returns is None or candidate_returns.empty:
        return []
    hits: List[SieveHit] = []
    paused = dict(paused or {})
    mkt = as_naive_day_series(market, name=getattr(market, "name", None) or "MKT")
    extra = extra_controls
    for col in candidate_returns.columns:
        name = str(col).upper()
        if name in NON_CANDIDATE_TICKERS:
            hits.append(
                SieveHit(
                    name=name,
                    leftover_ir=float("nan"),
                    placebo_abs_ir=float("nan"),
                    neighbor_ir=float("nan"),
                    neighbor_verdict="SKIP",
                    n_days=0,
                    mean_betas={},
                    verdict="SKIP_NON_ASSET",
                    notes=["vol/level series is not an equity-force candidate"],
                )
            )
            continue
        if name in HARD_EXCLUDED_LEGS:
            hits.append(
                SieveHit(
                    name=name,
                    leftover_ir=float("nan"),
                    placebo_abs_ir=float("nan"),
                    neighbor_ir=float("nan"),
                    neighbor_verdict="SKIP",
                    n_days=0,
                    mean_betas={},
                    verdict="SKIP_EXCLUDED",
                    notes=["paused-force recycle refused"],
                )
            )
            continue
        if name in WAIT_TICKERS and not allow_wait:
            hits.append(
                SieveHit(
                    name=name,
                    leftover_ir=float("nan"),
                    placebo_abs_ir=float("nan"),
                    neighbor_ir=float("nan"),
                    neighbor_verdict="SKIP",
                    n_days=0,
                    mean_betas={},
                    verdict="SKIP_WAIT",
                    notes=["Force 4 / WAIT ticker; not scannable"],
                )
            )
            continue
        y = candidate_returns[col]
        ctrl = pd.DataFrame({mkt.name: mkt})
        if extra is not None:
            for c in extra.columns:
                ctrl[c] = extra[c]
        hits.append(sieve_one(y, ctrl, paused, name=name, lookback=lookback))
    return hits


def sieve_from_prices(
    prices: pd.DataFrame,
    *,
    market: str = "SPY",
    extra_control_tickers: Optional[Sequence[str]] = None,
    candidate_tickers: Optional[Sequence[str]] = None,
    paused: Optional[Mapping[str, pd.Series]] = None,
    allow_wait: bool = False,
) -> List[SieveHit]:
    if wait_hits(prices.columns) and not allow_wait:
        # Presence of WAIT columns in a cache is fine; scoring them is not.
        pass
    rets = _align_returns(prices)
    if market not in rets.columns:
        raise ValueError(f"sieve requires market column {market}")
    if candidate_tickers is None:
        skip = {market.upper()}
        if extra_control_tickers:
            skip.update(t.upper() for t in extra_control_tickers)
        candidate_tickers = [c for c in rets.columns if str(c).upper() not in skip]
    extra = None
    if extra_control_tickers:
        present = [t for t in extra_control_tickers if t in rets.columns]
        if present:
            extra = rets[present]
    paused = paused if paused is not None else load_default_paused()
    return sieve_panel(
        rets[list(candidate_tickers)],
        rets[market],
        paused,
        extra_controls=extra,
        allow_wait=allow_wait,
    )
