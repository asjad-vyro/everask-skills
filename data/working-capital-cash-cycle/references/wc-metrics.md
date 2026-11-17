# Working capital metrics cookbook

All figures below are placeholders to show the method. Use only the user's numbers, computed in `execute_code`.

## Countback DSO (use when sales are seasonal)

Walk backwards through monthly sales until the AR balance is used up.

1. Start with AR and the latest month's sales. If AR is at least that month's sales, subtract the sales and count all the days of that month.
2. Move to the previous month and repeat.
3. In the first month that is not fully covered, count `remaining AR / that month's sales x days in that month`.
4. Countback DSO = total days counted.

Simple DSO (AR / average sales x days) misstates the figure after a strong or weak quarter. Lead with countback when at least three months of sales are given, and show simple DSO beside it.

## Aging migration (roll rates)

For each aging bucket, divide the amount that moved to the next-older bucket this month by the bucket's balance last month. Build a table with rows "from" bucket and columns "to" bucket plus "collected".

- Rising roll rates mean collections discipline is slipping before headline DSO moves.
- The roll rate from 61-90 into 90+ is the early warning for bad debt and feeds the provision.
- Headline DSO can look stable while bad debt rises: strong new sales dilute the ratio, write-offs and factoring remove old items, and credit notes reset aging. Check all four.
- Look at overdue concentration in named accounts: a few large late payers matter more than many small ones.

## Early-payment discount rule

For terms "d% off if paid within X days, otherwise net N":
`APR = d/(1-d) x 365/(N-X)` with `d` as a decimal.
Take the discount if the APR is higher than the cost of the cash used to pay early; otherwise pay on day N. The APR is also the breakeven cost of funds. Paying early with no discount is free lending to the supplier.

## Peak versus average working capital

Month-end balances understate intra-month peaks (payroll dates, tax payments, stock builds before a sales spike). For sizing a credit facility, ask for or estimate the peak; say it is an estimate. For an acquisition working-capital peg, a 12-month average neutralises seasonality, and every account in the peg must be defined explicitly. Peg disputes are usually about definitions.

## Growth's working-capital cost

`Change in working capital needed ~ (CCC / 365) x change in annual revenue`. This is approximate (it treats the whole cycle as revenue-funded). A longer cycle makes every extra unit of growth need more cash: show this when the user mentions growth plans.

## Period-end window dressing

Signs: DPO spikes at each quarter-end then falls back, receivables factored in the last week, stock cut by delaying receipts. Use period averages to see through it, and set targets against the same month of the prior year so a seasonal business is not pushed into a quarter-end scramble.
