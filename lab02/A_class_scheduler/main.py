# Joshua Evans (thejoshuaevans.com)
# Original instructions:
# https://lcc-cit.github.io/CS212-CourseMaterials/Labs/Lab02-ConstraintSolvers/CS212_Lab02_Instructions_GroupA-V2.html
import sys

from class_scheduler_data import (
    Classroom,
    Instructor,
    Section,
    SolverConflictError,
)
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
    print(e)
    sys.exit(1)

# Print the solution
print_decisions(decisions)
print_metadata(metadata)
