# Joshua Evans (thejoshuaevans.com)
# Instructions:
# https://lcc-cit.github.io/CS212-CourseMaterials/Labs/Lab01-Python/GroupC/CS212_Lab01_Instructions_GroupC.html
# PC Component Compatibility Checker

# Create a system that checks the compatibility of two core PC components: the CPU
# Socket Type and the RAM Type. The system should output whether the components are
# Compatible or Incompatible.
# CPU Socket Type  Required RAM Type  Result if Correct RAM  Result if Incorrect RAM
# LGA1700          DDR5               Compatible             Incompatible
# AM4              DDR4               Compatible             Incompatible
# Other            Any                Incompatible           Incompatible
#
# Translate the program from either JavaScript or C# into Python

cpu_socket_ram = {"LGA1700": "DDR5", "AM4": "DDR4"}
"""Map connecting cpu socket to ram type"""

result_strings = {True: "COMPATIBLE", False: "INCOMPATIBLE"}
"""Map connection success state (of the connection is valid) to the result string"""


def check_compatibility(socket_type: str, ram_type: str) -> str:
    """Check whether a CPU socket type and RAM type are compatible.

    Args:
        socket_type (str): The CPU socket type, such as "LGA1700" or "AM4".
        ram_type (str): The RAM type, such as "DDR4" or "DDR5".

    Returns:
        str: "Compatible", or "Incompatible" (optionally followed by a reason).
    """
    # Normalizes parameters
    socket_type = socket_type.upper()
    ram_type = ram_type.upper()

    if socket_type not in cpu_socket_ram or ram_type not in cpu_socket_ram.values():
        # Any unrecognized argument is incompatible
        return f"{result_strings[False]} - unrecognized argument"

    if cpu_socket_ram[socket_type] == ram_type:
        return f"{result_strings[True]}"
    else:
        return f"{result_strings[False]} - the {socket_type} socket does not support {ram_type} RAM"
