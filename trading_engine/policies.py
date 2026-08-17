"""
Trading decision policies.

Three modes:
- full_autonomy: execute without human
- require_approval: every proposal needs explicit human approval
- timed_window: human has a window; after timeout → go-ahead or no-go
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PolicyMode(str, Enum):
    FULL_AUTONOMY = "full_autonomy"
    REQUIRE_APPROVAL = "require_approval"
    TIMED_WINDOW = "timed_window"


@dataclass
class PolicyConfig:
    mode: PolicyMode = PolicyMode.REQUIRE_APPROVAL
    # For timed_window only
    window_minutes: int = 60
    # After timeout: True = go-ahead (execute), False = no-go (cancel)
    timeout_go_ahead: bool = False
    # Optional human identifier / channel for notifications
    human_channel: Optional[str] = None

    def to_dict(self):
        return {
            "mode": self.mode.value,
            "window_minutes": self.window_minutes,
            "timeout_go_ahead": self.timeout_go_ahead,
            "human_channel": self.human_channel,
        }
