"""Observable inventory. Not seeds. Not a freeze. No tickers."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

from force_ideas.state import active_frozen_forces

PATH = Path(__file__).resolve().parent / "paradoxes-20.yaml"


def load() -> Dict[str, Any]:
    return yaml.safe_load(PATH.read_text()) or {}


def items() -> List[Dict[str, Any]]:
    return list(load().get("items") or [])


def summary() -> Dict[str, Any]:
    rows = items()
    by = {}
    for it in rows:
        by[it["seed_status"]] = by.get(it["seed_status"], 0) + 1
    cousins = [it["id"] for it in rows if it.get("cousin") and it["cousin"] != "none"]
    tickers = []
    for it in rows:
        blob = yaml.safe_dump(it).upper()
        for t in ("ITA", "XAR", "PPA", "AAPL", "SPY", "QQQ"):
            if f" {t} " in f" {blob} " or f"[{t}]" in blob:
                tickers.append(t)
    return {
        "n_items": len(rows),
        "by_status": by,
        "cousins_refused": cousins,
        "admitted_as_seeds": False,
        "cannot_promote": True,
        "capital": 0,
        "active_frozen": active_frozen_forces(),
        "ticker_hits": tickers,
        "already_frozen": [it["id"] for it in rows if it.get("seed_status") == "already_frozen"],
    }
