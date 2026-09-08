#!/usr/bin/env python3
"""NO_RESULT is terminal. Not a prompt to attach tickers."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_engine.freeze import FreezeError, attach_instruments, load_freeze
from force_ideas.state import (
    StateError,
    assert_capital_zero,
    assert_freight_v1_immutable,
    assert_no_result_terminal,
    assert_prosecutor_forbidden,
    assert_transition,
    fs0001_desk,
)
from force_ideas.t5_gate import t5_unlock_or_reason


def test_desk():
    d = fs0001_desk()
    assert d["status"] == "FROZEN"
    assert d["t5_status"] == "NO_RESULT"
    assert d["t5_ready"] is False
    assert d["instruments"] == []
    assert d["scannable"] is False
    assert d["prosecutor_allowed"] is False
    assert d["capital"] == 0
    assert d["research_state"] == "T5_NO_RESULT"
    print("PASS FS-0001 desk is FROZEN / T5 NO_RESULT")


def test_terminal_transitions():
    assert_transition("SEED", "HYPOTHESIS")
    assert_transition("FROZEN", "T5_NO_RESULT")
    try:
        assert_transition("T5_NO_RESULT", "T5_READY")
        raise AssertionError("NO_RESULT must not promote to T5_READY")
    except StateError:
        pass
    try:
        assert_transition("T5_NO_RESULT", "SCANNABLE")
        raise AssertionError("NO_RESULT must not become scannable")
    except StateError:
        pass
    try:
        assert_transition("T5_NO_RESULT", "PROSECUTOR")
        raise AssertionError("NO_RESULT must not invoke prosecutor")
    except StateError:
        pass
    print("PASS T5_NO_RESULT is terminal")


def test_guards():
    assert_no_result_terminal()
    assert_prosecutor_forbidden()
    assert_capital_zero()
    assert_freight_v1_immutable()
    print("PASS NO_RESULT / prosecutor / capital / freight-v1 guards")


def test_attach_still_locked():
    fh = load_freeze(ROOT / "config" / "hypotheses" / "FS-0001.yaml")
    try:
        attach_instruments(fh, ["AAA"], ["SPY"])
        raise AssertionError("attach must fail")
    except FreezeError:
        pass
    ok, _ = t5_unlock_or_reason("FS-0001")
    assert ok is False
    print("PASS attach_instruments locked while t5_ready=false")


def test_quarter_ledger():
    p = ROOT / "force_learning" / "research_outcomes" / "2026-Q3.md"
    text = p.read_text()
    assert "NO_RESULT" in text
    assert "Capital: $0" in text
    assert "Hypothesis rescue: none" in text
    print("PASS 2026-Q3 ledger records NO_RESULT")


def test_frozen_yaml_not_rewritten():
    text = (ROOT / "force_ideas" / "frozen" / "FS-0001.v1.yaml").read_text()
    assert "t5_quarter_lock" not in text
    assert "T5 not attached" in text
    print("PASS frozen YAML not used as the operational overlay")


def main():
    test_desk()
    test_terminal_transitions()
    test_guards()
    test_attach_still_locked()
    test_quarter_ledger()
    test_frozen_yaml_not_rewritten()
    print("ALL NO-RESULT-LOCK TESTS PASSED")



if __name__ == "__main__":
    main()
