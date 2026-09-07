# FS-0001 T5 data-contract report

as_of: 2026-09-07
status: **NO_RESULT**
T5_READY: False
PROSECUTOR_ALLOWED: False
CAPITAL_ALLOWED: False
new_version_required: false

T5 resource: freight (lighting is observatory-only).
No IR. No Sharpe. No ticker. No instrument ranking. Capital $0.

## Decision

**NO_RESULT.** The freight contract does not satisfy all preregistered requirements
deterministically enough to unlock T5.

This is not NEW_VERSION_REQUIRED. FS-0001 T0–T4 stay immutable.

## Blockers

1. `resource_unit_cost` is not available as a cross-country physical monetary
   cost per tonne-kilometre from IEA / OECD / ITF / Eurostat.
2. Eurostat SPPI is a producer-price index for transport services, not
   harmonized cost/tkm. Substituting it is proxy substitution.
3. IEA `I_TKM_E` is energy per tkm (intensity, native sign −). The frozen
   observable is `resource_efficiency_index` with sign +. Inversion is an
   unfrozen transformation.
4. Efficiency and unit cost are frozen as *leading*, but no immutable lead
   horizon is encoded. Selecting the horizon after outcomes is prohibited.
5. Revisions are normal. A vintage rule can be specified; it is **not activated**.

## Cell table

| Cell | Result |
|---|---|
| efficiency_data | NO_RESULT (substrate available, observable not operationalized) |
| unit_cost_construction | NO_RESULT — FAIL, decisive |
| aggregate_use_data | NO_RESULT (tkm available, definition lock incomplete) |
| primary_geography | PASS (named multi-country; not US-only) |
| second_geography | PASS (EU named; no replacement) |
| lead_lag_observability | NO_RESULT (roles frozen, horizon unresolved) |
| T5_READY | False |

## Efficiency

IEA defines TKM and I_TKM_E (energy to move one tonne one kilometre). The
substrate exists. The frozen +1 efficiency index does **not**. `1/I_TKM_E`
must not be introduced silently at T5.

## Unit cost (decisive failure)

OECD/ITF freight is physical million tkm, not cost/tkm.
Eurostat SPPI measures price *movements* in transport services, not a
standardized monetary cost per physical tonne-kilometre.
`SPPI / TKM`, fuel-price indices, and revenue/TKM from mixed populations are
proxy substitutions and are refused.

## Aggregate use

Physical tkm is available from IEA, OECD/ITF, and Eurostat, **conditional on
one frozen source/definition**. Eurostat road freight is nationality then
territorialized; rail/IWW are territorial. Mixing with OECD/ITF national
definitions needs a pre-frozen harmonization rule. No replacement geography.

## Lead / lag

Causal direction is conceptual. Empirical lag is not specified (1y / 2y / 3y /
same-year-before-release / distributed). Allowed leads `[1, 2, 3]` years are
listed but **rule: null**. Picking the best lag from IR is prohibited.

## Vintage (specified, not activated)

For reference year Y, use the latest public release by 31 December of Y+1.
Hash the raw file. Later revisions are a new vintage. Do not overwrite the
research panel. **activated: false.**

## What this audit does not do

- attach tickers or instruments
- backtest, IR, Sharpe
- run the prosecutor
- scan Force 4
- loosen placebo or Conc A
- substitute lighting for freight
- introduce Cass/FRED efficiency construction
- construct a freight-cost proxy
- select a new geography
- allocate capital

NO_RESULT is a successful research outcome.
FS-0001 remains frozen. T5 remains locked.

See also: `docs/FS-0001-T5-DATA-SOURCE-MATRIX.md`, `config/t5/fs0001_freight_contract.yaml`.
