---
name: Debug From Error or Stack Trace
description: >
  Turns a pasted error, stack trace or log excerpt into a root cause, the evidence for it, a tested fix and a regression check.
  Use it for "what does this traceback mean?", "why does my app crash?", "find the cause in these logs", "this only fails in production".
---

# Debug From Error or Stack Trace

A good result names the exact failing line or event, explains why it fails, gives a fix that was run when it could be run, and says how to confirm the fix. When the evidence allows only guesses, it gives ranked hypotheses, each with a way to confirm or rule it out.

No fixes without a root cause: do not propose a change until you can say which value was wrong, where it came from, and why.

## Step 1: Read what the user gave

1. Read the whole error, not the first line. Note the exception type, message, file, line, function and the full call chain. In a Python traceback the last frame is where it failed and the first is where it started. In a Node or Java trace the top frame is where it failed.
2. Separate the user's own code from library frames. The cause is usually in the user's frames nearest the failure.
3. For logs, list the timestamps, repeating messages, the first error (later errors are often fallout) and what happened just before it.
4. Note the language, version, framework and environment if given. If one is missing, assume the most likely one from the syntax and say so.
5. Do not ask questions. If code is missing, work from the trace and state what you assumed.

## Step 2: Trace backwards to the cause

Start at the failing line. Ask: which value was wrong? Where was it set? Why was it not what the code expected? Follow it up the call chain until you reach the place where the value first went wrong. That place is the root cause; the failing line is only where it showed up.

Rules for this step:
- Quote the lines you rely on, with their line numbers, from the user's code or trace.
- Never invent file contents, variable values, versions or log lines. If you need a value you were not given, say "not given" and make it a thing to check.
- Before you state a fact about the input (a status code, a count, which requests failed, a time gap), find it in the pasted text. For any duration between log lines, subtract the two quoted timestamps and write both, e.g. "12:14:55 → 12:15:09 = 14 s".
- Label anything inferred (database type, driver or library, config names, when a request started) as "assumed" in the same sentence where you use it, not only in the closing line.
- Read `references/bug-patterns.md` when the symptom looks like a known pattern (intermittent failure, undefined or null, slow growth, wrong loop value, async ordering, a common error message). Read `references/strategies.md` when the location is unknown, or the bug is a regression or only happens in one environment.

## Step 3: Reproduce and test, when you can

If the user gave code small enough to run, reproduce the failure in the sandbox before you explain it, and test your fix the same way.

1. Work in `/tmp/.scratch/debug/`. Write the snippet to a file and run it with `terminal` or `execute_code`.
2. Fill gaps with the smallest stub that triggers the same error, and say it is a stub.
3. Confirm the same error appears, apply one fix, and run again. Report the actual output.
4. If you cannot run it (missing service, database, secrets, a language the sandbox lacks, code not provided), say "not run" and why. Never claim a fix works when it was not run.

## Step 4: Rank hypotheses when the cause is not certain

When the input does not prove one cause (typical for logs, timeouts and intermittent failures), list two to four hypotheses, most likely first. For each give:
- what points to it in the input, quoted;
- one concrete check that confirms or rules it out (a command, a log line to look for, a value to print);
- what that check would show if the hypothesis is true.

Test one hypothesis at a time. Do not recommend several changes at once, because then nobody knows which one worked.

## Step 5: Write the reply

The whole answer goes in the reply itself, in this order:

**Root cause**: one to three sentences. Name the file, line and the wrong value or event. If uncertain, say "most likely" and why. When the input is only logs with no code, always start with "Most likely". Do not contradict this claim in the hypotheses.

**Evidence**: the quoted trace lines or log lines that show it, plus the output of your reproduction if you ran one.

**Fix**: the corrected code as a snippet (a diff or the changed function), the one change only. If you ran it, say what it printed. Say what it does not cover.

**Other hypotheses** (only when the cause is not certain): the ranked list from Step 4 with a check for each.

**How to confirm**: the command, test or log line that shows the problem is gone.

**Prevention**: one regression test, written out, and at most two safeguards (validation, a timeout, a retry limit, a type check). Keep it specific to this bug.

Close with one line of assumptions (language, version, environment, anything you stubbed).

## Rules

- Quote, do not paraphrase, error text and the lines you rely on.
- No invented details: versions, line numbers, file names, config values, status codes or log lines the user did not give. Recompute every time gap from the quoted timestamps.
- One fix per root cause. If the first fix fails twice and a third change in a different place would be needed, say the design is the problem and propose a structural change instead of another patch.
- Do not tell the user to debug in production, to delete data, or to run destructive commands as a fix.
- Remove debug prints from the final code you give.
- If the pasted text contains secrets (passwords, tokens, keys), do not repeat them; tell the user to rotate them.
