---
name: Interactive Calculator Designer
description: >
  Designs and builds a working ROI, pricing, savings or cost calculator: inputs, formulas, result layout, methodology note and an honest email gate, as a spec plus a single-file HTML page.
  Use it for "design an ROI calculator", "build a pricing estimator", "what inputs should my savings calculator have", "make a lead-magnet calculator".
---

# Interactive Calculator Designer

A good calculator gives the visitor a result they can defend to a boss or a partner, shows the maths behind it, and earns the email by offering something extra (a PDF, a saved scenario), never by hiding the answer. Finish the whole job in one reply: spec first, then a working page.

## Hard rules

- The result is always shown free, before any email ask. Never gate the headline number.
- Use only figures the user gave. Any default, benchmark, price or rate you add is labelled "assumption (edit me)" in the spec and in the page, and benchmarks carry a source only if a search returned one. Never invent a statistic, a source, a customer or a "typical" industry figure. If a number is unknown, make it an input the visitor fills, with a placeholder, not a hidden constant.
- Do every sum in `execute_code` or Node. Never calculate in your head, and copy the computed values into the reply.
- Every modelling constant you choose is an assumption, not only prices and rates: time bands and their thresholds, multipliers, add-on amounts, discount percentages, range widths ("±8%") and review dates. List each one in the Assumptions line and in a constants table marked "assumption (edit me)", and make each one editable in the page.
- Ask no questions. If something is missing, choose the most common reading, say so in one "Assumptions" line, and go on.
- Nothing is sent anywhere. The email form in the page is a front-end stub that shows a confirmation and stores nothing, and the spec says where a real form endpoint would go.

## Step 1: Decide if a calculator is the right tool

Check in two or three lines: does the visitor face a real calculation in a decision, is it non-trivial (several inputs or branching, not "price x 12"), and can the maker disclose the method honestly? If it fails, say which test fails and what to build instead (a checklist or template), then still deliver the closest honest version the user asked for.

Name which of three kinds the design is. Aim for the third:
- Vanity calculator: a number with no defensible method ("score: 87" of what?).
- Lead-trap: real maths, result hidden behind an email form.
- Transparent decision tool: free result, visible method, email earned by extra value.

## Step 2: Spec the inputs

Read `references/inputs-and-results.md` for input and result patterns before writing the table. Produce a table: input, unit, type (number, slider, dropdown, toggle), default or placeholder, why it matters to the maths. Rules:
- Every input must change the output. Five to eight inputs is the usual ceiling; cut the rest.
- Prefer the user's own figures as defaults. Where you must default, mark it as an assumption.
- If the user gave no figures, leave the fields empty with placeholders, for example `placeholder="e.g. 1000"`. If you prefill a default anyway, the page must show a visible "assumption (edit me)" tag next to that field, not only in the reply.
- Add one-line help text for any input the visitor may not know how to find.

## Step 3: Write the formulas

Give each formula in plain notation with named variables, one per line, in calculation order, then one worked example using the user's own numbers (or clearly labelled sample numbers if they gave none, computed with code). Include: the headline result, the 2 to 4 pieces of the breakdown that add up to it, and a payback or break-even figure when money is spent up front. State rounding: show no more precision than the inputs justify. When a shown figure is rounded, give the unrounded value from the code next to it, for example "$84.47, shown as $85".

After the formulas, give a **Constants table**: constant, value, used in which formula, marked "assumption (edit me)" unless the user gave it. Spell out every helper mapping in full, for example "weight < 10 kg → 45 min; 10–20 kg → 60 min; ...", so the user can reproduce every step.

## Step 4: Design the result and the gate

Read `references/methodology-and-gating.md` for the methodology note and tier design.
- Result layout, top to bottom: headline number with units, one-line comparison to the visitor's current state, breakdown, a simple bar comparison, then the methodology note, then the next step.
- Methodology note: formulas, every assumption with its source or "assumption", the date the defaults were last checked, and what the calculator does not cover. Use the date only if the user gave one; otherwise write "Defaults last checked: [date – fill in]".
- Tier 1, free: headline, breakdown, chart, methodology. Tier 2, email: PDF or emailed copy of the full report with the inputs. Tier 3, account: saved scenarios and comparisons, only if the maker has accounts. Each tier must add real value over the one before.

## Step 5: Build the page

Build one self-contained `.html` file (inline CSS and JS, no libraries, works on a phone, labels on every field, keyboard usable, results update live as inputs change, sensible handling of empty or negative input). Load the built-in `frontend-design` skill with `skill_view` for the visual style if the user cares about look; otherwise a clean neutral style. Put the formulas in one JS function that takes the inputs and returns the results, so it can be tested.

Test it: write the same function into a small Node script, run it on three input sets (the worked example, a zero or empty case, a large case) with `terminal`, and check the output matches your hand-written worked example. Fix any mismatch before publishing. Then publish the page with `publish_artifact`, `kind: "html_preview"`.

Any extra example you quote, such as a below-break-even case, a break-even count or a large test case, must list every input it uses, including rates. Its numbers must come from this code run. If you did not compute it, leave it out.

## Step 6: Reply

The reply itself holds the full deliverable, in this order. Start directly with the Verdict line. Do not open with narration such as "I'll load the skill first...".

1. **Verdict**: one line on whether a calculator fits, and which kind this design is.
2. **Assumptions**: what you assumed because it was not given.
3. **Inputs table** (Step 2).
4. **Formulas and worked example** (Step 3), with the computed numbers.
5. **Result layout, methodology note and tier plan** (Step 4). Paste the methodology note as a verbatim block containing the formulas, every assumption, the date line and the exclusions. A summary or "it's on the page" does not count.
6. **The page**: the published preview and a two-line summary of what the test run showed.
7. **Before launch**: three or four items, for example confirm each assumption with real data, check it on a phone, add a real form endpoint, set a review date for the defaults.
