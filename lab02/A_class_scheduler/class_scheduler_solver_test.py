# Joshua Evans (thejoshuaevans.com)
"""Tests for the Lab 2 (Group A) class scheduler solver."""

import sys

import pytest
from class_scheduler_data import CsvFilename, Classroom, Flags, Instructor, Section, SolverConflictError, TIMESLOTS
from class_scheduler_solver import solve

classrooms = Classroom.read("csv")
instructors = Instructor.read("csv")
sections = Section.read("csv")

solved, metadata = solve(classrooms, instructors, sections)

@pytest.mark.parametrize("decision", solved)
def test_every_decision_is_complete(decision):
    """
    Every decision must include values from the original lists
    """
    assert decision.slot in TIMESLOTS
    assert decision.section in sections
    assert decision.instructor in instructors
    assert decision.room in classrooms

@pytest.mark.parametrize("decision", solved)
def test_no_room_time_collisions(decision):
    """
    The same room cannot be used at the same time in different sections
    """
    for other_decision in solved:
        if decision is other_decision: continue
        assert (
            decision.room != other_decision.room 
            or decision.slot != other_decision.slot
        )

@pytest.mark.parametrize("decision", solved)
def test_no_instructor_time_conflict(decision):
    """
    The same instructor cannot teach different sections at the same time
    """
    for other_decision in solved:
        if decision is other_decision: continue
        assert (
            decision.instructor != other_decision.instructor 
            or decision.slot != other_decision.slot
        )

@pytest.mark.parametrize("decision", solved)
def test_instructor_is_qualified(decision):
    """
    Every instructor must be qualified to teach the course they are assigned
    """
    assert decision.section.course in decision.instructor.qualified_courses

@pytest.mark.parametrize("instructor", instructors)
def test_instructor_workload(instructor):
    """
    No instructor should be assigned more sections than their `max_sections` limit.
    """
    course_count = 0
    for decision in solved:
        if decision.instructor is instructor:
            course_count += 1
    assert course_count <= instructor.max_sections

@pytest.mark.parametrize("decision", solved)
def test_section_time_window(decision):
    """
    Each section must be scheduled within its allowed time window.
    """
    assert decision.slot.index >= decision.section.earliest_slot
    assert decision.slot.index <= decision.section.latest_slot

@pytest.mark.parametrize("decision", solved)
def test_capacity_constraint(decision):
    """
    Each section must be assigned to a classroom with enough seats to accommodate all enrolled students.
    """
    assert decision.room.seats >= decision.section.enrollment

@pytest.mark.parametrize("decision", solved)
def test_instructor_availability(decision):
    """
    Instructors should not be scheduled in time slots during which they are unavailable.
    """
    assert decision.slot.index not in decision.instructor.unavailable_slots

@pytest.mark.parametrize(
    ("data_folder", "expected_rules"),
    [
        (
            "unsolvable_data/domain",
            ["domain_section"]
        ),
        (
            "unsolvable_data/room_conflict",
            [
                "capacity_section_0",
                "capacity_section_8",
                "domain_section_0",
                "domain_section_8",
                "room_conflict_sections",
                "time_window_section_0",
                "time_window_section_8",
            ]
        ),
        (
            "unsolvable_data/instructor_conflict",
            [
                "domain_section_21",
                "domain_section_22",
                "instructor_conflict_sections",
                "qualification_section_21",
                "qualification_section_22",
                "time_window_section_21",
                "time_window_section_22",
            ]
        ),
        (
            "unsolvable_data/qualification",
            ["domain_section_23", "qualification_section_23"]
        ),
        (
            "unsolvable_data/workload",
            [
                "domain_section",
                "qualification_section",
                "workload_instructor",
            ]
        ),
        (
            "unsolvable_data/time_window",
            ["domain_section_2", "time_window_section_2"]
        ),
        (
            "unsolvable_data/capacity",
            ["capacity_section_0", "domain_section_0"]
        ),
        (
            "unsolvable_data/availability",
            [
                "availability_section_23",
                "domain_section_23",
                "qualification_section_23",
                "time_window_section_23",
            ]
        ),
    ],
)
def test_unsolvable_data_reports_the_broken_rule(data_folder, expected_rules):
    """
    An unsolvable data set should be rejected, with the rules it breaks among the reported conflicts
    """
    with pytest.raises(SolverConflictError) as error_info:
        solve(Classroom.read(data_folder), Instructor.read(data_folder), Section.read(data_folder))

    for expected_rule in expected_rules:
        # Match the whole label or a label that continues after an underscore, so that
        # `section_2` does not also match `section_23`
        assert any(
            conflict == expected_rule or conflict.startswith(f"{expected_rule}_")
            for conflict in error_info.value.conflicts
        )

@pytest.mark.parametrize(
    "flag_name",
    [
        "room_conflict",
        "instructor_conflict",
        "qualification",
        "workload",
        "time_window",
        "capacity",
        "availability",
    ],
)
def test_disabling_a_flag_lifts_its_rule(flag_name):
    """
    The data set that breaks a rule should become solvable once that rule's flag is switched off
    """
    data_folder = f"unsolvable_data/{flag_name}"
    unsolvable_sections = Section.read(data_folder)

    decisions, _ = solve(
        Classroom.read(data_folder),
        Instructor.read(data_folder),
        unsolvable_sections,
        Flags(**{flag_name: False}),
    )

    assert len(decisions) == len(unsolvable_sections)

if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
