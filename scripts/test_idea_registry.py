#!/usr/bin/env python3
"""Idea Observatory: empty is success. Cousins, tickers, quota, prosecutor imports refused."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_ideas.ids import next_seed_id  # noqa: E402
from force_ideas.screen import (  # noqa: E402
    ScreenError,
    assert_no_prosecutor_imports,
    empty_registry_is_success,
    registry_status,
    screen_card,
)

PROV = {
    "origin_date": "2026-09-04",
    "origin_source": "unit-test",
    "original_observation": "A persistent reporting lag is visible in a public statistic versus a physical count.",
    "why_this_exists": "The two measures disagree and the disagreement is not one print.",
    "version": 1,
}


def test_empty_or_admitted_cannot_promote():
    st = empty_registry_is_success()
    assert st["min_seeds"] == 0
    assert st["max_seeds"] == 8
    assert st["n_seeds"] <= 8
    assert st["no_result_is_success"] is True
    assert st["capital"] == 0
    assert st["promotion"] == "NOT_PERMITTED"
    if st["n_seeds"] == 0 and st["n_frozen"] == 0:
        assert st["empty"] is True
        assert st["evidence_status"] == "no_result"
    print("PASS registry cannot promote (empty or admitted)")


def test_next_id():
    nxt = next_seed_id(ROOT / "force_ideas")
    assert nxt.startswith("FS-")
    if (ROOT / "force_ideas" / "seeds" / "FS-0001.yaml").exists():
        assert nxt != "FS-0001"
    print("PASS next id does not collide with existing seeds")


def test_valid_seed_admits():
    card = {
        "state": "seed",
        "seed_id": "FS-0001",
        "origin_type": "measurement_discontinuity",
        "phenomenon": "A real-world process is changing faster than the official statistic that capital uses.",
        "mechanism": "Reporting lag delays the information that allocators act on.",
        "failure_condition": "If the official series is revised coincident with the process, the idea dies.",
        "independence_note": "Not F1 memory, not F2 power, not F3 longevity, not F4 defense.",
        "tickers": [],
        "scannable": False,
        "capital": 0,
        "cannot_promote": True,
        **PROV,
    }
    out = screen_card(card, writing_to="seeds")
    assert out["verdict"] == "admit"
    assert out["promotion"] == "NOT_PERMITTED"
    assert out["freeze_ready"] is False
    print("PASS valid seed admits and is not freeze-ready")


def test_missing_observation_refused():
    card = {
        "state": "seed",
        "seed_id": "FS-0002",
        "origin_type": "contradiction",
        "phenomenon": "credentialing delays persist",
        "failure_condition": "if licenses issue in days",
        "origin_date": "2026-09-04",
        "tickers": [],
        "capital": 0,
        "cannot_promote": True,
        "version": 1,
    }
    try:
        screen_card(card)
        raise AssertionError("should refuse missing observation")
    except ScreenError as e:
        assert "provenance" in str(e).lower() or "observation" in str(e).lower()
    print("PASS missing original_observation refused")


def test_ticker_refused():
    card = {
        "state": "seed",
        "seed_id": "FS-0003",
        "origin_type": "contradiction",
        "phenomenon": "something persistent about logistics contracts",
        "failure_condition": "if contracts reprice annually without lag",
        "tickers": ["AAPL"],
        "capital": 0,
        "cannot_promote": True,
        **PROV,
    }
    try:
        screen_card(card)
        raise AssertionError("should refuse tickers")
    except ScreenError as e:
        assert "tickers" in str(e).lower()
    print("PASS tickers on a seed refused")


def test_force4_refused():
    card = {
        "state": "seed",
        "seed_id": "FS-0004",
        "origin_type": "policy",
        "phenomenon": "ITA/XAR/PPA as a sovereign capacity Force",
        "failure_condition": "n/a",
        "tickers": ["ITA", "XAR"],
        "capital": 0,
        "cannot_promote": True,
        **PROV,
    }
    try:
        screen_card(card)
        raise AssertionError("should refuse Force 4")
    except ScreenError as e:
        msg = str(e).lower()
        assert "wait" in msg or "cousin" in msg or "ita" in msg
    print("PASS Force 4 / ITA refused")


def test_f2_cousin_refused():
    card = {
        "state": "seed",
        "seed_id": "FS-0005",
        "origin_type": "physical_constraint",
        "phenomenon": "Data center power and GPU power shortages redistribute value along the grid.",
        "failure_condition": "if interconnect queues clear in months",
        "tickers": [],
        "capital": 0,
        "cannot_promote": True,
        **PROV,
    }
    try:
        screen_card(card)
        raise AssertionError("should refuse F2 cousin")
    except ScreenError as e:
        assert "cousin" in str(e).lower()
    print("PASS F2 neighborhood cousin refused")


def test_ir_on_seed_refused():
    card = {
        "state": "seed",
        "seed_id": "FS-0006",
        "origin_type": "contradiction",
        "phenomenon": "institutional budgeting cycles lag physical orders",
        "failure_condition": "if budgets reprice continuously",
        "observed_ir": 0.7,
        "tickers": [],
        "capital": 0,
        "cannot_promote": True,
        **PROV,
    }
    try:
        screen_card(card)
        raise AssertionError("should refuse IR")
    except ScreenError as e:
        assert "ir" in str(e).lower() or "statistic" in str(e).lower()
    print("PASS IR on a seed refused")


def test_missing_origin_refused():
    card = {
        "state": "seed",
        "seed_id": "FS-0007",
        "phenomenon": "a persistent bottleneck in credentialing",
        "failure_condition": "if licensing becomes instantaneous",
        "tickers": [],
        "capital": 0,
        "cannot_promote": True,
        **PROV,
    }
    try:
        screen_card(card)
        raise AssertionError("should refuse missing origin_type")
    except ScreenError as e:
        assert "origin_type" in str(e)
    print("PASS missing origin_type refused")


def test_seed_cap():
    tmp = ROOT / "force_ideas" / "_tmp_cap"
    if tmp.exists():
        shutil.rmtree(tmp)
    (tmp / "seeds").mkdir(parents=True)
    shutil.copy(ROOT / "force_ideas" / "registry.yaml", tmp / "registry.yaml")
    for i in range(8):
        (tmp / "seeds" / f"s{i}.yaml").write_text("state: seed\n")
    card = {
        "state": "seed",
        "seed_id": "FS-0008",
        "origin_type": "human_observation",
        "phenomenon": "credentialing bottlenecks persist across cycles",
        "failure_condition": "if licenses issue in days",
        "tickers": [],
        "capital": 0,
        "cannot_promote": True,
        **PROV,
    }
    try:
        screen_card(card, registry_root=tmp, writing_to="seeds")
        raise AssertionError("9th seed should refuse")
    except ScreenError as e:
        assert "cap" in str(e).lower() or "quota" in str(e).lower()
    shutil.rmtree(tmp)
    print("PASS 9th seed refused (max 8, no quota)")


def test_hypothesis_without_t4_not_freeze_ready():
    card = {
        "state": "hypothesis",
        "hypothesis_id": "friction_budgeting",
        "origin_type": "institutional_friction",
        "hypothesis": "Capital budgeting cycles delay reallocation after a persistent constraint appears.",
        "mechanism": "Annual capex calendars and committee mandates slow the response.",
        "observables": [
            {"name": "capex_authorizations", "predicted_sign": 1, "lead": "leading"}
        ],
        "independence_dimensions": [{"kind": "instrument", "note": "not enough alone"}],
        "failure_condition": "if reallocation is continuous",
        "tickers": [],
        "capital": 0,
        "cannot_promote": True,
        **PROV,
    }
    out = screen_card(card, writing_to="hypotheses")
    assert out["verdict"] == "admit"
    assert out["freeze_ready"] is False
    assert any("T4" in m for m in out["missing_for_freeze"])
    print("PASS T4 missing keeps freeze_ready false")


def test_frozen_version_immutable():
    tmp = ROOT / "force_ideas" / "_tmp_frozen"
    if tmp.exists():
        shutil.rmtree(tmp)
    (tmp / "frozen").mkdir(parents=True)
    shutil.copy(ROOT / "force_ideas" / "registry.yaml", tmp / "registry.yaml")
    (tmp / "frozen" / "FS-0001.v1.yaml").write_text("seed_id: FS-0001\nversion: 1\n")
    card = {
        "state": "frozen",
        "seed_id": "FS-0001",
        "hypothesis_id": "FS-0001",
        "origin_type": "contradiction",
        "hypothesis": "A named mechanism that is long enough to count.",
        "mechanism": "Institutions reallocate only on annual calendars.",
        "tickers": [],
        "capital": 0,
        "cannot_promote": True,
        **PROV,
    }
    try:
        screen_card(card, registry_root=tmp, writing_to="frozen")
        raise AssertionError("should refuse mutate")
    except ScreenError as e:
        assert "immutable" in str(e).lower() or "frozen" in str(e).lower()
    shutil.rmtree(tmp)
    print("PASS frozen FS-0001 v1 is immutable")


def test_fs0001_admitted_no_tickers():
    from force_ideas.screen import screen_path
    from force_engine.freeze import load_freeze

    seed = ROOT / "force_ideas" / "seeds" / "FS-0001.yaml"
    hyp = ROOT / "force_ideas" / "hypotheses" / "FS-0001.yaml"
    freeze_path = ROOT / "config" / "hypotheses" / "FS-0001.yaml"
    assert seed.exists() and hyp.exists() and freeze_path.exists()
    s = screen_path(seed, writing_to="seeds")
    assert s["verdict"] == "admit"
    assert s["freeze_ready"] is False
    h = screen_path(hyp, writing_to="hypotheses")
    assert h["verdict"] == "admit"
    assert h["freeze_ready"] is True, h.get("missing_for_freeze")
    fh = load_freeze(freeze_path)
    assert fh.freeze_complete is True
    assert fh.tickers == []
    assert fh.hypothesis_id == "FS-0001"
    assert not any(o.lead == "leading" for o in fh.observables) or True
    assert any(o.lead == "leading" for o in fh.observables)
    st = empty_registry_is_success()
    assert st["n_seeds"] >= 1
    assert st["awaiting_t5"] is True
    assert st["cannot_promote"] is True
    assert st["capital"] == 0
    print("PASS FS-0001 admitted, T0–T4 complete, tickers empty, awaiting T5")


def test_no_prosecutor_imports():
    assert_no_prosecutor_imports()
    print("PASS gatekeeper does not import evaluate/neutralize/pipeline")


def test_status_matches_yaml():
    st = registry_status()
    spec = yaml.safe_load((ROOT / "force_ideas" / "registry.yaml").read_text())
    assert st["max_seeds"] == spec["max_seeds"] == 8
    assert spec["min_seeds"] == 0
    print("PASS registry yaml lock (max 8, min 0)")


def main():
    test_empty_or_admitted_cannot_promote()
    test_next_id()
    test_valid_seed_admits()
    test_missing_observation_refused()
    test_ticker_refused()
    test_force4_refused()
    test_f2_cousin_refused()
    test_ir_on_seed_refused()
    test_missing_origin_refused()
    test_seed_cap()
    test_hypothesis_without_t4_not_freeze_ready()
    test_frozen_version_immutable()
    test_fs0001_admitted_no_tickers()
    test_no_prosecutor_imports()
    test_status_matches_yaml()
    print("ALL IDEA-REGISTRY TESTS PASSED")


if __name__ == "__main__":
    main()
