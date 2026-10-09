"""Maksym Kholodenko, Group B, Lab 2"""
"""Main program for CS 212 Lab 2."""

import sys
from pathlib import Path

from data_loader import load_data
from scheduler_solver import solve_schedule
from schedule_checker import check_schedule, print_check_results


def print_schedule(schedule):
    """Print a schedule in a readable table."""
    print(
        f"{'Slot':<5} {'Time':<9} {'Flight':<8} {'Dest':<6} "
        f"{'Crew':<5} {'Captain':<15} {'Aircraft':<10}"
    )
    print("-" * 70)

    for row in schedule:
        print(
            f"{row['slot']:<5} {row['time']:<9} {row['flight_number']:<8} "
            f"{row['destination']:<6} {row['crew_id']:<5} "
            f"{row['captain']:<15} {row['tail_number']:<10}"
        )


def run_dataset(folder):
    """Load one data folder, solve it, and print the result."""
    print(f"\n=== Data set: {folder} ===")
    flights, crews, aircraft = load_data(folder)
    result = solve_schedule(flights, crews, aircraft)

    if result["status"] == "sat":
        print("Result: SAT")
        print_schedule(result["schedule"])

        print("\nPlain Python schedule check:")
        check_results = check_schedule(result["schedule"], flights, crews, aircraft)
        print_check_results(check_results)

    elif result["status"] == "unsat":
        print("Result: UNSAT")
        print("Conflicting constraint groups:", ", ".join(result["unsat_core"]))

    else:
        print("Result: UNKNOWN")
        print("The solver timed out or could not determine satisfiability.")

    return result


def main():
    """Run the normal data set and any unsolvable data sets."""
    data_folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    run_dataset(data_folder)

    unsolvable_root = data_folder / "unsolvable_data"
    if unsolvable_root.exists():
        print("\n=== Checking unsolvable_data examples ===")
        for folder in sorted(unsolvable_root.iterdir()):
            if folder.is_dir():
                run_dataset(folder)


if __name__ == "__main__":
    main()
