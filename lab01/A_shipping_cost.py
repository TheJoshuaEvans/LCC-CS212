# Joshua Evans (thejoshuaevans.com)
# Instructions:
# https://lcc-cit.github.io/CS212-CourseMaterials/Labs/Lab01-Python/GroupA/CS212_Lab01_Instructions_GroupA.html
# Shipping Cost Calculator

# This program calculates the shipping cost based on the package’s Weight (in kg) and
# the Destination Zone (A, B, or C). The system must apply base costs and surcharges
# using the following tiered structure:
# Zone 	Weight ≤5 kg 	5 < Weight ≤10 kg 	Weight > 10 kg
# A 	$10.00 	        $15.00 	            $20.00
# B 	$15.00 	        $20.00 	            $25.00
# C 	$20.00 	        $25.00 	            $30.00
#
# Translate the program from either JavaScript or C# into Python

zone_base_costs_dollars = {"A": 10.00, "B": 15.00, "C": 20.00}
"""Base shipping cost for each destination zone."""

weight_tier_breakpoints = {"1->2": 5.0, "2->3": 10.0}
"""Values that define the boundary between weight tiers"""

weight_tier_surcharge_dollars = [0.00, 5.00, 10.00]
"""Additional charge based on the weight tier"""


def _get_weight_tier(weight_kg: float) -> int:
    """Get the weight tier of a weight value in kg

    Args:
        weight_kg (float): The weight of the package in kilograms.

    Returns:
        int: The weight tier, 0, 1, or 2
    """
    if weight_kg <= weight_tier_breakpoints["1->2"]:
        return 0
    if weight_kg <= weight_tier_breakpoints["2->3"]:
        return 1
    return 2


def calculate_shipping_cost(weight_kg: float, zone: str) -> float:
    """Calculate the shipping cost based on weight and destination zone.

    Args:
        weight_kg (float): The weight of the package in kilograms.
        zone (str): The destination zone ("A", "B", or "C").

    Returns:
        float: The total shipping cost in dollars.
    """
    zone = zone.capitalize()  # Normalize zone

    # Validation
    if zone not in zone_base_costs_dollars:
        raise ValueError(
            f"Zone must be one of {list(zone_base_costs_dollars.keys())}, got '{zone}'"
        )

    total_cost_dollars = (
        zone_base_costs_dollars[zone]
        + weight_tier_surcharge_dollars[_get_weight_tier(weight_kg)]
    )
    return total_cost_dollars
