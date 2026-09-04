"""Immutable Force-seed identifiers. FS-0001 v1 is never overwritten."""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional, Tuple

import yaml

ID_RE = re.compile(r"^FS-(\d{4})$")
VER_RE = re.compile(r"^v?(\d+)$", re.I)


class IdError(RuntimeError):
    pass


def parse_id(raw: str) -> Optional[str]:
    s = str(raw or "").strip()
    m = ID_RE.match(s)
    return m.group(0) if m else None


def parse_version(raw) -> int:
    if raw is None or raw == "":
        return 1
    if isinstance(raw, int):
        return int(raw)
    m = VER_RE.match(str(raw).strip())
    if not m:
        raise IdError(f"version must be an integer, got {raw!r}")
    return int(m.group(1))


def card_key(card: dict) -> Tuple[str, int]:
    sid = parse_id(str(card.get("seed_id") or card.get("hypothesis_id") or ""))
    if not sid:
        raise IdError("real cards use seed_id like FS-0001 (templates may use _)")
    return sid, parse_version(card.get("version"))


def existing_ids(root: Path) -> List[str]:
    ids = []
    for folder in ("seeds", "hypotheses", "frozen", "rejected", "refined", "verified"):
        d = root / folder
        if not d.exists():
            continue
        for p in d.glob("*.yaml"):
            if p.name.startswith("_"):
                continue
            raw = yaml.safe_load(p.read_text()) or {}
            sid = parse_id(str(raw.get("seed_id") or raw.get("hypothesis_id") or p.stem.split(".")[0]))
            if sid:
                ids.append(sid)
    return sorted(set(ids))


def next_seed_id(root: Path) -> str:
    nums = []
    for sid in existing_ids(root):
        m = ID_RE.match(sid)
        if m:
            nums.append(int(m.group(1)))
    n = (max(nums) + 1) if nums else 1
    return f"FS-{n:04d}"


def frozen_path(root: Path, seed_id: str, version: int) -> Path:
    return root / "frozen" / f"{seed_id}.v{version}.yaml"


def refuse_mutate_frozen(root: Path, seed_id: str, version: int) -> None:
    p = frozen_path(root, seed_id, version)
    if p.exists():
        raise IdError(
            f"{seed_id} v{version} is frozen and immutable. Open v{version + 1} as a new hypothesis."
        )
