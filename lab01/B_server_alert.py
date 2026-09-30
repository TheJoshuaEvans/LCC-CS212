# Joshua Evans (thejoshuaevans.com)
# Instructions:
# https://lcc-cit.github.io/CS212-CourseMaterials/Labs/Lab01-Python/GroupB/CS212_Lab01_Instructions_GroupB.html
# Server Status and Priority Alert

# Create a simplified system for monitoring a server cluster. The system uses a
# Health Code (1=Critical, 2=Warning, 3=Optimal) and the Time Since Last Check
# (in hours) to determine the required response priority.
# Health Code    Time Since Last Check (H)  Alert Priority
# 1 (Critical)   Any                        HIGH
# 2 (Warning)    >4 Hours                   HIGH
# 2 (Warning)    ≤4 Hours                   MEDIUM
# 3 (Optimal)    >10 Hours                  LOW
# 3 (Optimal)    ≤10 Hours                  CLEAR

from typing import Literal, NamedTuple

Priority = Literal["CLEAR", "LOW", "MEDIUM", "HIGH"]
"""Allowed priority strings"""


class HealthCode(NamedTuple):
    value: int
    """The integer health code identifier"""
    base_priority: Priority
    """The default priority level"""
    upgrades: bool = False
    """If the health code upgrades"""
    upgrades_in_hours: float = None
    """Number of hours until a stale code upgrades priority"""
    upgrades_to_priority: Priority = None
    """The new priority after the upgrade"""


health_codes = {
    1: HealthCode(1, "HIGH"),
    2: HealthCode(2, "MEDIUM", True, 4.0, "HIGH"),
    3: HealthCode(3, "CLEAR", True, 10.0, "LOW"),
}
"""Possible system health codes"""


def get_alert_priority(health_code: int, hours_since_check: float) -> str:
    """Determine the alert priority from a server's health and time since last check.

    Args:
        health_code (int): The server's health (1=Critical, 2=Warning, 3=Optimal).
        hours_since_check (float): Hours since the server was last checked.

    Returns:
        str: The alert priority ("HIGH", "MEDIUM", "LOW", or "CLEAR").

    Raises:
        ValueError: If health_code is not 1, 2, or 3, or hours_since_check is
            negative.
    """
    # Validation
    if health_code not in health_codes:
        raise ValueError(
            f"Health code must be one of {list(health_codes.keys())}, got {health_code}"
        )
    if hours_since_check < 0:
        raise ValueError(
            f"Hours since last check must be greater than 0, got {hours_since_check}"
        )

    provided_health_code = health_codes[health_code]
    if (
        provided_health_code.upgrades
        and hours_since_check > provided_health_code.upgrades_in_hours
    ):
        return provided_health_code.upgrades_to_priority
    else:
        return provided_health_code.base_priority
