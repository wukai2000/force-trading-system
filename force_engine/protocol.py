"""FORCE_PROTOCOL_v1.0 provenance. Hashes and version only. Cannot promote."""
from __future__ import annotations

import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "config" / "protocol.yaml"


def load_protocol(path: Optional[Path] = None) -> Dict[str, Any]:
    p = Path(path) if path is not None else PROTOCOL_PATH
    return yaml.safe_load(p.read_text()) or {}


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def git_commit(repo: Optional[Path] = None) -> str:
    cwd = Path(repo) if repo is not None else ROOT
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(cwd),
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except Exception:
        return "unknown"


def provenance(extra_files: Optional[List[str]] = None) -> Dict[str, Any]:
    proto = load_protocol()
    files = list(proto.get("locked_files") or [])
    if extra_files:
        files.extend(extra_files)
    hashes = {}
    for rel in files:
        p = ROOT / rel
        hashes[rel] = file_sha256(p) if p.exists() else "missing"
    return {
        "protocol_id": str(proto.get("protocol_id") or "FORCE_PROTOCOL_v1.0"),
        "locked": str(proto.get("locked") or ""),
        "code_commit": git_commit(),
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "file_sha256": hashes,
        "cannot_promote": True,
        "promotion": "NOT_PERMITTED",
        "capital": int(proto.get("capital") or 0),
        "force4": str(proto.get("force4") or "wait"),
        "no_result_is_success": bool(proto.get("no_result_is_success", True)),
        "milestone": str(proto.get("milestone") or "blind_falsification"),
    }
