"""FS-0001.v2 is a measurement-audit candidate. Not a freeze. Not a v1 rescue."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


import yaml

from force_ideas.state import active_frozen_forces, fs0001_desk

CAND = Path(__file__).resolve().parents[2] / "force_ideas" / "candidates" / "FS-0001.v2.yaml"
INV = Path(__file__).resolve().parent / "metadata" / "iea_cube_inventory.json"




class V2Error(RuntimeError):
    pass


def load_v2() -> Dict[str, Any]:
    return yaml.safe_load(CAND.read_text()) or {}


def assert_v2_not_frozen() -> Dict[str, Any]:
    spec = load_v2()
    if spec.get("frozen") is True or spec.get("status") != "MEASUREMENT_AUDIT_REQUIRED":
        raise V2Error("v2 is not freeze-ready")
    if spec.get("t5_ready") is True:
        raise V2Error("v2 cannot set T5_READY")
    if spec.get("autonomous_freeze") is True:
        raise V2Error("no autonomous freeze")
    if spec.get("energy_is_not_unit_cost") is not True:
        raise V2Error("MJ/tkm is not v1 unit cost")
    if spec.get("v1_monetary_path") != "CLOSED":
        raise V2Error("v1 monetary path stays closed")
    if spec.get("iea_eei_wired") is True:
        raise V2Error("do not pretend the IEA cube is wired (403)")
    if spec.get("lead_rule") == "locked" or spec.get("lead_rule") in (1, 2, "1", "2"):
        raise V2Error("lead length is not locked; memos disagreed")
    refused = spec.get("refused") or []
    for tok in (
        "tkm_per_mj_as_second_observable",
        "eurostat_road_energy_over_road_tkm",
        "utilization_as_frozen_third",
        "treating_mj_tkm_as_v1_unit_cost",
        "silent_freeze",
    ):
        if tok not in refused:
            raise V2Error(f"missing refuse: {tok}")
    frozen = active_frozen_forces()
    if frozen != ["FS-0001"]:
        raise V2Error(f"frozen slot must remain FS-0001 v1, got {frozen}")
    desk = fs0001_desk()
    if desk.get("t5_status") != "NO_RESULT" or desk.get("t5_ready") is True:
        raise V2Error("v2 audit cannot reopen v1 T5")
    if int(spec.get("capital") or 0) != 0 or int(desk.get("capital") or 0) != 0:
        raise V2Error("capital must be 0")
    inv = json.loads(INV.read_text())
    if inv.get("cube_obtained") is True or spec.get("cube_obtained") is True:
        raise V2Error("IEA cube was not obtained this run")
    for key in ("qualifying_truck_pairs", "qualifying_train_pairs", "qualifying_both"):
        if int(inv.get(key) or 0) != 0 or int(spec.get(key) or 0) != 0:
            raise V2Error(f"{key} must be 0 until the real cube is enumerated")
    if inv.get("inventory_verdict") != "NO_RESULT":
        raise V2Error("empty inventory is NO_RESULT, not SUFFICIENT")
    if inv.get("reconstructed_panel_refused") is not True:
        raise V2Error("fabricated 31/27/25 panel is refused")
    if inv.get("direction_filter_applied") is True:
        raise V2Error("FILTER 2 cannot run on an empty FILTER 1 universe")
    return spec

