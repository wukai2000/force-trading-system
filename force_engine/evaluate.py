"""
Candidate evaluation — residual series only.

Promotion metrics are computed exclusively on a NeutralizedPanel.
Raw excess vs SPY/VOO is attached only under diagnostic keys and cannot pass a gate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

import numpy as np
import pandas as pd

from .neutralize import NeutralizationError, NeutralizedPanel


def annualized_ir(resid: pd.Series, periods_per_year: int = 252) -> float:
    s = resid.dropna()
    if len(s) < 60 or float(s.std()) == 0:
        return float("nan")
    return float(s.mean() / s.std() * np.sqrt(periods_per_year))


def sign_placebo_ir(resid: pd.Series, n: int = 50, seed: int = 24) -> float:
    rng = np.random.default_rng(seed)
    vals = resid.dropna().values
    if len(vals) < 60:
        return float("nan")
    irs = []
    for _ in range(n):
        signs = rng.choice(np.array([-1.0, 1.0]), size=len(vals))
        irs.append(annualized_ir(pd.Series(vals * signs)))
    return float(np.nanmean(irs))


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
    mean_betas = {
        c: float(panel.betas[f"beta_{c}"].mean())
        for c in panel.controls
        if f"beta_{c}" in panel.betas.columns
    }

    min_ir = float(gate.get("min_clean_ir", 0.40))
    max_p = float(gate.get("max_placebo_ir", 0.15))
    min_years = float(gate.get("min_overlap_years", 8))
    fail: List[str] = []
    if years < min_years:
        fail.append(f"overlap {years:.1f}y < {min_years}y")
    if not (ir >= min_ir):
        fail.append(f"IR {ir:.3f} < {min_ir}")
    if not (p_ir < max_p):
        fail.append(f"placebo IR {p_ir:.3f} ≥ {max_p}")
    for c, b in mean_betas.items():
        cap_key = f"max_abs_mean_beta_{c}"
        cap = gate.get(cap_key, 0.80)
        if abs(b) >= float(cap):
            fail.append(f"|β_{c}| {abs(b):.3f} ≥ {cap} (stealth factor)")

    metrics = {
        "years": years,
        "n_days": int(len(resid)),
        "clean_ir": ir,
        "placebo_ir": p_ir,
        "mean_betas": mean_betas,
        "hedge_weights_last": panel.latest_hedge_weights,
        "raw_basket_ir_diagnostic_only": annualized_ir(panel.basket),
    }
    verdict = "PROMOTE_CANDIDATE" if not fail else "FAIL_GATE"
    return GateResult(verdict=verdict, metrics=metrics, failures=fail)
