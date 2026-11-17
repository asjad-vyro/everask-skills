---
name: Working Capital and Cash Cycle
description: >
  Calculates DSO, DIO, DPO and the cash conversion cycle from the user's figures, shows where cash is stuck and sizes how much each fix would free up.
  Use it for "what is my cash conversion cycle", "calculate DSO and DPO", "how much cash would I free up if I cut DSO by 10 days", "should I take the early-payment discount", "why is cash tied up in receivables".
---

# Working Capital and Cash Cycle

A good result is a short working-capital review built only from the user's numbers: the metrics table, a plain diagnosis of where cash is stuck, the cash each lever would release, and a ranked action list. The whole job is finished in one reply. Never open with questions.

## Step 1: Collect the inputs from the message or files

Look for: revenue, COGS, receivables (AR), inventory, payables (AP), the period they cover (a year unless stated), currency, and optionally payment terms, supplier discount terms and cost of funds.

- If AR, AP and inventory are balances at one date and the P&L figures are for a year, use them as given. If the user gives opening and closing balances, use the average.
- If something is missing, do not stop. Compute whatever the given figures allow, say which metric could not be computed and what figure would unlock it. A service business with no inventory has DIO of 0: say so.
- If COGS is missing but revenue is given, say DIO and DPO need COGS, and show DSO only. Do not guess a margin.
- Use the user's currency and units (thousands, millions, B). If none is stated, write plain numbers with no symbol.

## Step 2: Do every calculation in `execute_code`

Never do arithmetic in your head. Run Python with the user's figures and copy the printed results into the reply. Formulas (period length `D` = 365 for a year, 90 for a quarter, 30 for a month):

- `DSO = AR / Revenue x D`
- `DIO = Inventory / COGS x D`
- `DPO = AP / COGS x D`  (on COGS, not revenue)
- `CCC = DSO + DIO - DPO`
- One day of revenue = `Revenue / D`; one day of COGS = `COGS / D`
- Cash released by cutting DSO by n days = `n x (Revenue / D)`
- Cash released by cutting DIO by n days, or by lengthening DPO by n days = `n x (COGS / D)`
- Working capital tied up in the cycle (rough funding need) = `(Revenue / D) x CCC`. This is an approximation: say so.
- Early-payment discount APR for terms "d% discount if paid in X days, otherwise net N" = `d/(1-d) x 365/(N-X)`. Take the discount only if this APR is higher than the user's cost of funds. Also give the cost of funds at which the decision flips (the APR itself).

Round days to one decimal and money to the nearest whole unit. State which formulas and period you used.

## Step 3: Diagnose

Read `references/wc-metrics.md` when the user gives monthly sales or aging data, asks about seasonality, bad debt, growth, or an acquisition working-capital peg, or says DSO looks fine but problems exist. Skip it for a plain "compute my CCC" request.

Without peer or history data, do not invent benchmarks. Say that no benchmark was given and that the user should compare against their own history, their stated terms, or sector peers (one `web_search` for a sector median is allowed only if the user asks for a benchmark; cite the link and say it is a rough guide).

For each component, state what the number means against the user's stated terms (for example, a DSO well above their stated net-30 terms means customers pay late or billing is slow), and name the most likely causes as hypotheses to check, not facts: terms creep, billing delays, disputes, slack collections, safety stock, slow movers, paying suppliers early with no discount.

## Step 4: Rank the levers and size them

Use these levers, fastest first, and size each with the Step 2 formulas using a stated, assumed number of days (label it "assumed target", never as a forecast):

1. Billing hygiene: invoice on delivery, fix dispute root causes.
2. Collections cadence: dunning calendar, credit holds, named collector owners.
3. Terms governance: standard terms by segment, approval for exceptions.
4. Payables: pay on terms, not early; take discounts only when APR beats cost of funds.
5. Inventory: SKU-level stock policy, supplier lead times, consignment.
6. Structural: receivables financing, supply-chain finance, dynamic discounting. Say these cost money and cost them before recommending.

Each action needs the operational risk (customer or supplier relationship, stock-outs).

## Step 5: Reply in this shape

The reply itself holds the whole review. Do not build a file unless the user asks for one.

```
## Working capital review

**Inputs used:** <figures, period, currency, any assumption>

| Metric | Days | How calculated |
|---|---|---|
| DSO | <n> | AR / revenue x <D> |
| DIO | <n> | Inventory / COGS x <D> |
| DPO | <n> | AP / COGS x <D> |
| Cash conversion cycle | <n> | DSO + DIO - DPO |

**Cash tied up:** <amount> (about <CCC> days of revenue; an approximation)

**Diagnosis:** <two to four bullets, one per component that stands out, each with the evidence and a hypothesis to check>

**Cash release by lever**
| Lever | Assumed change | Cash released | Difficulty / risk |
|---|---|---|---|

**Action plan:** <three to five numbered actions: lever, target days (assumed), owner role, first step, risk>

**Not given / assumptions:** <what was missing and what you assumed>

This is analysis from the figures provided, not financial advice.
```

If the user asked something narrow (one calculation, or a discount decision), answer that first in two or three lines with the working shown, then add only the sections that help.

## Hard rules

- Use only figures the user gave or that a tool returned. Never invent balances, terms, benchmarks, peer medians or customer names. Write "not given" where a figure is missing.
- Every number in the reply comes from `execute_code` output.
- A simple year-end DSO hides seasonality: when monthly sales are given, also compute the countback DSO (see the reference) and say which one you lead with.
- Cash released is an estimate of one-off cash, not recurring profit.
