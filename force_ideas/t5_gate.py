"""T5 unlock for frozen FS-* hypotheses.

T0–T4 freeze is not permission to name tickers.
Need: frozen data contract + named second geography + DATA_READY.
Freight FRED overlays are refused as a mutation of FS-0001 v1.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml

ROOT = Path(__file__).resolve().parent
CONTRACTS = ROOT / "data_contracts"

REFUSED_FS0001_V1_SERIES = frozenset(
    {
        "CASSEXP",
        "RAILFRTINTERMODAL",
        "RAILFRTINTERMODALD11",
        "TSIFRHT",
        "TSIFRGHT",
        "FRGSHPNS",
        "FRGEXPNS",
    }
)


def load_index() -> Dict[str, Any]:
    p = CONTRACTS / "index.yaml"
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text()) or {}


def load_contract(
    force_id: str = "FS-0001",
    version: int = 1,
    resource: Optional[str] = None,
) -> Dict[str, Any]:
    if resource is None:
        resource = str(load_index().get("t5_resource") or "freight")
    p = CONTRACTS / f"{force_id}-{resource}-v{version}.yaml"
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text()) or {}


def load_lighting_contract() -> Dict[str, Any]:
    return load_contract("FS-0001", 1, resource="lighting")



def refused_series_hits(raw: Any) -> Tuple[str, ...]:
    """Scan operational series fields, not the documented refuse list."""
    parts = []
    if isinstance(raw, dict):
        skip = {"refuse", "fred_ids_refused", "reason", "known_limitations", "note"}
        for k, v in raw.items():
            if str(k) in skip:
                continue
            parts.extend(_series_values(v))
        blob = " ".join(parts).upper()
    else:
        blob = str(raw).upper()
    return tuple(sorted(s for s in REFUSED_FS0001_V1_SERIES if s in blob))


def _series_values(v: Any) -> list:
    if v is None or v is False or v is True:
        return []
    if isinstance(v, dict):
        out = []
        for key in ("series", "fred", "fred_series_id", "id", "name"):
            if key in v:
                out.append(str(v.get(key) or ""))
        for child in v.values():
            out.extend(_series_values(child))
        return out
    if isinstance(v, (list, tuple)):
        out = []
        for item in v:
            out.extend(_series_values(item))
        return out
    return [str(v)]



def t5_unlock_or_reason(force_id: str) -> Tuple[bool, str]:
    fid = str(force_id or "").strip().upper()
    if not fid.startswith("FS-"):
        return True, "non-FS id: data-contract gate does not apply"
    if fid != "FS-0001":
        return False, f"{fid}: no data contract"
    idx = load_index()
    if idx.get("t5_resource") != "freight":
        return False, "T5 resource is freight; silent swap refused"
    if idx.get("prosecutor_allowed") or idx.get("capital_allowed"):
        return False, "prosecutor/capital still false"
    lighting = load_lighting_contract()
    if lighting.get("t5_candidate") is True:
        return False, "lighting is observatory-only and cannot unlock T5"
    contract = load_contract("FS-0001", 1, resource="freight")
    if not contract:
        return False, "no freight data contract on disk"
    lock = contract.get("lock") or {}
    if contract.get("resource_class") != "freight" or lock.get("resource_class") != "freight":
        return False, "freight lock broken"
    if str((contract.get("independent_geography") or {}).get("name")) != "European_Union":
        return False, "second geography must stay European_Union"
    if contract.get("instruments") or contract.get("tickers"):
        return False, "contract must keep instruments empty"
    if contract.get("prosecutor_allowed") or contract.get("capital_allowed"):
        return False, "prosecutor/capital still false"
    hits = refused_series_hits(contract)
    if hits:
        return False, f"US FRED freight overlay refused: {hits}"
    for key in ("efficiency", "unit_cost", "aggregate_use"):
        series = str((contract.get(key) or {}).get("series") or "TBD")
        if series.strip().upper() in {"", "TBD"}:
            return False, f"{key}.series is TBD; measurement contract not frozen"
    meta = Path(__file__).resolve().parents[1] / "data" / "meta" / "fs0001_t5_contract.json"
    if meta.exists():
        import json

        report = json.loads(meta.read_text())
        if report.get("t5_ready") is True:
            return True, "DATA_READY"
        return False, f"observatory status={report.get('status', 'NO_RESULT')} t5_ready=false"
    return False, "observatory has not reported DATA_READY"




def assert_t5_unlock(force_id: str) -> None:
    ok, reason = t5_unlock_or_reason(force_id)
    if not ok:
        raise T5LockError(
            f"{force_id}: T5 instrument attachment refused — {reason}. "
            "T5 ≠ prosecutor. T5 ≠ capital. Lighting contract NO_RESULT is success."
        )


class T5LockError(RuntimeError):
    pass
