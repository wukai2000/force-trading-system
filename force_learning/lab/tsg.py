"""TSG-0001 v0.1. Spec loadable. Mining and fitting refused."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "force_ideas" / "inventory" / "tsg_0001.yaml"
VINTAGE_MARK = ROOT / "data" / "lab" / "crude" / "e1i_vintages.ok"


class TsgError(RuntimeError):
    pass


def load() -> Dict[str, Any]:
    return yaml.safe_load(SPEC.read_text()) or {}


def assert_tsg() -> Dict[str, Any]:
    spec = load()
    if spec.get("id") != "TSG-0001":
        raise TsgError("id is TSG-0001")
    if spec.get("version") != "v0.1":
        raise TsgError("v0.1 only")
    if spec.get("status") != "FROZEN_SPEC_PREMATURE":
        raise TsgError("premature freeze")
    if spec.get("mining_permitted") is not False:
        raise TsgError("mining not permitted")
    if spec.get("fitting_permitted") is not False:
        raise TsgError("fitting not permitted")
    if spec.get("scoring_permitted") is not False:
        raise TsgError("scoring not permitted")
    if spec.get("br_0001_amendment") is not False:
        raise TsgError("do not amend BR-0001")
    if spec.get("h2_authorized") is not False:
        raise TsgError("H2 not authorized")
    if spec.get("u_breaks_word") is not True:
        raise TsgError("U breaks the word")
    if spec.get("current_label") != "PREMATURE":
        raise TsgError("label is PREMATURE")
    if "M5" not in (spec.get("models_locked") or []):
        raise TsgError("M5 stays locked")
    refused = spec.get("next_refused") or []
    for tok in ("mine_motifs", "prefixspan", "add_letters", "promote"):
        if tok not in refused:
            raise TsgError(f"missing refuse {tok}")
    return spec


def report() -> Dict[str, Any]:
    spec = assert_tsg()
    return {
        "id": spec["id"],
        "version": spec["version"],
        "label": spec["current_label"],
        "why": spec["why"],
        "parent_tape": spec["parent_tape"],
        "vintages_ready": VINTAGE_MARK.is_file(),
        "mining_permitted": False,
        "fitting_permitted": False,
        "h2_authorized": False,
        "models_authorized": spec["models_authorized"],
        "models_locked": spec["models_locked"],
        "alphabet": spec["alphabet_default"],
        "capital": 0,
        "identified": False,
    }
