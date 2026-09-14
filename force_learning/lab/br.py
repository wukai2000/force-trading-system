"""BR-0001 harness. Freeze is loadable. Scoring is refused until E1.I vintages exist."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "force_ideas" / "inventory" / "br_0001.yaml"
VINTAGE_MARK = ROOT / "data" / "lab" / "crude" / "e1i_vintages.ok"


class BrError(RuntimeError):
    pass


def load() -> Dict[str, Any]:
    return yaml.safe_load(SPEC.read_text()) or {}


def assert_br() -> Dict[str, Any]:
    spec = load()
    if spec.get("id") != "BR-0001":
        raise BrError("id is BR-0001")
    if spec.get("parent") != "MTS-0001":
        raise BrError("parent is MTS-0001")
    if spec.get("status") != "FROZEN_SPEC":
        raise BrError("spec is frozen")
    if spec.get("scoring_permitted") is not False:
        raise BrError("scoring is not permitted")
    if spec.get("e1i_status") != "not_run":
        raise BrError("E1.I is not run")
    if spec.get("promotion") != "NOT_PERMITTED":
        raise BrError("promotion not permitted")
    if spec.get("identified") is not False or spec.get("n_seeds") != 0:
        raise BrError("not identified")
    if spec.get("do_not_select_another_episode") is not True:
        raise BrError("do not pick a new episode")
    if spec.get("no_new_observables") is not True:
        raise BrError("no new observables")
    if spec.get("x", {}).get("id") != "production_kbd":
        raise BrError("x stays production_kbd")
    if spec.get("path_c") != "narrow_classification_only":
        raise BrError("Path C is narrow")
    if spec.get("current_label") != "REFUSED":
        raise BrError("current label is REFUSED")
    refused = spec.get("next_refused") or []
    for tok in ("new_episode", "mts_0002", "retune_rule", "tickers", "promote"):
        if tok not in refused:
            raise BrError(f"missing refuse {tok}")
    return spec


def vintages_ready() -> bool:
    return VINTAGE_MARK.is_file()


def report() -> Dict[str, Any]:
    spec = assert_br()
    return {
        "id": spec["id"],
        "parent": spec["parent"],
        "label": spec["current_label"],
        "why": spec["why_refused"],
        "e1i": spec["e1i_status"],
        "vintages_ready": vintages_ready(),
        "scoring_permitted": False,
        "x": spec["x"]["id"],
        "episode": spec["episode_locked"],
        "path_c": spec["path_c"],
        "ontology": spec["ontology"],
        "capital": 0,
        "n_seeds": 0,
        "identified": False,
    }


def refuse_score(reason: str = "e1i_vintages_missing") -> Dict[str, Any]:
    out = report()
    out["refused"] = True
    out["reason"] = reason
    return out
