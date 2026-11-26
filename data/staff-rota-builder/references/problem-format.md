# Problem file format for `scripts/solve_rota.py`

Write one JSON file. Every value comes from the user, or is an assumption you will state in the reply. Leave a key out when the user gave no such rule: a rule that is not in the file is not applied.

```json
{
  "title": "<optional title for the sheet>",
  "days": ["<day label 1>", "<day label 2>", "..."],
  "week_length": 7,
  "weekend_days": ["<label>", "<label>"],
  "shifts": [
    {"name": "<shift name>", "start": "HH:MM", "end": "HH:MM", "night": false},
    {"name": "<shift with no clock times>", "hours": 4}
  ],
  "demand": [
    {"day": "*", "shift": "<shift name>", "count": 2},
    {"day": "weekend", "shift": "<shift name>", "count": 1, "role": "<role>"}
  ],
  "people": [
    {"name": "<name>", "role": "<role>", "skills": ["<role>"], "fte": 1,
     "max_shifts_per_week": 4, "max_hours_per_week": 30, "max_consecutive_days": 4,
     "unavailable_days": ["<label>"],
     "unavailable": [{"day": "<label>", "shift": "<shift name>"}]}
  ],
  "rules": {
    "max_shifts_per_week": 5,
    "max_hours_per_week": 40,
    "max_consecutive_days": 5,
    "min_rest_hours": 11,
    "forbidden_next_day": [["<shift name>", "<shift name>"]],
    "max_weekend_shifts": 4,
    "max_night_shifts_per_week": 3,
    "min_shifts_per_week": 3
  },
  "layout": "people_down",
  "labels": {"person": "<column title in the user's language>", "sheet_rota": "...", "sheet_hours": "...", "sheet_rules": "..."},
  "rtl": false,
  "time_limit": 20,
  "seed": 1
}
```

The numbers above only show where numbers go. Use the user's.

## Fields

- `days`: one label per day, in order, in the user's language. For several weeks list every day (labels may repeat, `week_length` says where a week ends). A day in `demand`, `unavailable_days` or `weekend_days` is a label (matches every day with that label), an integer (that one day, counting from 0), a list of those, `"*"` (every day), `"weekend"` or `"weekday"`.
- `shifts`: `start` and `end` as `HH:MM` (an end earlier than the start means the shift runs past midnight). `night: true` marks a night shift for the night counts and `max_night_shifts_per_week`. With no clock times give `hours`; then `min_rest_hours` is measured from the stated start, so leave that rule out unless the times are real.
- `demand`: how many people each shift needs on which days. `role` (optional) means every one of those places must be filled by someone whose `role` or `skills` include it. Use two rows for one shift to ask for "1 lead plus 1 anyone".
- `people[].fte`: share of a full week, used only to judge fairness (a half-time person is expected to work about half). Default 1.
- Per-person `max_*` keys override the same key in `rules`.
- `min_shifts_per_week` is a target: missing it is reported as a warning, never forced.
- `forbidden_next_day`: pairs `[earlier day's shift, next day's shift]` that one person must not work back to back.
- `layout`: `people_down` (people in rows, days across: default) or `days_down`.
- `labels`: text for every heading in the sheets. When the user does not write English, set ALL of these, or the file will show English words: `person`, `day`, `role`, `shifts`, `hours`, `weekend`, `nights`, `total`, `staffed`, `legend`, `rule`, `type`, `status`, `details`, `sheet_rota`, `sheet_hours`, `sheet_rules`, plus `type_hard` and `type_soft` (words for required and target), `ok_text` (the word shown in Details for a passing rule, for example "OK" in their language) and `rule_text`, an object that maps each English rule name the script prints to its translation: "Every slot has the required number of people", "At most one shift per person per day", "Nobody is placed when unavailable", "Role or skill required by a slot is met", "Maximum shifts per week", "Maximum hours per week", "Maximum night shifts per week", "Maximum weekend shifts", "Maximum consecutive working days", "Rest between shifts". Only translate the ones that appear. `rule_text` replaces matching text, so a longer rule name that starts with one of these is translated in part. The words PASS, FAIL and WARN stay as they are. Set `"rtl": true` for Arabic, Hebrew, Persian or Urdu sheets.

## What the script prints

JSON with `status` (`complete` or `partial`), `positions_total`, `positions_filled`, `assignments`, `per_person` (shifts, hours, weekend and night counts), `rule_report` (each rule with `PASS`, `FAIL` or `WARN` and details), `fairness` (largest gap between two people, per full-time share), `unfilled` (for each place not filled, who was blocked and why), `capacity` (when the weekly caps alone make it impossible), `search` (`proved_impossible` is true when every way was tried, `ran_out_of_time` when it stopped early) and `xlsx` (the file written when you pass `--out`).
