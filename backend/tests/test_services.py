"""Unit tests for pure business rules and appointment scheduling logic."""

from datetime import datetime

import pytest

from app.services import can_transition, end_time


@pytest.mark.parametrize(
    ("current", "new", "allowed"),
    [
        ("SCHEDULED", "CHECKED_IN", True),
        ("SCHEDULED", "CANCELLED", True),
        ("SCHEDULED", "NO_SHOW", True),
        ("SCHEDULED", "COMPLETED", False),
        ("CHECKED_IN", "COMPLETED", True),
        ("CHECKED_IN", "CANCELLED", True),
        ("COMPLETED", "CANCELLED", False),
        ("CANCELLED", "SCHEDULED", True),
        ("NO_SHOW", "SCHEDULED", True),
        ("CHECKED_IN", "CHECKED_IN", True),
    ],
)
def test_can_transition(current, new, allowed):
    assert can_transition(current, new) is allowed


def test_end_time_adds_duration():
    assert end_time(datetime(2030, 5, 10, 10, 15), 45) == datetime(2030, 5, 10, 11, 0)
