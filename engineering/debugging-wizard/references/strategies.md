# Isolation strategies

Pick the one that fits and say which you used.

| Situation | Strategy |
|---|---|
| Error line known, cause not | **Trace backwards**: what value caused it, where was it set, where did it first diverge from what was expected |
| Bug somewhere in a long pipeline | **Binary search**: print or check the value at the midpoint; the bug is in the half where it goes wrong; repeat |
| Complex bug, big input | **Minimal reproduction**: shrink the input and remove dependencies one at a time until the smallest case still fails; keep that case as the bug report and the test |
| It used to work | **Compare**: list what changed (code, dependencies, config, data, environment) and test one change at a time. If the user has version control, `git bisect` finds the first bad commit; `git bisect run <test command>` automates it |
| Logic gives wrong results with no error | **Explain line by line**: state what each line should do and what it does with the actual values; the first mismatch is the bug |
| Works locally, fails elsewhere | **Diff the environments**: versions, environment variables, permissions, data, network, time zone, locale |
| Intermittent | **Make it deterministic**: add a fixed seed, a delay or a forced ordering, run it many times, log timestamps and identifiers to see the interleaving |

## Instrumentation

Temporary prints at the boundaries where data enters and leaves a step (`print(f"{value=}")` in Python, `console.log({ value })` in JavaScript). Print type and value. Remove them from any code you hand back.

Debuggers when the user can run them: `python -m pdb script.py` or `breakpoint()`; `node --inspect-brk script.js`; `dlv debug` for Go.

## When fixes keep failing

If a fix fails, go back to the evidence and form a new hypothesis; do not stack a second change on top. After three failed fixes in different places, the assumption underneath is probably wrong: write down what the code assumes, find where that is violated, and propose a structural change.
