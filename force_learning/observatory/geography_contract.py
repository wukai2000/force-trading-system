"""Pre-registered geography. Naming ≠ evidence. No returns."""
from __future__ import annotations

from typing import Any, Dict, Mapping


def check(contract: Mapping[str, Any]) -> Dict[str, str]:
    primary = contract.get("primary_geography") or {}
    second = contract.get("independent_geography") or {}
    lock = contract.get("lock") or {}
    us_only = bool(primary.get("us_only"))
    primary_ok = (
        str(primary.get("type") or "") in {"multi_country", "multi_country_panel"}
        and not us_only
        and str(lock.get("primary_geography") or "multi_country") == "multi_country"
    )
    second_ok = str(second.get("name") or "") == "European_Union"
    if str(lock.get("independent_geography") or "") not in {"", "European_Union"}:
        second_ok = second_ok and str(lock.get("independent_geography")) == "European_Union"
    return {
        "primary": "PASS" if primary_ok else "NO_RESULT",
        "second": "PASS" if second_ok else "NO_RESULT",
        "primary_wired": "NO_RESULT",
        "second_wired": "NO_RESULT",
        "note": "Named geography is an independence dimension, not a PASS on the Force.",
    }
