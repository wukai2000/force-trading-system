"""EvidenceRecord — research output, not a screener verdict.

Three concepts, never fused:

  A. Evidence   what we observed (Null A/B, IR, Conc B) — no pass/fail
  B. Veto       what contradicts the Force hypothesis (Conc A, clocks, spanning)
  C. Promotion  always NOT_PERMITTED from this module

A planted-alpha residual still cannot promote.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd

from .evaluate import annualized_ir
from .false_discovery import audit_residual
from .protocol import provenance


class PromotionError(RuntimeError):
    """Raised if a caller asks the evidence module to promote."""


@dataclass
class EvidenceRecord:
    protocol_id: str
    candidate_id: str
    evidence_status: str  # uninteresting | interesting | no_result
    vetoes: List[str]
    promotion: str
    observed_ir: Optional[float]
    n_days: int
    null_a: Dict[str, Any]
    null_b: Dict[str, Any]
    conc_a: Dict[str, Any]
    conc_b: Dict[str, Any]
    clocks: Dict[str, Any]
    mechanism: Dict[str, Any]
    neighbors: Dict[str, Any]
    provenance: Dict[str, Any]
    labels: List[str] = field(default_factory=list)
    cannot_promote: bool = True
    capital: int = 0
    note: str = (
        "EvidenceRecord. Null A/B and Conc B are descriptive. "
        "Conc A is the locked kill. Promotion is never automatic."
    )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["cannot_promote"] = True
        d["promotion"] = "NOT_PERMITTED"
        d["capital"] = 0
        return d


def _evidence_status(labels: List[str], observed_ir: float, p_one: Optional[float]) -> str:
    if not labels and (p_one is None or p_one != p_one):
        return "no_result"
    unusual = p_one is not None and p_one == p_one and p_one <= 0.05
    if unusual:
        return "interesting"
    return "uninteresting"


def _null_b_view(blocks: Dict[str, Any]) -> Dict[str, Any]:
    """Strip any temptation to PASS/FAIL. Report distributions only."""
    out = {}
    for k, v in (blocks or {}).items():
        if not isinstance(v, dict):
            continue
        out[str(k)] = {
            "block": v.get("block"),
            "n": v.get("n"),
            "frac_ir_ge_gate": v.get("frac_ir_ge_gate"),
            "p5": v.get("p5"),
            "p50": v.get("mean_ir"),
            "p95": v.get("p95"),
            "cannot_promote": True,
            "note": "descriptive stability distribution. not a pass/fail.",
        }
    return out


def record_from_residual(
    resid: pd.Series,
    *,
    candidate_id: str,
    source: str = "",
    n_sign: int = 400,
    n_block: int = 200,
    clocks: Optional[Dict[str, Any]] = None,
    mechanism: Optional[Dict[str, Any]] = None,
    neighbors: Optional[Dict[str, Any]] = None,
) -> EvidenceRecord:
    """Canonical research path. Draw counts are a computational sample."""
    audit = audit_residual(
        resid, force_id=candidate_id, source=source, n_sign=n_sign, n_block=n_block
    )
    p_one = audit.sign_null.get("empirical_p_value_one_sided")
    status = _evidence_status(audit.labels, audit.observed_ir, p_one)
    conc = audit.concentration or {}
    return EvidenceRecord(
        protocol_id="FORCE_PROTOCOL_v1.0",
        candidate_id=str(candidate_id),
        evidence_status=status,
        vetoes=list(audit.labels),
        promotion="NOT_PERMITTED",
        observed_ir=audit.observed_ir,
        n_days=audit.n_days,
        null_a={
            "observed_ir": audit.sign_null.get("observed_ir"),
            "percentile": audit.sign_null.get("observed_percentile"),
            "empirical_p_one_sided": p_one,
            "n": audit.sign_null.get("n"),
            "cannot_promote": True,
            "note": "descriptive. not a pass/fail.",
        },
        null_b=_null_b_view(audit.block_bootstrap),
        conc_a={
            "ir_persistence_ratio": conc.get("ir_persistence_ratio"),
            "kill": bool(conc.get("ir_persistence_kill")),
            "cannot_promote": True,
            "note": "locked kill when persistence ≥ 0.40",
        },
        conc_b={
            "pnl_mass_top5": conc.get("pnl_mass_top5"),
            "pnl_mass_top10": conc.get("pnl_mass_top10"),
            "cannot_promote": True,
            "note": "descriptive. do not fuse with Conc A.",
        },
        clocks=clocks or {"role": "veto_only", "attached": False},
        mechanism=mechanism
        or {
            "role": "veto_only",
            "status": "queued",
            "cannot_promote": True,
            "note": "mechanism cannot rescue statistics or promote",
        },
        neighbors=neighbors or {"role": "spanning_diagnostic", "attached": False},
        provenance=provenance(),
        labels=list(audit.labels),
        cannot_promote=True,
        capital=0,
    )


def no_result_record(reason: str = "No hypothesis met the pre-freeze requirements.") -> EvidenceRecord:
    """A quarter with no candidate is a successful research period."""
    return EvidenceRecord(
        protocol_id="FORCE_PROTOCOL_v1.0",
        candidate_id="NO_RESULT",
        evidence_status="no_result",
        vetoes=[],
        promotion="NOT_PERMITTED",
        observed_ir=None,
        n_days=0,
        null_a={"note": "no candidate"},
        null_b={"note": "no candidate"},
        conc_a={"kill": False, "note": "no candidate"},
        conc_b={"note": "no candidate"},
        clocks={"role": "veto_only", "attached": False},
        mechanism={"status": "queued", "cannot_promote": True},
        neighbors={"attached": False},
        provenance=provenance(),
        labels=["NO_RESULT"],
        cannot_promote=True,
        capital=0,
        note=reason + " Capital $0. This is a success state.",
    )


def refuse_promote() -> None:
    raise PromotionError(
        "EvidenceRecord cannot promote. Promotion is a human decision after "
        "paper, and no leftover is paper-authorized. Capital $0."
    )


def ir_of(resid: pd.Series) -> float:
    return annualized_ir(resid)
