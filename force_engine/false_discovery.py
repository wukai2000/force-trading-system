"""
False-discovery *diagnostics*.

The locked promotion gate remains sign-randomization placebo IR < 0.15
in force_engine.evaluate. These extra statistics exist because a walk of
many as-of dates inflates discovery even when each single date is clean.

They cannot promote a failing residual and they cannot loosen the locked gate.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from .evaluate import annualized_ir


@dataclass
class DiscoveryDiagnostics:
    n: int
    observed_ir: float
    time_shuffle_ir: float
    deflated_sharpe: float
    note: str


def time_shuffle_ir(resid: pd.Series, n: int = 50, seed: int = 7) -> float:
    """Permute the residual path (destroys serial structure). Mean IR should be ~0."""
    rng = np.random.default_rng(seed)
    vals = pd.Series(resid).dropna().to_numpy()
    if len(vals) < 60:
        return float("nan")
    irs = []
    for _ in range(n):
        shuf = rng.permutation(vals)
        irs.append(annualized_ir(pd.Series(shuf)))
    return float(np.nanmean(irs))


def deflated_sharpe_ratio(
    resid: pd.Series,
    *,
    n_trials: int = 1,
    observations_per_year: int = 252,
) -> float:
    """
    Bailey-Borwein-Lopez de Prado DSR-style deflation of the observed IR.

    Approximation used for research logging only:
        DSR ≈ Φ( (SR - SR0) * sqrt(T-1) / sqrt(1 - γ3*SR + ((γ4-1)/4)*SR^2) )
    with SR0 ≈ expected max SR under n_trials independent tests.
    """
    s = pd.Series(resid).dropna().astype(float)
    n = len(s)
    if n < 60 or float(s.std()) == 0:
        return float("nan")
    sr = annualized_ir(s)
    # daily SR
    daily_sr = float(s.mean() / s.std())
    t = float(n)
    g3 = float(s.skew())
    g4 = float(s.kurtosis() + 3.0)  # Pearson
    # expected max Sharpe under n_trials (normal approx)
    from math import erfc, sqrt, log, exp

    if n_trials < 1:
        n_trials = 1
    # inverse Mills / extreme-value approx for E[max] of N(0,1)
    if n_trials == 1:
        sr0 = 0.0
    else:
        z = sqrt(2.0 * log(n_trials))
        sr0 = z - (log(log(n_trials)) + log(4.0 * np.pi)) / (2.0 * z)
        sr0 = sr0 / sqrt(observations_per_year)  # daily units
    denom = sqrt(max(1e-12, 1.0 - g3 * daily_sr + ((g4 - 1.0) / 4.0) * daily_sr**2))
    x = ((daily_sr - sr0) * sqrt(t - 1.0)) / denom
    # Φ(x)
    dsr = 0.5 * erfc(-x / sqrt(2.0))
    return float(dsr)


def diagnose(resid: pd.Series, n_trials: int = 1) -> DiscoveryDiagnostics:
    s = pd.Series(resid).dropna()
    return DiscoveryDiagnostics(
        n=int(len(s)),
        observed_ir=annualized_ir(s),
        time_shuffle_ir=time_shuffle_ir(s),
        deflated_sharpe=deflated_sharpe_ratio(s, n_trials=n_trials),
        note="diagnostic only; locked gate is still sign-randomization placebo IR < 0.15",
    )
