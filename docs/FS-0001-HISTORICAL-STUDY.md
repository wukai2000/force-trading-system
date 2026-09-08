# FS-0001 historical feasibility study

as_of: 2026-09-08
decision: **NO_RESULT**
T5_READY: False
NEW_VERSION_REQUIRED: False
episode_search: False
capital: $0

This is a study of whether the three frozen observables can be constructed.
It is not a Force test. No tickers. No residuals. No ΔDemand ranking.

## Ready for study ≠ ready for trading

| Layer | State |
|---|---|
| T0–T4 | FROZEN (unchanged) |
| Historical feasibility | INVESTIGATED |
| Aggregate use (tkm) | OECD/ITF coverage-wired |
| Efficiency (tkm/energy) | IEA EEI HTTP 403 — unwired |
| Unit cost (currency/tkm) | **critical blocker** |
| T5 | NO_RESULT |
| Instruments / prosecutor / capital | locked |

## What was actually retrieved

OECD.ITF `DSD_TRENDS@DF_TRENDSFREIGHT` annual freight, unit = million tkm.

2000–2024 physical modes (road, rail, IWW, pipeline, coastal, inland total):

- 5,339 geo×mode×year observations
- 55 geographies
- 25 years
- EU named geography: 2,735 observations, 25 countries

Eurostat `RAIL_GO_TOTAL` (million tkm) is an independent-geography source class, not a replacement for OECD.

World Bank `IS.RRS.GOOD.MT.K6` (rail tkm, 1995–2021, 142 geos) is a **cross-check**, not a primary.

IEA Energy End-uses and Efficiency Indicators: **403**. Energy numerator/denominator for efficiency is not in this vault.

## Unit cost

The OECD freight file contains **no currency**. It cannot produce currency/tkm.

Eurostat service-producer prices exist as an index. Using them would be proxy substitution and is refused.

No historically comparable currency-per-tonne-km series was constructed. That is the remaining scientific bottleneck. It is not a reason to change the frozen definition.

## What was not done (on purpose)

- No search for “famous cheap-freight episodes”
- No pre-registered efficiency-threshold event study (would require energy + unit cost)
- No SPPI / fuel / revenue÷tkm as unit cost
- No 1970 Frankenstein stitch (1970–2024 rows exist in OECD but missingness is structural; comparability beats antiquity)
- No FS-0002
- No tickers, IR, prosecutor, capital

## Mechanical decision

Three-observable contract is **not** satisfied.

- DATA_READY: no
- NO_RESULT: **yes** (qualifying test still cannot be run)
- NEW_VERSION_REQUIRED: no (hypothesis is not the problem)

Raw extracts are local (`force_learning/vault/raw/`, gitignored). Hashes live in `force_learning/vault/metadata/coverage.json`. Re-fetch: `python -c 'from force_learning.vault.fetch import fetch_all; fetch_all()'`.
