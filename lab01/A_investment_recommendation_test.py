# Joshua Evans (thejoshuaevans.com)
"""Tests for the Lab 1 (Group A, Part 2) financial product recommendation system."""

import pytest
from A_investment_recommendation import recommend_product


@pytest.mark.parametrize(
    ("horizon_years", "risk_tolerance", "expected_product"),
    [
        # Short-Term (< 5 years)
        (0, "Low", "High-Yield Savings Account"),
        (4.99, "Low", "High-Yield Savings Account"),
        (0, "High", "Short-Term Corporate Bonds"),
        (4.99, "High", "Short-Term Corporate Bonds"),
        # Long-Term (>= 5 years)
        (5, "Low", "Government Bonds/Index Fund"),
        (30, "Low", "Government Bonds/Index Fund"),
        (5, "High", "Diversified Stock Portfolio"),
        (30, "High", "Diversified Stock Portfolio"),
    ],
)
def test_recommendation_table(horizon_years, risk_tolerance, expected_product):
    """Every row of the spec table, including both sides of the 5-year boundary"""
    assert recommend_product(horizon_years, risk_tolerance) == expected_product


@pytest.mark.parametrize("risk_tolerance", ["low", "HIGH", "hIgH"])
def test_risk_tolerance_is_case_insensitive(risk_tolerance):
    """Risk tolerance should be accepted in any case"""
    assert recommend_product(10, risk_tolerance) == recommend_product(
        10, risk_tolerance.capitalize()
    )


@pytest.mark.parametrize("risk_tolerance", ["Medium", "", "L", "Low-High"])
def test_invalid_risk_tolerance_raises(risk_tolerance):
    """A risk tolerance other than Low or High should raise a value error"""
    with pytest.raises(ValueError):
        recommend_product(10, risk_tolerance)


@pytest.mark.parametrize("horizon_years", [-1, -0.01])
def test_negative_horizon_raises(horizon_years):
    """A negative investment horizon should raise a value error"""
    with pytest.raises(ValueError):
        recommend_product(horizon_years, "LOW")
