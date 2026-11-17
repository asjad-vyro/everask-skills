# Templates for task, spike and epic, and the severity scales

## Task

```
TITLE: <verb> <object> <qualifier>
TYPE: Task | OWNER: <unassigned> | PARENT STORY: <link or none> | ESTIMATE: <not given>

TASK SPEC
<what changes, in plain language, two to five sentences; what, not how, unless the how is a constraint>

TOUCHES (name what the source supports; mark guesses "likely")
- Files or modules: <...>
- Services: <...>
- Feature flags: <...>
- Tables or schemas: <...>
- Config or infrastructure: <...>

DOES NOT TOUCH
- <nearby things that must stay unchanged>

QA NOTES
- <what to check; what existing behaviour must not regress>

DEFINITION OF DONE
- [ ] <observable outcome>
- [ ] Tests added or updated: <which>
- [ ] Nothing outside TOUCHES changed, or the change is noted in the PR
```

A task should fit in one to two days; otherwise split along the touches list (one service, migration or surface per task), ordered by dependency (schema before code that reads it, flag before code behind it). "Done" and "Tested" are not a definition of done.

## Spike

```
TITLE: Spike: <the question, shortened>
TYPE: Spike | OWNER: <unassigned> | PARENT: <epic or story the answer unblocks>

QUESTION
<one sentence ending in a question mark>

WHY NOW
<the decision that is blocked until this is answered>

TIMEBOX
<N working days; hard stop. If the user gave none, propose one and mark it (assumed)>

EXIT CRITERIA
<what counts as an answer, for example a recommendation between the named options with cost and one risk per option>

RESOURCES TO EVALUATE
- <services, internal systems, documentation>

OUT OF SCOPE
- <what the spike will not investigate>

OUTPUT ARTIFACT
Decision memo with: Recommendation; Options considered (fit, cost, risk); Evidence; Still unknown; Follow-up tickets.
```

If time runs out, the memo says what is still unknown. "We looked into it" is not an output.

## Epic

```
TITLE: <outcome in a few words>
TYPE: Epic | DATE OPENED: <not given> | OWNER: <one name or unassigned>

GOAL
<one sentence, the outcome for users or the business>

SUCCESS METRIC
- Metric: <one primary metric>
- Baseline: <value and date, or not given>
- Target: <value, or not given>
- Measured by: <date or window>

KILL CRITERIA (observable, dated, owned by one person)
- <signal that ends the epic early>

ROADMAP FITMENT
- Quarter / objective / dependencies: <as given, else not given>

SCOPE
- In: <...>
- Out: <...>

CHILD ITEMS
- <stories and spikes>
```

Kill criteria are written before the work starts. If the user gave no numbers, propose a shape such as "adoption below <threshold> after <N> weeks" and mark thresholds as assumed.

## Severity scale

| Level | Meaning |
|---|---|
| S1 critical | Data loss, security exposure, or a core flow fully blocked for many users |
| S2 major | Core flow degraded, or blocked for a segment, with no workaround |
| S3 minor | Non-core flow broken, or a workaround exists |
| S4 cosmetic | Visual or copy defect, no functional impact |

## Priority scale

| Level | Meaning |
|---|---|
| P0 | Drop current work, fix now |
| P1 | Fix in the current sprint |
| P2 | Fix this quarter |
| P3 | Backlog |

Set severity from the defect. Set priority from severity plus reach, revenue, timing and cost of delay.
