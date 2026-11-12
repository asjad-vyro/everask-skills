# Sizing rules for the special cases

Read the parts that apply to this run. Every default here (60 days, 1.5x, 90 days, 400 days) can be replaced by a figure the user gives; say which you used.

## When the two rates disagree

| Pattern | Reading | Action |
|---|---|---|
| 7-day close to 28-day | Steady | Plan on the numbers as they are |
| 7-day much higher | Trending up, or one bulk order | Look at the order lines or daily figures before believing it |
| 7-day much lower | Cooling, or out of stock part of the week | Check stock was available all week |
| 7-day zero, 28-day positive | Stopped selling, or ran out | Check stock history before calling it dead |

When the rates differ by more than 50%, look at the individual orders or daily figures before recommending anything. One order far above the item's usual size (a wholesale order, a job) is a one-off, not a trend. Report it and recompute both rates without it. With order lines, drop just that order. With daily totals, replace that day with the item's typical day (the median of its other days) so the day count stays right. Then apply the normal rules to those rates: the higher one for days of cover, the 28-day one for sizing. Show both sets on the line, for example: `12.6/day with the 60-unit order on 3 Nov, 4.0/day without it, planning on 4.0`. Several larger orders across different days are a trend: say so, and let the higher rate stand for cover.

## Stock-out periods

A day with no stock is not a day with no demand. Velocity = units sold / days the item was in stock. If the data has no stock history, a zero-sales stretch next to a zero or near-zero count is a stock-out, and the user may say so. Write it plainly: "out of stock 20 of the last 28 days: that is suppressed demand, not slow sales; planning on 1.5/day." Skipping this under-orders the items that keep running out: the zero days drag the rate down, the next order is smaller, the item runs out sooner.

## Returns, promotions, bundles

- Returns: net them out of the period they were sold in, not the one they came back in.
- Promotions: a discount period is not a baseline. If the user mentions a sale, note it and size on the rate outside it.
- Bundles and kits: a bundle sale uses up component stock. If the data shows bundles and their contents, count the components; otherwise say component rates may be understated.

## Pack size and supplier minimums

- Round up to a full pack unless that goes over 90 days of cover at the sizing rate: then round down. Say which way.
- A minimum order (value or units) is almost always on the whole supplier order, not each line. Check the supplier total first: several short lines may clear it together, and splitting a line to hit it orders stock nobody needs.
- If the order still falls short, never round up silently. Give the three numbers: excess units, excess cost, excess days. Illustration with made-up numbers: "Minimum is 1,000; the order as sized is 888. Clearing it takes one more case (40 units, 148, about 10 extra days at 4.1/day). The draft PO is at 888; add the case if the supplier won't ship below the minimum." The user decides.

## Seasonality

- Under 400 days of history: no computed factor. Say how many days you have, plan on the current 28-day rate, and apply any multiple the user gave, labelled "sized at 1.8x current rate per your estimate, not from history". The label is what lets the user recalibrate next season.
- 400 days or more: compare the planning window with the same window last year.
  `seasonal_factor = units sold in the same window last year / units sold in the 28 days before that window, last year`
  Apply it to the sizing rate, and to the stockout rate when projecting into the season. A factor above 3x or below 0.3x is shown to the user, not applied silently: it usually means a promotion, a stock-out or a one-off in last year's data. Prefer category-level factors for items with thin history. If the item was out of stock in last year's window, last year's units understate demand: say so instead of applying the factor.
- Known events the user names (a big job, a promotion, a supplier price rise that may justify buying early, a supplier shutdown that often doubles lead times) are one-time adjustments on specific items, always labelled as the user's, not computed.
- Show both numbers on an adjusted line: `Current 0.4/day (28d); seasonal 1.9x per your estimate; sizing at 0.76/day`.

## When the user names the end of the season

Sizing 60 days of stock at the busy rate six weeks before the season ends buys a month of stock for a month that won't happen. When the user gives an end date, cap the order at the days left in the season, and never silently:

```
days_left       = season_end_date - expected_arrival_date   (order date + lead time)
target_uncapped = (60 + lead_time) * sizing_rate
target_capped   = days_left * sizing_rate
```

Show both and say which one goes on the PO: "the season ends 47 days after this order lands, not 60; capped order 309 units, uncapped 440; the extra would sit until next season." The user can override: some items keep fine and are worth carrying over. If the season ends before the stock could land, don't order: put the item on the watch list for next season with its decide-by date.

## Watch list for named seasons

A pool heater sells nothing in February and that is not dead stock, it is February. Only when the user names the season (never inferred from a quiet month or from what the item sounds like), a zero-sales item goes on a dated watch list instead of the slow-mover list: item, the season start date as the user gave it, and the decide-by date = season start - lead time. Without a date, "seasonal, check later" is how the first hot week gets missed. When the decide-by date arrives with still no sales history, ask the user for an expected rate rather than sizing from a season that hasn't started.

```
Pool heater, 400k BTU   SKU PHT-400   (made-up example)
  Velocity   0/day (28d); the user says the season starts around May 15
  On hand    4 units
  Decide by  April 10 (35-day lead time before the season start)
  Status     WATCH, not a slow mover
```
