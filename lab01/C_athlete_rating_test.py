# Joshua Evans (thejoshuaevans.com)
"""Tests for the Lab 1 (Group C, Part 2) athlete performance rating system."""

import sys

import pytest
from C_athlete_rating import rate_athlete


@pytest.mark.parametrize(
    ("speed_score", "strength_score", "expected_rating"),
    [
        # Elite: speed >= 90 AND strength >= 80
        (90, 80, "Elite"),
        (100, 100, "Elite"),
        # Just missing Elite still leaves Advanced
        (89, 80, "Advanced"),
        (90, 79, "Advanced"),
        # Advanced: speed >= 70 OR strength >= 70
        (70, 0, "Advanced"),
        (0, 70, "Advanced"),
        (70, 69, "Advanced"),
        (69, 70, "Advanced"),
        # Intermediate: speed of at least 50
        (50, 0, "Intermediate"),
        (69, 69, "Intermediate"),
        # Beginner: everything else
        (49, 69, "Beginner"),
        (0, 0, "Beginner"),
    ],
)
def test_rating_tiers(speed_score, strength_score, expected_rating):
    """Each tier, on both sides of every score boundary"""
    assert rate_athlete(speed_score, strength_score) == expected_rating


@pytest.mark.parametrize(
    ("speed_score", "strength_score"),
    [(-1, 50), (101, 50), (50, -1), (50, 101)],
)
def test_out_of_range_score_raises(speed_score, strength_score):
    """A score outside 0-100 should raise a value error"""
    with pytest.raises(ValueError):
        rate_athlete(speed_score, strength_score)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
