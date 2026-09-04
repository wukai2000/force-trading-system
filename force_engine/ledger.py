"""Researcher intervention ledger.

Exploration is allowed. Exploration masquerading as confirmation is not.
A first evaluation of a leftover should have intervention_count = 0.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "data" / "meta" / "intervention_ledger.json"

KINDS = (
    "candidate_definition",
    "universe_change",
    "control_change",
    "parameter_change",
    "date_window_change",
    "cost_change",
    "post_result_modification",
    "protocol_bump",
    "instrument_hardening",
    "explorer_registry",
)


def load_ledger(path: Optional[Path] = None) -> Dict[str, Any]:
    p = Path(path) if path is not None else LEDGER_PATH
    if not p.exists():
        return {
            "protocol_id": "FORCE_PROTOCOL_v1.0",
            "cannot_promote": True,
            "entries": [],
        }
    return json.loads(p.read_text())


def save_ledger(data: Dict[str, Any], path: Optional[Path] = None) -> Path:
    p = Path(path) if path is not None else LEDGER_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    data["cannot_promote"] = True
    p.write_text(json.dumps(data, indent=2))
    return p


def append_entry(
    *,
    kind: str,
    reason: str,
    candidate_id: str = "",
    counts: Optional[Dict[str, int]] = None,
    protocol_from: str = "FORCE_PROTOCOL_v1.0",
    protocol_to: str = "FORCE_PROTOCOL_v1.0",
    path: Optional[Path] = None,
) -> Dict[str, Any]:
    if kind not in KINDS:
        raise ValueError(f"unknown intervention kind {kind!r}")
    data = load_ledger(path)
    zeros = {k: 0 for k in KINDS}
    if counts:
        zeros.update({k: int(v) for k, v in counts.items() if k in KINDS})
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "kind": kind,
        "reason": reason,
        "candidate_id": candidate_id,
        "counts": zeros,
        "intervention_count": int(sum(zeros.values())),
        "protocol_from": protocol_from,
        "protocol_to": protocol_to,
        "cannot_promote": True,
    }
    data.setdefault("entries", []).append(entry)
    save_ledger(data, path)
    return entry
