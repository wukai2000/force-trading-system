# Independent state/event pair — consolidation 2026-09-21

Three Explorer notes. One screening object. Not a freeze. Not a Force.
Capital `$0`. E1.I stays `FAIL` / `NO_RESULT`. `e1i_vintages.ok` unwritten.
n_seeds=0. Q4 stay frozen.

This is a measurement-architecture search. It is not a rescue of EP-NC-2011,
not a new episode, and not Path D.

## What each note actually is

| Source | Leading pair | Status it wanted | Status here |
|---|---|---|---|
| Note 1 (C-AIS-01 / C-HYD-01) | AIS waiting at existing berths → new berth handover + first working call | `CANDIDATE_FOR_GATEKEEPER`; hydrology PARTIAL | **Keep.** Only note that refuses freeze and writes kill questions. |
| Note 2 (MEP-001/002/003) | AIS density → navigation opening; USGS → dam; highway sensors → bridge | `CANDIDATE_FOR_GATEKEEPER`; none freeze | **Keep the gates.** Drop the 1970 lock as an AIS example. |
| Note 3 (CAND-0001) | Commercial AIS DWT dwell → Harbour Master NTM first tie-up | `CANDIDATE_FOR_FREEZE`, class I4 | **Overclaim.** Keep the kills of 0002/0003/0004. Dismiss freeze, I4, DWT, Spire/Orbcomm. |

Same failure mode as the 2011 NC notes and the Gate 1 briefs: one note restates the contract; one adds useful structure; one substitutes a prettier tape and calls it frozen.

## Unified object (screening only)

`SE-AIS-01` = operating state of *existing* wet infrastructure, from a public
AIS point tape, versus independently documented physical opening of
*incremental* marine civil works.

- **A:** USCG NAIS → NOAA/BOEM Marine Cadastre bulk points, calendar 2009+.
- **B:** construction handover + first commercial working call, from
  operator / port-authority / USACE engineering record. Not AIS occupancy
  of a new polygon.
- **Independence:** I3 provisional. Not I4.
- **Not frozen.** Rule, polygons, port universe, missingness, `h` are unwritten.

Hydrology is a **family**, not one pair. Note 1’s B is first potable water.
Note 2’s B is dam/reservoir operation. Note 3’s B is spillway-gate actuation
(then rejected). Do not collapse them.

## Keep (law)

1. **Different filenames are not independence.** Independence is different
   physical objects, collection mechanisms, clocks, retention, and revision,
   with no shared upstream inventory required to build either side.
2. **AIS occupancy of a new polygon is I1.** That collapses A and B onto the
   same radio inventory. Event evidence may not consult AIS.
3. **DWT is not in the AIS sentence.** A deadweight join is a ship-registry
   inventory. Forbidden as `S_t`.
4. **Archive existence ≠ availability at `t`.** Cadastre proves points were
   emitted. It does not prove a researcher could have written a frozen
   congestion state at `t`. Derived waiting-time was not an official statistic.
5. **Polygons, universe, missingness, `S_t` rule, and `h` freeze blind to `E`,
   or the pair dies.** None of the notes did that.
6. **Imputation of 2009–2014 coverage holes is forbidden.** Drop the port.
7. **Waiting time is a family.** Anchorage count, queue hours, berth dwell,
   turnaround are different states. Until one rule is frozen, state
   determinism fails.
8. **Restricting to US Cadastre after seeing global ports is geography shopping.**
9. **“Zero shared infrastructure” is false until proven.** Harbour Master, VTS,
   and NTM often consume AIS. That is why the class is I3, not I4.
10. **USGS gages are a clean A.** Pairing a drought with the plant later built
    is selection. Fill vs O&M vs first water vs gate actuation are different
    events. Approved-vs-provisional rating-curve revision kills `S_t` if the
    approved series is used as if it were first-print.
