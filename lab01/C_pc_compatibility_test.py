# Joshua Evans (thejoshuaevans.com)
"""Tests for the Lab 1 (Group C, Part 1) PC component compatibility checker."""

import pytest
from C_pc_compatibility import check_compatibility

# The spec table says "Compatible"/"Incompatible" and the original program says
# "COMPATIBLE"/"INCOMPATIBLE (reason)", so the tests ignore case and only check
# how each result starts.
COMPATIBLE = "COMPATIBLE"
INCOMPATIBLE = "INCOMPATIBLE"


def _status(socket_type: str, ram_type: str) -> str:
    """Upper-cased result of check_compatibility, for comparing against the spec"""
    return check_compatibility(socket_type, ram_type).upper()


@pytest.mark.parametrize(
    ("socket_type", "ram_type", "expected_status"),
    [
        # LGA1700 needs DDR5
        ("LGA1700", "DDR5", COMPATIBLE),
        ("LGA1700", "DDR4", INCOMPATIBLE),
        # AM4 needs DDR4
        ("AM4", "DDR4", COMPATIBLE),
        ("AM4", "DDR5", INCOMPATIBLE),
        # Any other socket is incompatible with any RAM
        ("AM5", "DDR5", INCOMPATIBLE),
        ("LGA1200", "DDR4", INCOMPATIBLE),
        ("", "DDR5", INCOMPATIBLE),
    ],
)
def test_compatibility_table(socket_type, ram_type, expected_status):
    """Every row of the spec table, with both correct and incorrect RAM"""
    assert _status(socket_type, ram_type).startswith(expected_status)


@pytest.mark.parametrize(
    ("socket_type", "ram_type", "expected_status"),
    [
        pytest.param("LGA1700", "DDR5", COMPATIBLE, id="LGA1700-DDR5"),
        pytest.param("AM4", "DDR5", INCOMPATIBLE, id="AM4-DDR5"),
        pytest.param("am4", "ddr4", COMPATIBLE, id="am4-ddr4-lowercase"),
    ],
)
def test_original_program_examples(socket_type, ram_type, expected_status):
    """All the examples from the original program should be correct"""
    assert _status(socket_type, ram_type).startswith(expected_status)


@pytest.mark.parametrize(
    ("socket_type", "ram_type"),
    [("lga1700", "ddr5"), ("Am4", "Ddr4"), ("aM4", "dDR4")],
)
def test_input_is_case_insensitive(socket_type, ram_type):
    """Socket and RAM types should be accepted in any case"""
    assert _status(socket_type, ram_type).startswith(COMPATIBLE)
