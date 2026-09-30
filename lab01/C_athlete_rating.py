# Joshua Evans (thejoshuaevans.com)
# Instructions:
# https://lcc-cit.github.io/CS212-CourseMaterials/Labs/Lab01-Python/GroupC/CS212_Lab01_Instructions_GroupC.html
# Athlete Performance Rating

# Design an expert system that assigns a performance Rating to an athlete based on
# their Speed Score (0-100) and Strength Score (0-100). The system must assign the
# highest applicable tier.
# - Elite: Speed Score ≥90 AND Strength Score ≥80.
# - Advanced: Speed Score ≥70 OR Strength Score ≥70.
# - Intermediate: Speed Score ≥50.
# - Beginner: All other scores.

max_score = 100
elite_speed_score = 90
elite_strength_score = 80
advanced_score = 70
intermediate_speed_score = 50


def rate_athlete(speed_score: float, strength_score: float) -> str:
    """Assign the highest performance rating an athlete qualifies for.

    Args:
        speed_score (float): The athlete's speed score, from 0 to 100.
        strength_score (float): The athlete's strength score, from 0 to 100.

    Returns:
        str: The rating ("Elite", "Advanced", "Intermediate", or "Beginner").

    Raises:
        ValueError: If either score is outside 0-100.
    """
    if (
        speed_score < 0
        or speed_score > max_score
        or strength_score < 0
        or strength_score > max_score
    ):
        raise ValueError(
            f"Invalid speed/strength score. Must be between 0 and {max_score}, got {speed_score}/{strength_score}"
        )

    if speed_score >= elite_speed_score and strength_score >= elite_strength_score:
        return "Elite"
    if speed_score >= advanced_score or strength_score >= advanced_score:
        return "Advanced"
    if speed_score >= intermediate_speed_score:
        return "Intermediate"
    return "Beginner"
