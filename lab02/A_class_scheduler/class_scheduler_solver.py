# Joshua Evans (thejoshuaevans.com)
from z3 import Solver, Int, And, Or, Implies, Sum, If, Not, Or, sat, unsat

from class_scheduler_data import SolverConflictError, Classroom, Instructor, Section, TIMESLOTS, Decision, Metadata, Flags

def solve(classrooms: list[Classroom], instructors: list[Instructor], sections: list[Section], flags: Flags = Flags()) -> tuple[list[Decision], Metadata]:
    """
    Generate a scheduling solution for the provided parameters, if one exists

    Args:
        classrooms (list[Classrooms]): List of available classrooms
        instructors (list[Instructor]): List of instructors that can teach
        sections (list[Section]): List of "class sections" representing a single class cohort
        flags (Flags, optional): Constraint flags
    
    Returns:
        list[Decision]: A list of scheduling decisions, one for each provided section
        Metadata: Metadata about the generated schedule
    """
    solver = Solver()

    # ==== Data ====
    # The decisions are made per-section
    slot_indexes = []
    instructor_indexes = []
    room_indexes = []
    for section in sections:
        id = section.section_id
        slot_indexes.append(Int(f"slot_{id}"))
        instructor_indexes.append(Int(f"instructor_{id}"))
        room_indexes.append(Int(f"room_{id}"))


    # ==== Constraints ====
    # 1. [domain] Every section gets a time slot (0 to 7), an instructor, and a classroom that exist in the data.
    for i, section in enumerate(sections):
        # Define the possible range of values for each decision
        solver.assert_and_track(And(
            slot_indexes[i] >= 0,
            slot_indexes[i] < len(TIMESLOTS),
            instructor_indexes[i] >= 0,
            instructor_indexes[i] < len(instructors),
            room_indexes[i] >= 0,
            room_indexes[i] < len(classrooms)
        ), f"domain_section_{i}")

    # 2. [room_conflict] No two sections can use the same classroom in the same time slot.
    if flags.room_conflict:
        for i in range(len(sections)):
            for j in range(len(sections)):
                if i == j: continue # Don't compare the same sections
                solver.assert_and_track(Not(And(
                    room_indexes[i] == room_indexes[j],
                    slot_indexes[i] == slot_indexes[j]
                )), f"room_conflict_sections_{i}_{j}")

    # 3. [instructor_conflict] No instructor can be assigned to two sections in the same time slot.
    if flags.instructor_conflict:
        for i in range(len(sections)):
            for j in range(len(sections)):
                if i == j: continue # Don't compare the same sections
                solver.assert_and_track(Not(And(
                    instructor_indexes[i] == instructor_indexes[j],
                    slot_indexes[i] == slot_indexes[j]
                )), f"instructor_conflict_sections_{i}_{j}")

    # 4. [qualification] Each section is taught by an instructor who is qualified to teach that course.
    if flags.qualification:
        for i, section in enumerate(sections):
            for j, instructor in enumerate(instructors):
                if section.course not in instructor.qualified_courses:
                    solver.assert_and_track(instructor_indexes[i] != j, f"qualification_section_{i}_instructor_{j}")

    # 5. [workload] No instructor is assigned more sections than their `max_sections` limit: 3 for full-time 
    # #             instructors and 2 for part-time instructors.
    if flags.workload:
        for i, instructor in enumerate(instructors):
            count = Sum([If(instructor_indexes[j] == i, 1, 0) for j in range(len(sections))])
            solver.assert_and_track(count <= instructor.max_sections, f"workload_instructor_{i}")

    # 6. [time_window] Each section meets within its allowed time window (`earliest_slot` to `latest_slot`).
    # For example, an evening section must be in slot 6 or 7.
    if flags.time_window:
        for section in sections:
            for i, slot in enumerate(TIMESLOTS):
                if (
                    slot.index < section.earliest_slot
                    or slot.index > section.latest_slot
                ):
                    solver.assert_and_track(slot_indexes[sections.index(section)] != i, f"time_window_section_{sections.index(section)}_slot_{i}")

    # Challenge 1: Classroom capacity and instructor availability. Make the problem more realistic by adding two more rules.
    # 7. [capacity] Each section is in a classroom with at least as many seats as the section’s enrollment.
    if flags.capacity:
        for i, section in enumerate(sections):
            for j, room in enumerate(classrooms):
                if room.seats < section.enrollment:
                    solver.assert_and_track(room_indexes[i] != j, f"capacity_section_{i}_room_{j}")

    # 8. [availability] No instructor is scheduled in a time slot listed as unavailable for them.
    if flags.availability:
        for i, section in enumerate(sections):
            for j, instructor in enumerate(instructors):
                for unavailable_slot in instructor.unavailable_slots:
                    solver.assert_and_track(Implies(
                        instructor_indexes[i] == j,
                        slot_indexes[i] != unavailable_slot
                    ), f"availability_section_{i}_instructor_{j}_slot_{unavailable_slot}")

    # Challenge 2: Minimizing part-time sections. The department would rather give its full-time instructors
    # a full load than rely on part-time instructors. Find a schedule that has as few sections taught by part-time
    # instructors as possible, and print that number and the schedule that goes with it.
    part_time_terms = []
    for j in range(len(sections)):
        # A list of conditions: "section j is taught by part-time instructor w"
        taught_by_part_time = []
        for w in range(len(instructors)):
            if instructors[w].max_sections == 2:    # part-time
                taught_by_part_time.append(instructor_indexes[j] == w)
        # Count 1 if any of those conditions is true
        part_time_terms.append(If(Or(taught_by_part_time), 1, 0))
    part_time_sections = Sum(part_time_terms)

    # No schedule can have fewer part-time sections than this: the full-time instructors can only
    # cover so many sections between them, and every section beyond that must go to a part-timer
    full_time_capacity = sum(
        instructor.max_sections for instructor in instructors if instructor.max_sections != 2
    )
    lowest_possible = max(0, len(sections) - full_time_capacity)


    # ==== Solve! ====
    solver.set("timeout", 10000) # Don't let a single check run forever

    # Each pass asks for a schedule with fewer part-time sections than the last one found, so the
    # last schedule found is the best one
    best_model = None
    limit = None # The first pass has no limit: any valid schedule will do
    while True:
        solver.push() # Checkpoint, so this pass's limit can be taken back out
        if limit is not None:
            solver.assert_and_track(part_time_sections <= limit, f"part_time_limit_{limit}")

        result = solver.check()
        if result == sat:
            best_model = solver.model()

            if flags.minimize_part_time == False:
                # We were instructed to not minimize part-time instructors, so we can stop on the first passing model
                break
        elif best_model is None:
            # Not even the first pass found a schedule
            if result == unsat:
                raise SolverConflictError("No valid schedule found.", conflicts=solver.unsat_core())
            raise ValueError(f"Solver returned unknown result: {result}. This is likely caused by a timeout.")

        solver.pop() # Back to the checkpoint, which removes this pass's limit

        if result != sat:
            break # Nothing beats the best schedule found (or the solver ran out of time trying)

        best_count = best_model.eval(part_time_sections).as_long()
        if best_count <= lowest_possible:
            break # Can't be improved on, so there's no need to ask
        limit = best_count - 1

    final_decisions = []
    for i, section in enumerate(sections):
        slot_index = best_model.eval(slot_indexes[i], model_completion=True).as_long()
        instructor_index = best_model.eval(instructor_indexes[i], model_completion=True).as_long()
        room_index = best_model.eval(room_indexes[i], model_completion=True).as_long()

        final_decisions.append(Decision(section, TIMESLOTS[slot_index], instructors[instructor_index], classrooms[room_index]))

    # Generate the metadata
    metadata = Metadata(
        part_time_sections=best_model.eval(part_time_sections).as_long(),
        flags=flags,
    )

    return final_decisions, metadata
