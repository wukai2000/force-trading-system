"""
Price fetcher — yfinance + local parquet cache.

Limits: yfinance rate-limits aggressively. Cache daily; only backfill gaps.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Optional

import pandas as pd

from .cache import LastFetch, load_parquet, save_parquet, upsert_by_index

DEFAULT_TICKERS = ["MAGS", "SMH", "SPMO", "VOO", "DRAM", "SPY", "QQQ"]


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    # yfinance may return MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    cols = {c.lower(): c for c in df.columns}
    out = pd.DataFrame(index=pd.to_datetime(df.index).tz_localize(None))
    for std in ("open", "high", "low", "close", "volume"):
        if std in cols:
            out[std] = pd.to_numeric(df[cols[std]], errors="coerce")
        elif std.capitalize() in df.columns:
            out[std] = pd.to_numeric(df[std.capitalize()], errors="coerce")
    out = out.dropna(how="all")
    out.index.name = "date"
    return out


def fetch_ticker(
    ticker: str,
    period: str = "2y",
    sleep_s: float = 1.0,
) -> Optional[pd.DataFrame]:
    """Download one ticker; return normalized OHLCV or None on failure."""
    try:
        import yfinance as yf
    except ImportError as e:
        raise ImportError("yfinance required: pip install yfinance") from e

    time.sleep(sleep_s)  # polite backoff
    try:
        raw = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        return _normalize(raw)
    except Exception as e:
        print(f"[prices] {ticker} failed: {type(e).__name__}: {e}")
        return None


def update_prices(
    tickers: Optional[Iterable[str]] = None,
    period: str = "2y",
    sleep_s: float = 1.2,
) -> dict:
    """
    Fetch and upsert each ticker into data/prices/{TICKER}.parquet.
    Updates last_fetch meta.
    """
    tickers = list(tickers or DEFAULT_TICKERS)
    lf = LastFetch()
    results = {}
    today = datetime.now(timezone.utc).date().isoformat()

    for t in tickers:
        new = fetch_ticker(t, period=period, sleep_s=sleep_s)
        rel = f"prices/{t.replace('/', '_')}.parquet"
        if new is None or new.empty:
            results[t] = {"ok": False, "rows": 0}
            continue
        existing = load_parquet(rel)
        combined = upsert_by_index(existing, new)
        save_parquet(combined, rel)
        lf.set(f"prices:{t}", today)
        results[t] = {
            "ok": True,
            "rows": len(combined),
            "last": str(combined.index.max().date()),
        }
        print(f"[prices] {t}: {results[t]}")
    return results


if __name__ == "__main__":
    update_prices()
