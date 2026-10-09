"""Maksym Kholodenko, Group B, Lab 2"""
"""Plain Python schedule checker for CS 212 Lab 2.

This checker does not use Z3. It checks a completed schedule against all six
scheduling rules from the lab instructions.
"""

from collections import Counter


def _indexes(flights, crews, aircraft):
    flights_by_number = {flight["flight_number"]: flight for flight in flights}
    crews_by_id = {crew["crew_id"]: crew for crew in crews}
    aircraft_by_tail = {plane["tail_number"]: plane for plane in aircraft}
    return flights_by_number, crews_by_id, aircraft_by_tail


def check_domain(schedule, flights, crews, aircraft):
    """Check that every flight has an existing slot, crew, and aircraft."""
    issues = []
    flights_by_number, crews_by_id, aircraft_by_tail = _indexes(
        flights, crews, aircraft
    )

    scheduled_flights = [row.get("flight_number") for row in schedule]
    scheduled_set = set(scheduled_flights)
    expected_set = set(flights_by_number)

    for flight_number in sorted(expected_set - scheduled_set):
        issues.append(f"Missing flight: {flight_number}")

    for flight_number in sorted(scheduled_set - expected_set):
        issues.append(f"Unknown flight: {flight_number}")

    duplicate_counts = Counter(scheduled_flights)
    for flight_number, count in duplicate_counts.items():
        if count > 1:
            issues.append(f"Flight {flight_number} appears {count} times")

    for row in schedule:
        flight_number = row.get("flight_number")
        slot = row.get("slot")
        crew_id = row.get("crew_id")
        tail_number = row.get("tail_number")

        if not isinstance(slot, int) or slot < 0 or slot > 7:
            issues.append(f"{flight_number}: invalid slot {slot}")

        if crew_id not in crews_by_id:
            issues.append(f"{flight_number}: unknown crew {crew_id}")

        if tail_number not in aircraft_by_tail:
            issues.append(f"{flight_number}: unknown aircraft {tail_number}")

    return issues


def check_aircraft_conflict(schedule):
    """Check that no two flights use the same aircraft in the same slot."""
    issues = []
    seen = {}

    for row in schedule:
        key = (row["slot"], row["tail_number"])
        if key in seen:
            issues.append(
                f"Aircraft conflict in slot {row['slot']}: "
                f"{seen[key]} and {row['flight_number']} use {row['tail_number']}"
            )
        else:
            seen[key] = row["flight_number"]

    return issues


def check_crew_conflict(schedule):
    """Check that no crew works two flights in the same slot."""
    issues = []
    seen = {}

    for row in schedule:
        key = (row["slot"], row["crew_id"])
        if key in seen:
            issues.append(
                f"Crew conflict in slot {row['slot']}: "
                f"{seen[key]} and {row['flight_number']} use {row['crew_id']}"
            )
        else:
            seen[key] = row["flight_number"]

    return issues


def check_qualification(schedule, flights, crews):
    """Check that each flight is assigned to a qualified crew."""
    issues = []
    flights_by_number = {flight["flight_number"]: flight for flight in flights}
    crews_by_id = {crew["crew_id"]: crew for crew in crews}

    for row in schedule:
        flight = flights_by_number.get(row["flight_number"])
        crew = crews_by_id.get(row["crew_id"])

        if flight is None or crew is None:
            continue

        if flight["destination"] not in crew["qualified_destinations"]:
            issues.append(
                f"{row['flight_number']}: {row['crew_id']} is not qualified "
                f"for {flight['destination']}"
            )

    return issues


def check_workload(schedule, crews):
    """Check that no crew exceeds their max_flights limit."""
    issues = []
    counts = Counter(row["crew_id"] for row in schedule)
    crews_by_id = {crew["crew_id"]: crew for crew in crews}

    for crew_id, count in counts.items():
        if crew_id not in crews_by_id:
            continue

        max_flights = crews_by_id[crew_id]["max_flights"]
        if count > max_flights:
            issues.append(
                f"{crew_id} works {count} flights, but the limit is {max_flights}"
            )

    return issues


def check_time_window(schedule, flights):
    """Check that each flight is scheduled within its allowed time window."""
    issues = []
    flights_by_number = {flight["flight_number"]: flight for flight in flights}

    for row in schedule:
        flight = flights_by_number.get(row["flight_number"])
        if flight is None:
            continue

        if row["slot"] < flight["earliest_slot"] or row["slot"] > flight["latest_slot"]:
            issues.append(
                f"{row['flight_number']} is in slot {row['slot']}, "
                f"but allowed window is {flight['earliest_slot']} to "
                f"{flight['latest_slot']}"
            )

    return issues


def check_schedule(schedule, flights, crews, aircraft):
    """Return a dictionary of rule names to lists of issues."""
    return {
        "domain": check_domain(schedule, flights, crews, aircraft),
        "aircraft_conflict": check_aircraft_conflict(schedule),
        "crew_conflict": check_crew_conflict(schedule),
        "qualification": check_qualification(schedule, flights, crews),
        "workload": check_workload(schedule, crews),
        "time_window": check_time_window(schedule, flights),
    }


def schedule_is_valid(schedule, flights, crews, aircraft):
    """Return True if the schedule passes all six rule checks."""
    results = check_schedule(schedule, flights, crews, aircraft)
    return all(len(issues) == 0 for issues in results.values())


def print_check_results(results):
    """Print checker results in a readable format."""
    for rule_name, issues in results.items():
        if issues:
            print(f"FAIL: {rule_name}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"PASS: {rule_name}")
