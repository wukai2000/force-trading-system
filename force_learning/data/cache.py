"""
Persistence helpers: last_fetch tracking + CSV read/write.

Note: Parquet binary writes are unreliable on some sandbox FS layers;
CSV is the durable default for the Force 1 data skeleton.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DATA_ROOT = _REPO_ROOT / "data"
_META_PATH = _DATA_ROOT / "meta" / "last_fetch.json"


def data_root() -> Path:
    return _DATA_ROOT


def _ensure_meta() -> None:
    _META_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not _META_PATH.exists():
        _META_PATH.write_text("{}")


class LastFetch:
    def __init__(self, path: Optional[Path] = None):
        self.path = path or _META_PATH
        _ensure_meta()
        self._data: Dict[str, str] = {}
        self.load()

    def load(self) -> None:
        try:
            self._data = json.loads(self.path.read_text())
        except Exception:
            self._data = {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2, sort_keys=True))

    def get(self, key: str) -> Optional[str]:
        return self._data.get(key)

    def set(self, key: str, iso_date: str) -> None:
        self._data[key] = iso_date
        self.save()

    def all(self) -> Dict[str, str]:
        return dict(self._data)


def _csv_path(rel_path: str) -> Path:
    """Accept .parquet or .csv rel paths; always store as .csv."""
    p = Path(rel_path)
    if p.suffix.lower() == ".parquet":
        p = p.with_suffix(".csv")
    return _DATA_ROOT / p


def load_parquet(rel_path: str) -> Optional[pd.DataFrame]:
    """Load series table (CSV under data/). Name kept for compatibility."""
    path = _csv_path(rel_path)
    if not path.exists() or path.stat().st_size == 0:
        return None
    try:
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        df.index = pd.to_datetime(df.index)
        return df
    except Exception as e:
        print(f"[cache] read failed {path}: {e}")
        return None


def save_parquet(df: pd.DataFrame, rel_path: str) -> Path:
    """Save as CSV (atomic replace)."""
    path = _csv_path(rel_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    df.to_csv(tmp, index=True)
    os.replace(tmp, path)
    return path


def upsert_by_index(existing: Optional[pd.DataFrame], new: pd.DataFrame) -> pd.DataFrame:
    if existing is None or existing.empty:
        return new.sort_index()
    combined = pd.concat([existing, new])
    combined = combined[~combined.index.duplicated(keep="last")]
    return combined.sort_index()
