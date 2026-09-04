# Leading observables — T2 library, veto-only

Locked 2026-09-03. Catalog: `config/leading_observables.yaml`.

These series **complement** a Force. They do not identify one. They do
not nowcast GDP/NFP. They do not size a book.

```
role: veto_only
cannot_promote: true
capital: 0
force4: wait
refuse_timing_overlay: true
```

`IR(s_t, r_t)` with `s` from this catalog is **refused**. That is the MAGS
move at the clock layer. A passing residual may be vetoed. A failing
residual cannot be rescued.

## Learn / dismiss (the pasted four-bucket note)

| Bucket | Wired here | Dismissed |
|---|---|---|
| Physical | Cass freight, rail carloads, industrial electric (diagnostic) | port congestion, satellite thermal, ADS-B, ISM supplier deliveries (FRED 404) |
| Labor | manufacturing hours, temp help, initial claims | LinkedIn scrape, WARN NLP, H-1B filings |
| Intent / NLP | patent / legislation / health-spend **named, unwired** (existing Force-3 stubs) | 10-K MD&A sentiment, earnings-call prosody, lobbying spend |
| Credit plumbing | HY OAS, NFCI, BAA10Y, DFII10 (already L2), SLOOS tightening, SOFR/EFFR/RRP (diagnostic) | private-credit covenants. COT stays in `fetch_cot`. |

A Force is a **pre-specified economic mechanism**. “Leads industrial
production by 1–3 months” is a nowcast claim, not T0.

## Wiring

- FRED graph CSV → `data/macro/<short>.csv`
- Missing cache → ClockBus `None` → **no veto, no promote, no synthetic**
- Default bus upgrades `credit_spreads` (HY OAS) and `real_10y_yield` (DFII10) when cached
- `catalog_clock_bus()` also registers other wired *veto* ids
- GPR stays the L4 high-z special case in `clocks.py`

## Commands

```
PYTHONPATH=. python scripts/test_leading_observables.py
PYTHONPATH=. python scripts/run_leading_observables.py
PYTHONPATH=. python scripts/run_leading_observables.py --fetch
```

`--promote`, `--scan-force4`, `--time-residual` exit 2.

T2 names from this catalog may be copied into a future
`config/hypotheses/*.yaml` freeze. Tickets still come **after** T0–T4.
Do not attach ITA/XAR/PPA/XLI. Do not recycle F1/F2/F3 legs.
