# Joshua Evans (thejoshuaevans.com)
"""Tests for the Lab 2 (Group A) class scheduler solver."""

import sys

import pytest
from class_scheduler_data import (
    TIMESLOTS,
    Classroom,
    Decision,
    Flags,
    Instructor,
    Section,
    SolverConflictError,
)
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


# ==== Schedule checker ====
# One check for each rule that can be switched off, written in plain Python (no Z3). Every check
# takes one decision and the whole schedule it belongs to, and returns True when that decision
# breaks the rule.


def breaks_room_conflict(decision: Decision, schedule: list[Decision]) -> bool:
    """True if another section uses the same classroom in the same time slot"""
    for other_decision in schedule:
        if decision is other_decision:
            continue
        if (
            decision.room == other_decision.room
            and decision.slot == other_decision.slot
        ):
            return True
    return False


def breaks_instructor_conflict(decision: Decision, schedule: list[Decision]) -> bool:
    """True if the instructor teaches another section in the same time slot"""
    for other_decision in schedule:
        if decision is other_decision:
            continue
        if (
            decision.instructor == other_decision.instructor
            and decision.slot == other_decision.slot
        ):
            return True
    return False


def breaks_qualification(decision: Decision, schedule: list[Decision]) -> bool:
    """True if the instructor is not qualified to teach the section's course"""
    return decision.section.course not in decision.instructor.qualified_courses


def breaks_workload(decision: Decision, schedule: list[Decision]) -> bool:
    """True if the instructor is assigned more sections than their `max_sections` limit"""
    section_count = 0
    for other_decision in schedule:
        if other_decision.instructor == decision.instructor:
            section_count += 1
    return section_count > decision.instructor.max_sections


def breaks_time_window(decision: Decision, schedule: list[Decision]) -> bool:
    """True if the section meets outside its `earliest_slot` to `latest_slot` window"""
    return (
        decision.slot.index < decision.section.earliest_slot
        or decision.slot.index > decision.section.latest_slot
    )


def breaks_capacity(decision: Decision, schedule: list[Decision]) -> bool:
    """True if the classroom has fewer seats than the section's enrollment"""
    return decision.room.seats < decision.section.enrollment


def breaks_availability(decision: Decision, schedule: list[Decision]) -> bool:
    """True if the section meets in a time slot its instructor is unavailable for"""
    return decision.slot.index in decision.instructor.unavailable_slots


RULE_CHECKS = {
    "room_conflict": breaks_room_conflict,
    "instructor_conflict": breaks_instructor_conflict,
    "qualification": breaks_qualification,
    "workload": breaks_workload,
    "time_window": breaks_time_window,
    "capacity": breaks_capacity,
    "availability": breaks_availability,
}
"""The check for each rule, by the name of the rule's flag"""


@pytest.mark.parametrize("decision", solved)
def test_no_room_time_collisions(decision):
    """
    The same room cannot be used at the same time in different sections
    """
    assert not breaks_room_conflict(decision, solved)


@pytest.mark.parametrize("decision", solved)
def test_no_instructor_time_conflict(decision):
    """
    The same instructor cannot teach different sections at the same time
    """
    assert not breaks_instructor_conflict(decision, solved)


@pytest.mark.parametrize("decision", solved)
def test_instructor_is_qualified(decision):
    """
    Every instructor must be qualified to teach the course they are assigned
    """
    assert not breaks_qualification(decision, solved)


@pytest.mark.parametrize("decision", solved)
def test_instructor_workload(decision):
    """
    No instructor should be assigned more sections than their `max_sections` limit.
    """
    assert not breaks_workload(decision, solved)


@pytest.mark.parametrize("decision", solved)
def test_section_time_window(decision):
    """
    Each section must be scheduled within its allowed time window.
    """
    assert not breaks_time_window(decision, solved)


@pytest.mark.parametrize("decision", solved)
def test_capacity_constraint(decision):
    """
    Each section must be assigned to a classroom with enough seats to accommodate all enrolled students.
    """
    assert not breaks_capacity(decision, solved)


@pytest.mark.parametrize("decision", solved)
def test_instructor_availability(decision):
    """
    Instructors should not be scheduled in time slots during which they are unavailable.
    """
    assert not breaks_availability(decision, solved)


@pytest.mark.parametrize(
    ("data_folder", "expected_rules"),
    [
        ("unsolvable_data/domain", ["domain_section"]),
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
            ],
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
            ],
        ),
        (
            "unsolvable_data/qualification",
            ["domain_section_23", "qualification_section_23"],
        ),
        (
            "unsolvable_data/workload",
            [
                "domain_section",
                "qualification_section",
                "workload_instructor",
            ],
        ),
        ("unsolvable_data/time_window", ["domain_section_2", "time_window_section_2"]),
        ("unsolvable_data/capacity", ["capacity_section_0", "domain_section_0"]),
        (
            "unsolvable_data/availability",
            [
                "availability_section_23",
                "domain_section_23",
                "qualification_section_23",
                "time_window_section_23",
            ],
        ),
    ],
)
def test_unsolvable_data_reports_the_broken_rule(data_folder, expected_rules):
    """
    An unsolvable data set should be rejected, with the rules it breaks among the reported conflicts
    """
    with pytest.raises(SolverConflictError) as error_info:
        solve(
            Classroom.read(data_folder),
            Instructor.read(data_folder),
            Section.read(data_folder),
        )

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
        Flags(**{flag_name: False}, minimize_part_time=False),
    )

    assert len(decisions) == len(unsolvable_sections)


@pytest.mark.parametrize("flag_name", RULE_CHECKS)
def test_schedule_made_without_a_rule_is_caught(flag_name):
    """
    A schedule broken on purpose should be caught by the check for the rule it breaks. The data set
    that breaks a rule can only be scheduled by breaking that rule, so solving it with the rule's
    flag switched off gives a broken schedule
    """
    data_folder = f"unsolvable_data/{flag_name}"
    broken_schedule, _ = solve(
        Classroom.read(data_folder),
        Instructor.read(data_folder),
        Section.read(data_folder),
        Flags(**{flag_name: False}, minimize_part_time=False),
    )
    breaks_rule = RULE_CHECKS[flag_name]

    assert any(breaks_rule(decision, broken_schedule) for decision in broken_schedule)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
