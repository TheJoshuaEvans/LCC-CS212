# availability

Breaks rule 8, `availability`.

In `instructors.csv`, the five instructors qualified for CS260 all have `unavailable_slots` of `6;7`: James Chen (I02), Robert Nguyen (I04), David Kim (I06), Carlos Rivera (I08) and Omar Haddad (I10). Section S24 is a CS260 section that can only meet in slot 6 or 7, so nobody who can teach it is free then.

The conflict needs three other rules as well, so they appear alongside `availability` in the report: `time_window` (S24 is evening only), `qualification` (only those five can teach CS260) and `domain`.
