"""Load force definitions from config/*.yaml so the engine is not hard-coded."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

from .base import Force, ForceStatus

_REPO = Path(__file__).resolve().parents[1]
_CONFIG = _REPO / "config"

_STATUS_MAP = {
    "candidate": ForceStatus.CANDIDATE,
    "formalized": ForceStatus.FORMALIZED,
    "formalized_phase_a_locked": ForceStatus.FORMALIZED,
    "historical_series": ForceStatus.HISTORICAL_SERIES,
    "residualized": ForceStatus.RESIDUALIZED,
    "paper": ForceStatus.PAPER,
    "paused": ForceStatus.PAUSED,
    "falsified": ForceStatus.FALSIFIED,
    "falsified_paused": ForceStatus.FALSIFIED,
    "phase_a_failed_paused": ForceStatus.PAUSED,
}


def _load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def force_from_yaml(path: Path) -> Force:
    raw = _load_yaml(path)
    tg = raw.get("ticket_group") or {}
    status_key = str(raw.get("status", "candidate")).lower()
    status = _STATUS_MAP.get(status_key, ForceStatus.CANDIDATE)
    force_id = str(raw.get("force_id") or path.stem)
    name = str(raw.get("name") or force_id.replace("_", " "))
    return Force(
        id=force_id,
        name=name,
        one_sentence=str(raw.get("one_sentence") or "").strip(),
        status=status,
        signature_notes=str(raw.get("paused_reason") or ""),
        tradable=str(raw.get("tradable") or "residual_spread"),
        legs=list((tg.get("legs") or [])),
        controls=list((tg.get("controls") or [])),
        meta={
            "version": raw.get("version"),
            "gate": raw.get("gate") or {},
            "clocks": raw.get("clocks") or {},
            "yaml_path": str(path),
            "scan_allowed": bool(raw.get("scan_allowed", False)),
        },
    )


def load_registered_forces() -> List[Force]:
    forces = []
    for p in sorted(_CONFIG.glob("force*.yaml")):
        try:
            forces.append(force_from_yaml(p))
        except Exception as e:
            print(f"[loader] skip {p.name}: {e}")
    return forces
