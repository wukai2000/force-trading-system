# EvidenceRecord — FORCE_PROTOCOL_v1.0

Locked 2026-09-04. Milestone: **Blind Falsification**, not “find a Force.”

The canonical research path is:

```
frozen protocol → residual → EvidenceRecord
```

It does **not** return PASS/FAIL as a screener. It returns three separate
objects:

| Concept | Meaning | Can promote? |
|---|---|---|
| **Evidence** | what we observed (IR, Null A percentile/p, Null B distributions, Conc B mass) | no |
| **Veto** | what contradicts a Force (Conc A kill, clock, spanning, mechanism-absent) | no |
| **Promotion** | always `NOT_PERMITTED` from code | — |

F2 is the demonstration: Null A p ≈ 0.032 (interesting) **and**
Conc A persist 0.435 (veto). Capital $0.

## What this package does

- `config/protocol.yaml` — version lock + hashes of locked files
- `config/negative_controls.yaml` — F1/F2/F3 fixtures
- `force_engine/evidence.py` — EvidenceRecord
- `force_engine/protocol.py` — commit + sha256 provenance
- `force_engine/ledger.py` — researcher intervention counts
- CI: `.github/workflows/research_contract.yml` (no live bars)

`evaluate_candidate` stays the **gate** path (synthetic tests, freeze
refuse). It is not replaced. The research path does not auto-call 5k
Null A draws inside that function.

## What this package does not do

- Invent a leftover to “prove the machinery” (P3 stays queued)
- Scan Force 4
- Let mechanism rescue statistics
- Fuse Null B into pass/fail
- Change Conc A
- Global controls for every Force (controls remain T5 after freeze)

## Commands

```
PYTHONPATH=. python scripts/test_negative_control_contract.py
PYTHONPATH=. python scripts/test_evidence_record.py
PYTHONPATH=. python scripts/run_evidence_record.py
PYTHONPATH=. python scripts/run_evidence_record.py --candidate f3
```

`--promote` and `--scan-force4` exit 2.

A quarter with no candidate:

```
evidence_status: no_result
promotion: NOT_PERMITTED
capital: 0
```

is a **successful** research period.
