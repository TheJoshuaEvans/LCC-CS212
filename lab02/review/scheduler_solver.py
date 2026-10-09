"""Maksym Kholodenko, Group B, Lab 2"""
"""Z3 constraint model for CS 212 Lab 2.

The solver receives already-loaded data and returns either a valid schedule or
the constraint groups that make the data unsatisfiable.
"""

try:
    from z3 import Solver, Int, Bool, Or, Implies, Sum, If, sat, unsat
except ImportError as error:
    raise ImportError(
        "The z3-solver package is required. Install it with: pip install z3-solver"
    ) from error


SLOT_TIMES = {
    0: "6:00 am",
    1: "8:00 am",
    2: "10:00 am",
    3: "12:00 pm",
    4: "2:00 pm",
    5: "4:00 pm",
    6: "6:00 pm",
    7: "8:00 pm",
}

CONSTRAINT_GROUPS = [
    "domain",
    "aircraft_conflict",
    "crew_conflict",
    "qualification",
    "workload",
    "time_window",
]


def _or_equal(variable, allowed_values):
    """Return a Z3 expression requiring variable to equal one allowed value."""
    if not allowed_values:
        return False
    return Or(*[variable == value for value in allowed_values])


def build_solver(flights, crews, aircraft, timeout_ms=10000):
    """Build the Z3 solver, variables, and tracking flags."""
    solver = Solver()
    solver.set("timeout", timeout_ms)

    slot = []
    crew = []
    plane = []

    for flight in flights:
        flight_id = flight["flight_number"]
        slot.append(Int("slot_" + flight_id))
        crew.append(Int("crew_" + flight_id))
        plane.append(Int("plane_" + flight_id))

    flags = {name: Bool(name) for name in CONSTRAINT_GROUPS}
    flag_list = list(flags.values())

    def add(group, constraint):
        """Add a constraint guarded by its tracking group flag."""
        solver.add(Implies(flags[group], constraint))

    # Rule 1: every flight gets a valid slot, crew, and aircraft.
    for j in range(len(flights)):
        add("domain", slot[j] >= 0)
        add("domain", slot[j] <= 7)
        add("domain", crew[j] >= 0)
        add("domain", crew[j] < len(crews))
        add("domain", plane[j] >= 0)
        add("domain", plane[j] < len(aircraft))

    # Rule 2: no two flights can use the same aircraft in the same slot.
    for j in range(len(flights)):
        for k in range(j + 1, len(flights)):
            add(
                "aircraft_conflict",
                Or(slot[j] != slot[k], plane[j] != plane[k]),
            )

    # Rule 3: no crew can be assigned to two flights in the same slot.
    for j in range(len(flights)):
        for k in range(j + 1, len(flights)):
            add(
                "crew_conflict",
                Or(slot[j] != slot[k], crew[j] != crew[k]),
            )

    # Rule 4: crew must be qualified for the flight destination.
    for j, flight in enumerate(flights):
        destination = flight["destination"]
        qualified_crew_indexes = [
            w
            for w, crew_info in enumerate(crews)
            if destination in crew_info["qualified_destinations"]
        ]
        add("qualification", _or_equal(crew[j], qualified_crew_indexes))

    # Rule 5: no crew is assigned more flights than their max_flights limit.
    for w, crew_info in enumerate(crews):
        terms = []
        for j in range(len(flights)):
            terms.append(If(crew[j] == w, 1, 0))
        add("workload", Sum(terms) <= crew_info["max_flights"])

    # Rule 6: each flight departs within its allowed time window.
    for j, flight in enumerate(flights):
        add("time_window", slot[j] >= flight["earliest_slot"])
        add("time_window", slot[j] <= flight["latest_slot"])

    variables = {
        "slot": slot,
        "crew": crew,
        "plane": plane,
    }

    return solver, variables, flags, flag_list


def solve_schedule(flights, crews, aircraft, timeout_ms=10000):
    """Solve the scheduling problem and return a result dictionary."""
    solver, variables, flags, flag_list = build_solver(
        flights, crews, aircraft, timeout_ms=timeout_ms
    )

    result = solver.check(*flag_list)

    if result == sat:
        model = solver.model()
        schedule = []

        for j, flight in enumerate(flights):
            slot_value = model.eval(variables["slot"][j], model_completion=True).as_long()
            crew_index = model.eval(variables["crew"][j], model_completion=True).as_long()
            plane_index = model.eval(variables["plane"][j], model_completion=True).as_long()

            crew_info = crews[crew_index]
            aircraft_info = aircraft[plane_index]

            schedule.append(
                {
                    "slot": slot_value,
                    "time": SLOT_TIMES[slot_value],
                    "flight_number": flight["flight_number"],
                    "destination": flight["destination"],
                    "crew_id": crew_info["crew_id"],
                    "captain": crew_info["captain"],
                    "tail_number": aircraft_info["tail_number"],
                }
            )

        schedule.sort(key=lambda row: (row["slot"], row["flight_number"]))
        return {
            "status": "sat",
            "schedule": schedule,
            "unsat_core": [],
        }

    if result == unsat:
        return {
            "status": "unsat",
            "schedule": [],
            "unsat_core": [str(group) for group in solver.unsat_core()],
        }

    return {
        "status": "unknown",
        "schedule": [],
        "unsat_core": [],
    }
