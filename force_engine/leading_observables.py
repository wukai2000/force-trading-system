"""Non-price leading observables — T2 library, veto-only.

Cannot promote. Cannot become a timing signal s_t. Cannot scan Force 4.
IR(s_t, r_t) against a residual is refused (the MAGS move at the clock layer).

Wired series are FRED caches under data/macro/<short>.csv.
Unwired / refused series return None and never veto.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import yaml

from .dates import naive_day_index

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "config" / "leading_observables.yaml"
MACRO_DIR = ROOT / "data" / "macro"


class TimingOverlayError(RuntimeError):
    """Raised when a caller tries to use the catalog as s_t."""


@dataclass
class ObservableSpec:
    id: str
    category: str
    role: str
    status: str
    fred: Optional[str] = None
    short: Optional[str] = None
    freq: Optional[str] = None
    lookback: int = 36
    veto_when: str = "never"
    z_threshold: float = 1.5
    clock_slot: Optional[str] = None
    note: str = ""
    reason: str = ""

    @property
    def is_wired(self) -> bool:
        return self.status == "wired" and bool(self.fred) and bool(self.short)

    @property
    def is_refused(self) -> bool:
        return self.status == "refused" or self.role == "refused"


@dataclass
class ClockReading:
    spec_id: str
    z: Optional[float]
    opposition: Optional[float]
    veto_flag: bool
    last_date: Optional[str]
    n: int
    status: str
    note: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.spec_id,
            "z": self.z,
            "opposition": self.opposition,
            "veto_flag": self.veto_flag,
            "last_date": self.last_date,
            "n": self.n,
            "status": self.status,
            "note": self.note,
        }


@dataclass
class Catalog:
    cannot_promote: bool
    capital: int
    force4: str
    refuse_timing_overlay: bool
    note: str
    observables: List[ObservableSpec] = field(default_factory=list)

    def by_id(self, oid: str) -> ObservableSpec:
        for o in self.observables:
            if o.id == oid:
                return o
        raise KeyError(oid)

    def wired(self) -> List[ObservableSpec]:
        return [o for o in self.observables if o.is_wired]

    def refused(self) -> List[ObservableSpec]:
        return [o for o in self.observables if o.is_refused]

    def fred_map(self) -> Dict[str, str]:
        return {o.fred: o.short for o in self.wired() if o.fred and o.short}


def load_catalog(path: Optional[Path] = None) -> Catalog:
    path = Path(path) if path is not None else CATALOG_PATH
    raw = yaml.safe_load(path.read_text()) or {}
    obs: List[ObservableSpec] = []
    for row in raw.get("observables") or []:
        obs.append(
            ObservableSpec(
                id=str(row["id"]),
                category=str(row.get("category") or ""),
                role=str(row.get("role") or "diagnostic"),
                status=str(row.get("status") or "unwired"),
                fred=row.get("fred"),
                short=row.get("short"),
                freq=row.get("freq"),
                lookback=int(row.get("lookback") or 36),
                veto_when=str(row.get("veto_when") or "never"),
                z_threshold=float(row.get("z_threshold") or 1.5),
                clock_slot=row.get("clock_slot"),
                note=str(row.get("note") or ""),
                reason=str(row.get("reason") or ""),
            )
        )
    return Catalog(
        cannot_promote=bool(raw.get("cannot_promote", True)),
        capital=int(raw.get("capital") or 0),
        force4=str(raw.get("force4") or "wait"),
        refuse_timing_overlay=bool(raw.get("refuse_timing_overlay", True)),
        note=str(raw.get("note") or "").strip(),
        observables=obs,
    )


def read_macro_series(short: str, macro_dir: Optional[Path] = None) -> Optional[pd.Series]:
    d = Path(macro_dir) if macro_dir is not None else MACRO_DIR
    p = d / f"{short}.csv"
    if not p.exists() or p.stat().st_size == 0:
        return None
    df = pd.read_csv(p)
    date_col = df.columns[0]
    val_col = "value" if "value" in df.columns else df.columns[-1]
    idx = naive_day_index(df[date_col])
    s = pd.to_numeric(df[val_col], errors="coerce")
    out = pd.Series(s.to_numpy(), index=idx, name=short)
    out = out.replace(".", np.nan).astype(float)
    return out[~out.index.duplicated(keep="last")].dropna().sort_index()


def last_z(s: pd.Series, lookback: int) -> Optional[float]:
    s = s.dropna().astype(float)
    if len(s) < max(8, lookback // 3):
        return None
    win = min(int(lookback), len(s))
    window = s.iloc[-win:]
    mu = float(window.mean())
    sd = float(window.std(ddof=1))
    if not np.isfinite(sd) or sd == 0:
        return None
    return float((window.iloc[-1] - mu) / sd)


def signed_opposition(z: Optional[float], veto_when: str) -> Optional[float]:
    """ClockBus convention: more negative = more opposition (except GPR)."""
    if z is None or not np.isfinite(z):
        return None
    vw = (veto_when or "never").lower()
    if vw == "high_z":
        return float(-z)
    if vw == "low_z":
        return float(z)
    return None


def veto_flag(z: Optional[float], spec: ObservableSpec) -> bool:
    if z is None or not np.isfinite(z):
        return False
    if spec.role not in ("veto",) or spec.veto_when == "never":
        return False
    thr = abs(float(spec.z_threshold))
    if spec.veto_when == "high_z":
        return z >= thr
    if spec.veto_when == "low_z":
        return z <= -thr
    return False


def read_one(spec: ObservableSpec, macro_dir: Optional[Path] = None) -> ClockReading:
    if spec.is_refused:
        return ClockReading(
            spec_id=spec.id,
            z=None,
            opposition=None,
            veto_flag=False,
            last_date=None,
            n=0,
            status="refused",
            note=spec.reason or spec.note,
        )
    if spec.status in ("unwired", "wired_elsewhere"):
        return ClockReading(
            spec_id=spec.id,
            z=None,
            opposition=None,
            veto_flag=False,
            last_date=None,
            n=0,
            status=spec.status,
            note=spec.note,
        )
    if not spec.short:
        return ClockReading(spec.id, None, None, False, None, 0, "unwired", spec.note)
    series = read_macro_series(spec.short, macro_dir=macro_dir)
    if series is None or series.empty:
        return ClockReading(
            spec_id=spec.id,
            z=None,
            opposition=None,
            veto_flag=False,
            last_date=None,
            n=0,
            status="cache_missing",
            note="FRED cache missing; ClockBus returns None (no veto, no promote)",
        )
    z = last_z(series, spec.lookback)
    return ClockReading(
        spec_id=spec.id,
        z=None if z is None else round(z, 4),
        opposition=None if z is None else (
            None if signed_opposition(z, spec.veto_when) is None
            else round(signed_opposition(z, spec.veto_when), 4)
        ),
        veto_flag=veto_flag(z, spec),
        last_date=str(series.index.max().date()),
        n=int(len(series)),
        status="wired" if z is not None else "too_short",
        note=spec.note,
    )


def report(catalog: Optional[Catalog] = None, macro_dir: Optional[Path] = None) -> Dict[str, Any]:
    cat = catalog or load_catalog()
    readings = [read_one(o, macro_dir=macro_dir) for o in cat.observables]
    veto_ids = [r.spec_id for r in readings if r.veto_flag]
    return {
        "cannot_promote": True,
        "capital": cat.capital,
        "force4": cat.force4,
        "refuse_timing_overlay": cat.refuse_timing_overlay,
        "n_observables": len(cat.observables),
        "n_wired_cache": sum(1 for r in readings if r.status == "wired"),
        "n_refused": sum(1 for r in readings if r.status == "refused"),
        "n_unwired": sum(1 for r in readings if r.status in ("unwired", "cache_missing", "wired_elsewhere")),
        "veto_ids": veto_ids,
        "readings": [r.as_dict() for r in readings],
        "note": "Diagnostic. Veto flags do not promote. Do not use as s_t.",
    }


def opposition_reader(spec_id: str, catalog: Optional[Catalog] = None, macro_dir: Optional[Path] = None):
    """ClockBus reader: returns signed opposition or None. Never promotes."""

    def _read() -> Optional[float]:
        cat = catalog or load_catalog()
        spec = cat.by_id(spec_id)
        r = read_one(spec, macro_dir=macro_dir)
        return r.opposition

    _read.__name__ = f"opposition_{spec_id}"
    return _read


def refuse_timing_overlay(residual: Optional[pd.Series] = None, signal: Optional[pd.Series] = None) -> None:
    raise TimingOverlayError(
        "IR(s_t, r_t) with s from the leading-observables catalog is refused. "
        "Clocks veto a passing residual; they do not time it. "
        "See docs/RESEARCH_PROTOCOL.md."
    )


def register_catalog_on_bus(bus, catalog: Optional[Catalog] = None, macro_dir: Optional[Path] = None):
    """Register wired veto slots onto an existing ClockBus. Cannot promote."""
    cat = catalog or load_catalog()
    for spec in cat.observables:
        if not spec.is_wired:
            continue
        if spec.role != "veto":
            continue
        slot = spec.clock_slot or spec.id
        bus.register_leading(slot, opposition_reader(spec.id, catalog=cat, macro_dir=macro_dir))
    return bus
