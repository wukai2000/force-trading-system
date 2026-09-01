"""
Candidate evaluation — residual series only.

Promotion metrics are computed exclusively on a NeutralizedPanel.
Raw excess vs SPY/VOO is attached only under diagnostic keys and cannot pass a gate.

Placebo (LOCKED intent 2026-08-28, implemented 2026-08-31):
    mean |IR| of sign-randomized copies of the residual.

Signed-mean placebo concentrates near 0 and cannot kill a concentrated path (F2).
Raw `p_ir < 0.15` is unpassable at ~8y because Gaussian E[|IR|] ≈ 0.25.
Kill when copies keep a large fraction of observed |IR| (F2 0.325/0.725 = 0.45).

PLACEBO_RELAX / SKIP_PLACEBO / RELAX_GATE are refused.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping

import numpy as np
import pandas as pd

from .neutralize import NeutralizationError, NeutralizedPanel


_BANNED_PLACEBO_ENV = ("PLACEBO_RELAX", "SKIP_PLACEBO", "RELAX_GATE")

DEFAULT_MAX_PLACEBO_IR = 0.15
DEFAULT_MAX_PLACEBO_FRAC = 0.40


def _refuse_placebo_bypass() -> None:
    for name in _BANNED_PLACEBO_ENV:
        val = os.environ.get(name)
        if val and val not in ("0", "false", "False", ""):
            raise NeutralizationError(
                f"{name}={val!r} is refused. Placebo concentration kill cannot be bypassed."
            )


def annualized_ir(resid: pd.Series, periods_per_year: int = 252) -> float:
    s = resid.dropna()
    if len(s) < 60 or float(s.std()) == 0:
        return float("nan")
    return float(s.mean() / s.std() * np.sqrt(periods_per_year))


def sign_placebo_ir(resid: pd.Series, n: int = 50, seed: int = 24) -> float:
    """Mean |IR| of `n` sign-randomized copies. Order-invariant IR needs the abs."""
    rng = np.random.default_rng(seed)
    vals = resid.dropna().values
    if len(vals) < 60:
        return float("nan")
    irs = []
    for _ in range(n):
        signs = rng.choice(np.array([-1.0, 1.0]), size=len(vals))
        irs.append(annualized_ir(pd.Series(vals * signs)))
    return float(np.nanmean(np.abs(irs)))


def null_abs_ir_floor(n_days: int) -> float:
    """E[|IR|] of Gaussian white noise ≈ sqrt(2/π) * sqrt(252/T)."""
    if n_days < 2:
        return float("nan")
    return float(np.sqrt(2.0 / np.pi) * np.sqrt(252.0 / n_days))


def placebo_frac_of_observed(p_ir: float, ir: float) -> float:
    ir_abs = abs(ir) if np.isfinite(ir) else float("nan")
    if not (np.isfinite(p_ir) and np.isfinite(ir_abs) and ir_abs > 1e-8):
        return float("nan")
    return float(p_ir / ir_abs)


def is_concentrated_placebo(
    p_ir: float,
    ir: float,
    *,
    max_placebo_ir: float = DEFAULT_MAX_PLACEBO_IR,
    max_frac: float = DEFAULT_MAX_PLACEBO_FRAC,
) -> bool:
    """True when sign-randomization does not destroy the IR (F2-class path / noise)."""
    frac = placebo_frac_of_observed(p_ir, ir)
    return bool(
        np.isfinite(p_ir)
        and np.isfinite(frac)
        and p_ir >= max_placebo_ir
        and frac >= max_frac
    )


@dataclass
class GateResult:
    verdict: str
    metrics: Dict[str, Any]
    failures: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.verdict == "PROMOTE_CANDIDATE"


def evaluate_neutralized(
    panel: NeutralizedPanel,
    gate: Mapping[str, Any],
    *,
    neutralized: bool = False,
) -> GateResult:
    """
    `neutralized=True` must be passed explicitly by the caller as an assertion
    that they did not feed a raw basket residual. This is the F1/F2 tripwire.
    """
    _refuse_placebo_bypass()
    if not neutralized:
        raise NeutralizationError(
            "evaluate_neutralized() requires neutralized=True. "
            "Raw long-only baskets are not candidates (F1/F2 meta-learning)."
        )
    if panel is None or panel.residual is None or panel.residual.dropna().empty:
        raise NeutralizationError("empty residual")

    resid = panel.residual.dropna()
    years = (resid.index.max() - resid.index.min()).days / 365.25
    ir = annualized_ir(resid)
    p_ir = sign_placebo_ir(resid)
    n_days = int(len(resid))
    null_floor = null_abs_ir_floor(n_days)
    placebo_frac = placebo_frac_of_observed(p_ir, ir)
    mean_betas = {
        c: float(panel.betas[f"beta_{c}"].mean())
        for c in panel.controls
        if f"beta_{c}" in panel.betas.columns
    }

    min_ir = float(gate.get("min_clean_ir", 0.40))
    max_p = float(gate.get("max_placebo_ir", DEFAULT_MAX_PLACEBO_IR))
    min_years = float(gate.get("min_overlap_years", 8))
    max_placebo_frac = float(gate.get("max_placebo_frac_of_observed", DEFAULT_MAX_PLACEBO_FRAC))
    fail: List[str] = []
    if years < min_years:
        fail.append(f"overlap {years:.1f}y < {min_years}y")
    if not (ir >= min_ir):
        fail.append(f"IR {ir:.3f} < {min_ir}")
    if is_concentrated_placebo(p_ir, ir, max_placebo_ir=max_p, max_frac=max_placebo_frac):
        fail.append(
            f"placebo |IR| {p_ir:.3f} is {placebo_frac:.0%} of observed IR "
            f"(≥ {max_placebo_frac:.0%}; concentration / F2-class path)"
        )
    for c, b in mean_betas.items():
        cap_key = f"max_abs_mean_beta_{c}"
        cap = gate.get(cap_key, 0.80)
        if abs(b) >= float(cap):
            fail.append(f"|β_{c}| {abs(b):.3f} ≥ {cap} (stealth factor)")

    metrics = {
        "years": years,
        "n_days": n_days,
        "clean_ir": ir,
        "placebo_ir": p_ir,
        "placebo_metric": "mean_abs_sign_randomized_ir",
        "placebo_frac_of_observed": placebo_frac,
        "placebo_null_abs_ir_floor": null_floor,
        "mean_betas": mean_betas,
        "hedge_weights_last": panel.latest_hedge_weights,
        "raw_basket_ir_diagnostic_only": annualized_ir(panel.basket),
    }
    verdict = "PROMOTE_CANDIDATE" if not fail else "FAIL_GATE"
    return GateResult(verdict=verdict, metrics=metrics, failures=fail)
