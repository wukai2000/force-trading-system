"""
Force definition and suggestion primitives.

A Force is a persistent structural driver.
Its "signature" is the filter/transformation that makes the force visible
in historical data for pattern recognition.
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


@dataclass
class Force:
    """Minimal force definition."""

    id: str
    name: str
    one_sentence: str
    status: ForceStatus = ForceStatus.CANDIDATE
    # Signature = the filter / transformation that surfaces the pattern
    signature_notes: str = ""
    # Free-form metadata (transmission channels, related assets, etc.)
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "one_sentence": self.one_sentence,
            "status": self.status.value,
            "signature_notes": self.signature_notes,
            "meta": self.meta,
        }


@dataclass
class ForceSuggestion:
    """Output of the force engine for one force at one point in time."""

    force_id: str
    force_name: str
    # Directional intensity: positive = force supportive of risk assets / theme,
    # negative = headwind. Scale is arbitrary for now (later calibrated).
    intensity: float
    confidence: float  # 0–1
    rationale: str
    timestamp: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "force_id": self.force_id,
            "force_name": self.force_name,
            "intensity": self.intensity,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "timestamp": self.timestamp,
            "raw": self.raw,
        }
