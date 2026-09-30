# Joshua Evans (thejoshuaevans.com)
# Instructions:
# https://lcc-cit.github.io/CS212-CourseMaterials/Labs/Lab01-Python/GroupB/CS212_Lab01_Instructions_GroupB.html
# Meeting Room Reservation System

# Build a reservation system that recommends a meeting room based on the number of
# Attendees and whether a Projector is Needed (True/False).
# Attendees        Projector Needed  Recommended Room
# 1-5 (Small)      Any               Room Alpha (No Projector)
# 6-15 (Medium)    True              Room Beta (Has Projector)
# 6-15 (Medium)    False             Room Gamma (No Projector)
# 16+ (Large)      Any               Reservation Denied (No large rooms)
#
# Translate the program from either JavaScript or C# into Python
from dataclasses import dataclass


@dataclass
class Room:
    """A room available in the reservation system"""

    name: str
    """The full name of the room"""
    capacity: int
    """The maximum capacity of the room"""
    has_projector: bool = False
    """If the room has a projector available"""


available_rooms = {
    "alpha": Room("Room Alpha", 5),
    "beta": Room("Room Beta", 15, True),
    "gamma": Room("Room Gamma", 15),
}
"""All of the currently available rooms"""

denied_str = "Reservation Denied"
"""String to present to the user when a reservation is denied"""


def recommend_room(attendees: int, projector_needed: bool) -> str:
    """Recommend a meeting room based on group size and projector needs.

    Args:
        attendees (int): The number of people attending the meeting.
        projector_needed (bool): Whether the meeting needs a projector.

    Returns:
        str: The recommended room, or a message that the reservation is denied.

    Raises:
        ValueError: If attendees is less than 1.
    """
    # Validation
    if attendees < 1:
        raise ValueError(f"Must have at least one attendee, got {attendees}")

    if attendees <= available_rooms["alpha"].capacity:
        # Ignore projector requests for groups that will fit in alpha
        projector_needed = False

    for room in available_rooms.values():
        # Return the first room that fits all parameters
        if room.capacity >= attendees and room.has_projector == projector_needed:
            return room.name

    # No room was found, return rejection
    return denied_str
