"""Independence screen / Gatekeeper.

Explorer output enters here. The Prosecutor is not called.
Tickers, IR, F1–F4 cousins, and a 9th seed are refused.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = Path(__file__).resolve().parent / "registry.yaml"
SEEDS_DIR = Path(__file__).resolve().parent / "seeds"
HYP_DIR = Path(__file__).resolve().parent / "hypotheses"
FROZEN_DIR = Path(__file__).resolve().parent / "frozen"

# Modules the Explorer/Gatekeeper must never import.
_BANNED_IMPORTS = frozenset(
    {
        "force_engine.evaluate",
        "force_engine.neutralize",
        "force_engine.pipeline",
        "force_engine.false_discovery",
        "force_engine.sieve",
        "force_engine.discovery",
    }
)

_PRICE_KEYS = frozenset(
    {
        "tickers",
        "controls",
        "instruments",
        "legs",
        "universe",
        "basket",
    }
)
_STAT_KEYS = frozenset(
    {
        "observed_ir",
        "sharpe",
        "ir",
        "information_ratio",
        "pnl",
        "backtest",
        "residual",
    }
)

from force_engine.guards import WAIT_TICKERS, HARD_EXCLUDED_LEGS  # noqa: E402
from force_engine.freeze import hypothesis_from_mapping  # noqa: E402


class ScreenError(RuntimeError):
    """Raised when a card is not allowed to proceed."""


def load_registry(path: Optional[Path] = None) -> Dict[str, Any]:
    p = Path(path) if path is not None else REGISTRY_PATH
    return yaml.safe_load(p.read_text()) or {}


def _blob(card: Mapping[str, Any]) -> str:
    parts = []
    for k in (
        "seed_id",
        "hypothesis_id",
        "name",
        "phenomenon",
        "mechanism",
        "hypothesis",
        "observable_guess",
        "who_gains_loses",
        "note",
    ):
        v = card.get(k)
        if v:
            parts.append(str(v))
    for item in card.get("observables") or []:
        if isinstance(item, dict):
            parts.append(str(item.get("name") or ""))
        else:
            parts.append(str(item))
    return " ".join(parts).lower()


def _as_list(v: Any) -> List[str]:
    if v is None:
        return []
    if isinstance(v, str):
        return [v] if v.strip() else []
    return [str(x) for x in v if str(x).strip()]


def _named_tickers(card: Mapping[str, Any]) -> List[str]:
    out: List[str] = []
    for k in _PRICE_KEYS:
        out.extend(_as_list(card.get(k)))
    return [t.upper() for t in out]


def _yaml_files(folder: Path) -> List[Path]:
    if not folder.exists():
        return []
    return sorted(
        p
        for p in folder.glob("*.yaml")
        if not p.name.startswith("_") and p.name != "registry.yaml"
    )


def registry_status(root: Optional[Path] = None) -> Dict[str, Any]:
    base = Path(root) if root is not None else Path(__file__).resolve().parent
    spec = load_registry(base / "registry.yaml" if (base / "registry.yaml").exists() else REGISTRY_PATH)
    n_seeds = len(_yaml_files(base / "seeds"))
    n_hyp = len(_yaml_files(base / "hypotheses"))
    n_frozen = len(_yaml_files(base / "frozen"))
    empty = n_seeds == 0 and n_hyp == 0 and n_frozen == 0
    return {
        "protocol_id": spec.get("protocol_id"),
        "n_seeds": n_seeds,
        "n_hypotheses": n_hyp,
        "n_frozen": n_frozen,
        "max_seeds": int(spec.get("max_seeds") or 8),
        "min_seeds": int(spec.get("min_seeds") or 0),
        "empty": empty,
        "no_result": empty,
        "no_result_is_success": True,
        "cannot_promote": True,
        "promotion": "NOT_PERMITTED",
        "capital": 0,
        "force4": "wait",
        "one_frozen_at_a_time": bool(spec.get("one_frozen_at_a_time", True)),
    }


def _cousin_hits(card: Mapping[str, Any], spec: Mapping[str, Any]) -> List[str]:
    blob = _blob(card)
    hid = str(card.get("seed_id") or card.get("hypothesis_id") or "").lower()
    hits: List[str] = []
    for nb_name, nb in (spec.get("ban_neighborhoods") or {}).items():
        ids = [str(x).lower() for x in (nb.get("ids") or [])]
        if hid in ids:
            hits.append(nb_name)
            continue
        for kw in nb.get("keywords") or []:
            if str(kw).lower() in blob:
                hits.append(f"{nb_name}:{kw}")
                break
    return hits


def _stat_hits(card: Mapping[str, Any]) -> List[str]:
    hits = []
    for k in _STAT_KEYS:
        v = card.get(k)
        if v is None or v == "" or v is False:
            continue
        if isinstance(v, list) and not v:
            continue
        hits.append(k)
    return hits


def screen_card(
    card: Mapping[str, Any],
    *,
    registry_root: Optional[Path] = None,
    writing_to: str = "seeds",
) -> Dict[str, Any]:
    """Gatekeeper. Returns a verdict dict or raises ScreenError."""
    spec = load_registry(
        (Path(registry_root) / "registry.yaml")
        if registry_root is not None
        else REGISTRY_PATH
    )
    status = registry_status(registry_root)
    reasons: List[str] = []

    origin = str(card.get("origin_type") or "").strip()
    allowed_origins = set(spec.get("origin_types") or [])
    if origin not in allowed_origins:
        reasons.append(f"origin_type {origin!r} not in {sorted(allowed_origins)}")

    tickers = _named_tickers(card)
    if tickers:
        reasons.append(f"tickers/instruments before freeze: {tickers}")
    wait = [t for t in tickers if t in WAIT_TICKERS]
    if wait:
        reasons.append(f"Force 4 WAIT tickers: {wait}")
    recycled = [t for t in tickers if t in HARD_EXCLUDED_LEGS]
    if recycled:
        reasons.append(f"paused-force recycle: {recycled}")

    stats = _stat_hits(card)
    if stats:
        reasons.append(f"return statistics on an idea card: {stats}")

    cousins = _cousin_hits(card, spec)
    if cousins:
        reasons.append(f"cousin of paused/wait Force: {cousins}")

    if str(card.get("origin_type") or "") == "backtest" or str(card.get("origin") or "") == "backtest":
        reasons.append("backtest-derived origin is refused")

    if writing_to == "seeds" and status["n_seeds"] >= int(spec.get("max_seeds") or 8):
        # Count is of existing files; a new write would exceed the cap.
        reasons.append(
            f"seed cap {spec.get('max_seeds')} already reached; quota-filling is refused"
        )

    if writing_to == "frozen" and status["n_frozen"] >= 1 and spec.get("one_frozen_at_a_time"):
        reasons.append("one frozen hypothesis at a time")

    if card.get("scannable") is True:
        reasons.append("scannable=true is refused on an idea card")
    if int(card.get("capital") or 0) != 0:
        reasons.append("capital must be 0")
    if card.get("cannot_promote") is False:
        reasons.append("cannot_promote must stay true")

    if reasons:
        raise ScreenError("; ".join(reasons))

    state = str(card.get("state") or writing_to.rstrip("s"))
    freeze_ready = False
    missing: List[str] = []
    if state in {"hypothesis", "frozen"} or writing_to in {"hypotheses", "frozen"}:
        payload = dict(card)
        if not payload.get("hypothesis_id"):
            payload["hypothesis_id"] = payload.get("seed_id") or "unnamed"
        try:
            fh = hypothesis_from_mapping(payload)
            freeze_ready = bool(fh.freeze_complete)
            missing = list(fh.missing)
        except Exception as e:
            missing = [str(e)]
            freeze_ready = False

    return {
        "verdict": "admit",
        "state": state,
        "freeze_ready": freeze_ready,
        "missing_for_freeze": missing,
        "cannot_promote": True,
        "promotion": "NOT_PERMITTED",
        "capital": 0,
        "note": "admitted to registry only. not a Force. tester not invoked.",
    }


def screen_path(path: Path, *, writing_to: str = "seeds") -> Dict[str, Any]:
    raw = yaml.safe_load(Path(path).read_text()) or {}
    if not isinstance(raw, dict):
        raise ScreenError("card must be a YAML mapping")
    return screen_card(raw, writing_to=writing_to)


def assert_no_prosecutor_imports(module_path: Optional[Path] = None) -> None:
    p = Path(module_path) if module_path is not None else Path(__file__).resolve()
    tree = ast.parse(p.read_text())
    imported: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
        elif isinstance(node, ast.Import):
            imported.extend(a.name for a in node.names)
    bad = [m for m in imported if m in _BANNED_IMPORTS]
    if bad:
        raise ScreenError(f"Gatekeeper imported prosecutor modules: {bad}")


def empty_registry_is_success(root: Optional[Path] = None) -> Dict[str, Any]:
    st = registry_status(root)
    if st["empty"]:
        st["evidence_status"] = "no_result"
        st["note"] = "No hypothesis met the pre-freeze requirements. Capital $0. Success."
    return st
