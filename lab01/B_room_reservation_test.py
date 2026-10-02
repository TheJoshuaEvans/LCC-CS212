# Joshua Evans (thejoshuaevans.com)
"""Tests for the Lab 1 (Group B, Part 1) meeting room reservation system."""

import sys

import pytest
from B_room_reservation import recommend_room

# The spec table and the original program word the rooms differently, so the
# tests only check how each recommendation starts.
ALPHA = "Room Alpha"
BETA = "Room Beta"
GAMMA = "Room Gamma"
DENIED = "Reservation Denied"


@pytest.mark.parametrize(
    ("attendees", "projector_needed", "expected_room"),
    [
        # Small (1-5): projector doesn't matter
        (1, False, ALPHA),
        (1, True, ALPHA),
        (5, False, ALPHA),
        (5, True, ALPHA),
        # Medium (6-15) with projector
        (6, True, BETA),
        (15, True, BETA),
        # Medium (6-15) without projector
        (6, False, GAMMA),
        (15, False, GAMMA),
        # Large (16+): projector doesn't matter
        (16, False, DENIED),
        (16, True, DENIED),
        (100, False, DENIED),
        (100, True, DENIED),
    ],
)
def test_room_table(attendees, projector_needed, expected_room):
    """Every row of the spec table, at both edges of each attendee range"""
    assert recommend_room(attendees, projector_needed).startswith(expected_room)


@pytest.mark.parametrize(
    ("attendees", "projector_needed", "expected_room"),
    [
        pytest.param(4, False, ALPHA, id="4-no-projector"),
        pytest.param(12, True, BETA, id="12-projector"),
        pytest.param(10, False, GAMMA, id="10-no-projector"),
    ],
)
def test_original_program_examples(attendees, projector_needed, expected_room):
    """All the examples from the original program should be correct"""
    assert recommend_room(attendees, projector_needed).startswith(expected_room)


@pytest.mark.parametrize("attendees", [0, -1])
def test_invalid_attendees_raises(attendees):
    """Fewer than one attendee should raise a value error"""
    with pytest.raises(ValueError):
        recommend_room(attendees, False)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
