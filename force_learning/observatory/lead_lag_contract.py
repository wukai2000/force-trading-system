"""Lead/lag is pre-registered. Searching against returns is refused."""
from __future__ import annotations

from typing import Any, Dict, Mapping


ALLOWED = (1, 2, 3)


def check(contract: Mapping[str, Any]) -> Dict[str, Any]:
    ll = contract.get("lead_lag") or {}
    leads = tuple(ll.get("allowed_leads") or [])
    locked = True
    if leads != ALLOWED:
        locked = False
    if ll.get("search_after_returns") is True:
        locked = False
    if str(ll.get("selection") or "") != "pre_registered":
        locked = False
    return {
        "lead_lag": "PASS" if locked else "NO_RESULT",
        "allowed_leads": list(leads),
        "search_after_returns": bool(ll.get("search_after_returns")),
        "note": "Leads 1–3 years are frozen. Do not pick the best lag from IR.",
    }
