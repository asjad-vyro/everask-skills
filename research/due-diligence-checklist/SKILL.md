---
name: Due Diligence Checklist Builder
description: >
  Builds a tailored due diligence checklist and red-flag log for a deal, company or vendor, as an Excel workbook plus a summary in the reply.
  Use it for "build a due diligence checklist", "diligence request list", "what do we need to check before buying this business", "data room review", "red-flag tracker".
---

# Due Diligence Checklist Builder

A good result is a request list the deal team can send tomorrow: every item belongs to a workstream, has a priority and a status, the items that matter most for this particular target come first, and a red-flag log is ready to fill in. It is a working tool, not professional legal, tax or financial advice.

## Step 1: Fix the scope from what the user gave

Never ask questions first. Read the message (and any attachments) and settle these five points. For anything not given, pick a sensible default and record it as an assumption:

- Target: name, sector, business model, size (headcount, revenue if given).
- Deal type: acquisition, add-on, investment or growth equity, merger, carve-out, vendor or partner check. Default: acquisition of the whole business.
- Depth: light for a small deal (under about 25 people or a simple business), standard for mid-size, deep for large or regulated targets.
- Key concerns the user named (customer concentration, key person, regulatory, IP, debt, and so on). These become P0.
- Timeline: LOI or close date if given, otherwise "not stated".

If the user attached a data room index or document list, use it in Step 4. Use `clarify` only if there is no target or deal at all.

## Step 2: Build the checklist

Read `references/workstreams.md` for the item bank and the sector add-ons. Select the workstreams that apply to this deal, and pick items by depth: light is about 40 to 60 items, standard 70 to 100, deep up to 130. Do not paste every item from the bank. Add the sector items that match the target. Every item gets:

- ID (for example FIN-03), Workstream, Item (what to request, written as a specific document or answer, not a topic), Why it matters (one short line), Priority, Status (all "Not started" unless the user gave progress), Owner (blank), Due (blank), Notes.

Priority rules:
- P0: gates the LOI or closing, or is directly tied to a concern the user named. Make at least the user's named concerns P0, and put their items first in their workstream.
- P1: needed before signing.
- P2: confirmatory, can finish after signing or post-close.

Status values: Not started, Requested, Received, In review, Complete, Red flag.

## Step 3: Seed the red-flag log

Add 5 to 10 "watch for" red flags specific to this target and its named concerns, drawn from the item bank and the user's facts. Each has: what to look for, workstream, severity if confirmed (deal-breaker, significant, manageable), a possible mitigant, and the likely effect on price or terms, in words only (no percentages or amounts). Label these as hypotheses to test, not findings. Never state that the target has a problem the user did not report.

## Step 4: Data room gap check (only if a document list is given)

Compare the list against the checklist. Mark items as covered when a document plausibly answers them, and list the P0 and P1 items with no matching document as gaps. Do not claim a document contains something you have not read.

## Step 5: Build the workbook

Load the built-in `xlsx` skill with `skill_view` and follow it. Create `Due_Diligence_Checklist_<Target>.xlsx` with three sheets:

1. `Summary`: target, deal type, depth, timeline, assumptions, then a table by workstream with item counts, P0 counts and percent complete. Use live formulas (COUNTIFS) over the Checklist sheet so it updates when statuses change, and a note on how to use it.
2. `Checklist`: all items, frozen header row, filters on, a dropdown on Status and Priority, wrapped text, sensible column widths.
3. `Red flags`: the seeded flags, with empty rows below for new ones.

Count items per workstream in `execute_code` first so the numbers you quote match the file. Publish the file with `publish_artifact` (`kind: "document"`).

## Step 6: The reply

Put this in the reply itself, in full, after publishing:

1. Two lines on scope, and an "Assumptions" list of every default you chose.
2. A table of workstreams with item counts and P0 counts.
3. The P0 items in full (ID, item, why it matters), grouped by workstream.
4. The seeded red flags as a short table.
5. Next steps: the first five requests to send to the other side, in order.

## Hard rules

- No invented numbers anywhere in the checklist, red flags or reply: no percentage thresholds (such as "flag anything above 5%"), no price-impact or escrow or earn-out percentages, no currency amounts, no benchmarks. Describe effects in words ("could justify a lower price, an earn-out or a holdback") and let the user set levels. Do not assume a currency or country; if you use country-specific terms, name the jurisdiction as an assumption.
- Use only the facts the user gave; everything else is marked as an assumption. Do not invent figures, company details, findings, legal requirements or benchmarks.
- Laws, tax rules and regulatory thresholds change and differ by country. Name the area to check (for example "data protection compliance in the target's markets") and do not cite specific rules or numbers unless you looked them up with `web_search` and link the source.
- Do not stop to ask for approval; deliver the whole job in one reply.
- Match the language of the user's message.
- If the target is a vendor or partner rather than an acquisition, drop the valuation items and use the vendor items in the item bank.
