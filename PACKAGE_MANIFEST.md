# force-trading-system-20260904-instrument

Snapshot of `/fts` at local commit after FORCE_PROTOCOL_v1.0.
Capital $0. Trump Account = SPYM. Force 4 WAIT. F1–F3 negative-control fixtures.

## Adds vs 20260902-null1

| Date | Content |
|---|---|
| 2026-09-03 | T2 leading-observable catalog (FRED veto-only; NLP/satellite refused) |
| 2026-09-04 | FORCE_PROTOCOL_v1.0: EvidenceRecord, negative-control contract, intervention ledger, CI research_contract.yml |

## Do not

- Scan Force 4 / ITA/XAR/PPA/XLI
- Unpause F1/F2/F3
- Invent a leftover to “prove” the evaluator
- Treat EvidenceRecord as PASS/FAIL
- Fuse Null B into a gate
- Auto-promote

## Commands

```
PYTHONPATH=. python scripts/test_negative_control_contract.py
PYTHONPATH=. python scripts/test_evidence_record.py
PYTHONPATH=. python scripts/run_evidence_record.py
```
