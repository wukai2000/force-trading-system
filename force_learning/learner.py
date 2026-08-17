"""
Force Learning component.

Responsibilities:
- Ingest Grok discussions / observations
- Design and run experiments (historical tests, residualization)
- Formulate or refine forces and their signatures
- Continuously improve and push updates into the force_engine

This is the home of the observation → claims → laws cycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from force_engine.base import Force, ForceStatus
from force_engine.engine import ForceEngine, DEFAULT_FORCES


@dataclass
class ExperimentResult:
    experiment_id: str
    force_id: str
    description: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "force_id": self.force_id,
            "description": self.description,
            "metrics": self.metrics,
            "notes": self.notes,
            "timestamp": self.timestamp,
        }


class ForceLearner:
    """
    Minimal learner that can:
    - hold a working set of forces
    - accept new observations / claims from Grok discussions
    - record experiment results
    - feed an updated ForceEngine
    """

    def __init__(self, initial_forces: Optional[List[Force]] = None):
        self.forces: List[Force] = list(initial_forces or DEFAULT_FORCES)
        self.observations: List[Dict[str, Any]] = []
        self.experiments: List[ExperimentResult] = []
        self._exp_counter = 0

    def ingest_observation(self, source: str, content: str, meta: Optional[Dict] = None):
        """Record a Grok discussion snippet or external observation."""
        self.observations.append(
            {
                "source": source,
                "content": content,
                "meta": meta or {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def record_experiment(
        self,
        force_id: str,
        description: str,
        metrics: Optional[Dict[str, Any]] = None,
        notes: str = "",
    ) -> ExperimentResult:
        self._exp_counter += 1
        result = ExperimentResult(
            experiment_id=f"exp-{self._exp_counter:04d}",
            force_id=force_id,
            description=description,
            metrics=metrics or {},
            notes=notes,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.experiments.append(result)
        return result

    def update_force_status(self, force_id: str, status: ForceStatus):
        for f in self.forces:
            if f.id == force_id:
                f.status = status
                return True
        return False

    def update_signature_notes(self, force_id: str, notes: str):
        for f in self.forces:
            if f.id == force_id:
                f.signature_notes = notes
                return True
        return False

    def get_force_engine(self) -> ForceEngine:
        """Produce a ForceEngine seeded with the current learned forces."""
        return ForceEngine(forces=self.forces)

    def summary(self) -> Dict[str, Any]:
        return {
            "n_forces": len(self.forces),
            "n_observations": len(self.observations),
            "n_experiments": len(self.experiments),
            "forces": [f.to_dict() for f in self.forces],
        }


def main():
    import json

    learner = ForceLearner()
    learner.ingest_observation(
        source="grok_conversation",
        content="US structural advantages (USD + tech + military) appear resilient across regimes.",
    )
    print(json.dumps(learner.summary(), indent=2))


if __name__ == "__main__":
    main()
