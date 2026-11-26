---
name: Staff Rota Builder
description: >
  Builds a fair staff rota or shift schedule from your people, shifts and rules, solved in code and checked rule by rule, as an Excel file.
  Use it for "make a rota", "shift schedule for my staff", "who works which shift", "roster for my team", "invigilation timetable", "on-call rota".
---

# Staff Rota Builder

The user gets an .xlsx rota (grid, hours per person, rule check) in which every hard rule holds and the work is spread fairly, or, when no such rota exists, an exact statement of which slot or rule cannot be met plus the closest rota with the gaps listed.

**Never invent** a person, a limit, a legal rule, a shift time, an unavailable day or a contract: use what the user gave, and where something is missing write it as an assumption in the reply. Do not state labour-law limits from memory; use only limits the user gives, and say local rules and contracts should be checked.

**Language.** Write the reply, the sheet headings and the day labels in the language the user wrote in, unless they ask for another. Keep their names, shift names and figures exactly as given. The first words of the reply are the result: never "I'll load the skill", "I'll start by reading your sheet" or any other narration of tool use, and no English sentence before a reply in another language.

## Step 1: Read the request

Take people, shifts or slots, how many people each needs, and the rules from the message and any attachment (an attached .xlsx or .csv of staff is read for you). Collect:

- **People**: name, role or skills if any, weekly limit (shifts or hours), days they cannot work, part-time share.
- **Shifts and demand**: names, clock times if given, which days, how many people each needs, and which role if it matters.
- **Rules**: maximum shifts or hours a week, maximum days in a row, minimum rest or "no night then morning", weekend and night limits.
- **Period**: the days to cover. If the user gave none, use one week, Monday to Sunday labelled in their language, and say so. Do not invent calendar dates; label days only with dates the user gave.

Do not open with questions. If something essential is missing (no shifts, or no way to tell how many staff are needed), decide the simplest reading, state it as an assumption, and go on. Ask once with `clarify` only if there are no people at all or no shifts at all and nothing can be assumed.

Where the user gave no cap, leave it out: a missing limit is not a rule. Where the user said "fair", the script balances hours, weekend shifts and night shifts for you.

## Step 2: Write the problem file

Read `references/problem-format.md`, then write `/tmp/.scratch/staff-rota-builder/problem.json` (run `mkdir -p /tmp/.scratch/staff-rota-builder` first) with `write_file`. Put every heading of the file in the user's language through `labels` (the format file lists all keys, including the rule names; an untranslated key shows English in the sheet), and set `"rtl": true` for right-to-left languages. If the user gave no shift length or clock times, name the assumed length in the reply and say that hours totals follow from it.

## Step 3: Solve in code

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is in its `scripts/` folder. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `solve_rota.py` under `~/.computer/skills` with `search_files`.

```
python3 SKILL_DIR/scripts/solve_rota.py /tmp/.scratch/staff-rota-builder/problem.json --out /tmp/.scratch/staff-rota-builder/<meaningful-name>.xlsx
```

Never assign people by hand and never do the sums in your head: the script's output is the source for every name, count and total in your reply. If it reports `error`, fix the problem file and run again. If openpyxl is missing, run it without `--out` and build the workbook with the built-in `xlsx` skill (load it with `skill_view`, follow it including its delivery step, and do not call `publish_artifact` for that file).

## Step 4: Read the result

- `status` is `complete` and no rule is `FAIL`: the rota is valid.
- `status` is `partial`: no rota satisfies everything. Do not hide this or loosen a rule yourself. Report from `unfilled` and `capacity` exactly which day and shift is short, how many people are missing and what blocks each person (for example "already on a shift that day", "max shifts per week", "unavailable"). Say whether `search.proved_impossible` is true (every way was tried) or `ran_out_of_time` (not proven). Offer the smallest change that would fix it, for example one more person for a named shift or one more shift allowed for named people, as a suggestion only; do not rebuild with it unless the user asked. Deliver the partial rota too, with its gaps visible.
- `WARN` lines are soft targets that were missed; list them.
- Fairness: quote `fairness` (largest gap in hours, weekend shifts and night shifts between two people, per full-time share) and say plainly if some gap cannot be removed (for example a person who cannot work weekends).

## Step 5: Deliver

1. Publish the file with `publish_artifact` (`kind: "document"`, a meaningful filename in the user's language). The file is built by the script, not by a built-in skill, so you publish it.
2. Reply with the result in full, in the user's language:
   - one line: the period, people and positions filled (`positions_filled` of `positions_total`);
   - the rota as a Markdown table (people down, days across, a shift name or a dash) built from `assignments`; for more than 14 days show the first 14 and say the rest is in the file;
   - a table per person from `per_person`: shifts, hours, weekend shifts, night shifts;
   - the rule check: every rule from `rule_report` with PASS, FAIL or WARN;
   - the assumptions you made;
   - any gap, as in Step 4;
   - one line: labour rules and contracts differ by place, so check the result against the rules that apply.

The reply holds the rota itself; the file is the copy to print or share.

## When the user asks for a change

Typical: "Ben is ill on Tuesday", "add a person", "make Saturday need three". Change only that in `problem.json`, keep every other input as it was, solve again with the same file name, publish the new file, and say in one line what changed. Say which people's shifts moved, because a rota already shared with staff should change as little as possible. Do this by editing the same `problem.json`; to keep the old assignments steady where possible, keep `seed` unchanged.

## Self-check before you reply

- Every name, count and total comes from the script output, not from memory.
- No limit, rule, day, date or shift was added that the user did not give, except those listed under assumptions.
- A `partial` result is labelled as such, with the exact gap.
- The file is published and the reply holds the rota in full.
- The reply and every sheet heading, rule name and note in the file are in the user's language, and the reply does not start by narrating tool use.
