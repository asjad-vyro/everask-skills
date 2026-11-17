---
name: Customer Segmentation (RFM and Clusters)
description: >
  Splits a customer list or orders CSV into named segments (best customers, at risk, lapsed, new), sizes each one and says what to do with it.
  Use it for "segment my customers", "RFM analysis", "who are my best customers", "cluster my users", "which segment should I win back".
---

# Customer Segmentation (RFM and Clusters)

A good result is a short report: segments with plain business names, how many customers and how much revenue each holds, what defines each one, and one concrete action per segment. The numbers come from a script run on the user's data, never from memory.

## Step 1: Decide the method and the columns

1. Look at the attached file or pasted data (use `read_file` or `execute_code` to print the header and a few rows). Pasted text: save it to `/tmp/.scratch/customer-segmentation/data.csv` first.
2. Pick the shape:
   - **Orders file** (one row per order): needs a customer id, an order date and an order amount.
   - **Customer table** (one row per customer): needs a customer id plus days since last purchase, number of orders and total spend. If the table has only other columns (plan, sessions, revenue), use `kmeans` on those after building the three fields from the closest columns, and say which you used.
3. Pick the method:
   - **RFM** (default) when the data is purchases. It gives named segments a marketer can act on.
   - **k-means** when the user asks for "clusters", or wants groups found from the data rather than rules.
   - If the user wants segments by an existing field (plan, region, channel), do not cluster: group by that field with `execute_code` and report size, average and index (segment average divided by overall average, times 100).
4. Do not ask the user which method or columns. Choose, and state the choice and any assumption (for example "order_total is treated as revenue, refunds dropped") in the reply.

## Step 2: Run the script

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the script is `scripts/segment.py`. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `segment.py` under `~/.computer/skills` with `search_files`.

Orders file:

```
python SKILL_DIR/scripts/segment.py rfm --csv <file> --customer-col <id column> --date-col <date column> --amount-col <amount column> --out-dir /tmp/.scratch/customer-segmentation/out
```

Customer table: replace the date and amount options with `--recency-col <col> --frequency-col <col> --monetary-col <col>`.

For clusters, use `kmeans` instead of `rfm`; add `--k <number>` only if the user asked for a number of groups. Add `--as-of YYYY-MM-DD` if the user gave a reporting date; otherwise the day after the last order is used.

The script prints the data notes (rows dropped, date range), a segment summary table, and example customer ids per segment, and writes `customers_segmented.csv` and `segment_summary.csv` to the out folder. If it exits with a message about a column, fix the option and rerun. Do the arithmetic you add yourself (shares, differences, uplift) in `execute_code`, never by hand.

## Step 3: Interpret

Read `references/segment-playbook.md` now. It has the RFM segment definitions, an action for each segment, how to name and judge k-means clusters, and the pitfalls to check.

1. RFM: use the segment names the script printed. Check each segment's size is at least about 30 customers; fold smaller ones into the nearest neighbour in the playbook and say so.
2. k-means: name each cluster from its averages (for example "high spend, frequent, recent" is the best customers; "recent, one order, low spend" is new). Quote the silhouette score and say plainly if it is below 0.25 (groups are not clearly separated, so treat them as a rough guide).
3. Find the three things the user will care about most: the segment holding the most revenue, the biggest at-risk revenue (customers who used to buy a lot and have gone quiet), and the largest segment of one-time buyers.
4. Match the action to the user's goal if they gave one (win-back, loyalty, acquisition). If they gave none, give the best-customer, at-risk and new-customer actions.

## Step 4: Reply

Put the whole report in the reply (do not just say a report is ready). Use this shape, and take every number from the script output:

1. **Headline**: two sentences: how many customers and orders were analysed, and the one finding that matters most (for example `<share of revenue>` from `<share of customers>` in the top segment).
2. **Data and method**: three lines at most: method, columns used, rows dropped, as-of date, assumptions.
3. **Segment table**: segment, customers, % of customers, % of revenue, average orders, average spend, average days since last order, spend index (100 = overall average).
4. **One short paragraph per segment** (largest revenue first): who they are in one line, then "Action:" with one concrete step (offer, message or channel) and the segment's example customer ids from the script output.
5. **Priorities**: the top three actions in order, each with the segment and the reason in numbers from the table.
6. **Caveats**: one to three lines (thresholds are relative to this customer base, no costs or margins given, small segments, not a forecast).

Then publish the full customer-level result: `publish_artifact` with `kind: "file"` for `customers_segmented.csv` (the user can load it back into their CRM or email tool). Skip the file if the user only asked a question.

## Hard rules

- Every figure comes from the user's data through the script or `execute_code`. Never invent customers, revenue, conversion rates or expected uplift. Do not promise results for an action; say what to test.
- Without data, do not make up a segmentation of the user's customers. Explain the method, the segments and the columns you need, in the Step 4 shape with placeholders marked as such, and say what to send.
- If more than a quarter of the rows were dropped, or there are fewer than 30 customers, say so at the top of the reply and treat the result as indicative.
- Segment thresholds are relative (quintiles of this customer list), not industry benchmarks. Say so once.
- Personal data stays in the sandbox and the published file; do not send it anywhere or contact the customers.
- Do not mention these steps or file names in the reply beyond the published file.
