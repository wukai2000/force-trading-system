"""Lighting operationalization for FS-0001. Probe only. Never invent series."""
from __future__ import annotations

from typing import Any, Dict

import requests

# Public IEA pages. Full EEI is paid. A 200 on the marketing page ≠ DATA_READY.
IEA_EEI_HIGHLIGHTS = (
    "https://www.iea.org/data-and-statistics/data-product/"
    "energy-efficiency-indicators-highlights"
)
IEA_EEI_FULL = (
    "https://www.iea.org/data-and-statistics/data-product/"
    "energy-end-uses-and-efficiency-indicators"
)


def _probe(url: str) -> Dict[str, Any]:
    try:
        r = requests.get(url, timeout=20, allow_redirects=True)
        return {"ok": r.status_code == 200, "status_code": r.status_code, "url": url}
    except Exception as e:
        return {"ok": False, "status_code": None, "url": url, "error": f"{type(e).__name__}: {e}"}


def lighting_availability() -> Dict[str, Any]:
    highlights = _probe(IEA_EEI_HIGHLIGHTS)
    full = _probe(IEA_EEI_FULL)
    # Page reachable ≠ series wired. We do not parse paywalled XLSB/ZIP.
    wired = False
    cell = "NO_RESULT"
    return {
        "efficiency": cell,
        "unit_cost": cell,
        "aggregate_use": cell,
        "lead_lag": cell,
        "wired": wired,
        "source": "IEA_EEI",
        "probes": {"highlights": highlights, "full_product": full},
        "reason": (
            "IEA EEI lighting efficacy / lumen-hours is not in the local cache. "
            "Highlights are a limited free subset; the extended database is paid. "
            "US DOE is validation-only. No synthetic lighting panel."
        ),
    }
