"""Force Laboratory — reconstruct tug-of-war. No IR. No tickers."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

INV = Path(__file__).resolve().parents[2] / "force_ideas" / "inventory"
REDESIGN = INV / "force_redesign.yaml"
ARCH = INV / "force_archetypes.yaml"
LAB = INV / "force_lab.yaml"


class LabError(RuntimeError):
    pass


def _load(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text()) or {}


def load() -> Dict[str, Any]:
    return {
        "redesign": _load(REDESIGN),
        "archetypes": _load(ARCH),
        "lab": _load(LAB),
    }


def report() -> Dict[str, Any]:
    spec = load()
    lab = spec["lab"]
    ex = lab.get("experiments") or {}
    return {
        "research_status": spec["redesign"].get("research_status"),
        "object": spec["redesign"].get("object"),
        "n_seeds": 0,
        "capital": 0,
        "n_archetypes": len((spec["archetypes"].get("archetypes") or [])),
        "e1": (ex.get("E1_historical_reconstruction") or {}).get("status"),
        "e2": (ex.get("E2_blind_reconstruction") or {}).get("status"),
        "episodes": [
            {"id": e["id"], "status": e.get("status"), "returns_used": e.get("returns_used")}
            for e in lab.get("episodes") or []
        ],
    }


def assert_lab() -> Dict[str, Any]:
    spec = load()
    rd, ar, lab = spec["redesign"], spec["archetypes"], spec["lab"]
    if rd.get("research_status") != "FORCE_LABORATORY":
        raise LabError("status is FORCE_LABORATORY")
    if rd.get("object") != "ForceFingerprint":
        raise LabError("object is ForceFingerprint")
    if rd.get("returns_define_force") is not False:
        raise LabError("returns do not define a Force")
    if rd.get("capital") != 0 or lab.get("capital") != 0:
        raise LabError("capital is 0")
    if rd.get("n_seeds") != 0:
        raise LabError("n_seeds is 0")
    if rd.get("domain_shopping") != "closed":
        raise LabError("domain shopping stays closed")
    if rd.get("mqa_still_binds") is not True:
        raise LabError("MQA still binds")
    if rd.get("frozen_forces") != ["FS-0001"]:
        raise LabError("only FS-0001 is frozen")
    if rd.get("tickers"):
        raise LabError("no tickers")
    if lab.get("ir_test") is not False or lab.get("tickers"):
        raise LabError("lab does not test IR or tickers")
    if ar.get("admitted_as_seeds") is not False or ar.get("frozen") is not False:
        raise LabError("archetypes are not seeds")
    if len(ar.get("archetypes") or []) != 8:
        raise LabError("eight archetypes")
    ex = lab.get("experiments") or {}
    if (ex.get("E1_historical_reconstruction") or {}).get("status") != "PROTOCOL_OPEN":
        raise LabError("E1 is protocol-open")
    if (ex.get("E1_historical_reconstruction") or {}).get("returns_allowed") is not False:
        raise LabError("E1 forbids returns")
    for k in ("E2_blind_reconstruction", "E3_competing_force", "E4_market_efficiency_challenge", "E5_financial_transmission"):
        if (ex.get(k) or {}).get("status") != "LOCKED":
            raise LabError(f"{k} is locked")
    eps = lab.get("episodes") or []
    if len(eps) != 3:
        raise LabError("three protocol episodes, not a quota")
    if any(e.get("returns_used") is True for e in eps):
        raise LabError("episodes must not use returns")
    by = {e["id"]: e for e in eps}
    if by.get("EP-CRUDE-2014", {}).get("status") != "MECHANICAL_REPLAY":
        raise LabError("crude is the first replay")
    if by.get("EP-CRUDE-2014", {}).get("identified") is True:
        raise LabError("crude is not identified")
    if by.get("EP-NC-2011", {}).get("status") != "NEGATIVE_CONTROL":
        raise LabError("2011 is the negative control")

    refused = (rd.get("refused") or []) + (lab.get("refused") or [])
    for tok in ("ticker_basket", "residual_ir_search", "fs0002", "nbi_reopen", "reconstruct_with_returns"):
        if tok not in refused:
            raise LabError(f"missing refuse: {tok}")
    return spec
