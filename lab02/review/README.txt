CS 212 Lab 2 - Scheduling with a Constraint Solver

Files:
- main.py: runs the scheduler and prints the schedule or unsat core.
- data_loader.py: loads CSV files and converts values.
- scheduler_solver.py: contains the Z3 model and solving code.
- schedule_checker.py: plain Python checker for the six scheduling rules.
- test_scheduler.py: tests the checker, real data, and unsolvable_data examples.
- flights.csv, crews.csv, aircraft.csv: normal data set.
- unsolvable_data/: three modified data sets that should be unsatisfiable.

How to run:
1. Install Z3:
   pip install z3-solver

2. Run the main program from this folder:
   python main.py

3. Run tests:
   python -m pytest test_scheduler.py

Note:
The optional challenges are not included. This solution focuses on the required
Lab 2 functionality.
