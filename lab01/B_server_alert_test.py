# Joshua Evans (thejoshuaevans.com)
"""Tests for the Lab 1 (Group B, Part 2) server status and priority alert system."""

import pytest
from B_server_alert import get_alert_priority


@pytest.mark.parametrize(
    ("health_code", "hours_since_check", "expected_priority"),
    [
        # Code 1 is Critical: time doesn't matter
        (1, 0, "HIGH"),
        (1, 4, "HIGH"),
        (1, 100, "HIGH"),
        # Code 2 is Warning: HIGH after 4 hours
        (2, 0, "MEDIUM"),
        (2, 4, "MEDIUM"),
        (2, 4.01, "HIGH"),
        (2, 100, "HIGH"),
        # Code 3 is Optimal: LOW after 10 hours
        (3, 0, "CLEAR"),
        (3, 10, "CLEAR"),
        (3, 10.01, "LOW"),
        (3, 100, "LOW"),
    ],
)
def test_priority_table(health_code, hours_since_check, expected_priority):
    """Every row of the spec table, on both sides of each hour boundary"""
    assert get_alert_priority(health_code, hours_since_check) == expected_priority


@pytest.mark.parametrize("health_code", [0, 4, -1])
def test_invalid_health_code_raises(health_code):
    """A health code other than 1, 2, or 3 should raise a value error"""
    with pytest.raises(ValueError):
        get_alert_priority(health_code, 1)


@pytest.mark.parametrize("hours_since_check", [-1, -0.01])
def test_negative_hours_raises(hours_since_check):
    """A negative time since last check should raise a value error"""
    with pytest.raises(ValueError):
        get_alert_priority(3, hours_since_check)
