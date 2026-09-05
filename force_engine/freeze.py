"""T0–T4 provenance freeze. Instruments come AFTER this, never before.

A Force candidate may not name tickers, call evaluate_candidate, or
write a scannable YAML until:

  T0  one-sentence hypothesis
  T1  economic mechanism
  T2  observables (at least one *leading*, with predicted sign)
  T3  predicted signs (stored on each observable)
  T4  independence dimensions (geography / instrument / manifestation / …)

T5 (names) is attach_instruments() and is refused until freeze_complete.
T5+ evaluation is still queued for a genuinely new leftover. This module
does not search, does not scan Force 4, and cannot promote.

Mechanism-absence kill (frozen leading observable missing → KILL) is
Phase C *evaluation* when those series exist. This file only requires
that they be *named*. It does not expand ClockBus.

F1/F2/F3 are grandfathered as negative_control — they already exist and
are not revival candidates.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

import yaml

from .guards import (
    HARD_EXCLUDED_LEGS,
    WAIT_TICKERS,
    RecycleError,
    WaitLockError,
    refuse_qqq_as_leg,
    refuse_recycled_legs,
    refuse_wait_scan,
)


class FreezeError(RuntimeError):
    """Raised when a caller tries to name tickers or evaluate before T0–T4."""


# Already-failed objects. Re-evaluation is a negative-control, not a new Force.
GRANDFATHERED_FORCE_IDS = {
    "ai_infra_memory_bottleneck",
    "energy_x_ai_power_coupling",
    "longevity_healthspan_demand",
    "f1",
    "f2",
    "f3",
    "f2_oos_hedged",
    "f2_resid_l2",
    "f2_resid_ols",
}

ALLOWED_LEAD = frozenset({"leading", "contemporaneous", "lagging"})
ALLOWED_DIM_KIND = frozenset(
    {"geography", "instrument", "manifestation", "market_expression"}
)

MIN_HYPOTHESIS_CHARS = 12
MIN_MECHANISM_CHARS = 12


def _norm_sign(v: Any) -> int:
    s = str(v).strip().lower() if not isinstance(v, (int, float)) else v
    if s in (1, 1.0, "+1", "+", "plus", "positive", "pos"):
        return 1
    if s in (-1, -1.0, "-1", "-", "minus", "negative", "neg"):
        return -1
    raise FreezeError(
        f"observable predicted_sign must be +1 or -1, got {v!r}. "
        "T3 is frozen before tickers."
    )


def _as_str_list(v: Any) -> List[str]:
    if v is None:
        return []
    if isinstance(v, str):
        return [v] if v.strip() else []
    return [str(x) for x in v if str(x).strip()]


@dataclass
class FrozenObservable:
    name: str
    predicted_sign: int
    lead: str
    absent_kills: bool = True

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "predicted_sign": int(self.predicted_sign),
            "lead": self.lead,
            "absent_kills": bool(self.absent_kills),
        }


@dataclass
class IndependenceDim:
    kind: str
    note: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {"kind": self.kind, "note": self.note}


@dataclass
class FrozenHypothesis:
    hypothesis_id: str
    hypothesis: str
    mechanism: str
    observables: List[FrozenObservable] = field(default_factory=list)
    independence_dimensions: List[IndependenceDim] = field(default_factory=list)
    tickers: List[str] = field(default_factory=list)
    controls: List[str] = field(default_factory=list)
    instruments_attached: bool = False
    scannable: bool = False
    capital: int = 0
    cannot_promote: bool = True
    research_role: str = "candidate"
    note: str = ""
    missing: List[str] = field(default_factory=list)

    @property
    def freeze_complete(self) -> bool:
        """Computed. YAML cannot claim complete if T0–T4 are empty."""
        return not self.missing

    def as_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "hypothesis": self.hypothesis,
            "mechanism": self.mechanism,
            "observables": [o.as_dict() for o in self.observables],
            "independence_dimensions": [d.as_dict() for d in self.independence_dimensions],
            "tickers": list(self.tickers),
            "controls": list(self.controls),
            "freeze_complete": self.freeze_complete,
            "instruments_attached": bool(self.instruments_attached),
            "scannable": False,
            "capital": 0,
            "cannot_promote": True,
            "research_role": self.research_role,
            "missing": list(self.missing),
            "note": self.note
            or "T5 instruments only after freeze_complete. evaluate_candidate cannot promote.",
        }


def _parse_observables(raw: Any) -> List[FrozenObservable]:
    out: List[FrozenObservable] = []
    if not raw:
        return out
    for row in raw:
        if not isinstance(row, Mapping):
            raise FreezeError(f"observable must be a mapping, got {type(row)}")
        name = str(row.get("name") or "").strip()
        if not name:
            raise FreezeError("observable missing name")
        lead = str(row.get("lead") or "").strip().lower()
        if lead not in ALLOWED_LEAD:
            raise FreezeError(
                f"observable {name!r} lead must be one of {sorted(ALLOWED_LEAD)}, got {lead!r}"
            )
        sign = _norm_sign(row.get("predicted_sign"))
        absent = row.get("absent_kills", True)
        out.append(
            FrozenObservable(
                name=name,
                predicted_sign=sign,
                lead=lead,
                absent_kills=bool(absent if absent is not None else True),
            )
        )
    return out


def _parse_dims(raw: Any) -> List[IndependenceDim]:
    out: List[IndependenceDim] = []
    if not raw:
        return out
    for row in raw:
        if isinstance(row, str):
            kind = row.strip().lower()
            note = ""
        elif isinstance(row, Mapping):
            kind = str(row.get("kind") or "").strip().lower()
            note = str(row.get("note") or "")
        else:
            raise FreezeError(f"independence dimension must be str or mapping, got {type(row)}")
        if kind not in ALLOWED_DIM_KIND:
            raise FreezeError(
                f"independence kind must be one of {sorted(ALLOWED_DIM_KIND)}, got {kind!r}. "
                "US equity cousins are not an independence dimension."
            )
        out.append(IndependenceDim(kind=kind, note=note))
    return out


def missing_t0_t4(
    *,
    hypothesis: str,
    mechanism: str,
    observables: Sequence[FrozenObservable],
    independence_dimensions: Sequence[IndependenceDim],
) -> List[str]:
    miss: List[str] = []
    if len((hypothesis or "").strip()) < MIN_HYPOTHESIS_CHARS:
        miss.append("T0_hypothesis")
    if len((mechanism or "").strip()) < MIN_MECHANISM_CHARS:
        miss.append("T1_mechanism")
    if not observables:
        miss.append("T2_observables")
    elif not any(o.lead == "leading" for o in observables):
        miss.append("T2_at_least_one_leading_observable")
    kinds = {d.kind for d in independence_dimensions}
    if len(kinds) < 2:
        miss.append("T4_independence_dimensions_need_two_kinds")
    return miss


def hypothesis_from_mapping(raw: Mapping[str, Any], *, default_id: str = "") -> FrozenHypothesis:
    hid = str(raw.get("hypothesis_id") or default_id or "").strip()
    if not hid:
        raise FreezeError("hypothesis_id required")
    obs = _parse_observables(raw.get("observables"))
    dims = _parse_dims(raw.get("independence_dimensions"))
    hyp = str(raw.get("hypothesis") or "")
    mech = str(raw.get("mechanism") or "")
    miss = missing_t0_t4(
        hypothesis=hyp, mechanism=mech, observables=obs, independence_dimensions=dims
    )
    tickers = [str(t).upper() for t in _as_str_list(raw.get("tickers") or raw.get("legs"))]
    controls = [str(t).upper() for t in _as_str_list(raw.get("controls"))]
    if tickers and miss:
        raise FreezeError(
            f"{hid}: tickers {tickers} named before T0–T4 complete (missing {miss}). "
            "That is Option-B. Instruments attach only after freeze_complete."
        )
    if any(t in WAIT_TICKERS for t in tickers):
        raise WaitLockError(
            f"{hid}: WAIT tickers {sorted(WAIT_TICKERS & set(tickers))} cannot be freeze instruments. "
            "Force 4 stays wait."
        )
    if any(t in HARD_EXCLUDED_LEGS for t in tickers):
        raise RecycleError(
            f"{hid}: paused F1/F2/F3 legs {sorted(HARD_EXCLUDED_LEGS & set(tickers))} cannot be reused."
        )
    role = str(raw.get("research_role") or "candidate")
    if hid.lower() in GRANDFATHERED_FORCE_IDS or hid.lower() in {"f1", "f2", "f3"}:
        role = "negative_control"
    fh = FrozenHypothesis(
        hypothesis_id=hid,
        hypothesis=hyp,
        mechanism=mech,
        observables=obs,
        independence_dimensions=dims,
        tickers=tickers,
        controls=controls,
        instruments_attached=bool(raw.get("instruments_attached")) and bool(tickers) and not miss,
        research_role=role,
        note=str(raw.get("note") or ""),
        missing=miss,
    )
    claimed = raw.get("freeze_complete")
    if claimed in (True, "true", "True", 1) and miss:
        raise FreezeError(
            f"{hid}: YAML freeze_complete=true but missing {miss}. Completeness is computed."
        )
    if raw.get("scannable") in (True, "true", "True", 1):
        raise FreezeError(f"{hid}: freeze records cannot be scannable. Discovery cannot promote.")
    if int(raw.get("capital") or 0) != 0:
        raise FreezeError(f"{hid}: capital must be 0")
    return fh


def load_freeze(path: Path) -> FrozenHypothesis:
    p = Path(path)
    if not p.exists():
        raise FreezeError(f"no freeze file: {p}")
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, Mapping):
        raise FreezeError(f"{p} is not a mapping")
    return hypothesis_from_mapping(raw, default_id=p.stem)


def write_freeze(fh: FrozenHypothesis, path: Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.safe_dump(fh.as_dict(), sort_keys=False, allow_unicode=True), encoding="utf-8")
    return p


def assert_freeze_complete(fh: FrozenHypothesis) -> None:
    if not fh.freeze_complete:
        raise FreezeError(
            f"{fh.hypothesis_id}: freeze incomplete ({fh.missing}). "
            "T5 instruments and evaluate_candidate are refused until T0–T4 are filled. "
            "No Force 4. Capital $0."
        )


def attach_instruments(
    fh: FrozenHypothesis,
    legs: Sequence[str],
    controls: Sequence[str],
) -> FrozenHypothesis:
    """T5. Refused until freeze_complete. Still cannot promote. Still not scannable."""
    assert_freeze_complete(fh)
    hid = str(fh.hypothesis_id or "").strip().upper()
    if hid.startswith("FS-"):
        from force_ideas.t5_gate import T5LockError, assert_t5_unlock

        try:
            assert_t5_unlock(hid)
        except T5LockError as e:
            raise FreezeError(str(e)) from e
    legs_u = [str(t).upper() for t in legs]
    ctrl_u = [str(t).upper() for t in controls]
    if not legs_u or not ctrl_u:
        raise FreezeError("T5 requires both legs and controls")
    refuse_qqq_as_leg(legs_u)
    refuse_wait_scan(legs_u + ctrl_u, allow_wait_sketch=False)
    refuse_recycled_legs(legs_u, research_paused=False)
    out = FrozenHypothesis(
        hypothesis_id=fh.hypothesis_id,
        hypothesis=fh.hypothesis,
        mechanism=fh.mechanism,
        observables=list(fh.observables),
        independence_dimensions=list(fh.independence_dimensions),
        tickers=legs_u,
        controls=ctrl_u,
        instruments_attached=True,
        research_role=fh.research_role,
        note=fh.note,
        missing=[],
    )
    return out


def refuse_evaluate_unfrozen(
    force_id: str,
    legs: Sequence[str],
    *,
    freeze: Optional[FrozenHypothesis] = None,
    allow_unfrozen: bool = False,
    allow_wait_sketch: bool = False,
) -> None:
    """Call from pipeline.evaluate_candidate. Grandfathered F1/F2/F3 skip freeze."""
    fid = str(force_id or "").strip()
    refuse_wait_scan(legs, allow_wait_sketch=allow_wait_sketch)
    if fid.lower() in GRANDFATHERED_FORCE_IDS:
        return
    if allow_unfrozen:
        return
    if freeze is None:
        raise FreezeError(
            f"{fid}: evaluate_candidate refused — no T0–T4 freeze. "
            "A new leftover must freeze mechanism, leading observables, and "
            "independence dimensions BEFORE prices are inspected. "
            "Paused F1/F2/F3 are the only grandfathered ids. Force 4 stays WAIT."
        )
    assert_freeze_complete(freeze)
    if not freeze.instruments_attached or not freeze.tickers:
        raise FreezeError(
            f"{fid}: freeze is complete but T5 instruments are not attached. "
            "Call attach_instruments() after T4, then evaluate."
        )
    want = {str(t).upper() for t in legs}
    have = {str(t).upper() for t in freeze.tickers}
    if want != have:
        raise FreezeError(
            f"{fid}: spec legs {sorted(want)} != freeze tickers {sorted(have)}. "
            "Cannot swap names after freeze."
        )


def is_grandfathered(force_id: str) -> bool:
    return str(force_id or "").strip().lower() in GRANDFATHERED_FORCE_IDS
