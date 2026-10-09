from class_scheduler_data import Decision


def print_decisions(decisions: list[Decision]):
    """
    Pretty-print a list of section scheduling decisions
    """
    # Sort the decision by slot
    decisions = sorted(decisions, key=lambda d: d.slot.index)

    # Print a pretty table
    print("|------------|--------|-----------------|-----------|----------|")
    print("| Section ID | Course | Instructor Name |   Room    |   Time   | ")
    print("|------------|--------|-----------------|-----------|----------|")
    for decision in decisions:
        slot = decision.slot
        section = decision.section
        room = decision.room
        instructor = decision.instructor
        print(
            f"| {section.section_id:^10} | {section.course:<6} | {instructor.name:^15} | {room.room_id:<9} | {slot.time_string:>8} |"
        )
    print("|------------|--------|-----------------|-----------|----------|")


def print_metadata(metadata):
    """
    Pretty-print the metadata about the generated schedule
    """
    print(f"Part-time sections: {metadata.part_time_sections}")
    print("Flags:")
    for field in metadata.flags.__dataclass_fields__:
        print(f"  {field}: {getattr(metadata.flags, field)}")
