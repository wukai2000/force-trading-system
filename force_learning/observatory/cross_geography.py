"""Second geography must be named before T5. Naming ≠ evidence."""
from __future__ import annotations

from typing import Any, Dict, Mapping


def geography_named(contract: Mapping[str, Any]) -> Dict[str, str]:
    primary = contract.get("primary_geography") or {}
    second = contract.get("independent_geography") or {}
    primary_ok = (
        str(primary.get("type") or "") == "multi_country_panel"
        and primary.get("us_doe_primary") is False
        and str(primary.get("source") or "") == "IEA_EEI"
    )
    second_ok = str(second.get("name") or "") == "European_Union"
    return {
        "primary": "PASS" if primary_ok else "NO_RESULT",
        "second": "PASS" if second_ok else "NO_RESULT",
        "primary_wired": "NO_RESULT",
        "second_wired": "NO_RESULT",
        "note": "Named geography is an independence dimension, not a PASS on the Force.",
    }
