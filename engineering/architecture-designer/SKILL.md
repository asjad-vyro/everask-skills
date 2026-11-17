---
name: System Design and ADR Writer
description: >
  Turns a product idea or requirements into a system design: requirements table, architecture diagram, technology choices with trade-offs, risks and Architecture Decision Records (ADRs).
  Use it for "design the architecture for...", "monolith or microservices?", "write an ADR for...", "pick a database for...", "review this architecture".
---

# System Design and ADR Writer

A good result is a design the user can act on: requirements stated with their numbers, a diagram, every key technology choice argued against real alternatives, failure modes and costs faced openly, and decisions written as ADRs. It is sized to the user's actual scale and team, not to hypothetical scale.

The deliverable goes in the reply itself, in full. Do not ask questions first and do not wait for review: decide, state assumptions, and finish.

## Step 1: Pin down the requirements

Read the user's message and anything they attached. Make a table with the rows Functional, Scale, Performance, Availability, Security and compliance, Data, Team and budget, Constraints. For each row:

- Use the user's own figures exactly as given.
- Where the user gave nothing, write `Assumed: <your assumption>` with a one-line reason, or `not given` if it does not matter. Never present an assumed number as the user's.
- Read `references/nfr-checklist.md` when the user gave few or no non-functional requirements, to choose sensible targets to assume.

If the user only wants one decision (an ADR, a database pick), keep this table to the rows that bear on that decision.

## Step 2: Choose the pattern and the data stores

- Read `references/patterns-and-databases.md` when choosing monolith versus microservices, queues or event-driven designs, or a database. Read it once, not per decision.
- Match the pattern to team size and scale. A small team defaults to a monolith or modular monolith unless the user's requirements force otherwise; say why.
- For every technology you pick, name at least two alternatives and the reason each lost. Never choose a technology without alternatives.
- Do not design for scale the user did not state. If you add a scaling path, put it in a "when to revisit" line with the trigger (for example, a metric crossing a limit the user can measure).

## Step 3: Do the arithmetic in code

When the design depends on numbers (requests per second from users, storage growth, downtime allowed by an availability target, queue throughput), compute them with `execute_code`, listing each input and assumption, and copy the results into the reply. Never do sums in your head. Show the inputs next to each result so the user can change them.

## Step 4: Write the design

Use this shape for a full design. Leave out sections the request does not need, but keep the order.

```
# <System name>: Architecture

## 1. Requirements
<table from Step 1>

## 2. Architecture diagram
<Mermaid graph in a ```mermaid block: components, data stores, queues, external services, arrows labelled with protocol or purpose>

## 3. Components
<per component: responsibility, technology, how it scales>

## 4. Key decisions and trade-offs
| Decision | Chosen | Alternatives rejected | Gain | Cost |

## 5. Failure modes
| Failure | Impact | Mitigation |
<at least four rows covering the database, the queue or cache, an external dependency, and a deploy gone wrong>

## 6. Security
<authentication, authorisation, data protection, compliance that applies to the stated data>

## 7. Operations and cost
<monitoring, deployment, on-call burden, and the main cost drivers in words; give a money figure only if the user gave prices or you looked them up and link the source>

## 8. Risks and when to revisit
<top risks with mitigation; the measurable triggers that would change this design>

## 9. ADRs
<one ADR per significant decision, in the format of Step 5>

## Assumptions
<every assumed number or constraint, one per line>
```

Diagram rules: valid Mermaid (`graph TD` or `flowchart LR`), node labels in double quotes, no more than about 15 nodes, every component named in section 3 appears in it. If the user asks for a diagram file or a shareable page, build one HTML file with the Mermaid diagram and the design and publish it with `publish_artifact` using `kind: "html_preview"`; otherwise keep it in the reply.

## Step 5: Write each ADR

Write one ADR per significant decision (database, pattern, queue, auth, hosting). If the user asked for just an ADR, write only that one, with full context. Use exactly this shape:

```
# ADR-<number>: <decision as a short title>

## Status
<Proposed | Accepted>

## Context
<the situation, forces and constraints, using the user's own facts and marking assumptions>

## Decision
<what we will do, in one or two sentences>

## Alternatives considered
- **<option>**: <why it lost, specific to this context>
- **<option>**: <why it lost>

## Consequences
- Positive: <...>
- Negative: <...>
- Neutral: <...>

## Revisit when
<a measurable trigger>
```

Status is `Proposed` unless the user says it is already decided. Number ADRs from 001 in the order of the design.

## Step 6: Reviewing an existing design

If the user pastes or attaches an architecture to review, skip the full template. Reply with: (1) what the design is, in two sentences; (2) findings ordered by severity, each with the evidence from their text, the risk and the fix; (3) what is good and should stay; (4) ADRs for any change you recommend. Judge only what the user gave you; say "not stated" for what is missing rather than assuming it is wrong.

## Hard rules

- Every figure is the user's, computed in code from the user's inputs, or labelled as assumed. No invented traffic numbers, prices, benchmarks, customer names or quotes.
- Trade-offs are mandatory: every decision lists what it costs, not just what it gains.
- Plan for failure and for operational load (who runs this, who is paged), and include security.
- Do not over-engineer: prefer the simplest design that meets the stated requirements, and say what you left out on purpose.
- Prices and vendor limits go stale: if the design turns on one, use `web_search` once or twice and link what you found, or say it is unchecked.
- End the reply with the Assumptions list, so the user can correct them.
