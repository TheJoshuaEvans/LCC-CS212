# Maksym Kholodenko, Group B, Lab 1, Problem 1 Solution: Meeting Room Reservation System
# This system recommends a meeting room based on the number of attendees and whether a projector is needed.



def recommend_room(attendees, projector_needed):
    room = "N/A"

    print("\n--- Meeting Room Reservation ---")
    print(f"Request: Attendees={attendees}, Projector Needed={projector_needed}")

    # Check the number of attendees
    if attendees >= 1 and attendees <= 5:
        # Small room: projector does not matter
        room = "Room Alpha (Small, No Projector)"

    elif attendees >= 6 and attendees <= 15:
        # Medium room: choose based on projector need
        if projector_needed:
            room = "Room Beta (Medium, Has Projector)"
        else:
            room = "Room Gamma (Medium, No Projector)"

    elif attendees >= 16:
        # Large room: not available
        room = "Reservation Denied (No large rooms available)"

    else:
        # Invalid attendee count
        room = "Error: Invalid number of attendees."

    print(f"Recommended Room: {room}")
    print("---------------------------------")


# Example 1: Small group, projector not needed
recommend_room(4, False)

# Example 2: Medium group, projector needed
recommend_room(12, True)

# Example 3: Medium group, projector not needed
recommend_room(10, False)

# Example 4: Large group, no large rooms available
recommend_room(20, True)


