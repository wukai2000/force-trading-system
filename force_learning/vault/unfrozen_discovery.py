"""Unfrozen discovery is observatory only. No T0. No F2 rename. No lag peek."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from force_ideas.state import active_frozen_forces, fs0001_desk

PATH = Path(__file__).resolve().parents[2] / "force_ideas" / "inventory" / "unfrozen_discovery.yaml"


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
    if "OP_DATA_FEASIBILITY_GRID_QUEUE_1990_2025" not in (nxt.get("not") or []):
        raise UnfrozenError("grid-queue operation is refused")
    refused = spec.get("refused") or []
    for tok in (
        "new_frozen_force",
        "grid_queue_as_promising",
        "f2_rename",
        "unregistered_80_88_utilization_threshold",
        "twenty_to_thirty_system_hunt",
        "lag_test_before_series_list",
        "iea_mods_as_wired",
    ):
        if tok not in refused:
            raise UnfrozenError(f"missing refuse: {tok}")
    if active_frozen_forces() != ["FS-0001"]:
        raise UnfrozenError("frozen slot unchanged")
    desk = fs0001_desk()
    if desk.get("t5_status") != "NO_RESULT" or desk.get("t5_ready") is True:
        raise UnfrozenError("discovery cannot reopen T5")
    return spec
