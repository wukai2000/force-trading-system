"""Unfrozen discovery is observatory only. No T0. No F2 rename. No lag peek."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from force_ideas.state import active_frozen_forces, fs0001_desk

PATH = Path(__file__).resolve().parents[2] / "force_ideas" / "inventory" / "unfrozen_discovery.yaml"
CLAIMED = Path(__file__).resolve().parents[2] / "force_ideas" / "inventory" / "claimed_series.yaml"
MISSION = Path(__file__).resolve().parents[2] / "force_ideas" / "inventory" / "explorer_mission.yaml"
CENSUS = Path(__file__).resolve().parents[2] / "force_ideas" / "inventory" / "architecture_census.yaml"








class UnfrozenError(RuntimeError):
    pass


def load() -> Dict[str, Any]:
    return yaml.safe_load(PATH.read_text()) or {}


def assert_unfrozen() -> Dict[str, Any]:
    spec = load()
    if spec.get("frozen") is True or spec.get("t0_issued") is True:
        raise UnfrozenError("discovery is not a freeze or T0")
    if spec.get("admitted_as_seeds") is not False:
        raise UnfrozenError("not seeds")
    if int(spec.get("capital") or 0) != 0:
        raise UnfrozenError("capital must be 0")
    if spec.get("new_frozen_forces_this_quarter") != 0:
        raise UnfrozenError("zero new frozen Forces")
    by = {c["id"]: c for c in spec.get("candidates") or []}
    if by["UD-01"].get("lag_test_permitted") is True or by["UD-01"].get("t0_ready") is True:
        raise UnfrozenError("UD-01 is not ready and may not run the lag test")
    if by["UD-07"].get("promising") is True or by["UD-07"].get("classification") != "DUPLICATE_OF_EXISTING_FORCE":
        raise UnfrozenError("grid/queue is F2, not PROMISING")
    if by["UD-07"].get("unregistered_threshold_pct") not in (None, "null"):
        raise UnfrozenError("80-88% threshold is not locked")
    if by["UD-08"].get("promising") is True:
        raise UnfrozenError("Clarksons/IHS are not HIGH feasibility")
    if by["UD-02"].get("iea_mods_wired") is True:
        raise UnfrozenError("IEA MODS is not wired")
    nxt = spec.get("next_operation") or {}
    if nxt.get("inspect_comovement") is True:
        raise UnfrozenError("do not inspect co-movement yet")
    if nxt.get("id") != "SERIES_ID_INVENTORY_ONLY":
        raise UnfrozenError("next op is series-id inventory only")
    if nxt.get("extracted") is True:
        raise UnfrozenError("claimed series are not extracted")
    claimed = yaml.safe_load(CLAIMED.read_text()) or {}
    if claimed.get("extracted") is True or claimed.get("order_test_run") is True:
        raise UnfrozenError("do not run order tests this turn")
    if claimed.get("event_inventory_built") is True:
        raise UnfrozenError("event inventory is not built")
    if spec.get("rank_disagreement", {}).get("winner") not in (None, "none"):
        raise UnfrozenError("do not pick a rank winner")
    if spec.get("census_m3") != "CONVENTIONAL_EXPLANATION_DOMINATES":
        raise UnfrozenError("M3 is conventional, not physical")
    if by["UD-01"].get("cf_same_period_identity") != "refused":
        raise UnfrozenError("same-period CF identity is refused")
    if by["UD-04"].get("classification") != "DATA_FEASIBILITY_PROBLEM":
        raise UnfrozenError("constraint migration has no constraint clock")
    if spec.get("q4_default") != "stay_frozen":
        raise UnfrozenError("Q4 default is stay frozen")
    mission = yaml.safe_load(MISSION.read_text()) or {}
    if mission.get("search_to") != "measurement_architecture_then_transition_then_mechanism":
        raise UnfrozenError("explorer mission inversion not locked")
    if mission.get("census_size_this_quarter") != 0:
        raise UnfrozenError("50-200 census is refused")
    if 7 in (mission.get("levels_open_this_quarter") or []):
        raise UnfrozenError("T0 level is blocked this quarter")
    if "fifty_to_two_hundred_chain_census" not in (mission.get("refused") or []):
        raise UnfrozenError("50-200 census must be refused")
    if "bottleneck_signature_proxy" not in (mission.get("refused") or []):
        raise UnfrozenError("bottleneck signatures are constraint-migration rescue")
    if mission.get("clocks_first_not_variables") is not True:
        raise UnfrozenError("clocks first, not variables")
    if mission.get("seed_finder_this_quarter") is True:
        raise UnfrozenError("do not run the seed finder this quarter")
    census = yaml.safe_load(CENSUS.read_text()) or {}
    if census.get("n") != 0 or census.get("census_run") is True:
        raise UnfrozenError("architecture census stays empty")
    if census.get("admitted_as_seeds") is True:
        raise UnfrozenError("architectures are not seeds")
    if census.get("oecd_infrastructure_investment") != "monetary_spend_refused":
        raise UnfrozenError("OECD investment is spend, not a physical response")
    refused = spec.get("refused") or []



    for tok in (
        "new_frozen_force",
        "grid_queue_as_promising",
        "f2_rename",
        "unregistered_80_88_utilization_threshold",
        "twenty_to_thirty_system_hunt",
        "lag_test_before_series_list",
        "iea_mods_as_wired",
        "same_period_capacity_factor_identity",
        "order_test_this_turn",
        "fifty_to_two_hundred_chain_census",
        "bottleneck_signature_proxy",
        "architecture_census_v1_this_quarter",



    ):
        if tok not in refused:
            raise UnfrozenError(f"missing refuse: {tok}")
    if active_frozen_forces() != ["FS-0001"]:
        raise UnfrozenError("frozen slot unchanged")
    desk = fs0001_desk()
    if desk.get("t5_status") != "NO_RESULT" or desk.get("t5_ready") is True:
        raise UnfrozenError("discovery cannot reopen T5")
    return spec
