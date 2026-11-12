# Pipeline Stages, Deal Desk, Data Hygiene and Metrics

The parts of RevOps that sit after the marketing-to-sales handoff. Every number here is a starting template: replace it with the user's own policy or baseline.

## Pipeline Stages

| Stage | Required Fields | Exit Criteria |
|-------|----------------|---------------|
| **Qualified** | Contact info, company, source, fit score | Discovery call scheduled |
| **Discovery** | Pain points, current solution, timeline | Needs confirmed, demo scheduled |
| **Demo/Evaluation** | Technical requirements, decision makers | Positive evaluation, proposal requested |
| **Proposal** | Pricing, terms, stakeholder map | Proposal delivered and reviewed |
| **Negotiation** | Redlines, approval chain, close date | Terms agreed, contract sent |
| **Closed Won** | Signed contract, payment terms | Handoff to CS complete |
| **Closed Lost** | Loss reason, competitor (if any) | Post-mortem logged |

Rename or merge stages to match how the user actually sells. Every stage needs an owner, required fields and an exit test a rep can check.

### Stage Hygiene

- **Required fields per stage**: don't let reps advance a deal without filling in the required data
- **Stale deal alerts**: flag deals that sit in a stage beyond the average time (for example 2x the average days for that stage)
- **Stage skip detection**: alert when deals jump stages (Qualified to Proposal, skipping Discovery)
- **Close date discipline**: pushed dates must include a reason; no silent pushes

### Pipeline Metrics

| Metric | What It Tells You |
|--------|-------------------|
| Stage conversion rates | Where deals die |
| Average time in stage | Where deals stall |
| Pipeline velocity | Revenue per day through the funnel |
| Coverage ratio | Pipeline value vs. quota |
| Win rate by source | Which channels produce real revenue |

Coverage needed is roughly 1 divided by the win rate (a 25% win rate needs about 4x coverage). The "3-4x" figure is commonly quoted; set the user's number from their own win rate.

---

## Deal Desk

### When You Need One

Set the triggers with the user. Typical ones:
- Contract value above a threshold (a common example is $25K a year; use the user's own)
- Non-standard payment terms (net-90, quarterly billing)
- Multi-year contracts with custom pricing
- Volume discounts beyond published tiers
- Custom legal terms or SLAs

### Approval Tiers (example: replace with the user's policy)

| Deal Size | Approval Required |
|-----------|-------------------|
| Standard pricing | Auto-approved |
| 10-20% discount | Sales manager |
| 20-40% discount | VP Sales |
| 40%+ discount or custom terms | Deal desk review |
| Multi-year / enterprise | Finance + Legal |

If the user gives their own limits, build the matrix from those and keep the same shape. For every tier add the approver's turnaround time (for example one business day) and what the rep submits with the request: deal size, discount, reason, competitor, term.

### Non-Standard Terms Handling

Document every exception. Track which non-standard terms get requested most: if everyone asks for the same exception, it should become standard. Review quarterly.

This is a process template, not legal or financial advice; have finance and legal review the limits and terms.

---

## Data Hygiene and Enrichment

### Dedup Strategy

- **Matching rules**: email domain + company name + phone as primary match keys
- **Merge priority**: the CRM record wins over the marketing automation record; the most recent activity wins for fields
- **Scheduled dedup**: run a weekly automated dedup with manual review for edge cases

### Required Fields Enforcement

- Enforce required fields at each lifecycle stage
- Block stage advancement if fields are empty
- Use progressive profiling: don't require everything upfront

### Enrichment Tools (optional: none is required, and the CRM's built-in enrichment may be enough)

| Tool | Strength |
|------|----------|
| Clay | Waterfall enrichment across many providers |
| Apollo | Contact data and outbound sequences |
| ZoomInfo | Enterprise B2B company and contact data |

### Quarterly Audit Checklist

- Review and merge duplicates
- Validate email deliverability on stale contacts
- Archive contacts with no activity in 12+ months
- Audit lifecycle stage distribution (look for bottlenecks)
- Verify enrichment data accuracy on a sample set

---

## RevOps Metrics Dashboard

### Key Metrics

| Metric | Formula / Definition | Target |
|--------|---------------------|--------|
| Lead-to-MQL rate | MQLs / total leads | Set from the user's last two quarters |
| MQL-to-SQL rate | SQLs / MQLs | Set from the user's last two quarters |
| SQL-to-Opportunity | Opportunities / SQLs | Set from the user's last two quarters |
| Pipeline velocity | (# deals x avg deal size x win rate) / avg sales cycle | Varies by contract size |
| CAC | Total sales + marketing spend / new customers | Falling over time |
| LTV:CAC ratio | Customer lifetime value / CAC | 3:1 is a commonly quoted floor |
| Speed-to-lead | Time from form fill to first rep contact | The response-time target in the routing rules |
| Win rate | Closed-won / all closed opportunities | Set from the user's last two quarters |

Where the user has no history yet, say the targets are blank until about two months of data exist, and show how to measure each one.

### Dashboard Structure

Build three views:
1. **Marketing view**: lead volume, MQL rate, source attribution, cost per MQL
2. **Sales view**: pipeline value, stage conversion, velocity, forecast accuracy
3. **Executive view**: CAC, LTV:CAC, revenue vs. target, pipeline coverage
