"""Back-compat wrapper. Canonical report is validation_report.build()."""
from __future__ import annotations

from typing import Any, Dict

from .validation_report import build


def report_fs0001() -> Dict[str, Any]:
    return build()
