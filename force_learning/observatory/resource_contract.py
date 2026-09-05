"""Validate the frozen T5 data contract. Never computes IR. Never names tickers."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from force_ideas.t5_gate import load_contract, refused_series_hits

from .cross_geography import geography_named
from .lighting import lighting_availability

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "meta" / "fs0001_lighting_contract.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def report_fs0001() -> Dict[str, Any]:
    contract = load_contract("FS-0001", 1)
    hits = refused_series_hits(contract)
    lighting = lighting_availability()
    geo = geography_named(contract)
    cells = {
        "efficiency_data": lighting["efficiency"],
        "unit_cost_construction": lighting["unit_cost"],
        "aggregate_use_data": lighting["aggregate_use"],
        "primary_geography": geo["primary"],
        "second_geography": geo["second"],
        "lead_lag_observability": lighting["lead_lag"],
    }
    data_ready = all(v == "PASS" for v in cells.values())
    payload = {
        "as_of": _now(),
        "force_id": "FS-0001",
        "resource": "lighting",
        "status": "DATA_READY" if data_ready else "NO_RESULT",
        "cells": cells,
        "t5_ready": False,  # even DATA_READY would still need a human T5; lighting is unwired
        "prosecutor_allowed": False,
        "capital_allowed": False,
        "cannot_promote": True,
        "instruments": [],
        "refused_fred_freight_overlay": True,
        "refused_series_in_contract": list(hits),
        "lighting": lighting,
        "geography": geo,
        "note": (
            "NO_RESULT is success. Do not switch v1 to freight/compute/water. "
            "Do not attach instruments. Do not run the prosecutor."
        ),
    }
    if hits:
        payload["status"] = "REFUSED"
    payload["t5_ready"] = False
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2))
    return payload

