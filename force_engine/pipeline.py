"""
Single evaluation entry for a force candidate.

Neutralization runs *before* any IR / gate / suggestion. Callers that skip
this module and hand a raw basket to evaluate.py will still be refused by
the neutralized=True tripwire; this module is the supported path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

import pandas as pd
import yaml

from .clocks import ClockBus, ClockState, default_clock_bus
from .evaluate import GateResult, annualized_ir, evaluate_neutralized
from .freeze import FrozenHypothesis, refuse_evaluate_unfrozen
from .neutralize import NeutralizationError, NeutralizedPanel, neutralize_prices


@dataclass
class CandidateSpec:
    force_id: str
    legs: List[str]
    controls: List[str]
    gate: Mapping[str, Any]
    tradable: str = "residual_spread"
    lookback: int = 60
    leading_clocks: List[str] = field(default_factory=list)


@dataclass
class PipelineResult:
    spec: CandidateSpec
    panel: NeutralizedPanel
    gate: GateResult
    clock: ClockState
    diagnostic: Dict[str, Any]


def spec_from_yaml(path: Path) -> CandidateSpec:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    tg = raw.get("ticket_group") or {}
    clocks = raw.get("clocks") or {}
    panel = raw.get("panel") or {}
    return CandidateSpec(
        force_id=str(raw.get("force_id") or path.stem),
        legs=list(tg.get("legs") or []),
        controls=list(tg.get("controls") or []),
        gate=raw.get("gate") or {},
        tradable=str(raw.get("tradable") or "residual_spread"),
        lookback=int(panel.get("ols_lookback_days") or 60),
        leading_clocks=list(clocks.get("leading") or []),
    )


def evaluate_candidate(
    spec: CandidateSpec,
    prices: pd.DataFrame,
    clock_bus: Optional[ClockBus] = None,
    *,
    freeze: Optional[FrozenHypothesis] = None,
    allow_unfrozen: bool = False,
    allow_wait_sketch: bool = False,
) -> PipelineResult:
    """
    Neutralize first, then gate, then leading-clock veto.

    A leading clock may downgrade PROMOTE_CANDIDATE → VETO_LEADING_CLOCK.
    It cannot upgrade FAIL_GATE.

    New (non-grandfathered) force_ids require a complete T0–T4 freeze
    with T5 instruments attached. Force 4 / WAIT tickers stay refused.
    """
    if spec.tradable != "residual_spread":
        raise NeutralizationError(
            f"refusing tradable={spec.tradable!r}; only residual_spread is evaluable"
        )
    if not spec.controls:
        raise NeutralizationError("refusing to score a basket with empty controls")
    if not spec.legs:
        raise NeutralizationError("refusing a candidate with empty legs")
    refuse_evaluate_unfrozen(
        spec.force_id,
        list(spec.legs) + list(spec.controls),
        freeze=freeze,
        allow_unfrozen=allow_unfrozen,
        allow_wait_sketch=allow_wait_sketch,
    )

    panel = neutralize_prices(prices, spec.legs, spec.controls, lookback=spec.lookback)
    gate = evaluate_neutralized(panel, spec.gate, neutralized=True)

    bus = clock_bus or default_clock_bus()
    last = float(panel.residual.dropna().iloc[-1]) if not panel.residual.dropna().empty else 0.0
    ir = float(gate.metrics.get("clean_ir") or annualized_ir(panel.residual))
    clock = bus.read(residual_last=last)
    clock = bus.veto_if_leading_contradicts(clock, ir)

    if clock.veto and gate.verdict == "PROMOTE_CANDIDATE":
        gate.verdict = "VETO_LEADING_CLOCK"
        gate.failures.append(clock.veto_reason)

    diagnostic = {
        "raw_basket_ir": gate.metrics.get("raw_basket_ir_diagnostic_only"),
        "legs": list(spec.legs),
        "controls": list(spec.controls),
        "leading_clocks": list(spec.leading_clocks),
        "note": "raw_basket_ir is diagnostic only and cannot pass a gate",
    }
    return PipelineResult(spec=spec, panel=panel, gate=gate, clock=clock, diagnostic=diagnostic)
