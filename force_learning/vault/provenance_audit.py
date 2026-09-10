"""Provenance/independence only. No panel. No lag. No seed."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

PATH = Path(__file__).resolve().parents[2] / "force_ideas" / "inventory" / "provenance_audit.yaml"


class ProvenanceError(RuntimeError):
    pass


def load() -> Dict[str, Any]:
    return yaml.safe_load(PATH.read_text()) or {}


def assert_provenance() -> Dict[str, Any]:
    spec = load()
    if spec.get("extracted_panel") is True or spec.get("lag_test") is True:
        raise ProvenanceError("provenance is not a panel or lag test")
    if spec.get("seed") is True or spec.get("t0") is True:
        raise ProvenanceError("provenance is not a seed")
    if spec.get("mechanism_audit") == "authorized":
        raise ProvenanceError("mechanism audit is not authorized")
    if spec.get("electricity_reopened") is True:
        raise ProvenanceError("electricity stays closed")
    by = {c["id"]: c for c in spec.get("candidates") or []}
    nbi = by["OA-NBI-CONDITION"]
    if nbi.get("status") == "QUALIFIES_FOR_DEEPER_AUDIT":
        raise ProvenanceError("NBI is PARTIAL; same-file Item 106")
    if nbi.get("independence", {}).get("not_PASS") is not True:
        raise ProvenanceError("NBI independence is not PASS")
    if "Item_106_year_reconstructed" != nbi["clocks"]["transition"]["field"]:
        raise ProvenanceError("NBI transition is Item 106")
    if "sufficiency_rating" not in (nbi.get("forbidden_precursors") or []):
        raise ProvenanceError("sufficiency rating is a formula, not a condition")
    soc = by["OA-SOC-PIPELINE"]
    if soc.get("architecture_class") != "PROJECT_DURATION":
        raise ProvenanceError("SOC starts→completions is project duration")
    if soc.get("independence", {}).get("precursor_vs_transition") != "SAME_SURVEY_TWO_DATE_FIELDS":
        raise ProvenanceError("SOC is one survey")
    lpms = by["OA-LPMS-LOCK"]
    if lpms.get("verdict") != "INSUFFICIENT_TO_JUDGE":
        raise ProvenanceError("LPMS rehab clock is unverified")
    if "usgs_ore_grade_to_expansion_as_qualifies" not in (spec.get("refused") or []):
        raise ProvenanceError("USGS grade QUALIFIES is refused")
    return spec
