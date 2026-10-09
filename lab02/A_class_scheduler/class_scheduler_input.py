import argparse
from class_scheduler_data import Flags

def parse_arguments() -> argparse.Namespace:
    """
    Read the command line arguments

    Returns:
        argparse.Namespace: The parsed arguments, one attribute per argument
    """
    parser = argparse.ArgumentParser(description="Schedule class sections, instructors and classrooms")
    parser.add_argument(
        "data_folder",
        nargs="?",
        default="csv",
        help="folder holding the CSV data files (default: %(default)s)",
    )

    flag_names = [flag_key for flag_key, _ in Flags()]
    parser.add_argument(
        "--disable-flags",
        nargs="+",
        default=[],
        choices=flag_names,
        metavar="FLAG",
        help=f"constraints to switch off, separated by spaces. Any of: {', '.join(flag_names)}",
    )

    # Construct a Flags object based on the disabled flags and apply it to the output
    parsed = parser.parse_args()
    disabled_flags = set(parsed.disable_flags)
    flags = Flags()
    for flag_key, flag_value in flags:
        if flag_key in disabled_flags:
            setattr(flags, flag_key, False)
    
    parsed.flags = flags
    return parsed
