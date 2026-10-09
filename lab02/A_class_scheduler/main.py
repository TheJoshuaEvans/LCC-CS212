# Joshua Evans (thejoshuaevans.com)
# Original instructions: 
# https://lcc-cit.github.io/CS212-CourseMaterials/Labs/Lab02-ConstraintSolvers/CS212_Lab02_Instructions_GroupA-V2.html
import argparse

from class_scheduler_data import SolverConflictError, Classroom, Instructor, Section, Flags
from class_scheduler_input import parse_arguments
from class_scheduler_presenter import print_decisions, print_metadata
from class_scheduler_solver import solve

if __name__ != "__main__":
    raise RuntimeError("This script should only be run as the main module.")

args = parse_arguments()

# Read the data source files
classrooms = Classroom.read(args.data_folder)
instructors = Instructor.read(args.data_folder)
sections = Section.read(args.data_folder)

# Safely find a solution
try:
    decisions, metadata = solve(classrooms, instructors, sections, args.flags)
except SolverConflictError as e:
    # Conflicts encountered by the solver are pre-rendered and can be directly printed
    print(e)
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred:\n{e}")
    exit(2)

# Print the solution
print_decisions(decisions)
print_metadata(metadata)
