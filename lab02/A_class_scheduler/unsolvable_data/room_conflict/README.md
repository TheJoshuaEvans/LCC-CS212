# room_conflict

Breaks rule 2, `room_conflict`.

In `sections.csv`, sections S01 and S09 both have `earliest_slot` 0 and `latest_slot` 0 (0 and 7 in the real data). With 38 and 36 students, each fits only the largest classroom, BLD19-116 (40 seats). Both would have to be in that room in slot 0.

The conflict needs three other rules as well, so they appear alongside `room_conflict` in the report: `capacity` (only one room is big enough), `time_window` (both are held to slot 0) and `domain`.

Everything else matches the files in `csv/`.
