"""
Price fetcher — Yahoo chart API (primary) + yfinance fallback + local parquet cache.

Yahoo's v8 chart endpoint with a browser User-Agent is more reliable than
yfinance's crumb client, which rate-limits aggressively from shared IPs.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Iterable, Optional

import pandas as pd
import requests

from .cache import LastFetch, load_parquet, save_parquet, upsert_by_index

DEFAULT_TICKERS = [
    "VST",
    "ETN",
    "PWR",
    "CEG",
    "XLU",
    "QQQ",
    "XLE",
    "SPY",
    "VOO",
    "MAGS",
    "SMH",
    "SPMO",
    "DRAM",
    # Force 3 locked universe (do not scan until lock is acknowledged)
    "IHF",
    "IHI",
    "XHS",
    "XLV",
    "XBI",
    "IBB",
    "TLT",
]

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
_PERIOD_RANGE = {
    "max": "max",
    "10y": "10y",
    "5y": "5y",
    "2y": "2y",
    "1y": "1y",
}


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
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


def _fetch_yahoo_chart(ticker: str, period: str = "max") -> Optional[pd.DataFrame]:
    rng = _PERIOD_RANGE.get(period, "max")
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
    # range=max is often truncated by Yahoo; explicit period1/period2 is reliable.
    if rng in ("max", "10y"):
        params = {"period1": 0, "period2": int(time.time()), "interval": "1d", "events": "div,splits"}
    else:
        params = {"range": rng, "interval": "1d", "events": "div,splits"}
    try:
        r = requests.get(url, params=params, headers={"User-Agent": _UA}, timeout=30)
        r.raise_for_status()
        payload = r.json()
    except Exception as e:
        print(f"[prices] chart {ticker} failed: {type(e).__name__}: {e}")
        return None
    result = (payload.get("chart") or {}).get("result") or []
    if not result:
        print(f"[prices] chart {ticker}: empty result")
        return None
    block = result[0]
    ts = block.get("timestamp") or []
    quote = ((block.get("indicators") or {}).get("quote") or [{}])[0]
    adj = ((block.get("indicators") or {}).get("adjclose") or [{}])[0]
    if not ts:
        return None
    close = adj.get("adjclose") or quote.get("close")
    df = pd.DataFrame(
        {
            "open": quote.get("open"),
            "high": quote.get("high"),
            "low": quote.get("low"),
            "close": close,
            "volume": quote.get("volume"),
        },
        index=pd.to_datetime(ts, unit="s"),
    )
    return _normalize(df)


def fetch_ticker(
    ticker: str,
    period: str = "2y",
    sleep_s: float = 1.0,
) -> Optional[pd.DataFrame]:
    """Download one ticker; return normalized OHLCV or None on failure."""
    time.sleep(sleep_s)
    df = _fetch_yahoo_chart(ticker, period=period)
    if df is not None and not df.empty:
        return df
    try:
        import yfinance as yf

        raw = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        return _normalize(raw)
    except Exception as e:
        print(f"[prices] yfinance {ticker} failed: {type(e).__name__}: {e}")
        return None


def update_prices(
    tickers: Optional[Iterable[str]] = None,
    period: str = "2y",
    sleep_s: float = 0.8,
) -> dict:
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
