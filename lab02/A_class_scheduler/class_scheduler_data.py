import csv
from collections.abc import Callable
from dataclasses import dataclass, fields
from enum import StrEnum
from pathlib import Path


class CsvFilename(StrEnum):
    CLASSROOMS = ("classrooms.csv",)
    INSTRUCTORS = ("instructors.csv",)
    SECTIONS = ("sections.csv",)


class SolverConflictError(Exception):
    """Raised when the solver encounters a conflict that prevents a valid schedule from being generated."""

    def __init__(self, message: str, conflicts: list[str] | None = None):
        raw_conflicts = conflicts or []
        self.conflicts = [str(c) for c in raw_conflicts]

        if self.conflicts:
            # One conflict per line, sorted so that conflicts from the same rule sit together
            conflict_lines = "\n".join(
                f"  - {conflict}" for conflict in sorted(self.conflicts)
            )
            message = f"{message}\nConflicts ({len(self.conflicts)}):\n{conflict_lines}"
        super().__init__(message)


def _normalize_path(dirname: str, filename: str) -> str:
    """
    Take a path relative to `class_scheduler_data.py` and converts it into an absolute path

    Args:
        dirname (str): The directory containing the CSV files relative to `class_scheduler_data.py`
        filename (str): Name of the file in the directory

    Returns:
        str: The absolute path to the file
    """
    root_dir_name = Path(__file__).parent  # The directory containing this script
    full_path = Path(root_dir_name, dirname, filename)
    return full_path


def _read_csv(dirname: str, filename: str, cb: Callable[[dict[str, str]], None]):
    """
    Read a CSV file, and run a callback over every row. The callback should accept a [str, str]
    dictionary, and its return value is not evaluated

    Args:
        dirname (str): The directory containing the CSV files relative to `class_scheduler_data.py`
        filename (str): Name of the file in the directory
        cb (Callable[[dict[str, str]], None]): Callback that is fired for every CSV row
    """
    file_path = _normalize_path(dirname, filename)
    with open(file_path, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            cb(row)


@dataclass
class Classroom:
    """
    A single physical classroom in the school building where class sections can meet and instructors teach
    """

    @staticmethod
    def read(dirname: str):
        classrooms = []
        _read_csv(
            dirname,
            CsvFilename.CLASSROOMS,
            lambda row: classrooms.append(Classroom(row["room_id"], int(row["seats"]))),
        )
        return classrooms

    room_id: str
    """Unique identifier for the room"""

    seats: int
    """The maximum number of students the classroom can accommodate"""


@dataclass
class Instructor:
    """
    An instructor who is available to teach in the school. Different instructors specialize
    in different subjects, and they have different limits on the number of courses they can
    teach in a single term
    """

    @staticmethod
    def read(dirname: str):
        instructors = []
        _read_csv(
            dirname,
            CsvFilename.INSTRUCTORS,
            lambda row: instructors.append(
                Instructor(
                    row["instructor_id"],
                    row["name"],
                    int(row["max_sections"]),
                    row["qualified_courses"].split(";"),
                    [int(slot) for slot in row["unavailable_slots"].split(";")],
                )
            ),
        )
        return instructors

    instructor_id: str
    """Unique identifier of the instructor"""

    name: str
    """The instructor's name"""

    max_sections: int
    """The maximum number of sections the instructor may teach"""

    qualified_courses: list[str]
    """Courses the instructor may teach"""

    unavailable_slots: list[int]
    """Time slots during which the instructor is unavailable"""


PART_TIME_ALLOWED_SECTION_COUNT = 2
"""The number of sections a part-time instructor is allowed to teach"""


@dataclass
class Section:
    """
    A class cohort. This represents the students taking a particular class at a particular time
    """

    @staticmethod
    def read(dirname: str):
        sections = []
        _read_csv(
            dirname,
            CsvFilename.SECTIONS,
            lambda row: sections.append(
                Section(
                    row["section_id"],
                    row["course"],
                    int(row["earliest_slot"]),
                    int(row["latest_slot"]),
                    int(row["enrollment"]),
                )
            ),
        )
        return sections

    section_id: str
    """Unique ID for the section"""

    course: str
    """The course the section is for"""

    earliest_slot: int
    """The earliest possible timeslot for this section"""

    latest_slot: int
    """The latest possible timeslot for this section"""

    enrollment: int
    """The number of students enrolled in the section"""


@dataclass(frozen=True)
class TimeSlot:
    """
    A single 1.5 hour segment of time that a class can occur within, defined by its start time
    """

    index: int
    """Index of the time slot. Used as a sort key"""

    time_string: str
    """The human-readable time string"""


TIMESLOTS = [
    TimeSlot(0, "8:00 am"),
    TimeSlot(1, "9:30 am"),
    TimeSlot(2, "11:00 am"),
    TimeSlot(3, "12:30 pm"),
    TimeSlot(4, "2:00 pm"),
    TimeSlot(5, "3:30 pm"),
    TimeSlot(6, "5:00 pm"),
    TimeSlot(7, "6:30 pm"),
]
"""
Pre-set time slots. These are not subject to change and so don't need to be ingested dynamically
"""


@dataclass
class Decision:
    """A scheduling decision for a single section"""

    section: Section
    """The section this decision is for"""

    slot: TimeSlot
    """The time when the class will take place"""

    instructor: Instructor
    """The instructor teaching this section"""

    room: Classroom
    """Classroom the section is being taught in"""


@dataclass
class Flags:
    """
    The set of flags indicating which constraints are active. All constraints are
    enabled by default.
    """

    room_conflict: bool = True
    instructor_conflict: bool = True
    qualification: bool = True
    workload: bool = True
    time_window: bool = True
    capacity: bool = True
    availability: bool = True
    minimize_part_time: bool = True
    """
    Whether to purposefully minimize the number of sections taught by part-time instructors. Minimized
    results can still occur by chance when this is set to `False`
    """

    def __iter__(self):
        """
        Iterate over the flag names and their current values.

        Yields:
            tuple[str, bool]: The name of the flag and its current value.
        """
        for field in fields(self):
            yield field.name, getattr(self, field.name)


@dataclass
class Metadata:
    """Metadata about the generated schedule"""

    part_time_sections: int
    """The number of sections taught by part-time instructors"""

    flags: Flags
    """The set of constraint flags used when generating the schedule"""
