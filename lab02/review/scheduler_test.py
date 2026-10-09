"""Maksym Kholodenko, Group B, Lab 2"""
"""Tests for CS 212 Lab 2.

The schedule checker itself is plain Python and does not use Z3.
The unsatisfiable-data tests call the Z3 solver to confirm that the expected
constraint group appears in the unsat core.
"""

from pathlib import Path

from data_loader import load_data
from schedule_checker import check_schedule, schedule_is_valid
from scheduler_solver import solve_schedule


BASE_DIR = Path(__file__).resolve().parent


KNOWN_VALID_SCHEDULE = [{'slot': 0, 'time': '6:00 am', 'flight_number': 'LC102', 'destination': 'PDX', 'crew_id': 'C01', 'captain': 'Linda Park', 'tail_number': 'N412LC'}, {'slot': 0, 'time': '6:00 am', 'flight_number': 'LC119', 'destination': 'MFR', 'crew_id': 'C10', 'captain': 'Sam Okafor', 'tail_number': 'N415LC'}, {'slot': 0, 'time': '6:00 am', 'flight_number': 'LC122', 'destination': 'RDM', 'crew_id': 'C06', 'captain': 'Daniel Ortiz', 'tail_number': 'N418LC'}, {'slot': 1, 'time': '8:00 am', 'flight_number': 'LC101', 'destination': 'PDX', 'crew_id': 'C10', 'captain': 'Sam Okafor', 'tail_number': 'N412LC'}, {'slot': 1, 'time': '8:00 am', 'flight_number': 'LC110', 'destination': 'BOI', 'crew_id': 'C06', 'captain': 'Daniel Ortiz', 'tail_number': 'N415LC'}, {'slot': 1, 'time': '8:00 am', 'flight_number': 'LC115', 'destination': 'SUN', 'crew_id': 'C05', 'captain': 'Grace Liu', 'tail_number': 'N418LC'}, {'slot': 2, 'time': '10:00 am', 'flight_number': 'LC105', 'destination': 'PDX', 'crew_id': 'C03', 'captain': 'Priya Shah', 'tail_number': 'N412LC'}, {'slot': 2, 'time': '10:00 am', 'flight_number': 'LC107', 'destination': 'SEA', 'crew_id': 'C09', 'captain': 'Rosa Delgado', 'tail_number': 'N415LC'}, {'slot': 2, 'time': '10:00 am', 'flight_number': 'LC111', 'destination': 'BOI', 'crew_id': 'C01', 'captain': 'Linda Park', 'tail_number': 'N418LC'}, {'slot': 3, 'time': '12:00 pm', 'flight_number': 'LC103', 'destination': 'PDX', 'crew_id': 'C08', 'captain': 'Kevin Walsh', 'tail_number': 'N412LC'}, {'slot': 3, 'time': '12:00 pm', 'flight_number': 'LC106', 'destination': 'SEA', 'crew_id': 'C07', 'captain': 'Nina Petrov', 'tail_number': 'N415LC'}, {'slot': 3, 'time': '12:00 pm', 'flight_number': 'LC109', 'destination': 'BOI', 'crew_id': 'C09', 'captain': 'Rosa Delgado', 'tail_number': 'N418LC'}, {'slot': 4, 'time': '2:00 pm', 'flight_number': 'LC113', 'destination': 'BOI', 'crew_id': 'C01', 'captain': 'Linda Park', 'tail_number': 'N412LC'}, {'slot': 4, 'time': '2:00 pm', 'flight_number': 'LC118', 'destination': 'MFR', 'crew_id': 'C03', 'captain': 'Priya Shah', 'tail_number': 'N415LC'}, {'slot': 4, 'time': '2:00 pm', 'flight_number': 'LC120', 'destination': 'MFR', 'crew_id': 'C02', 'captain': 'Marcus Hill', 'tail_number': 'N418LC'}, {'slot': 5, 'time': '4:00 pm', 'flight_number': 'LC114', 'destination': 'SUN', 'crew_id': 'C05', 'captain': 'Grace Liu', 'tail_number': 'N412LC'}, {'slot': 5, 'time': '4:00 pm', 'flight_number': 'LC121', 'destination': 'MFR', 'crew_id': 'C08', 'captain': 'Kevin Walsh', 'tail_number': 'N415LC'}, {'slot': 5, 'time': '4:00 pm', 'flight_number': 'LC123', 'destination': 'RDM', 'crew_id': 'C04', 'captain': 'Tom Becker', 'tail_number': 'N418LC'}, {'slot': 6, 'time': '6:00 pm', 'flight_number': 'LC104', 'destination': 'PDX', 'crew_id': 'C03', 'captain': 'Priya Shah', 'tail_number': 'N412LC'}, {'slot': 6, 'time': '6:00 pm', 'flight_number': 'LC108', 'destination': 'SEA', 'crew_id': 'C02', 'captain': 'Marcus Hill', 'tail_number': 'N415LC'}, {'slot': 6, 'time': '6:00 pm', 'flight_number': 'LC116', 'destination': 'SUN', 'crew_id': 'C05', 'captain': 'Grace Liu', 'tail_number': 'N418LC'}, {'slot': 7, 'time': '8:00 pm', 'flight_number': 'LC112', 'destination': 'BOI', 'crew_id': 'C07', 'captain': 'Nina Petrov', 'tail_number': 'N412LC'}, {'slot': 7, 'time': '8:00 pm', 'flight_number': 'LC117', 'destination': 'SUN', 'crew_id': 'C06', 'captain': 'Daniel Ortiz', 'tail_number': 'N415LC'}, {'slot': 7, 'time': '8:00 pm', 'flight_number': 'LC124', 'destination': 'RDM', 'crew_id': 'C04', 'captain': 'Tom Becker', 'tail_number': 'N418LC'}]


