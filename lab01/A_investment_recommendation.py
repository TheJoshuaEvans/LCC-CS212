# Joshua Evans (thejoshuaevans.com)
# Instructions:
# https://lcc-cit.github.io/CS212-CourseMaterials/Labs/Lab01-Python/GroupA/CS212_Lab01_Instructions_GroupA.html
# Financial Product Recommendation System

# Create a simplified expert system that recommends a suitable investment product
# based on two factors provided by the user: Investment Horizon (Short-Term: <5 years,
# or Long-Term: ≥5 years) and Risk Tolerance (Low or High).
# Horizon       Risk Tolerance  Recommended Product
# Short-Term    Low             High-Yield Savings Account
# Short-Term    High            Short-Term Corporate Bonds
# Long-Term     Low             Government Bonds/Index Fund
# Long-Term     High            Diversified Stock Portfolio

product_names = {
    "high_yield": "High-Yield Savings Account",
    "short_term": "Short-Term Corporate Bonds",
    "government": "Government Bonds/Index Fund",
    "diverse": "Diversified Stock Portfolio",
}
"""Full names of the available products"""

term_breakpoint_years = 5.0
"""Number of years after which investments are considered long term"""

tolerance_levels = {"low": "Low", "high": "High"}
"""Valid tolerance levels"""


def recommend_product(horizon_years: float, risk_tolerance: str) -> str:
    """Recommend an investment product based on horizon and risk tolerance.

    Args:
        horizon_years (float): The investment horizon in years.
        risk_tolerance (str): The investor's risk tolerance ("Low" or "High").

    Returns:
        str: The name of the recommended product.

    Raises:
        ValueError: If horizon_years is negative or risk_tolerance is not
            "Low" or "High".
    """
    risk_tolerance = risk_tolerance.capitalize()

    # Validation
    if risk_tolerance not in tolerance_levels.values():
        raise ValueError(
            f"Invalid risk tolerance. Expected one of {list(tolerance_levels.values())}, got {risk_tolerance}"
        )
    if horizon_years < 0:
        raise ValueError(
            f"Invalid investment horizon. Must be greater than or equal 0, got {horizon_years}"
        )

    result = ""
    if horizon_years < term_breakpoint_years:
        # Short term
        if risk_tolerance == tolerance_levels["low"]:
            result = product_names["high_yield"]
        else:  # High tolerance
            result = product_names["short_term"]
    else:
        # Short term
        if risk_tolerance == tolerance_levels["low"]:
            result = product_names["government"]
        else:  # High tolerance
            result = product_names["diverse"]

    return result
