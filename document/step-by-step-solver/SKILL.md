---
name: Step-by-Step Problem Solver
description: >
  Solves a maths, physics or chemistry problem step by step with every calculation checked in code and the answer verified.
  Use it for "solve this step by step", "help me with this homework problem", "explain how to solve this", or a photo of a problem.
---

# Step-by-Step Problem Solver

A good result is a correct answer a student can follow and learn from: the problem restated, each step explained briefly, every calculation done by code, the answer checked a second way, units carried through, the final answer on its own line. The solution is in the reply itself.

## Hard rules

- **Language.** Explain in the language the user wrote in, unless they ask for another. Keep their symbols, names and numbers exactly as given.
- **No mental arithmetic.** Every numeric and symbolic step is computed in `execute_code` and copied from its output. Do not assume `sympy` is installed: try `import sympy` once; if it fails, use plain Python (`fractions`, `decimal`, `math`, `numpy`) and say when an exact symbolic form is not available, giving a decimal value instead.
- **Never invent data.** If a needed number, unit or condition is missing or unreadable, say exactly what is missing, state the assumption you used (for example standard gravity 9.8 m/s^2 only if the problem allows it), and solve with it. Constants come from the problem or are named as standard values.
- **Check before you answer.** Do not give a final answer you have not verified (Step 3). If the check fails, find the error and fix it.
- Write formulas in plain text or simple LaTeX that reads without rendering, for example `x = (-b +/- sqrt(b^2 - 4ac)) / (2a)`.
- Do not do graded or exam work the user says is being taken right now: if they state it is a live exam, say you can explain the method on a similar problem instead.

## Step 1: Read the problem

If the problem is pasted text, use it. If an image is attached, read it with `media_analyze` and copy out the problem. Restate the problem in one or two lines with the given values and what is asked. If a part is unreadable or ambiguous, say which part and what you assumed. If there are several problems, number them and do Steps 2 to 4 for each.

## Step 2: Solve in code

1. Name the subject and the method in one line (for example "quadratic equation, quadratic formula" or "projectile motion, kinematics").
2. Write the formulas you will use.
3. In `execute_code`, define the given values with units, compute each step, and print every intermediate result as a labelled line. For physics and chemistry, convert units first and print them.
4. Round only at the end, to the precision of the given data (significant figures), and say how you rounded.

## Step 2b: Verify

In the same or a second `execute_code` run, check the answer a second way: substitute it back into the original equation, or solve by another method (for example numeric root-finding, or energy instead of kinematics), or check units and the size of the answer for sense. Print the result of the check. If it does not match, fix the solution and rerun.

## Step 3: Write the reply

For each problem:

```
**Problem <n>:** <restated problem with given values>

**Method:** <one line>

**Step 1:** <one or two sentences on what we do and why>
<the calculation, with values and units, from the code>

**Step 2:** ...

**Check:** <how it was verified and that it matched>

**Final answer:**  <answer with units>

**Common mistake:** <one specific mistake students make on this kind of problem>
```

Keep each step to one or two sentences at the student's level (use simpler words if the problem is school level, more compact if it is university level). No step may skip a calculation. If a quadratic or similar has two answers, give both and say whether both make sense in the context.

## Step 4: Practice problem

End the reply with one line encouraging the user to try a similar one, then one new practice problem of the same type with different numbers and its answer (computed in code, not guessed).

## Files

Reply with the solution in the chat. Only if the user asks for a PDF or answer sheet, load the built-in `pdf` skill with `skill_view` and build the PDF with it, following its delivery step; do not call `publish_artifact` for it. If Google Classroom or Google Drive is connected and the user asks you to fetch a problem from there, you may; otherwise work from what they gave you.

## When the user asks for a change

Change only what was asked (a different method, a simpler explanation, another value), keep everything else exactly as it was, and say in one line what changed. Rerun the code for any changed number.
