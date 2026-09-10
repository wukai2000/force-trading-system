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
        raise ProvenanceError("NBI is PARTIAL; Type B not Type A")
    if nbi.get("same_file_equals_one_act") is not False:
        raise ProvenanceError("same NBI tape is not one collection act")
    if nbi.get("independent_measurement_streams") != "not_established":
        raise ProvenanceError("NBI streams are not established")
    if nbi.get("independence", {}).get("I5_system") != "TYPE_B":
        raise ProvenanceError("NBI is Type B")
    if nbi.get("next_authorized_this_cycle") is True:
        raise ProvenanceError("state DOT hunt is not this cycle")
    if "item_106_as_clean_replacement" not in (nbi.get("forbidden_transition") or []):
        raise ProvenanceError("Item 106 is not a replacement clock")

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
    if "ADT_as_condition" not in (nbi.get("forbidden_precursors") or []):
        raise ProvenanceError("ADT is demand, not condition")
    if "faa_sdr_as_qualifies" not in (spec.get("refused") or []):
        raise ProvenanceError("FAA SDR QUALIFIES is refused")
    if "memo2_yes_on_nbi" not in (spec.get("refused") or []):
        raise ProvenanceError("memo-2 YES on NBI is refused")

    return spec
