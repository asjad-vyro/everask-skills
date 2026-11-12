---
name: Reorder Planner
description: >
  Turns sales and stock numbers into a buy list: what to reorder now, how many, and a draft PO for each supplier.
  Also shows what will run out before a delivery can land and how much cash sits in stock that isn't moving.
  Use it for "what should I reorder", "am I going to run out of anything", "how much should I order", "what's not moving", "how much cash is tied up in stock", "draft a PO for my supplier", or when the user shares a sales export and a stock count.
---

# Reorder Planner

Buy what sells, before it runs out, and stop buying what doesn't. A good result is a buy list the user can approve in a minute: per item, whether to order, how many, by when and at what cost, with the working behind every line; the items that will run out before a delivery can arrive; the cash in stock that isn't moving; and a draft purchase order per supplier. Every figure comes from the user's data or is labelled as an assumption.

## Step 1: Get the numbers

Work from what the user gave: attached files, pasted tables, or figures typed in the message. If the user asks you to pull sales or stock from Shopify, Square, QuickBooks, Google Sheets, Excel or Airtable and it is connected, read `references/connected_sources.md` and use it. If it isn't connected, don't ask the user to connect it: work from what they gave you and say which export would help.

Per item you need: SKU or name, units sold by date (daily, weekly, or one row per order), stock on hand, unit cost. Use when present: supplier, lead time in days, units already on order, pack size, minimum order, unit price, date of the stock count.

1. Map whatever column names the files use ("Qty" is units sold) and state the mapping in one line of the reply.
2. Measure every window back from the last date in the sales data, not from today. A day with no row is a day with zero sales. If weekly figures don't say which end is newest, assume oldest first and say so.
3. Stock count date: use the one the user gave. If none, assume the count matches the last sales date and say so. If the count is older than the last sales date, subtract the units sold since (not below zero) and say so.
4. Fill gaps without asking, and say what you assumed: no lead time means 14 days, marked "lead time assumed"; no units on order means none, "assumes nothing is inbound"; no unit cost means units only for that item; no supplier means "Supplier not given"; no pack size means whole units.
5. Run these checks in code and report the findings in two lines, naming the SKUs; say "none" only for a check that found nothing: negative stock; items with sales but no stock row, or stock but no sales; duplicate SKUs with different names; history under 28 days; zero-sales stretches that line up with zero stock.
6. A reorder point or low-stock level already in the data is context, not truth: it is often stale. Where it differs from yours, say so.

Do the arithmetic in code (`execute_code`, Python), not in your head, and print the table you will report. If sales or stock is missing entirely, ask once with `clarify` for it. If the user can't supply it, report only what the data supports (rates from sales, or stock value), with no dates or quantities, and name the columns needed (sales: SKU, date, units sold; stock: SKU, on hand, unit cost, lead time). Never invent data.

## Step 2: Work out how fast each item sells

For each item, as of the last sales date:

- `rate_7` = units sold in the last 7 days / 7
- `rate_28` = units sold in the last 28 days / 28 (weekly figures: divide each week by 7)

- Days with no stock are not days of zero demand. If the data or the user shows an item was out of stock for some days, divide by the days it was in stock only.
- If `rate_7` is more than 1.5 times `rate_28`, or under half of it, read `references/sizing_rules.md` before going further: one big order can make a slow item look like a bestseller for a week.
- An item with fewer than 28 days of history has no reliable rate. List it under "not enough history" by name with its units sold, days of history and the rate so far, marked unreliable. No days of cover, no stockout date, no quantity, no trial-order advice. If the user gives their own expected rate, use it and label it "user's estimate".

## Step 3: Days of cover, reorder point, status

For every item that sold something in the last 28 days:

```
stockout_rate = the higher of rate_7 and rate_28
position      = on_hand + on_order
days_of_cover = position / stockout_rate
buffer_days   = the user's safety stock if given, else min(30, max(7, lead_time / 2))
reorder_point = stockout_rate * (lead_time + buffer_days), rounded up
```

The higher rate is deliberate: being early costs a little, being late loses the sale. Take the first status that matches:

| Test | Status | What to say |
|---|---|---|
| days_of_cover < lead_time | Too late | Runs out in X days, a new order takes Y: about Y-X days without stock. Ordering now shortens the gap, it doesn't close it. |
| days_of_cover < lead_time + buffer_days (position at or below the reorder point) | Order now | X days of cover, Y-day lead time: this is the week. |
| days_of_cover < 45 | Order soon | Fine for now: give the order-by date. |
| days_of_cover <= 120 | Fine | No action. |
| days_of_cover > 120 | Overstock | Never a reorder: Step 5. |

Order-by date = last sales date + (days_of_cover - lead_time - buffer_days) days. Units on order count in the position: assume they land before stock runs out, and say so.

## Step 4: Size the order

For Too late and Order now items, and for Order soon items (listed, but kept out of the headline total):

```
sizing_rate = rate_28 (without any one-off order)
target      = (60 + lead_time) * sizing_rate
order_qty   = max(0, target - on_hand - on_order)
```

