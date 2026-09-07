# FS-0001 T5 data-source matrix

Audit date: 2026-09-07. Protocol: FORCE_PROTOCOL_v1.0. **NO_RESULT.**
This matrix is evidence, not an unlock. T5_READY=false. Capital $0.

| Frozen construct | Proposed source | Exact series | Unit | Geography | Frequency | Transformation | Timing | Availability | Compliance | Failure |
|---|---|---|---|---|---|---|---|---|---|---|
| resource_efficiency_index | IEA EEI / transport | I_TKM_E (freight energy intensity) | MJ/tkm | Multi-country IEA | Annual | Native is intensity (−); frozen observable is efficiency (+) | leading | substrate available | FAIL | Inversion 1/I_TKM_E is not frozen |
| resource_unit_cost | OECD/ITF; Eurostat SPPI | none preregistered | monetary / tkm required | multi-country + EU | annual/quarterly | would require construction | leading | not contractually available | FAIL | No harmonized cost/tkm; SPPI is a price index |
| aggregate_resource_use | IEA / OECD-ITF / Eurostat | freight tonne-kilometres | tkm | multi-country; EU countries | Annual | none if physical TKM | contemporaneous | available | PASS conditional | Needs one frozen source/definition |

## Source URLs (authoritative landing pages, not wired vintages)

| Source | URL | What it is | What it is not |
|---|---|---|---|
| IEA Energy End-uses and Efficiency Indicators | https://www.iea.org/data-and-statistics/data-product/energy-end-uses-and-efficiency-indicators | Country-level transport energy, activity, intensity (I_TKM_E, TKM) | Not a free full extract in this repo; not +1 efficiency |
| OECD/ITF freight | https://www.oecd.org/en/topics/sub-issues/freight-transport.html | Physical freight performance (million tkm) | Not monetary cost/tkm |
| Eurostat transport | https://ec.europa.eu/eurostat/web/transport/information-data/transport-data | Territorialized tkm; SPPI for transport services | SPPI ≠ cost/tkm |
| US DOE / Cass / FRED | — | — | Refused for this contract |

## Revision behavior

Eurostat and OECD document routine vintages. A deterministic rule is specifiable (Y observed by 31 Dec Y+1, hash, never silent overwrite) and is **not activated**.

## Explicit bans

SPPI as unit cost. Fuel-price as unit cost. Revenue/TKM from mixed populations. TKM/GDP as aggregate use. Modal-share as efficiency. Lighting silent rescue. Cass/FRED overlay. Replacement geography. Lead picked after IR.
