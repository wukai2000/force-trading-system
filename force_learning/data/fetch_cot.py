"""
CFTC COT fetcher — Public Reporting Socrata API (no key required).

Resource gpe5-46if = Traders in Financial Futures, Futures Only.
Weekly data. Use for major-move joint flags (USD / equity index contracts).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

import pandas as pd
import requests

from .cache import LastFetch, load_parquet, save_parquet, upsert_by_index

SOCRATA_BASE = "https://publicreporting.cftc.gov/resource"
DEFAULT_RESOURCE = "gpe5-46if"  # TFF futures only


def fetch_tff(limit: int = 5000, resource: str = DEFAULT_RESOURCE) -> Optional[pd.DataFrame]:
    url = f"{SOCRATA_BASE}/{resource}.json"
    params = {
        "$limit": limit,
        "$order": "report_date_as_yyyy_mm_dd DESC",
    }
    try:
        r = requests.get(url, params=params, timeout=60)
        r.raise_for_status()
        rows = r.json()
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        # Normalize key columns if present
        if "report_date_as_yyyy_mm_dd" in df.columns:
            df["report_date"] = pd.to_datetime(df["report_date_as_yyyy_mm_dd"])
            df = df.set_index("report_date").sort_index()
        return df
    except Exception as e:
        print(f"[cot] fetch failed: {type(e).__name__}: {e}")
        return None


def update_cot(limit: int = 5000) -> dict:
    lf = LastFetch()
    today = datetime.now(timezone.utc).date().isoformat()
    new = fetch_tff(limit=limit)
    rel = "cot/tff_futures.parquet"
    if new is None or new.empty:
        return {"ok": False, "rows": 0}

    existing = load_parquet(rel)
    # Socrata returns many columns as strings; keep raw for now
    if existing is not None and not existing.empty:
        # prefer index name alignment
        combined = pd.concat([existing, new])
        combined = combined[~combined.index.duplicated(keep="last")].sort_index()
    else:
        combined = new.sort_index()

    save_parquet(combined, rel)
    lf.set("cot:tff", today)
    result = {
        "ok": True,
        "rows": len(combined),
        "last": str(combined.index.max().date()) if len(combined) else None,
        "cols": list(combined.columns)[:12],
    }
    print(f"[cot] TFF: {result}")
    return result


def list_contract_names(sample: int = 200) -> List[str]:
    """Helper to discover contract_market_name values for filtering."""
    df = load_parquet("cot/tff_futures.parquet")
    if df is None or "contract_market_name" not in df.columns:
        update_cot(limit=sample)
        df = load_parquet("cot/tff_futures.parquet")
    if df is None:
        return []
    return sorted(df["contract_market_name"].dropna().unique().tolist())


if __name__ == "__main__":
    update_cot()
    names = list_contract_names()
    print(f"[cot] sample contracts ({min(15, len(names))}):")
    for n in names[:15]:
        print(" ", n)
