"""Epistemic governor. Standards do not move. Lessons must be class-level."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from aetl.ledger import SearchLedger

STATUSES = frozenset({"OBSERVED", "DERIVED", "DISCOVERED", "STATISTICALLY_SUPPORTED", "REPLICATED", "INTERPRETED", "MECHANISTICALLY_SUPPORTED", "REFUTED", "UNRESOLVED", "NO_RESULT", "REFUSED"})
RESERVED = frozenset({"FORCE_CANDIDATE", "FINANCIAL_TRANSMISSION_HYPOTHESIS"})
ALLOWED_TRANSITIONS = {
    None: {"DISCOVERED", "OBSERVED", "DERIVED", "NO_RESULT", "REFUSED"},
    "OBSERVED": {"DERIVED", "DISCOVERED", "NO_RESULT"},
    "DERIVED": {"DISCOVERED", "NO_RESULT"},
    "DISCOVERED": {"STATISTICALLY_SUPPORTED", "REFUTED", "UNRESOLVED", "NO_RESULT"},
    "STATISTICALLY_SUPPORTED": {"REPLICATED", "REFUTED", "UNRESOLVED", "INTERPRETED"},
    "REPLICATED": {"INTERPRETED", "UNRESOLVED", "REFUTED"},
    "INTERPRETED": {"MECHANISTICALLY_SUPPORTED", "UNRESOLVED", "REFUTED"},
    "MECHANISTICALLY_SUPPORTED": {"UNRESOLVED", "REFUTED"},
    "REFUTED": set(),
    "NO_RESULT": set(),
    "UNRESOLVED": {"REFUTED", "NO_RESULT"},
    "REFUSED": set(),
}
CERTIFIER_ONLY = frozenset({"STATISTICALLY_SUPPORTED", "REPLICATED", "REFUTED", "NO_RESULT"})
CHASING = re.compile(r"(threshold|window|lag|c\s*=|0\.\d{2}|try\s+\d|tighten|raise|lower).{0,40}(\d)", re.I)


@dataclass
class Candidate:
    candidate_id: str
    representation: dict
    grammar: dict
    claim_class: str
    lineage: list
    status: Optional[str] = None
    partition_used: list = field(default_factory=list)
    hindsight: bool = False


class GovernorError(RuntimeError):
    pass


class Governor:
    def __init__(self, ledger: SearchLedger, phase: str = "E0") -> None:
        self.ledger = ledger
        self.phase = phase
        self.certifier_battery_version = "BATTERY-E0-v1"
        self.hidden_cert_touched: set[str] = set()

    def refuse_reserved(self, status: str) -> None:
        if status in RESERVED or status.startswith("FORCE"):
            raise GovernorError(f"reserved status refused in phase {self.phase}: {status}")

    def set_status(self, cand: Candidate, new: str, actor: str) -> None:
        self.refuse_reserved(new)
        if new not in STATUSES:
            raise GovernorError(f"unknown status {new}")
        allowed = ALLOWED_TRANSITIONS.get(cand.status, set())
        if new not in allowed:
            raise GovernorError(f"illegal {cand.status} -> {new}")
        if new in CERTIFIER_ONLY and actor != "CERTIFIER":
            raise GovernorError(f"{actor} may not stamp {new}")
        if cand.hindsight and new == "STATISTICALLY_SUPPORTED":
            raise GovernorError("hindsight object cannot become STATISTICALLY_SUPPORTED")
        cand.status = new
        self.ledger.append(
            actor=actor,
            action="STATUS",
            candidate_id=cand.candidate_id,
            partition="CERTIFY" if actor == "CERTIFIER" else "LAB",
            outcome_summary=new,
            reason="governor_transition",
        )

    def check_lesson(self, text: str) -> str:
        if CHASING.search(text or ""):
            self.ledger.append(actor="GOVERNOR", action="REFUSE", reason="candidate_chasing_lesson", outcome_summary=(text or "")[:120])
            raise GovernorError("lesson encodes candidate-specific optimization")
        return text

    def touch_cert(self, candidate_id: str) -> None:
        if candidate_id in self.hidden_cert_touched:
            raise GovernorError("certification partition already touched")
        self.hidden_cert_touched.add(candidate_id)

    def may_open_historical(self, lab_report: dict) -> bool:
        return False