11. **EIA-860 COD plus EIA operations is I1.** Many tables are not an architecture.
12. **FAA deregistration is administrative.** Not physical retirement.
13. **One famous episode is not an architecture.** Panama 2016. Newt Graham 1970
    is also pre-AIS (public Cadastre starts 2009) — illegal as the AIS example.
14. **`CANDIDATE_FOR_FREEZE` requires the rule, universe, polygons, missingness,
    event definition, and contemporaneous availability already written.** They
    are not. Gatekeeper ≠ freeze.
15. **E1.I stays local FAIL.** This search does not reopen WPSR, `{A,B,U}`,
    BR-0001, or `e1i_vintages.ok`.

## Dismiss

| Item | Why |
|---|---|
| `CANDIDATE_FOR_FREEZE` for CAND-0001 | State rule, polygons, universe, missingness, `h` unfrozen. Vintage of derived `S_t` not clean. |
| Independence I4 | Same-port-complex risk; VTS/NTM may read AIS; polygons are a human overlay. I3 under bans, else I1. |
| Spire / Orbcomm / “immutable NMEA at t+1h” | Licensed commercial tape. Protocol refuses licensed cubes. Public family is Marine Cadastre. |
| DWT-megaton `S_t` | Registry join, not AIS. |
| AIS-first-occupancy as `E` | Restatement of A. |
| Outcome-driven port or plant lists | Circular selection. Kill question 7. |
| Imputation of missing AIS days | Protocol. |
| Note 2’s Newt Graham 1970 as the AIS pair | Event before the public tape. |
| Ranking AIS vs hydrology vs highway | Attractiveness is not measurement. winner = none. |
| C-RIG, C-ISO, C-ADS, C-NUC, C-CAN, MEP-004, MEP-005, CAND-0002, CAND-0003, CAND-0004 | Shared inventory, admin event, missing tape, single episode, or revision kill. |
| Reopening E1.I / scoring BR-0001 / Wave 1 / HOU-1 / Force 4 / FS-0002 / capital | Unchanged refusals. |
| Drawing polygons or ingesting AIS this pass | That is the freeze. It has not been authorized. |

## What this pass actually established

| Claim | Result |
|---|---|
| Broader architecture “impossible” | **False.** Independent A/B *can* be stated. That was the question after E1.I-local FAIL. |
| A freeze-worthy experiment | **Not produced.** |
| AIS → new civil works | `CANDIDATE_FOR_GATEKEEPER`. Seed = false. |
| Hydrology family | `PARTIAL`. Independence benchmark. Do not promote. |
| Highway loading → bridge open | `SCREENING`. Station-level vintage unsolved. |
| Winner | **none** |
| n_seeds | **0** |

## Hostile questions (from Note 1; they still bind)

1. If the first commercial vessel is known only because AIS shows it stopped
   there, is B independent of A? **No → I1 → die.**
2. Who publishes a contemporaneous commissioning date that does not originate
   in a terminal system that also consumes AIS?
3. Can the port universe and anchorage polygons be written from pre-2010 charts
   and official limits, with no later satellite/AIS-derived boundary?
4. Missingness 2009–2014: drop the port, or impute? Imputation dies.
5. Is “waiting time” one state or an unbounded family?
6. Does restricting to US Cadastre secretly change the geography after the fact?
7. How is `h` chosen without looking at when berths opened?
8. Name the pre-registered ports that must be kept even if they never expand.
9. Is first working call physical completion, or still “open” on paper?
10. If any of 1, 3, 4 (impute), 5, or 7 is yes, the output is `NO_RESULT`,
    not a repaired proxy.

None of those are answered this pass. Answering them from public documentation,
without polygons and without ingest, is the only later ACK. Silent default =
stay frozen.

## Next

`stay_frozen`

Optional later ACK (not this receipt): `ais_gatekeeper_docs_only_or_no_result`.

Do not freeze. Do not ingest AIS. Do not score. Do not open E1.I.
n_seeds=0. Capital $0.