That is 60 days of cover plus the lead time, because the stock has to last from the day it lands until the next order lands. Name both rates on the line: the higher one says when it runs out, the 28-day one says how much to buy. Sizing a 60-day order off a one-week spike is how cash ends up in a pallet. If the user states another target (say 45 days), use theirs and say so.

Then round up to the supplier's pack size, unless that goes over 90 days of cover at the sizing rate: then round down. Say which way you rounded. A supplier minimum applies to the whole supplier order, not each line, and is never met by padding silently (see `references/sizing_rules.md`). Cost every line (quantity x unit cost) and subtotal per supplier: the user is deciding about cash, not units.

## Step 5: Find the cash that isn't moving

- No sales in the last 28 days: slow mover. Cash tied up = on hand x unit cost. Never compute days of cover for it: nothing is selling, so nothing is running out.
- Over 120 days of cover: overstock. Excess units = position - 120 x stockout_rate, rounded down to whole units; cash tied up = excess x unit cost.
- Call it dead stock only if the history covers at least 90 days with no sales; otherwise say "no sales in the N days given". Suggest one action per item: clear it, bundle it with a fast seller, discount it, or stop reordering. Don't invent prices or discounts, and don't guess a season or an age from an item's name.
- Total the cash in this list and put it in the headline: it is often the most useful number.
- An item the user says belongs to a named season goes on a dated watch list instead: see `references/sizing_rules.md`.

## Step 6: Seasonality and known events

With under 400 days of history, don't adjust for season: say how many days you have, that nothing was adjusted, and that the user can give a multiple to resize with. Carry on. If the user gives a multiple, a promotion, a big job, a price rise or a supplier shutdown, apply it to the items it concerns and label those lines "per your estimate, not from history". Read `references/sizing_rules.md` when the user mentions any of these or a season or its end date, or the history is 400 days or more.

## Step 7: Write the reply

Put the full result in the reply, in this order:

1. **Headline**, two lines: the total to order now (Too late plus Order now) with the number of items and suppliers; how many items will run out before an order can arrive; the cash in slow stock; the Order soon total, separately.
2. **Buy list**: Item | Status | Order by | Order qty | Cost, sorted Too late, Order now, Order soon, Fine, Overstock. Add one plain sentence under it for each Too late item.
3. **Numbers behind it**: Item | On hand (+ on order) | Sales per day, 7d / 28d | Days of cover | Lead time + buffer | Reorder point.
4. **Order maths**, one line per ordered item. Shape, with a made-up item: `WID-500 Widget: (60 + 14) x 9.5/day = 703, minus 40 on hand and 120 on order = 543, rounded up to 550 (11 packs of 50) x 2.10 = 1,155.00`
5. **Slow stock**: Item | Why | Cash tied up | Suggested action, then the total.
6. **Not enough history**: item, days of history, units sold. No dates, no quantities.
7. **Assumptions and data notes**: count date, assumed lead times, nothing inbound, the defaults used, data-check findings.
8. **Draft purchase orders** (Step 8).

Up to about 20 items, list every item. With more, list only Too late, Order now and Order soon in the reply, and the rest in the workbook with counts.

When the user attached a file or there are more than five items, also build one .xlsx workbook: a sheet with every item and every number above, a sheet of slow stock, a sheet of assumptions. Load the built-in `xlsx` skill with `skill_view`, follow it, then publish the file with `publish_artifact` (kind `document`). The reply still holds the full buy list; the workbook is the working copy. If the workbook fails, say so in one line and finish the reply.

Show amounts in the user's currency; if the data names none, use plain numbers with no currency symbol. Close with one line naming what to confirm (assumed lead times, units on order, count date).

## Step 8: Draft the purchase orders

When the data names suppliers and costs, or the user asks for a PO, write one draft PO per supplier for its Too late and Order now lines (Order soon lines only if the user asks). Drafts only: nothing is ordered, emailed or created in any app unless the user says so, and the reply says that. With no supplier or cost and no PO asked for, skip this step in one line.

```
DRAFT PURCHASE ORDER - <supplier>
PO number: (yours to fill in)   Date: <order date>   Requested delivery: <lead time> days after the order date
Ship to / Bill to: <the user fills in>
SKU | Description | Qty | Pack | Unit cost | Line total
Subtotal | Freight and taxes: not included | Total
Unit costs are the last known ones from your file; confirm with the supplier.
```

State each PO total, so they add up to the headline. Under each PO put a short draft email in plain, neutral wording, noting it is not in the user's own voice: what is ordered and where the PO is; when it is needed (for Too late items, ask about faster delivery or a part shipment); a price check if the last known cost may be stale; how to confirm. No apologising, no over-explaining, no invented history with the supplier.

## Rules

- Do not invent a rate, lead time, cost, price, supplier or stockout date. Missing means flagged, or an assumption that is labelled.
- A stock-out period is not zero demand. Never reorder a slow mover or an overstocked item, and never compute days of cover for an item with no sales.
- Always subtract units on order. No seasonal multiplier without 400 days of history or the user's own figure.
- Every quantity shows its working, and every unit figure has its cost beside it.
- Never accept a supplier substitution or part shipment for the user: if they paste a supplier reply, report the change, recompute cover on what is actually coming, and let them decide.
- This is a planning aid built on the numbers provided, not financial advice. The user decides what to buy.
