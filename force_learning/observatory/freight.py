"""Freight operationalization for FS-0001 T5 preregistration.

Series stay TBD until frozen. Public page probes ≠ DATA_READY.
US FRED overlay (CASSEXP / RAILFRTINTERMODAL / TSIFRGHT) is refused.
"""
from __future__ import annotations

from typing import Any, Dict

import requests

OECD_ITF = "https://www.oecd.org/en/topics/sub-issues/freight-transport.html"
EUROSTAT_FREIGHT = "https://ec.europa.eu/eurostat/web/transport/information-data/transport-data"


def _probe(url: str) -> Dict[str, Any]:
    try:
        r = requests.get(url, timeout=20, allow_redirects=True)
        return {"ok": r.status_code == 200, "status_code": r.status_code, "url": url}
    except Exception as e:
        return {"ok": False, "status_code": None, "url": url, "error": f"{type(e).__name__}: {e}"}


def freight_availability(contract: Dict[str, Any]) -> Dict[str, Any]:
    series = {
        k: str((contract.get(k) or {}).get("series") or "TBD")
        for k in ("efficiency", "unit_cost", "aggregate_use")
    }
    frozen = all(v.strip().upper() not in {"", "TBD"} for v in series.values())
    probes = {"oecd_itf": _probe(OECD_ITF), "eurostat": _probe(EUROSTAT_FREIGHT)}
    cell = "NO_RESULT"
    return {
        "efficiency": cell,
        "unit_cost": cell,
        "aggregate_use": cell,
        "wired": False,
        "series_frozen": frozen,
        "series": series,
        "probes": probes,
        "reason": (
            "Freight series are TBD. A 200 on an OECD/Eurostat landing page is not a "
            "vintage. Do not fill series from US FRED. Do not invent ton-km."
        ),
    }
