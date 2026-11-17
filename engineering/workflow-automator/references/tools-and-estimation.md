# Tool choice and estimation

## Platform fit (qualitative; confirm current limits and pricing by search)

- Zapier: simple linear flows, non-technical owners, popular SaaS apps, live within hours, low volume. Per-task pricing gets costly at scale; branching and error handling are basic.
- Make: branching, loops, data transformation, array and JSON handling, error-handling routes, moderate volume.
- n8n (self-hosted or cloud): high volume, code nodes mixed with no-code, sub-workflows, strong error handling, data-residency needs. Needs a technical owner.
- Custom code: very low latency, logic a visual builder cannot express, core product flows, transactions and complex state. Highest build and maintenance cost.
- Power Automate: Microsoft-heavy environments (Microsoft 365, Teams, SharePoint, Dynamics), especially when already licensed.

Criteria to compare in the table: ease of setup, cost at this volume, support for the integrations this process needs, complex logic, error handling, hosting and data residency, who will maintain it. Rate each as high, medium or low and say why for this process.

## Hybrids

Zapier or Make for triggers plus n8n for logic; no-code for the common path plus custom code for exceptions; custom code for core logic plus no-code for notifications.

## Estimation rules

- Use the user's figures. Any figure they did not give is labelled "Assumption".
- Use median, not best-case, times. Separate active time from wait time; automation removes most wait time.
- Include exception handling: some share of runs will still need a person (state the assumed share).
- Use ranges ("saves 8 to 12 hours a month"), not a single number.
- Formula per step: saving per run = manual active time minus automated human time; monthly saving = saving per run times runs per month; annual = monthly times 12.
- Cost: platform subscription (from a search or marked as assumed), hosting if self-hosted, setup hours, and ongoing maintenance hours. Labour saved = hours saved times the hourly cost (user's or assumed).
- Break-even = one-off setup cost divided by net monthly saving.
- Compute all of this in `execute_code`, then paste the numbers into the tables.
