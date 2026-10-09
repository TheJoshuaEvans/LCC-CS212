# Class Scheduler

Joshua Evans, CS 212 Lab 2, Group A (V2)

Schedules a CS department's class sections with the Z3 constraint solver: each section gets a time slot, an instructor and a classroom. It covers the six required rules, both rules from Challenge 1 (`capacity` and `availability`) and Challenge 2 (as few part-time sections as possible).

[Lab instructions](https://lcc-cit.github.io/CS212-CourseMaterials/Labs/Lab02-ConstraintSolvers/CS212_Lab02_Instructions_GroupA-V2.html)

## Running it

Using [uv](https://docs.astral.sh/uv/), setup with
```sh
uv sync
```

Run the program with:

```sh
uv run main.py
```

This prints the schedule as a table sorted by time slot, then the number of sections taught by part-time instructors.

To use a different data set, give its folder:

```sh
uv run main.py unsolvable_data/capacity
```

When no schedule is possible, the program prints the constraints that conflict with each other. Each one is named after its rule and the rows involved, counting from 0. `capacity_section_0_room_3` is the capacity rule for the first section and the fourth classroom.

Rules can be switched off using the `disable-flags` argument, and multiple flags can be disabled at once:

```sh
uv run main.py --disable-flags capacity time_window
```

`uv run main.py --help` lists the rule names. The `domain` rule can't be switched off.

## Files

```sh
A_class_scheduler/
├── main.py                          # Runs the program
├── class_scheduler_input.py         # Command line arguments
├── class_scheduler_data.py          # CSV loading and the data classes
├── class_scheduler_presenter.py     # Printing the schedule
├── class_scheduler_solver_test.py   # Solver Tests
├── class_scheduler_solver.py        # The Z3 model and solving
├── csv/                             # The data files, including Challenge 1 columns
│   ├── classrooms.csv
│   ├── instructors.csv
│   └── sections.csv
└── unsolvable_data/                 # Data files with no solution for each rule
    ├── domain/
    ├── room_conflict/
    ├── instructor_conflict/
    ├── qualification/
    ├── workload/
    ├── time_window/
    ├── capacity/
    └── availability/
```

Each folder in `unsolvable_data` is named after the rule it breaks and has a README that says what was changed.

## Tests

```sh
uv run pytest
# or
uv run class_scheduler_solver_test.py
```

The tests check that:

- the schedule for the real data follows all eight rules,
- each data set in `unsolvable_data` is rejected, with the expected constraints among the conflicts,
- each of those data sets can be scheduled once the rule it breaks is switched off,
- each of those schedules, which had to break the rule that was switched off, is caught by the check for that rule.

## Requirements

The text of each item is from the lab instructions. Notes in italics say where this program does something differently.

- [x] **1. Data files.** Put the three CSV files in your project folder.
- [x] **2. Loading data.** Load each CSV file into a list of dictionaries, for example with `csv.DictReader`. Convert numbers to `int` and split the semicolon lists into Python lists. *Note: Loaded into data classes instead.*
- [x] **3. Decision variables.** For each section, create three Z3 `Int` variables: its time slot, its instructor (an index into the instructors list) and its classroom (an index into the classrooms list).
- [x] **4. Constraints.** Add constraints for all six scheduling rules.
- [x] **5. Solving.** Use a Z3 `Solver` to find a schedule. Read the values out of the model and return the schedule as a list of dictionaries. Print the schedule in a readable table sorted by time slot, showing the time, section, course, instructor and classroom. *Note: Returned as a list of `Decision` objects.*
- **6. Explaining an impossible schedule.**
  - [x] Create one Boolean tracking variable per constraint group and add each constraint as `Implies(group_flag, constraint)`. Call `check()` with all the flags as assumptions. *Each constraint is tracked by name with `assert_and_track`.*
  - [x] When the result is `unsat`, print the names of the groups in `unsat_core()`. *Note: Prints the name of each conflicting constraint, which starts with its group.*
  - [x] Make a folder named `unsolvable_data` with three modified copies of the data files, each of which breaks a different rule. *Note: Eight copies, one for each rule.*
  - [x] Your program must report the conflicting groups for each one.
  - [x] Keep each conflict small.
- [x] **7. Separation of concerns.** Keep the Z3 model and solving code in its own module, separate from file loading and from user input and output.
- **8. Testing.** Write a test module with a function that checks a schedule against all six rules in plain Python, without using Z3. *Note: One check function for each rule that can be switched off.* Use it to test that:
  - [x] the schedule from your real data passes every rule,
  - [x] each data set in `unsolvable_data` is reported as `unsat` with the expected constraint group in the core,
  - [x] the checker itself catches a schedule that you broke on purpose, for example by moving two sections into the same classroom at the same time. *Note: The broken schedules come from solving each `unsolvable_data` set with its rule switched off.*

### Challenge 1: Classroom capacity and instructor availability

- [x] **Rule 7, `capacity`.** Each section is in a classroom with at least as many seats as the section's enrollment.
- [x] **Rule 8, `availability`.** No instructor is scheduled in a time slot listed as unavailable for them.
- [x] Add the `seats`, `enrollment` and `unavailable_slots` columns and fill in values for every row.
- [x] The 5 classrooms have different numbers of seats, and at least 2 sections are too big for every classroom except the largest one.
- [x] Each instructor has 1 or 2 unavailable time slots.
- [x] Update your loading code for the new columns.
- [x] Add the two new groups to your tracking flags.
- [x] Add a data set to `unsolvable_data` that breaks each new rule.
- [x] Update your checker and tests to cover all eight rules.

### Challenge 2: Minimizing part-time sections

- [x] Find a schedule that has as few sections taught by part-time instructors as possible, and print that number and the schedule that goes with it.
- [x] **Option A: A loop with `push()` and `pop()`.** Keep using your `Solver`. In a loop, add a constraint that `part_time_sections` is at most *k*, check, then lower *k* and try again. Stop when the check is `unsat` or `unknown`, or when *k* reaches 6. *Note: The lowest possible value is calculated dynamically.*
