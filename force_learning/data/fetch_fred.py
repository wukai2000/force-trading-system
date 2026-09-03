"""
FRED fetcher — free graph CSV (no API key required for single-series CSV).

Official API also free with key (120 req/min); start with graph CSV for zero setup.
"""

from __future__ import annotations

from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
import requests
import yaml

from .cache import LastFetch, load_parquet, save_parquet, upsert_by_index

# series_id -> short name used in filenames / panel
DEFAULT_SERIES: Dict[str, str] = {
    "DTWEXBGS": "broad_usd",
    "DGS10": "us_10y",
    "DGS2": "us_2y",
    "FYONET": "federal_outlays_nominal",
}

# L2 state already used by layers.py (kept here so fetch_all can refresh them)
L2_SERIES: Dict[str, str] = {
    "VIXCLS": "vix_cls",
    "VXVCLS": "vxv_cls",
    "T10Y2Y": "t10y2y",
    "DFII10": "dfii10",
    "BAA10Y": "baa10y",
    "BAMLH0A0HYM2": "hy_oas",
    "NFCI": "nfci",
}

GRAPH_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
_REPO = Path(__file__).resolve().parents[2]
_CATALOG = _REPO / "config" / "leading_observables.yaml"


def clock_series_from_catalog(path: Optional[Path] = None) -> Dict[str, str]:
    p = Path(path) if path is not None else _CATALOG
    if not p.exists():
        return {}
    raw = yaml.safe_load(p.read_text()) or {}
    out: Dict[str, str] = {}
    for row in raw.get("observables") or []:
        if row.get("status") != "wired":
            continue
        fred = row.get("fred")
        short = row.get("short")
        if fred and short:
            out[str(fred)] = str(short)
    return out


def fetch_series(series_id: str, timeout: int = 30) -> Optional[pd.DataFrame]:
    url = GRAPH_CSV.format(series_id=series_id)
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        df = pd.read_csv(StringIO(r.text))
        date_col = next((c for c in df.columns if c.upper() in ("DATE", "OBSERVATION_DATE")), df.columns[0])
        val_col = next((c for c in df.columns if c != date_col), df.columns[-1])
        dates = pd.to_datetime(df[date_col])
        values = pd.to_numeric(df[val_col], errors="coerce")
        out = pd.DataFrame({"value": values.to_numpy()}, index=dates)
        out = out.dropna()
        out.index.name = "date"
        return out
    except Exception as e:
        print(f"[fred] {series_id} failed: {type(e).__name__}: {e}")
        return None


def update_macro(series_map: Optional[Dict[str, str]] = None) -> dict:
    series_map = series_map or DEFAULT_SERIES
    lf = LastFetch()
    today = datetime.now(timezone.utc).date().isoformat()
    results = {}

    for series_id, short in series_map.items():
        new = fetch_series(series_id)
        rel = f"macro/{short}.parquet"
        if new is None or new.empty:
            results[series_id] = {"ok": False, "rows": 0, "short": short}
            continue
        existing = load_parquet(rel)
        combined = upsert_by_index(existing, new)
        save_parquet(combined, rel)
        lf.set(f"macro:{series_id}", today)
        results[series_id] = {
            "ok": True,
            "short": short,
            "rows": len(combined),
            "last": str(combined.index.max().date()),
        }
        print(f"[fred] {series_id} ({short}): {results[series_id]}")
    return results


def update_clock_series() -> dict:
    """Fetch catalog + L2 FRED ids. Missing series stay unwired. Never invent."""
    merged = dict(L2_SERIES)
    merged.update(clock_series_from_catalog())
    return update_macro(merged)


if __name__ == "__main__":
    print("-- default --")
    update_macro()
    print("-- clock catalog + L2 --")
    update_clock_series()
