"""Survey engine for physical state → physical transition.

Tests SHAPE only. Does not freeze, lag-test, residualize, or admit seeds.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

PATH = Path(__file__).resolve().parents[2] / "force_ideas" / "inventory" / "physical_survey.yaml"

TERMINAL = {
    "SHAPE_INTERESTING",
    "PARTIAL",
    "WEAK",
    "PARKED",
    "DISMISSED_AS_DAM_CONDITION",
    "REJECTED",
}
FORBIDDEN_STATUS = {"QUALIFIES_FOR_DEEPER_AUDIT", "PROMISING_FOR_FORENSIC_AUDIT", "YES"}


class SurveyError(RuntimeError):
    pass


def load() -> Dict[str, Any]:
    return yaml.safe_load(PATH.read_text()) or {}


def survey(spec: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    spec = spec or load()
    rows = []
    for c in spec.get("candidates") or []:
        rows.append(
            {
                "id": c["id"],
                "status": c.get("status"),
                "qualifies": bool(c.get("qualifies")),
                "seed": bool(c.get("seed")),
                "audit_authorized": bool(c.get("audit_authorized")),
                "precursor": c.get("precursor") or c.get("reason"),
                "transition": c.get("transition"),
            }
        )
    return rows


def assert_survey() -> Dict[str, Any]:
    spec = load()
    if spec.get("seed") is True or spec.get("t0") is True:
        raise SurveyError("survey is not a seed")
    if int(spec.get("n_seeds") or 0) != 0:
        raise SurveyError("n_seeds must be 0")
    if spec.get("audit_authorized") is True:
        raise SurveyError("no survey audit is authorized")
    if spec.get("next_authorized_this_cycle") is True:
        raise SurveyError("next domain audit is not this cycle")
    if spec.get("lag_test") is True or spec.get("extracted_panel") is True:
        raise SurveyError("survey is not a lag or panel")
    if spec.get("winner") not in (None, "none"):
        raise SurveyError("survey has no winner")
    if spec.get("ranking_refused") is not True:
        raise SurveyError("ranking is refused")
    if spec.get("stop_further_domain_hunt") is not True:
        raise SurveyError("stop further domain hunt")
    refused = spec.get("refused") or []
    for tok in (
        "hours_cycles_to_retirement",
        "ten_promising_quota",
        "volcano_audit_this_cycle",
        "streamflow_dam_as_next",
        "attractiveness_rank",
        "fia_disturbance_code_as_event",
        "port_insar_to_municipal_contract",
        "grace_to_well_collapse_spatial",
    ):
        if tok not in refused:
            raise SurveyError(f"missing refuse: {tok}")
    by = {c["id"]: c for c in spec.get("candidates") or []}
    volc = by["OA-VOLCANO-ERUPTION"]
    if volc.get("status") != "SHAPE_INTERESTING" or volc.get("audit_authorized") is True:
        raise SurveyError("volcano is shape only; audit not authorized")
    if volc.get("qualifies") is True or volc.get("seed") is True:
        raise SurveyError("volcano is not a QUALIFIES or seed")
    if volc.get("frozen_vintage") != "REQUIRED_not_current_catalog":
        raise SurveyError("volcano requires frozen catalogs")
    fire = by["OA-FIA-MTBS-FIRE"]
    if fire.get("collapse_if") != "fia_own_fire_indicator_used_as_event":
        raise SurveyError("FIA disturbance code is not the fire event")
    dam = by["OA-STREAMFLOW-DAM"]
    if dam.get("status") != "DISMISSED_AS_DAM_CONDITION":
        raise SurveyError("streamflow is load, not dam fabric")
    for c in spec.get("candidates") or []:
        if c.get("status") in FORBIDDEN_STATUS:
            raise SurveyError(f"{c['id']} promoted")
        if c.get("qualifies") is True or c.get("seed") is True:
            raise SurveyError(f"{c['id']} admitted")
        if c.get("status") not in TERMINAL:
            raise SurveyError(f"{c['id']} unknown status {c.get('status')}")
    if "OA-AIRCRAFT-SDR" not in by or by["OA-AIRCRAFT-SDR"].get("status") != "PARTIAL":
        raise SurveyError("aircraft SDR is PARTIAL")
    if by["OA-DAM-SURVEILLANCE"].get("status") != "PARTIAL":
        raise SurveyError("dam surveillance is PARTIAL; NID is stock")
    if by["OA-VESSEL-PSIX"].get("status") != "PARTIAL":
        raise SurveyError("vessel PSIX is PARTIAL")
    cohort = spec.get("probe_cohort_6") or []
    if cohort != [
        "OA-VOLCANO-ERUPTION",
        "OA-FRA-ATIP",
        "OA-AIRCRAFT-SDR",
        "OA-LANDSLIDE-GEODETIC",
        "OA-DAM-SURVEILLANCE",
        "OA-VESSEL-PSIX",
    ]:
        raise SurveyError("probe cohort must be the six, not a ranking")
    if spec.get("probe_kind") != "landing_page_existence":
        raise SurveyError("probe is landing-page existence only")
    findings = (spec.get("last_probe") or {}).get("findings") or {}
    if (findings.get("OA-FRA-ATIP") or {}).get("precursor") != "ATIP_raw_not_public":
        raise SurveyError("ATIP raw geometry is not a public tape")
    if (findings.get("OA-DAM-SURVEILLANCE") or {}).get("precursor") != "NID_is_STOCK_inventory":
        raise SurveyError("NID is stock, not dam instrumentation")
    if (findings.get("OA-VOLCANO-ERUPTION") or {}).get("precursor") != "LIVE_USGS_API_not_frozen_vintage":
        raise SurveyError("volcano API is live, not a frozen vintage")
    return spec


