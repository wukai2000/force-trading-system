"""Observable-pair census. Inventory only. No freeze. No attractiveness ranking."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from force_ideas.state import active_frozen_forces, fs0001_desk

PATH = Path(__file__).resolve().parents[2] / "force_ideas" / "inventory" / "observable_pairs.yaml"


class PairCensusError(RuntimeError):
    pass


def load() -> Dict[str, Any]:
    return yaml.safe_load(PATH.read_text()) or {}


def assert_census() -> Dict[str, Any]:
    spec = load()
    if spec.get("cannot_promote") is not True or spec.get("admitted_as_seeds") is not False:
        raise PairCensusError("census is not a seed dump")
    if int(spec.get("capital") or 0) != 0:
        raise PairCensusError("capital must be 0")
    if spec.get("attractiveness_rank_refused") is not True:
        raise PairCensusError("attractiveness ranking must be refused")
    if spec.get("iea_cube_not_a_census_source") is not True:
        raise PairCensusError("IEA cube is not a census source this run")
    if spec.get("no_a_or_b_without_extract") is not True:
        raise PairCensusError("A/B grades require an official extract")
    pairs = spec.get("pairs") or []

    by_id = {p["id"]: p for p in pairs}
    freight = by_id["OP-01"]
    if freight.get("abandoned") is True:
        raise PairCensusError("do not abandon road freight because of 403")
    if freight.get("grade") not in ("X", "OPEN", "D"):
        raise PairCensusError("IEA freight is not A/B without the cube")
    for p in pairs:
        if p.get("grade") in ("A", "B") and p.get("historical_coverage") in (
            "cube_not_obtained",
            "not_extracted",
        ):
            raise PairCensusError(f"{p['id']} cannot be A/B without extract")
        if p.get("excellent") is True:
            raise PairCensusError(f"{p['id']} attractiveness ranking refused")
    if by_id["OP-08"].get("grade") != "REJECT":
        raise PairCensusError("data/comms stays REJECT")
    if by_id["OP-06"].get("mix_contamination") is not True:
        raise PairCensusError("electricity mix contamination must be flagged")
    refused = spec.get("refused") or []
    for tok in (
        "ranking_by_economic_attractiveness",
        "silent_v2_domain_swap",
        "abandoning_freight_because_403",
        "new_frozen_id",
    ):
        if tok not in refused:
            raise PairCensusError(f"missing refuse: {tok}")
    if active_frozen_forces() != ["FS-0001"]:
        raise PairCensusError("frozen slot unchanged")
    desk = fs0001_desk()
    if desk.get("t5_status") != "NO_RESULT" or desk.get("t5_ready") is True:
        raise PairCensusError("census cannot reopen T5")
    return spec
