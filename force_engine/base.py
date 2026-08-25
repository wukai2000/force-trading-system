"""
Force definition and suggestion primitives.

A Force is a persistent structural driver.
Its "signature" is the filter/transformation that makes the force visible
in historical data for pattern recognition.

After F1/F2: a force is only evaluable as a *neutralized residual spread*.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ForceStatus(str, Enum):
    CANDIDATE = "candidate"
    FORMALIZED = "formalized"
    HISTORICAL_SERIES = "historical_series"
    RESIDUALIZED = "residualized"
    PAPER = "paper"
    PAUSED = "paused"
    FALSIFIED = "falsified"


@dataclass
class Force:
    """Minimal force definition."""

    id: str
    name: str
    one_sentence: str
    status: ForceStatus = ForceStatus.CANDIDATE
    signature_notes: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)
    # After F1/F2 this defaults to residual spread; long-only is invalid for promotion.
    tradable: str = "residual_spread"
    legs: List[str] = field(default_factory=list)
    controls: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "one_sentence": self.one_sentence,
            "status": self.status.value,
            "signature_notes": self.signature_notes,
            "tradable": self.tradable,
            "legs": list(self.legs),
            "controls": list(self.controls),
            "meta": self.meta,
        }


@dataclass
class ForceSuggestion:
    """Output of the force engine for one force at one point in time."""

    force_id: str
    force_name: str
    intensity: float
    confidence: float
    rationale: str
    timestamp: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)
    # Hedge weights for the residual spread (control ticker -> weight to short)
    hedge_weights: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "force_id": self.force_id,
            "force_name": self.force_name,
            "intensity": self.intensity,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "timestamp": self.timestamp,
            "hedge_weights": self.hedge_weights,
            "raw": self.raw,
        }
