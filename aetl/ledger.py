"""Append-only SearchRecord. Discovery debt is the graph, not a scalar."""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Optional

ACTORS = frozenset({"EXPLORER", "INFERENCER", "PROSECUTOR", "CERTIFIER", "GOVERNOR", "HUMAN", "EXTERNAL"})
ACTIONS = frozenset({"PROPOSE", "TRANSFORM", "REPRESENT", "FIT", "TEST", "DISCARD", "CONTINUE", "LESSON", "INTERPRET", "STATUS", "REFUSE"})
PARTITIONS = frozenset({"DISCOVER", "DEVELOP", "PROSECUTE", "CERTIFY", "REPLICATE", "LAB"})


@dataclass
class SearchRecord:
    record_id: str
    parent_id: Optional[str]
    timestamp: float
    actor: str
    action: str
    candidate_id: Optional[str]
    partition: str
    info_set_id: str
    representation_hash: Optional[str]
    grammar_hash: Optional[str]
    search_burden_note: str
    external_inputs: list
    human_note: str
    outcome_summary: str
    reason: str
    lesson_id: Optional[str]
    code_version: str = "AETL-E0-v0.1"

    def to_dict(self) -> dict:
        return asdict(self)


class SearchLedger:
    def __init__(self) -> None:
        self.rows: list[SearchRecord] = []

    def append(self, **kw: Any) -> SearchRecord:
        actor = kw["actor"]
        action = kw["action"]
        part = kw.get("partition", "LAB")
        if actor not in ACTORS:
            raise ValueError(f"bad actor {actor}")
        if action not in ACTIONS:
            raise ValueError(f"bad action {action}")
        if part not in PARTITIONS:
            raise ValueError(f"bad partition {part}")
        rec = SearchRecord(
            record_id=str(uuid.uuid4())[:8],
            parent_id=kw.get("parent_id"),
            timestamp=time.time(),
            actor=actor,
            action=action,
            candidate_id=kw.get("candidate_id"),
            partition=part,
            info_set_id=kw.get("info_set_id", "UNSET"),
            representation_hash=kw.get("representation_hash"),
            grammar_hash=kw.get("grammar_hash"),
            search_burden_note=kw.get("search_burden_note", ""),
            external_inputs=list(kw.get("external_inputs") or []),
            human_note=kw.get("human_note", ""),
            outcome_summary=kw.get("outcome_summary", ""),
            reason=kw.get("reason", ""),
            lesson_id=kw.get("lesson_id"),
        )
        self.rows.append(rec)
        return rec

    def lineage(self, candidate_id: str) -> list[str]:
        return [r.record_id for r in self.rows if r.candidate_id == candidate_id]

    def burden(self, candidate_id: Optional[str] = None) -> dict:
        rows = [r for r in self.rows if candidate_id is None or r.candidate_id == candidate_id]
        return {
            "n_records": len(rows),
            "n_propose": sum(1 for r in rows if r.action == "PROPOSE"),
            "n_fit": sum(1 for r in rows if r.action == "FIT"),
            "n_test": sum(1 for r in rows if r.action == "TEST"),
            "n_human": sum(1 for r in rows if r.actor == "HUMAN"),
            "n_external": sum(1 for r in rows if r.actor == "EXTERNAL"),
            "note": "counts are diagnostics; not a penalty term",
        }

    def dump(self) -> list[dict]:
        return [r.to_dict() for r in self.rows]


def spec_hash(obj: Any) -> str:
    blob = json.dumps(obj, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()[:16]
