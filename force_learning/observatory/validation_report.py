"""Deterministic FS-0001 T5 report. DATA_READY or NO_RESULT. No IR."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from force_ideas.t5_gate import load_contract, load_index, load_lighting_contract, refused_series_hits

from .freight import freight_availability
from .geography_contract import check as geo_check
from .lead_lag_contract import check as lead_check
from .lighting import lighting_availability

ROOT = Path(__file__).resolve().parents[2]
JSON_OUT = ROOT / "data" / "meta" / "fs0001_t5_contract.json"
MD_OUT = ROOT / "docs" / "FS-0001-T5-DATA-CONTRACT-REPORT.md"
LIGHTING_JSON = ROOT / "data" / "meta" / "fs0001_lighting_contract.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build() -> Dict[str, Any]:
    idx = load_index()
    freight = load_contract("FS-0001", 1, resource="freight")
    lighting = load_lighting_contract()
    hits = refused_series_hits(freight)
    fr = freight_availability(freight)
    geo = geo_check(freight)
    ll = lead_check(freight)
    light = lighting_availability()
    cells = {
        "efficiency_data": fr["efficiency"],
        "unit_cost_construction": fr["unit_cost"],
        "aggregate_use_data": fr["aggregate_use"],
        "primary_geography": geo["primary"],
        "second_geography": geo["second"],
        "lead_lag_observability": ll["lead_lag"] if fr.get("series_frozen") else "NO_RESULT",
    }
    data_ready = all(v == "PASS" for v in cells.values()) and not hits
    payload = {
        "as_of": _now(),
        "force_id": "FS-0001",
        "t5_resource": idx.get("t5_resource"),
        "resource": "freight",
        "lighting_role": "observatory_only",
        "status": "DATA_READY" if data_ready else "NO_RESULT",
        "cells": cells,
        "t5_ready": False,
        "prosecutor_allowed": False,
        "capital_allowed": False,
        "cannot_promote": True,
        "instruments": [],
        "refused_us_fred_overlay": True,
        "refused_series_in_contract": list(hits),
        "freight": fr,
        "geography": geo,
        "lead_lag": ll,
        "lighting_diagnostic": {
            "efficiency": light["efficiency"],
            "reason": light.get("reason"),
            "t5_candidate": bool(lighting.get("t5_candidate")),
        },
        "note": (
            "NO_RESULT is success. Lighting cannot silently unlock T5. "
            "Do not attach instruments. Do not run the prosecutor. Capital $0."
        ),
    }
    if hits:
        payload["status"] = "REFUSED"
    payload["t5_ready"] = False
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(payload, indent=2))
    LIGHTING_JSON.write_text(
        json.dumps(
            {
                "as_of": payload["as_of"],
                "force_id": "FS-0001",
                "resource": "lighting",
                "status": "NO_RESULT",
                "t5_ready": False,
                "role": "observatory_only",
                "cells": {
                    "efficiency_data": light["efficiency"],
                    "unit_cost_construction": light["unit_cost"],
                    "aggregate_use_data": light["aggregate_use"],
                },
            },
            indent=2,
        )
    )
    MD_OUT.write_text(_markdown(payload))
    return payload


def _markdown(p: Dict[str, Any]) -> str:
    cells = p.get("cells") or {}
    lines = [
        "# FS-0001 T5 data-contract report",
        "",
        f"as_of: {p.get('as_of')}",
        f"status: **{p.get('status')}**",
        f"T5_READY: {p.get('t5_ready')}",
        f"PROSECUTOR_ALLOWED: {p.get('prosecutor_allowed')}",
        f"CAPITAL_ALLOWED: {p.get('capital_allowed')}",
        "",
        "T5 resource: freight (lighting is observatory-only).",
        "",
        "| Cell | Result |",
        "|---|---|",
    ]
    for k, v in cells.items():
        lines.append(f"| {k} | {v} |")
    lines.extend(
        [
            "",
            "No IR. No Sharpe. No ticker. No instrument ranking. Capital $0.",
            "",
            p.get("note") or "",
            "",
        ]
    )
    return "\n".join(lines) + "\n"