def test_real_data_known_schedule_passes_all_rules():
    """A known schedule from the real data should pass all six rule checks."""
    flights, crews, aircraft = load_data(BASE_DIR)
    results = check_schedule(KNOWN_VALID_SCHEDULE, flights, crews, aircraft)

    assert results == {
        "domain": [],
        "aircraft_conflict": [],
        "crew_conflict": [],
        "qualification": [],
        "workload": [],
        "time_window": [],
    }


def test_checker_catches_broken_aircraft_conflict():
    """The plain Python checker should catch a deliberate aircraft conflict."""
    flights, crews, aircraft = load_data(BASE_DIR)
    broken_schedule = [dict(row) for row in KNOWN_VALID_SCHEDULE]

    broken_schedule[1]["slot"] = broken_schedule[0]["slot"]
    broken_schedule[1]["tail_number"] = broken_schedule[0]["tail_number"]

    results = check_schedule(broken_schedule, flights, crews, aircraft)

    assert results["aircraft_conflict"]
    assert not schedule_is_valid(broken_schedule, flights, crews, aircraft)


def test_solver_finds_schedule_for_real_data():
    """The real data should be satisfiable."""
    flights, crews, aircraft = load_data(BASE_DIR)
    result = solve_schedule(flights, crews, aircraft)

    assert result["status"] == "sat"
    assert schedule_is_valid(result["schedule"], flights, crews, aircraft)


def test_unsolvable_qualification_data_reports_expected_core():
    """The no-qualified-crew data set should report qualification in the core."""
    folder = BASE_DIR / "unsolvable_data" / "qualification_no_crew"
    flights, crews, aircraft = load_data(folder)
    result = solve_schedule(flights, crews, aircraft)

    assert result["status"] == "unsat"
    assert "qualification" in result["unsat_core"]


def test_unsolvable_time_window_data_reports_expected_core():
    """The impossible time-window data set should report time_window in the core."""
    folder = BASE_DIR / "unsolvable_data" / "time_window_impossible"
    flights, crews, aircraft = load_data(folder)
    result = solve_schedule(flights, crews, aircraft)

    assert result["status"] == "unsat"
    assert "time_window" in result["unsat_core"]


def test_unsolvable_workload_data_reports_expected_core():
    """The workload-conflict data set should report workload in the core."""
    folder = BASE_DIR / "unsolvable_data" / "workload_conflict"
    flights, crews, aircraft = load_data(folder)
    result = solve_schedule(flights, crews, aircraft)

    assert result["status"] == "unsat"
    assert "workload" in result["unsat_core"]
