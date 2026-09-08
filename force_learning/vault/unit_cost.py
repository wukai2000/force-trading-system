"""Unit-cost audit lock. Cousins are not a T5 construction."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

AUDIT = Path(__file__).resolve().parent / "unit_cost_audit.yaml"

COUSIN_TOKENS = (
    "sbs",
    "sppi",
    "itic",
    "cif",
    "unctad",
    "bts",
    "ton-mile",
    "ton_mile",
    "cnr",
    "mitma",
    "cass",
    "drewry",
    "baltic dry",
    "bdi",
    "turnover",
    "revenue_over_tkm",
    "fuel_expenditure",
    "pur_meur",
    "v13110",
    "infrastructure investment",
    "infrastructure spend",
    "nama_10",
    "coicop",
    "cp07",
    "hicp",
    "cofog",
    "purchases of goods",
    "transport margin",
    "naio_10",
    "49.41",
    "nace 49.41",
    "hire-or-reward",
)




class UnitCostError(RuntimeError):
    pass


def load_audit() -> Dict[str, Any]:
    return yaml.safe_load(AUDIT.read_text()) or {}


def refuse_cousin(label: str) -> None:
    blob = str(label or "").lower()
    hits = [t for t in COUSIN_TOKENS if t in blob]
    if hits:
        raise UnitCostError(
            f"refused monetary cousin {label!r} ({hits}). "
            "NOT_CONSTRUCTIBLE_WITHOUT_DISCRETION. T5 stays NO_RESULT."
        )


def assert_not_constructible() -> Dict[str, Any]:
    spec = load_audit()
    if spec.get("verdict") != "NOT_CONSTRUCTIBLE_WITHOUT_DISCRETION":
        raise UnitCostError("unit-cost verdict mutated")
    if spec.get("t5_ready") is True or spec.get("t5_status") != "NO_RESULT":
        raise UnitCostError("unit-cost audit cannot set T5_READY")
    if spec.get("preregistered_construction_rule") not in (None, "none", ""):
        raise UnitCostError("no complete construction rule is permitted")
    if spec.get("joint_cost_tkm_coverage") != "empty":
        raise UnitCostError("joint cost/tkm coverage must stay empty")
    if spec.get("new_version_required") is True:
        raise UnitCostError("hypothesis is not the problem; do not require a new version")
    if int(spec.get("capital") or 0) != 0:
        raise UnitCostError("capital must be 0")
    if spec.get("oecd_eurostat_breakthrough") is True:
        raise UnitCostError("OECD/Eurostat is not a unit-cost breakthrough")
    if (spec.get("closest_failed_candidate") or {}).get("status") != "failed":
        raise UnitCostError("PUR_MEUR candidate must remain failed")
    if spec.get("independent_geography", {}).get("oecd_vs_eurostat_tkm") != "same_common_questionnaire":
        raise UnitCostError("OECD vs Eurostat tkm is the Common Questionnaire, not independence")
    if spec.get("national_accounts_breakthrough") is True:
        raise UnitCostError("national accounts are not a unit-cost breakthrough")
    if spec.get("measurement_dead_end") is True:
        raise UnitCostError("desk state is T5_NO_RESULT, not MEASUREMENT_DEAD_END")
    if spec.get("mapping_break") != "residence_vs_territoriality":
        raise UnitCostError("mapping break is residence vs territoriality")
    if spec.get("sppi_as_cost_deflator") != "identification_theatre":
        raise UnitCostError("deflating cost by SPPI is identification theatre")
    if spec.get("single_national_market_rescue") is True:
        raise UnitCostError("AU/NZ/DE single-market case studies do not satisfy frozen geography")
    return spec




def refused_ids() -> List[str]:
    return sorted((load_audit().get("refused_candidates") or {}).keys())
