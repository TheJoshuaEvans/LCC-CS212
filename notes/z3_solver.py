from z3 import Solver, Int, Sum, If, Implies, Sat

students = [
    "Alice",
    "Bob",
    "Charlie",
    "David",
    "Eve",
    "Frank",
    "Grace",
    "Hannah",
    "Ivy",
    "Jack",
    "Karen",
    "Leo",
    "Mona",
    "Nina",
    "Oscar",
]
num_students = len(students)
print(num_students)

MAX_GROUP_SIZE = 3
num_groups = math.ceil(num_students / MAX_GROUP_SIZE)
