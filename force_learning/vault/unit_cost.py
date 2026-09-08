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
    return spec


def refused_ids() -> List[str]:
    return sorted((load_audit().get("refused_candidates") or {}).keys())
