#!/usr/bin/env python3
"""Canonical research path → one EvidenceRecord. Cannot promote. Cannot scan Force 4."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_engine.evidence import no_result_record, record_from_residual, refuse_promote
from force_engine.neighbor import load_paused_residual_csv


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--candidate", default="", help="force_id for a stored residual (f1/f2/f3) or empty for NO_RESULT")
    p.add_argument("--csv", default="", help="optional residual csv")
    p.add_argument("--column", default="")
    p.add_argument("--n-sign", type=int, default=400)
    p.add_argument("--n-block", type=int, default=200)
    p.add_argument("--promote", action="store_true")
    p.add_argument("--scan-force4", action="store_true")
    args = p.parse_args()

    if args.promote:
        try:
            refuse_promote()
        except Exception as e:
            print(f"REFUSED: {e}")
            return 2
    if args.scan_force4:
        print("REFUSED: Force 4 remains WAIT.")
        return 2

    if not args.candidate and not args.csv:
        rec = no_result_record()
        out = ROOT / "data" / "meta" / "evidence_no_result.json"
        out.write_text(json.dumps(rec.to_dict(), indent=2, default=str))
        print(json.dumps({k: rec.to_dict()[k] for k in ("candidate_id", "evidence_status", "promotion", "capital")}, indent=2))
        print(f"wrote {out}")
        print("NO_RESULT is a successful research period. Capital $0.")
        return 0

    csv = Path(args.csv) if args.csv else None
    col = args.column or None
    if csv is None:
        defaults = {
            "f1": (ROOT / "data" / "force1" / "force1_factor_residualized.csv", "factor_clean_resid"),
            "f2": (ROOT / "data" / "force2" / "force2_walkforward_daily.csv", "resid_gross"),
            "f3": (ROOT / "data" / "force3" / "force3_daily_residual.csv", "resid_oos_hedged"),
        }
        if args.candidate not in defaults:
            print("REFUSED: unknown candidate. Do not scan Force 4. Use --csv or f1/f2/f3.")
            return 2
        csv, col = defaults[args.candidate]
    resid = load_paused_residual_csv(csv, column=col)
    if resid is None or resid.empty:
        print(f"REFUSED: residual missing at {csv}")
        return 2
    rec = record_from_residual(
        resid,
        candidate_id=args.candidate or csv.stem,
        source=str(csv),
        n_sign=args.n_sign,
        n_block=args.n_block,
    )
    out = ROOT / "data" / "meta" / f"evidence_{rec.candidate_id}.json"
    out.write_text(json.dumps(rec.to_dict(), indent=2, default=str))
    summary = {
        "candidate_id": rec.candidate_id,
        "evidence_status": rec.evidence_status,
        "vetoes": rec.vetoes,
        "promotion": rec.promotion,
        "observed_ir": rec.observed_ir,
        "protocol_id": rec.protocol_id,
        "code_commit": rec.provenance.get("code_commit"),
    }
    print(json.dumps(summary, indent=2, default=str))
    print(f"wrote {out}")
    print("PROMOTION=NOT_PERMITTED. Capital $0.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
