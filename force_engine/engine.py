"""
Force Engine.

After F1/F2: suggestions for a force with legs+controls are only emitted
from a neutralized residual. Paused/falsified forces emit intensity=0.
Long-only (empty controls) is rejected, not scored.
Raw prices never produce a score — a NeutralizedPanel is required.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .base import Force, ForceStatus, ForceSuggestion
from .clocks import default_clock_bus
from .evaluate import annualized_ir
from .loader import load_registered_forces
from .neutralize import NeutralizationError, NeutralizedPanel


class ForceEngine:
    def __init__(self, forces: Optional[List[Force]] = None):
        self.forces = forces if forces is not None else load_registered_forces()
        self.clocks = default_clock_bus()

    def list_forces(self) -> List[Force]:
        return list(self.forces)

    def suggest(
        self,
        market_context: Optional[Dict[str, Any]] = None,
        as_of: Optional[datetime] = None,
        neutralized_panels: Optional[Dict[str, NeutralizedPanel]] = None,
    ) -> List[ForceSuggestion]:
        as_of = as_of or datetime.now(timezone.utc)
        ts = as_of.isoformat()
        context = market_context or {}
        panels = neutralized_panels or {}
        suggestions: List[ForceSuggestion] = []

        for force in self.forces:
            if force.status in (ForceStatus.PAUSED, ForceStatus.FALSIFIED):
                suggestions.append(
                    ForceSuggestion(
                        force_id=force.id,
                        force_name=force.name,
                        intensity=0.0,
                        confidence=1.0,
                        rationale=f"Force '{force.name}' is {force.status.value}; no trade.",
                        timestamp=ts,
                        raw={"status": force.status.value, "tradable": force.tradable},
                    )
                )
                continue

            if not force.controls:
                suggestions.append(
                    ForceSuggestion(
                        force_id=force.id,
                        force_name=force.name,
                        intensity=0.0,
                        confidence=0.0,
                        rationale=(
                            f"Rejected: '{force.name}' has no controls. "
                            "Raw long-only baskets are not candidates (F1/F2)."
                        ),
                        timestamp=ts,
                        raw={"status": force.status.value, "error": "no_controls"},
                    )
                )
                continue

            panel = panels.get(force.id)
            if panel is None:
                suggestions.append(
                    ForceSuggestion(
                        force_id=force.id,
                        force_name=force.name,
                        intensity=0.0,
                        confidence=0.1,
                        rationale=(
                            f"No neutralized panel supplied for '{force.name}'. "
                            "Engine will not infer a raw-price score."
                        ),
                        timestamp=ts,
                        raw={"status": force.status.value, "awaiting": "neutralized_panel"},
                    )
                )
                continue

            try:
                ir = annualized_ir(panel.residual)
                last = float(panel.residual.dropna().iloc[-1]) if not panel.residual.dropna().empty else 0.0
                clock = self.clocks.read(residual_last=last)
                clock = self.clocks.veto_if_leading_contradicts(clock, ir if ir == ir else 0.0)
                intensity = float(panel.residual.dropna().iloc[-20:].mean() * 252) if len(panel.residual.dropna()) >= 20 else 0.0
                if clock.veto:
                    intensity = 0.0
                suggestions.append(
                    ForceSuggestion(
                        force_id=force.id,
                        force_name=force.name,
                        intensity=intensity,
                        confidence=0.4,
                        rationale=(
                            f"Residual spread vs {force.controls}. last IR(full)={ir:.3f}. "
                            + (f"VETO: {clock.veto_reason}" if clock.veto else "No leading-clock veto.")
                        ),
                        timestamp=ts,
                        hedge_weights=panel.latest_hedge_weights,
                        raw={
                            "status": force.status.value,
                            "tradable": "residual_spread",
                            "legs": force.legs,
                            "controls": force.controls,
                            "clean_ir": ir,
                            "clock_leading": clock.leading,
                            "veto": clock.veto,
                            "context_keys": list(context.keys()),
                        },
                    )
                )
            except NeutralizationError as e:
                suggestions.append(
                    ForceSuggestion(
                        force_id=force.id,
                        force_name=force.name,
                        intensity=0.0,
                        confidence=0.0,
                        rationale=str(e),
                        timestamp=ts,
                        raw={"error": "neutralization"},
                    )
                )
        return suggestions


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Force Engine")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    engine = ForceEngine()
    if args.demo:
        print("Registered forces:")
        for f in engine.list_forces():
            print(f"  {f.id:28s} {f.status.value:18s} legs={f.legs} ctrls={f.controls}")
        print("\nSuggestions (no panels → no raw scores):")
        for s in engine.suggest():
            print(json.dumps(s.to_dict(), indent=2)[:800])
            print("---")


if __name__ == "__main__":
    main()
