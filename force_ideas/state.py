"""Research state machine. NO_RESULT is terminal this quarter, not a prompt to hunt tickers.

SEED → HYPOTHESIS → FROZEN
                     ├─ T5_NO_RESULT  (terminal for the locked version)
                     └─ T5_READY → instruments → scannable → prosecutor

T5_NO_RESULT cannot become T5_READY, SCANNABLE, or prosecutor without a new version.
Does not import evaluate_candidate / neutralize / pipeline.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

import yaml

from force_ideas.t5_gate import t5_unlock_or_reason

ROOT = Path(__file__).resolve().parents[1]
IDEAS = Path(__file__).resolve().parent
FROZEN_DIR = IDEAS / "frozen"
AUDIT = ROOT / "config" / "t5" / "fs0001_freight_contract.yaml"
DESK = IDEAS / "desk.yaml"


def load_desk() -> Dict[str, Any]:
    if not DESK.exists():
        return {}
    return yaml.safe_load(DESK.read_text()) or {}


LEGAL = {
    "SEED": ("HYPOTHESIS",),
    "HYPOTHESIS": ("FROZEN",),
    "FROZEN": ("T5_NO_RESULT", "T5_READY"),
    "T5_NO_RESULT": (),  # terminal for this version
    "T5_READY": ("INSTRUMENTED",),
    "INSTRUMENTED": ("SCANNABLE",),
    "SCANNABLE": ("PROSECUTOR",),
    "PROSECUTOR": (),
}

REFUSED_FROM_NO_RESULT = (
    "T5_READY",
    "INSTRUMENTED",
    "SCANNABLE",
    "PROSECUTOR",
)


class StateError(RuntimeError):
    pass


def _yaml_files(d: Path) -> List[Path]:
    if not d.is_dir():
        return []
    return sorted(p for p in d.glob("*.yaml") if not p.name.startswith("_"))


def active_frozen_forces(registry_root: Optional[Path] = None) -> List[str]:
    base = Path(registry_root) if registry_root is not None else IDEAS
    ids: List[str] = []
    for p in _yaml_files(base / "frozen"):
        raw = yaml.safe_load(p.read_text()) or {}
        hid = str(raw.get("hypothesis_id") or raw.get("seed_id") or p.stem).strip()
        if hid and hid not in ids:
            ids.append(hid)
    return ids


def load_frozen_card(force_id: str = "FS-0001") -> Dict[str, Any]:
    for p in _yaml_files(FROZEN_DIR):
        raw = yaml.safe_load(p.read_text()) or {}
        hid = str(raw.get("hypothesis_id") or raw.get("seed_id") or "")
        if hid.upper() == force_id.upper():
            return raw
    return {}


def load_audit() -> Dict[str, Any]:
    if not AUDIT.exists():
        return {}
    return yaml.safe_load(AUDIT.read_text()) or {}


def fs0001_desk() -> Dict[str, Any]:
    card = load_frozen_card("FS-0001")
    audit = load_audit()
    desk = load_desk()
    ok, reason = t5_unlock_or_reason("FS-0001")
    t5_status = str(
        desk.get("t5_status") or audit.get("status") or card.get("t5_status") or "NO_RESULT"
    )
    return {
        "hypothesis_id": "FS-0001",
        "status": str(desk.get("status") or "FROZEN"),
        "t5_status": t5_status,
        "t5_ready": False,
        "t5_unlock": ok,
        "t5_unlock_reason": reason,
        "instruments": list(card.get("instruments") or desk.get("instruments") or []),
        "tickers": list(card.get("tickers") or desk.get("tickers") or []),
        "scannable": False,
        "prosecutor_allowed": False,
        "capital_allowed": False,
        "capital": 0,
        "force4": "wait",
        "one_frozen_at_a_time": True,
        "active_frozen_forces": active_frozen_forces(),
        "quarter_lock": str(desk.get("t5_quarter_lock") or "2026-Q3"),
        "research_state": "T5_NO_RESULT",
        "note": "NO_RESULT is terminal for FS-0001 v1 this quarter. Do not hunt tickers.",
    }



def assert_transition(src: str, dst: str) -> None:
    allowed = LEGAL.get(src, ())
    if dst not in allowed:
        raise StateError(f"illegal transition {src} → {dst}. from T5_NO_RESULT the next step is a new version, not tickers.")


def assert_no_result_terminal(force_id: str = "FS-0001") -> None:
    desk = fs0001_desk() if force_id == "FS-0001" else {}
    if desk.get("t5_status") != "NO_RESULT":
        raise StateError(f"{force_id}: expected t5_status NO_RESULT")
    if desk.get("t5_ready") is True:
        raise StateError("t5_ready must be false under NO_RESULT")
    if desk.get("instruments") or desk.get("tickers"):
        raise StateError("NO_RESULT cannot carry instruments")
    if desk.get("scannable") or desk.get("prosecutor_allowed"):
        raise StateError("NO_RESULT cannot be scannable / prosecutor")
    if int(desk.get("capital") or 0) != 0:
        raise StateError("capital must be 0")


def assert_prosecutor_forbidden() -> None:
    desk = fs0001_desk()
    if desk.get("scannable") or desk.get("prosecutor_allowed"):
        raise StateError("prosecutor forbidden while scannable=false")


def assert_capital_zero() -> None:
    if int(fs0001_desk().get("capital") or 0) != 0:
        raise StateError("capital allocation from a frozen-but-unvalidated Force is refused")


def assert_freight_v1_immutable() -> None:
    p = IDEAS / "data_contracts" / "FS-0001-freight-v1.yaml"
    raw = yaml.safe_load(p.read_text()) or {}
    lock = raw.get("lock") or {}
    if raw.get("resource_class") != "freight" or lock.get("resource_class") != "freight":
        raise StateError("freight v1 resource_class mutated")
    idx = yaml.safe_load((IDEAS / "data_contracts" / "index.yaml").read_text()) or {}
    if idx.get("t5_resource") != "freight":
        raise StateError("silent resource-class swap refused; that is a new version")
    if str((raw.get("efficiency") or {}).get("series") or "TBD").upper() != "TBD":
        raise StateError("filling freight series inside v1 is refused this quarter")
