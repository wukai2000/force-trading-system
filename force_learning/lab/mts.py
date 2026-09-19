"""MTS-0001. Spec frozen. Frontier not built. Do not retune."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

PATH = Path(__file__).resolve().parents[2] / "force_ideas" / "inventory" / "mts_0001.yaml"


class MtsError(RuntimeError):
    pass


def load() -> Dict[str, Any]:
    return yaml.safe_load(PATH.read_text()) or {}


def assert_mts() -> Dict[str, Any]:
    spec = load()
    if spec.get("id") != "MTS-0001":
        raise MtsError("id is MTS-0001")
    if spec.get("status") != "FROZEN_SPEC":
        raise MtsError("spec is frozen")
    if spec.get("purpose") != "methodological_test_only":
        raise MtsError("methodological test only")
    if spec.get("identified") is not False or spec.get("n_seeds") != 0:
        raise MtsError("not identified, n_seeds=0")
    if spec.get("do_not_select_another_episode") is not True:
        raise MtsError("do not pick a new episode")
    if spec.get("information_frontier") != "NOT_CONSTRUCTED":
        raise MtsError("frontier is not constructed")
    if spec.get("current_run", {}).get("valid_for_identification") is not False:
        raise MtsError("as-revised run is not identification")
    if spec.get("current_run", {}).get("verdict") != "NO_RESULT_MARGIN_TOO_SMALL":
        raise MtsError("smoke verdict locked")
    if spec.get("no_new_observables") is not True:
        raise MtsError("no new observables")
    if spec.get("next_authorized") != "stay_frozen":
        raise MtsError("next is stay_frozen")
    for tok in ("new_episode", "retune_rule", "sidecar", "tickers"):
        if tok not in (spec.get("next_refused") or []):
            raise MtsError(f"missing refuse {tok}")
    return spec
