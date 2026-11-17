---
name: Trend, Seasonality and Forecast
description: >
  Turns a sales, traffic or other metric history into a plain-English read of its trend, seasonality and anomalies, plus a forecast with a prediction range.
  Use it for "forecast the next 6 months", "find the seasonality in this data", "flag anomalies in this daily series", "is this month's drop normal?".
---

# Trend, Seasonality and Forecast

A good result tells the user what the series is doing (direction and rate, repeating pattern, odd points), gives a forecast with a range and an honest accuracy check, and says what to trust and what not to. Everything is calculated by the bundled script, never by hand.

## Step 1: Get the data into a CSV

- Attached file (.csv or .xlsx) or pasted numbers: save to `/tmp/.scratch/time-series-forecasting/data.csv` with a date column and one numeric column. For .xlsx, read it with `execute_code` and pandas. If a file has several metrics, use the one the user named; if none named, use the first numeric column and say so.
- If the user gave no data at all and only describes a goal, do not invent a series. Say what to provide (date column, one value column, at least 2 full seasonal cycles, for example 24 months), explain which method you would use, and use `web_search` only if they asked for public data (for example a public traffic or price history), citing the source.
- Never fill in, extend or "clean" the user's numbers except as the script does (it reports gaps and blanks).

## Step 2: Run the script

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the scripts are in its `scripts/` folder. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `ts_forecast.py` under `~/.computer/skills` with `search_files`.

```
python3 SKILL_DIR/scripts/ts_forecast.py --csv /tmp/.scratch/time-series-forecasting/data.csv --date-col <date column> --value-col <value column> --horizon <periods ahead> --out-dir /tmp/.scratch/time-series-forecasting/out
```

- Horizon: the user's, else 6 for monthly, 12 for weekly, 14 for daily; state which you used.
- Optional: `--freq D|W|M|Q` if the gaps are irregular, `--season N` to override the season length (default 7 daily, 52 weekly, 12 monthly, 4 quarterly; `0` for none). If the data is hourly, or the date column is a text label the script can't parse, aggregate or reformat it with `execute_code` first.
- It prints one JSON report and writes `forecast.csv` and `decomposition.csv` in the out folder. If it exits with a message, fix the cause (usually the date format or fewer than 8 points) and rerun once.
- Read the JSON `notes` field and report every note in the reply (too few cycles, no hold-out test, gaps filled).

## Step 3: Read the numbers

Read `references/forecast-guide.md` once, before writing, for how to word trend, seasonality, anomaly and accuracy findings and what the caveats are.

Use the JSON as follows:
- `trend`: `slope_per_period` and `slope_pct_of_mean_per_period` give the rate; `strength_0_to_1` says how much of the movement the line explains.
- `seasonality`: `index_additive` is how far each position sits above or below trend (in the metric's own units). Name the 2 highest and 2 lowest positions. Seasonality strength above about 0.6 means raw month-to-month changes mislead; below about 0.3 call it weak or absent.
- `anomalies_robust_z_gt_3.5`: points far from what trend and season predict. Show `actual`, `expected` and `gap_pct`. If the user asks "is this month normal?", answer from that point's `gap_pct` and whether it is in the list; if the point is not in the list it is within normal variation.
- `backtest`: error of the method on the last periods held out. Report the MAPE (average % miss) of the method used and of the seasonal-naive comparison. If the MAPE is above roughly 20%, say the forecast is rough.
- `forecast`: the table to show, with `lower_95` and `upper_95` as the range in which about 95% of outcomes should fall if the pattern holds.

Do any further arithmetic (totals over the horizon, year-over-year change, a revenue figure from units) in `execute_code`, and copy the results. Never calculate in your head.

## Step 4: Chart and reply

- Call `render_chart` once with the history plus forecast and its range, using the rows of `decomposition.csv` and `forecast.csv`. If the user also wants the files, publish the two CSVs with `publish_artifact` (`kind: "file"`). Do not build a workbook unless asked.
- The reply itself holds the full result, in this order:
  1. **Headline**: one or two sentences with the trend, the seasonal pattern and the forecast direction.
  2. **Data used**: periods, first and last date, frequency, season length assumed, and any gaps or skipped rows.
  3. **Trend**: direction and rate per period, and the total change over the history.
  4. **Seasonality**: the high and low positions with their size; or "no clear seasonality" and why.
  5. **Anomalies**: a table of period, actual, expected, gap %; or "none beyond normal variation". Give a possible cause only as a question for the user to check (campaign, outage, holiday); never state a cause as fact.
  6. **Forecast**: table of period, forecast, low, high, then the back-test accuracy in one line.
  7. **Assumptions and limits**: that the trend and season continue unchanged, that the range covers statistical noise only, not promotions, price changes or shocks, and the short-history warnings if any.
  8. **What to do with it**: two or three concrete next steps (for example plan capacity for the peak month, investigate the flagged dip).

## Rules

- Use only the user's data and the script's output. No made-up figures, benchmarks or causes; write "not given" or label an assumption.
- If there are fewer than 2 full seasonal cycles, say seasonality could not be estimated and the forecast is a trend line only.
- Never present the range as a guarantee. Round to a sensible number of digits and keep the user's units and currency.
- Finish in one reply. Decide and state assumptions instead of asking questions.
