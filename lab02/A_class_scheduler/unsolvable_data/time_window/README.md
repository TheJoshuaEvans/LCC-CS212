# time_window

Breaks rule 6, `time_window`.

In `sections.csv`, section S03 has `earliest_slot` 5 and `latest_slot` 3 (3 and 5 in the real data). No time slot is both 5 or later and 3 or earlier, so S03 can't be scheduled.
