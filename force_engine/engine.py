"""
Learned Force Engine (bare minimum).

Takes market/context input + registered forces + their signatures
and produces ForceSuggestion objects.

Later this will incorporate historical signature discovery,
residualization, and more sophisticated scoring.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .base import Force, ForceStatus, ForceSuggestion


# Hard-coded candidate forces (later loaded from Notion / config)
DEFAULT_FORCES: List[Force] = [
    Force(
        id="us_structural_advantages",
        name="US Structural Advantages (USD + Tech + Military)",
        one_sentence=(
            "The United States retains a durable structural edge over other large "
            "economies through the combination of dollar reserve status, technological "
            "leadership, and military primacy; this edge supports relative outperformance "
            "of US assets across both boom and recession regimes."
        ),
        status=ForceStatus.CANDIDATE,
        signature_notes=(
            "Relative US equity performance vs developed peers across regimes; "
            "interaction of DXY, tech relative strength, and defense/geopolitical stability."
        ),
        meta={
            "order": 1,
            "related": ["SPY", "QQQ", "DXY", "ITA", "EFA"],
        },
    ),
    Force(
        id="energy_ai_synergy",
        name="Energy × AI Computation/Communication Synergy",
        one_sentence=(
            "The intensifying coupling between energy supply and AI-driven computation/"
            "communication creates a durable demand and pricing-power dynamic stronger "
            "than either energy or AI considered in isolation."
        ),
        status=ForceStatus.CANDIDATE,
        signature_notes=(
            "Divergence of AI-related power demand vs traditional industrial demand; "
            "relative performance of AI-power names during AI investment accelerations."
        ),
        meta={"order": 2},
    ),
    Force(
        id="longevity_health_desire",
        name="Longevity / Health Desire",
        one_sentence=(
            "Persistent human desire for extended healthy lifespan creates a structural "
            "demand force for longevity and health industries that is only partially "
            "dependent on technological breakthroughs."
        ),
        status=ForceStatus.CANDIDATE,
        signature_notes=(
            "Demographic + cultural attention metrics vs pure R&D success; "
            "relative performance of demand-side health names during biotech disappointment periods."
        ),
        meta={"order": 3},
    ),
]


class ForceEngine:
    """Minimal force engine."""

    def __init__(self, forces: Optional[List[Force]] = None):
        self.forces = forces or list(DEFAULT_FORCES)

    def list_forces(self) -> List[Force]:
        return list(self.forces)

    def suggest(
        self,
        market_context: Optional[Dict[str, Any]] = None,
        as_of: Optional[datetime] = None,
    ) -> List[ForceSuggestion]:
        """
        Produce suggestions for all registered forces.

        Currently returns placeholder neutral suggestions.
        Real implementation will apply each force's signature to data
        and score intensity / confidence.
        """
        as_of = as_of or datetime.now(timezone.utc)
        ts = as_of.isoformat()
        context = market_context or {}

        suggestions: List[ForceSuggestion] = []
        for force in self.forces:
            # Placeholder logic — replace with signature-driven scoring
            intensity = 0.0
            confidence = 0.1
            rationale = (
                f"Placeholder: no historical signature applied yet for '{force.name}'. "
                f"Context keys present: {list(context.keys()) or 'none'}."
            )
            suggestions.append(
                ForceSuggestion(
                    force_id=force.id,
                    force_name=force.name,
                    intensity=intensity,
                    confidence=confidence,
                    rationale=rationale,
                    timestamp=ts,
                    raw={"status": force.status.value},
                )
            )
        return suggestions


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Force Engine demo")
    parser.add_argument("--demo", action="store_true", help="Run demo suggestions")
    args = parser.parse_args()

    engine = ForceEngine()
    if args.demo:
        print("Registered forces:")
        for f in engine.list_forces():
            print(f"  [{f.meta.get('order', '?')}] {f.name} ({f.status.value})")
        print("\nSuggestions:")
        for s in engine.suggest():
            print(json.dumps(s.to_dict(), indent=2))


if __name__ == "__main__":
    main()
