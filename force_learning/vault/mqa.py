"""Minimum Qualifying Architecture. All ten PASS. UNKNOWN is not PASS."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

PATH = Path(__file__).resolve().parents[2] / "force_ideas" / "inventory" / "mqa.yaml"
GATES = [
    "G1",
    "G2",
    "G3",
    "G4",
    "G5",
    "G6",
    "G7",
    "G8",
    "G9",
    "G10",
]


class MqaError(RuntimeError):
    pass


def load() -> Dict[str, Any]:
    return yaml.safe_load(PATH.read_text()) or {}


def _grade(scores: Dict[str, Any], gate: str) -> str:
    for k, v in scores.items():
        if k == gate or str(k).startswith(gate + "_"):
            return str(v)
    return "UNKNOWN"


def evaluate(candidate_id: str, spec: Dict[str, Any] | None = None) -> Dict[str, Any]:
    spec = spec or load()
    scores = (spec.get("scores") or {}).get(candidate_id) or {}
    grades = {g: _grade(scores, g) for g in GATES}
    promising = all(grades[g] == "PASS" for g in GATES)
    return {
        "id": candidate_id,
        "grades": grades,
        "promising": promising,
        "fail_note": scores.get("fail_note"),
    }


def report(spec: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    spec = spec or load()
    return [evaluate(cid, spec) for cid in (spec.get("scores") or {})]


def assert_mqa() -> Dict[str, Any]:
    spec = load()
    if spec.get("research_status") != "FORMALIZE":
        raise MqaError("status is FORMALIZE")
    if spec.get("domain_shopping") != "closed":
        raise MqaError("domain shopping is closed")
    if spec.get("landing_page_is_not_evidence") is not True:
        raise MqaError("landing pages are not evidence")
    if spec.get("unknown_is_not_pass") is not True:
        raise MqaError("UNKNOWN is not PASS")
    if spec.get("mostly_qualifies_forbidden") is not True:
        raise MqaError("mostly-qualifies is forbidden")
    if spec.get("promising_rule") != "all_ten_pass":
        raise MqaError("promising requires all ten PASS")
    if spec.get("qualified_architectures") != 0:
        raise MqaError("qualified_architectures is 0")

    if spec.get("cryptographic_immutability_not_required") is not True:
        raise MqaError("crypto is not a hard gate")
    if spec.get("wayback_tooling_this_cycle") is not False:
        raise MqaError("wayback scraper is not this cycle")
    if spec.get("edgar_as_trigger") != "refused":
        raise MqaError("EDGAR is not a physical archive")
    if spec.get("search_unit") != "institutional_measurement_architecture":
        raise MqaError("search unit is institutional architecture")
    refused = spec.get("refused") or []
    for tok in (
        "ten_more_domain_probes",
        "crypto_as_hard_gate",
        "eight_gate_collapse",
        "nbi_reopen",
        "fs0002",
        "promising_without_ten_pass",
        "sec_edgar_as_physical_archive",
    ):
        if tok not in refused:
            raise MqaError(f"missing refuse: {tok}")
    rows = report(spec)
    if not rows:
        raise MqaError("six-probe scores missing")
    if any(r["promising"] for r in rows):
        raise MqaError("no architecture is 10/10 PASS")
    if any(g not in ("PASS", "FAIL", "UNKNOWN") for r in rows for g in r["grades"].values()):
        raise MqaError("grades must be PASS/FAIL/UNKNOWN")
    return spec
