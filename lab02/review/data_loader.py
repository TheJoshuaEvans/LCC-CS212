"""Maksym Kholodenko, Group B, Lab 2"""
"""CSV loading utilities for CS 212 Lab 2.

This module only loads and cleans data. The Z3 model and solving code are kept
in scheduler_solver.py to keep the program separated into concerns.
"""

import csv
from pathlib import Path


def load_csv(filename):
    """Load a CSV file into a list of dictionaries."""
    with open(filename, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return list(reader)


def load_data(folder="."):
    """Load aircraft.csv, crews.csv, and flights.csv from a folder."""
    folder = Path(folder)

    aircraft = load_csv(folder / "aircraft.csv")
    crews = load_csv(folder / "crews.csv")
    flights = load_csv(folder / "flights.csv")

    for crew in crews:
        crew["max_flights"] = int(crew["max_flights"])
        crew["qualified_destinations"] = [
            destination.strip()
            for destination in crew["qualified_destinations"].split(";")
            if destination.strip()
        ]

    for flight in flights:
        flight["earliest_slot"] = int(flight["earliest_slot"])
        flight["latest_slot"] = int(flight["latest_slot"])

    return flights, crews, aircraft
