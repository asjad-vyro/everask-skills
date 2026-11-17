---
name: Workflow Automation Designer
description: >
  Turns a manual business process into a designed automated flow: before and after diagrams, a Zapier, Make or n8n pick, build steps and a time-saved estimate.
  Use it for "automate this process", "design a Zapier flow for...", "which steps can be automated and how many hours would it save".
---

# Workflow Automation Designer

A good result is a document someone could build from: the current process mapped step by step, an automated version with triggers, decision rules, human checkpoints and error handling, a justified tool choice, and a time-saved estimate with the arithmetic shown. It is written in one reply from what the user gave.

## Step 1: Read the process and fill gaps with assumptions

Pull out who does each step, what they do, in which tool, how long it takes, how long it waits, what goes wrong, how often it runs and at what volume. Do not ask questions and do not open with a list of them. For anything missing, make a plain assumption, label it "Assumption:" and collect all assumptions in one short list near the top. Volumes, durations and hourly cost the user did not give are assumptions, never facts. If the process is only a line or two, build a plausible step list from the stated goal and say so.

## Step 2: Map and score the current state

Read `references/analysis-and-design.md` first. Build the step table (actor, tool, duration, wait, failure modes), classify each step, score automation potential, impact and risk (1 to 5), and note every decision point and handoff.

## Step 3: Design the automated flow

Using the same file, define the trigger, each action, each decision gate with an explicit rule, any parallel steps, the human checkpoints for high-risk or ambiguous cases, and error handling at step, flow and system level.

## Step 4: Pick the tool and estimate the impact

Read `references/tools-and-estimation.md`. Compare the candidate platforms against this process's needs and recommend one (plus a hybrid if it helps). Do not quote platform prices or app counts from memory: run one `web_search` for the recommended platform's current pricing and link what you found, or write "check current pricing" and use clearly labelled assumptions. Do every sum (hours per run, per month, per year, cost, break-even) in `execute_code` and copy the results into the reply. Never do the maths in your head. This includes every percentage or share quoted in prose (for example "phase 1 covers X% of hands-on time"), every waiting-time figure (sum the wait column in code, both before and after), and every table total. A table total must equal the exact sum of its rows, with no rounding to a nicer number. Operations or tasks per run are always labelled "Assumption:". Quote a platform tier limit (tasks, operations, app counts) only if it appears in the search result you linked. Otherwise write "check current plan limits". Quote prices with their billing basis (monthly or annual), and only as they appear in the search result. Use ranges, show the formula, and use the user's own volume and hourly cost or label yours as assumptions.

## Step 5: Write the reply

The whole document goes in the reply, in full, in this order. The reply's first line is the `#` heading, with no preamble such as "I'll load the skill". Use plain text, no emojis. The two diagrams are fenced `mermaid` code blocks (`flowchart TD`, descriptive node IDs, labelled edges, colour classes from the reference file); keep each under about 20 nodes. Never use the reserved words `end`, `start`, `graph`, `subgraph`, `style`, `class` or `click` as node IDs. Use camelCase IDs such as `startNode` and `endNode`.

1. `# Workflow Automation: <process name>` and one-paragraph summary with the headline saving as a range
2. Assumptions (list)
3. Current state: narrative in two or three sentences, the Mermaid diagram, the step table
4. Pain points: bottlenecks, error-prone steps, redundant steps, and the scoring table
5. Automated design: the Mermaid diagram, trigger, action list, decision gates, human checkpoints, error handling
6. Tool recommendation: choice, why, comparison table of the platforms considered, integrations needed
7. Implementation plan: phases with quick wins first, prerequisites, how to test and cut over, risks
8. Impact: time-savings table (step, manual time, automated time, saving per run, saving per month), total, cost and break-even, qualitative benefits
9. Monitoring: what to track and when to alert

## Hard rules

- Never invent figures, customers, tool limits or prices. Anything not given by the user or a search result is labelled as an assumption. Do not present a guess as "typical" or industry-standard; label it "Assumption:".
- Every step the user named appears in the current-state table and diagram.
- Every decision has an explicit rule and a default path when data is missing.
- High-risk actions (payments, deletions, external messages) keep a human approval step.
- Drafts of emails or messages the automation would send are not sent; this skill only designs.
- Both diagrams and the time-savings table are always present. Do not shorten the document to a summary.
- Do not use connected apps. If the user pasted or described the process, work from that.
- The estimate is not professional advice; say that tool limits and prices should be confirmed before purchase.
