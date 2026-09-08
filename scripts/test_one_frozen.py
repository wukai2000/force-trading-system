#!/usr/bin/env python3
"""one_frozen_at_a_time: seeds unlimited (cap 8); only one FROZEN id."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_ideas.screen import ScreenError, screen_card
from force_ideas.state import active_frozen_forces

PROV = {
    "origin_type": "measurement_discontinuity",
    "origin_date": "2026-09-08",
    "origin_source": "unit-test",
    "original_observation": "A persistent reporting lag is visible in a public statistic versus a physical count.",
    "why_this_exists": "The two measures disagree and the disagreement is not one print.",
    "version": 1,
    "tickers": [],
    "scannable": False,
    "capital": 0,
    "cannot_promote": True,
}


def test_occupant_is_fs0001():
    ids = active_frozen_forces()
    assert ids == ["FS-0001"]
    print("PASS active_frozen_forces = [FS-0001]")


def test_second_freeze_refused():
    card = {
        "state": "frozen",
        "seed_id": "FS-0002",
        "hypothesis_id": "FS-0002",
        "phenomenon": "A second frozen hypothesis is not allowed while FS-0001 occupies the slot.",
        "mechanism": "one_frozen_at_a_time is a repository invariant, not a Notion note.",
        "failure_condition": "If a second freeze is admitted, the invariant is dead.",
        "independence_note": "Not F1 memory, not F2 power, not F3 longevity, not F4 defense.",
        **PROV,
    }
    try:
        screen_card(card, writing_to="frozen")
        raise AssertionError("second freeze must be refused")
    except ScreenError as e:
        assert "one frozen" in str(e).lower()
    print("PASS second frozen id refused")


def test_seed_still_admitted():
    card = {
        "state": "seed",
        "seed_id": "FS-0002",
        "phenomenon": "A real-world process is changing faster than the official statistic that capital uses.",
        "mechanism": "Reporting lag delays the information that allocators act on.",
        "failure_condition": "If the official series is revised coincident with the process, the idea dies.",
        "independence_note": "Not F1 memory, not F2 power, not F3 longevity, not F4 defense.",
        **PROV,
    }
    out = screen_card(card, writing_to="seeds")
    assert out["verdict"] == "admit"
    print("PASS new SEED still admitted while FS-0001 is frozen")


def main():
    test_occupant_is_fs0001()
    test_second_freeze_refused()
    test_seed_still_admitted()
    print("ALL ONE-FROZEN TESTS PASSED")


if __name__ == "__main__":
    main()
