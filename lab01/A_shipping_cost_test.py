# Joshua Evans (thejoshuaevans.com)
"""Tests for the Lab 1 (Group A, Part 1) shipping cost calculator."""

import pytest
from A_shipping_cost import calculate_shipping_cost


@pytest.mark.parametrize(
    ("weight_kg", "zone", "expected_cost"),
    [
        # Zone A
        (0.5, "A", 10.00),
        (5, "A", 10.00),
        (5.01, "A", 15.00),
        (10, "A", 15.00),
        (10.01, "A", 20.00),
        (50, "A", 20.00),
        # Zone B
        (0.5, "B", 15.00),
        (5, "B", 15.00),
        (5.01, "B", 20.00),
        (10, "B", 20.00),
        (10.01, "B", 25.00),
        (50, "B", 25.00),
        # Zone C
        (0.5, "C", 20.00),
        (5, "C", 20.00),
        (5.01, "C", 25.00),
        (10, "C", 25.00),
        (10.01, "C", 30.00),
        (50, "C", 30.00),
    ],
)
def test_rate_table(weight_kg, zone, expected_cost):
    """All values enumerated in the spec table should be correct"""
    assert calculate_shipping_cost(weight_kg, zone) == expected_cost


@pytest.mark.parametrize(
    ("weight_kg", "zone", "expected_cost"),
    [
        pytest.param(7.5, "A", 15.00, id="zone-A-7.5kg"),
        pytest.param(12.0, "C", 30.00, id="zone-C-12kg"),
    ],
)
def test_original_program_examples(weight_kg, zone, expected_cost):
    """All the examples from the original program should be correct"""
    assert calculate_shipping_cost(weight_kg, zone) == expected_cost


@pytest.mark.parametrize("zone", ["a", "b", "c"])
def test_zone_is_case_insensitive(zone):
    """Lower-case zones should be accepted"""
    assert calculate_shipping_cost(1, zone) == calculate_shipping_cost(1, zone.upper())


@pytest.mark.parametrize("zone", ["D", "", "AB", "1"])
def test_invalid_zone_raises(zone):
    """An invalid zone should raise a value error"""
    with pytest.raises(ValueError):
        calculate_shipping_cost(1, zone)
