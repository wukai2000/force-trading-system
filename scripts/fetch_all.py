#!/usr/bin/env python3
"""Refresh all Force 1 free streams (prices, FRED, COT) then rebuild weekly panel."""

from __future__ import annotations

import sys
from pathlib import Path

# allow running from repo root
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_learning.data.fetch_prices import update_prices
from force_learning.data.fetch_fred import update_macro
from force_learning.data.fetch_cot import update_cot
from force_learning.data.panel import build_weekly_panel


def main() -> None:
    print("=== Force 1 data refresh ===")
    print("-- prices --")
    update_prices()
    print("-- macro (FRED) --")
    update_macro()
    print("-- cot (CFTC TFF) --")
    update_cot()
    print("-- weekly panel --")
    build_weekly_panel()
    print("=== done ===")


if __name__ == "__main__":
    main()
