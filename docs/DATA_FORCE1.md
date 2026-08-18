# Force 1 data layer

## Layout

```
data/
  prices/     # daily OHLCV (CSV)
  macro/      # FRED series (CSV)
  cot/        # weekly CFTC TFF (CSV)
  flows/      # proxy (future)
  naming/     # weekly scores (future)
  state/      # force1_weekly.csv  ← consumable panel
  meta/last_fetch.json
config/force1.yaml
```

Persistence is **CSV** (parquet writes are unreliable on some environments).

## Commands

```bash
# from repo root
export PYTHONPATH=.
python -m force_learning.data.fetch_prices
python -m force_learning.data.fetch_fred
python -m force_learning.data.fetch_cot
python -m force_learning.data.panel

# or all
python scripts/fetch_all.py

# status
python scripts/dashboard_force1.py
python scripts/dashboard_force1.py --png
```

## Free-tier limits

| Stream | Limit |
|--------|--------|
| yfinance | Rate limits; sleep between tickers; cache CSV |
| FRED graph CSV | No key; stable |
| CFTC Socrata | No key; `$limit` pagination |
| GDELT / Trends | Not wired yet |

## v0 ticket group

Legs: QQQ, ITA, UUP  
Controls: SPY, EFA  
Lead-lag default: 4 weeks (`config/force1.yaml`)
