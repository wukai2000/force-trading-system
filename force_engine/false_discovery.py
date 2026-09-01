"""
False-discovery *diagnostics*.

The locked promotion gate is the concentration kill in force_engine.evaluate
(sign-randomization mean |IR| staying ≥40% of observed |IR|). These extra
statistics exist because a walk of many as-of dates inflates discovery even
when each single date is clean.

They cannot promote a failing residual and they cannot loosen the locked gate.

Permutation of the residual *values* leaves mean and std unchanged, so IR
is invariant. The old time_shuffle_ir was a no-op (PIT JSONs had
time_shuffle_ir == observed_ir). Use block bootstrap with replacement
and a concentration share instead.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .evaluate import annualized_ir, sign_placebo_ir


@dataclass
class DiscoveryDiagnostics:
    n: int
    observed_ir: float
    time_shuffle_ir: float
    block_bootstrap_mean_abs_ir: float
    concentration_top5_share: float
    placebo_abs_ir: float
    deflated_sharpe: float
    note: str


def time_shuffle_ir(resid: pd.Series, n: int = 50, seed: int = 7) -> float:
    """Kept as a regression probe: this MUST equal observed IR (order-invariant)."""
    rng = np.random.default_rng(seed)
    vals = pd.Series(resid).dropna().to_numpy()
    if len(vals) < 60:
        return float("nan")
    irs = []
    for _ in range(n):
        shuf = rng.permutation(vals)
        irs.append(annualized_ir(pd.Series(shuf)))
    return float(np.nanmean(irs))


def block_bootstrap_mean_abs_ir(
    resid: pd.Series, n: int = 50, block: int = 21, seed: int = 7
) -> float:
    """Resample contiguous blocks WITH replacement so mean/std can move."""
    rng = np.random.default_rng(seed)
    vals = pd.Series(resid).dropna().to_numpy()
    if len(vals) < 60:
        return float("nan")
    b = max(5, int(block))
    n_blocks = int(np.ceil(len(vals) / b))
    irs = []
    for _ in range(n):
        starts = rng.integers(0, max(1, len(vals) - b + 1), size=n_blocks)
        sample = np.concatenate([vals[s : s + b] for s in starts])[: len(vals)]
        irs.append(annualized_ir(pd.Series(sample)))
    return float(np.nanmean(np.abs(irs)))


def concentration_share(resid: pd.Series, q: float = 0.05) -> float:
    """Fraction of sum |r| coming from the largest q of |r| days (F2 diagnostic)."""
    s = pd.Series(resid).dropna().astype(float)
    if s.empty:
        return float("nan")
    mag = s.abs()
    k = max(1, int(round(len(mag) * q)))
    return float(mag.nlargest(k).sum() / (mag.sum() + 1e-12))


def deflated_sharpe_ratio(
    resid: pd.Series,
    *,
    n_trials: int = 1,
    observations_per_year: int = 252,
) -> float:
    """
    Bailey-Borwein-Lopez de Prado DSR-style deflation of the observed IR.
    Research logging only. Does not replace the locked concentration placebo.
    """
    s = pd.Series(resid).dropna().astype(float)
    n = len(s)
    if n < 60 or float(s.std()) == 0:
        return float("nan")
    daily_sr = float(s.mean() / s.std())
    t = float(n)
    g3 = float(s.skew())
    g4 = float(s.kurtosis() + 3.0)
    from math import erfc, sqrt, log

    if n_trials < 1:
        n_trials = 1
    if n_trials == 1:
        sr0 = 0.0
    else:
        z = sqrt(2.0 * log(n_trials))
        sr0 = z - (log(log(n_trials)) + log(4.0 * np.pi)) / (2.0 * z)
        sr0 = sr0 / sqrt(observations_per_year)
    denom = sqrt(max(1e-12, 1.0 - g3 * daily_sr + ((g4 - 1.0) / 4.0) * daily_sr**2))
    x = ((daily_sr - sr0) * sqrt(t - 1.0)) / denom
    dsr = 0.5 * erfc(-x / sqrt(2.0))
    return float(dsr)


def diagnose(resid: pd.Series, n_trials: int = 1) -> DiscoveryDiagnostics:
    s = pd.Series(resid).dropna()
    return DiscoveryDiagnostics(
        n=int(len(s)),
        observed_ir=annualized_ir(s),
        time_shuffle_ir=time_shuffle_ir(s),
        block_bootstrap_mean_abs_ir=block_bootstrap_mean_abs_ir(s),
        concentration_top5_share=concentration_share(s),
        placebo_abs_ir=sign_placebo_ir(s),
        deflated_sharpe=deflated_sharpe_ratio(s, n_trials=n_trials),
        note=(
            "diagnostic only; locked gate is concentration placebo "
            "(mean |IR| of sign-randomized copies staying ≥40% of observed). "
            "time_shuffle_ir equals observed_ir by construction (IR is order-invariant); "
            "use block_bootstrap_mean_abs_ir and concentration_top5_share."
        ),
    )
