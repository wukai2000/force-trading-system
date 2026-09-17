# EP-NC-2011 — bounded Wayback existence probe 2026-09-17

Authorized this pass: existence of Jan–Jul 2011 **US** WPSR issues.
Not I_t. Not a score. Not North Carolina. Not TWIP. Capital $0.

Spec: `force_ideas/inventory/ep_nc_2011.yaml`.
Prior consolidation: `docs/MEMO_2011_NC_CONSOLIDATION.md`.
Machine receipt: `artifacts/ep_nc_2011_wayback.json`.

## Bound

| Item | Value |
|---|---|
| Window | 30 Wednesdays 2011-01-05 … 2011-07-27 |
| Object | US Table 1 legs: production, commercial stocks ex-SPR, product supplied |
| Allowed | live EIA dated archive; Wayback if 404; capture ≤ a few days after Wednesday |
| Refused | TWIP / GDFU / PSM / PET / PADD 1C / Appendix D1 / coding missing as U / closest-snapshot as week |
| CDX search API | **503 Temporarily Offline** (not exhausted) |
| Year calendar for named rolling URLs | **Enumerated** (`__wb/calendarcaptures/2?date=2011`) |

Named rolling URLs calendared: `ir.eia.gov/wpsr/table1.csv`; `current/pdf/{table1,wpsrall,table4}.pdf` on `eia.gov` and `eia.doe.gov`.

## What exists

| Issue (Wed) | Where | Capture / lastmod vs release | Three legs? | Class |
|---|---|---|---|---|
| 2011-01-19 | Wayback `current/pdf/wpsrall.pdf` | PDF created 2011-01-20 08:24 ET; captured 2011-01-24; orig-lm 2011-01-20 18:00 GMT | full report PDF, cells not scraped | WAYBACK_NEAR_RELEASE |
| 2011-02-16 | Wayback `current/pdf/table4.pdf` | captured 2011-02-20 | stocks only | WAYBACK_NEAR_RELEASE_PARTIAL |
| 2011-05-11 | Wayback eia.doe.gov `table1.pdf` | XMP CreateDate 2011-05-11 08:18 ET; ModDate 11:03 ET; captured 2011-05-14 | Table 1 PDF (compressed) | WAYBACK_NEAR_RELEASE |
| 2011-05-18 | Wayback `ir.eia.gov/wpsr/table1.csv` | captured 2011-05-20; orig-lm 2011-05-18 11:46 GMT; week-ending 5/13 | yes, CSV in-repo | WAYBACK_NEAR_RELEASE |
| 2011-07-27 | **Live** unlisted HTML + `csv/table1.csv` | HTML lastmod 2012-02-09; **CSV lastmod 2011-07-27 17:00 GMT**; week-ending 7/22 | yes, CSV in-repo | LIVE_UNLISTED_NOT_FIRST_PRINT |

Live dated-archive GET sampled across Jan–Jul: **404** except **2011-07-27 200**. Dated **2011-08-03 200** (outside the hole). Year-index GET returned **403** this pass (WAF); do not re-litigate the Aug 3 listing from a blocked index.

SHA-256 (2 MB PDFs not stored):

| File | SHA-256 |
|---|---|
| Wayback wpsrall 20110124 | `56eabad5b1bdcaec9b94fd49f34c725ee15bc566bb105a1027198c948a14492c` |
| Wayback table1.pdf 20110514 | `a4f89f897d5d3569177e32b6aff6d7481d690446d22da8983a55ed41721d3942` |
| Wayback table1.csv 20110520 | `616f0308ae94d5c267420c1777f4a2bbdc94aafa64a17cf6a5214264081b2998` |
| Live 2011-07-27 table1.csv | `21dbed1132f1101589e246206f74e8240993001980153374fbabd804a5f9b4a6` |

In-repo extracts (existence only, not `I_t`):

| Issue | production kbd | stocks ex-SPR mb | product supplied kbd |
|---|---|---|---|
| 2011-05-18 | 5618 | 370.312 | 18515 |
| 2011-07-27 | 5377 | 354.025 | 18426 |

## Calendar of named rolling URLs (2011)

Jan–Jul **200** captures on the Table-1 family are sparse:

- `ir.eia.gov/wpsr/table1.csv` — one: 2011-05-20
- `eia.gov` `table1.pdf` — **none** in Jan–Jul (first 200 is 2011-08-13)
- `eia.gov` `wpsrall.pdf` — one: 2011-01-24
- `eia.doe.gov` `table1.pdf` — one 200: 2011-05-14
- `eia.doe.gov` `wpsrall.pdf` — one 200: 2011-05-14

A late capture of rolling `current/` is a **different week**, not a late copy of January.

## June 301s are not June files

Year calendar lists `eia.doe.gov` `table1.pdf` **301** at 2011-06-04 and 2011-06-22. Following those `id_` URLs redirected to `20110813075813` `eia.gov` `table1.pdf` (orig-lm 2011-08-10). Closest-snapshot / available-API is **not** week-level evidence. Those rows are **not** existence of June issues.

Landing-page captures of `eia.doe.gov` WPSR HTML are not Table 1.

## What this does not show

- A complete 30-issue first-print grid.
- First-print identity of the live July 27 file (HTML wrapper lastmod 2012; CSV lastmod is release Wednesday, still unlisted).
- That every missing HTML week has a near-release Wayback capture.
- Exhaustive CDX of every URL family (dated-archive URLs, FTP, other hosts).

## Gate

**Still UNRESOLVED.** Not FAIL: required US files exist for at least some cutoffs, including one near-release Table 1 CSV with all three legs. Not PASS: most of Jan–Jul is still 404 on live HTML, CDX was not exhausted, `e1i_vintages.ok` stays unwritten.

Missing issue remains `INCOMPLETE`, not `U`. Do not score BR-0001. Do not open Wave 1.

## Next

`2011_ep_nc_fill_remaining_or_fail`

If a later session happens: map remaining Jan–Jul Wednesdays onto near-release captures of the 2011 rolling `current/` path (or `ir.eia.gov/wpsr/table1.csv`) **without** treating closest-snapshot redirects as that week, then join to the official HTML grid from 2011-08-03. Silent default = later.
