# instructor_conflict

Breaks rule 3, `instructor_conflict`.

In `sections.csv`, sections S22 and S23 are for a new course, CS275 (CS260 in the real data), and both have `earliest_slot` 2 and `latest_slot` 2. In `instructors.csv`, CS275 is added to the `qualified_courses` of James Chen (I02) and nobody else. He would have to teach both sections in slot 2.

The conflict needs three other rules as well, so they appear alongside `instructor_conflict` in the report: `qualification` (only one instructor can teach CS275), `time_window` (both are held to slot 2) and `domain`.

Everything else matches the files in `csv/`.
