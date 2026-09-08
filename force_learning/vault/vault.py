"""FS-0001 Historical Evidence Vault. Acquisition ≠ T5 activation.

Does not import evaluate / neutralize / pipeline.
Does not search for confirmatory episodes.
Does not invent IEA/OECD panels.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import yaml

from force_ideas.state import fs0001_desk

ROOT = Path(__file__).resolve().parents[2]
VAULT = Path(__file__).resolve().parent
FEAS = VAULT / "feasibility.yaml"
OUT = ROOT / "data" / "meta" / "fs0001_vault.json"

REFUSED_EPISODE_VERBS = (
    "find every famous case",
    "select episodes that confirm",
    "search history for confirmatory",
)


def load_feasibility() -> Dict[str, Any]:
    return yaml.safe_load(FEAS.read_text()) or {}


def assert_not_activation() -> None:
    spec = load_feasibility()
    desk = fs0001_desk()
    if spec.get("t5_ready") is True or desk.get("t5_ready") is True:
        raise RuntimeError("vault cannot set T5_READY")
    if spec.get("scannable") or spec.get("prosecutor_allowed"):
        raise RuntimeError("vault cannot be scannable / prosecutor")
    if int(spec.get("capital") or 0) != 0:
        raise RuntimeError("vault capital must be 0")
    if spec.get("episode_search") is True:
        raise RuntimeError("episode search is discovery; refused")
    uc = spec.get("observables") or {}
    if (uc.get("unit_cost") or {}).get("status") != "critical_blocker":
        raise RuntimeError("unit cost is still the blocker; do not pretend otherwise")


def inventory_rows() -> List[Dict[str, str]]:
    obs = (load_feasibility().get("observables") or {})
    rows = []
    for key in ("efficiency", "unit_cost", "aggregate_use", "eu_geography", "cross_check"):
        rec = obs.get(key) or {}
        rows.append(
            {
                "observable": key,
                "source": str(rec.get("source") or rec.get("role") or ""),
                "status": str(rec.get("status") or ""),
                "depth": str(rec.get("historical_depth") or ""),
            }
        )
    return rows


def report() -> Dict[str, Any]:
    assert_not_activation()
    spec = load_feasibility()
    payload = {
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "force_id": "FS-0001",
        "role": "historical_evidence_vault",
        "t5_ready": False,
        "scannable": False,
        "prosecutor_allowed": False,
        "capital": 0,
        "episode_search": False,
        "wired_panels": False,
        "unit_cost_status": spec["observables"]["unit_cost"]["status"],
        "target_window": spec.get("target_window"),
        "rows": inventory_rows(),
        "note": (
            "Acquisition only. No invented tkm panel. No episode hunt. "
            "T5_NO_RESULT remains. Capital $0."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2))
    return payload
