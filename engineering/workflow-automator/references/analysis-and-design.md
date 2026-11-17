# Analysis and design method

## Current-state table

Columns: Step #, Action, Actor, Tool, Input, Output, Active time, Wait time, Failure modes.

Classify each step as one of: Manual-Repetitive (same every time, prime target), Manual-Judgment (needs rules or AI), Manual-Creative (templates or AI assist), Already Automated, Handoff (latency risk), Wait State.

## Scoring (1 to 5)

- Automation potential: 5 trivial, 1 needs human judgment
- Impact if automated: 5 massive, 1 marginal
- Risk if broken: 5 catastrophic, 1 easily recovered

High potential, high impact and low risk steps are phase 1. High-risk steps need error handling and a human fallback.

## Decision points

For each: the question, how it is decided today, data needed, each outcome, approach (rule-based, AI-assisted, or human), and the confidence threshold below which it goes to a human.

## Handoffs

For each: from, to, mechanism (email, chat, sheet, API), data passed, context lost, typical latency, how often it stalls.

## Triggers

Primary trigger: webhook or form submit, schedule, status change or threshold, manual button, incoming email or message. Secondary triggers resume a paused flow: timer expiry, a reply or approval, a payment or signature.

## Action spec

Per action: ID (A-1, A-2), name, type (API call, transform, notification, file operation, gate, wait), system, input, logic, output, retry policy, timeout, fallback (usually notify a person).

## Decision gate spec

Gate ID, condition, IF TRUE goes to, IF FALSE goes to, fields evaluated, what happens when data is missing, default path.

## Parallel blocks

Branches that can run at once, the join condition (all, any, N of M), timeout, what happens if one branch fails.

## Error handling, three levels

- Step: retries with backoff, then log and fall back
- Flow: failed runs go to a queue for review, a person is notified in a named channel, partial runs are rolled back where possible
- System: monitor the platform, handle rate limits, refresh credentials, use idempotency keys or duplicate checks

## Human checkpoints

Design them for judgment calls, money or reputation risk, exceptions outside the rules, and spot checks of a sample of automated decisions. For each: trigger, how the person is alerted, what context they see, actions available (approve, reject, edit, escalate), response deadline, and what happens when the deadline passes.

## Mermaid conventions

Descriptive node IDs (`checkInvoice`, not `A1`), every edge labelled, wait times on edges where relevant, subgraphs as swim lanes when several actors are involved, split anything over about 20 nodes. Colours:

- Manual step: `fill:#e0e0e0`
- Automated step: `fill:#4CAF50,color:#fff`
- Decision: `fill:#2196F3,color:#fff`
- Human checkpoint: `fill:#FF9800,color:#fff`
- Error path: `fill:#f44336,color:#fff`
- Wait state: `fill:#9C27B0,color:#fff`

Apply with `style nodeId fill:#...` lines at the end of the diagram. Keep node text free of parentheses and quotes that break Mermaid; wrap labels in double quotes.
