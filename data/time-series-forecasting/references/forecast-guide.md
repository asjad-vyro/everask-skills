# Wording and caveats for time series findings

## Components
- Trend: long-run direction. State it as a rate per period and as total change across the history.
- Seasonality: a pattern that repeats on a fixed calendar (weekday, month, quarter). Say which positions are high or low and by how much.
- Anomaly: a point far from what trend plus season predict. A one-period spike or dip that returns to normal matters less than a lasting level shift. A step change usually points to something that changed on that date (product, pricing, tracking, a data pipeline).
- Residual: what remains; it sets the width of the forecast range.

## Comparing periods
- Year over year removes seasonality: use it when seasonality is strong. Month over month is only fair on seasonally adjusted values.
- If last year contained an anomaly, a year-over-year comparison against it is distorted: say so.

## Method and accuracy
- The script fits a straight-line trend plus a repeating seasonal effect (added to the trend), and compares it with a "same period last cycle" forecast on the most recent held-out periods. It keeps whichever has the lower average miss. Outlier points are set aside while fitting, so one spike does not distort the pattern.
- MAPE is the average percentage miss on the held-out periods. Under about 10% is good, 10 to 20% usable for planning, above 20% rough.
- The range is a 95% prediction range from past errors. It does not cover promotions, price changes, launches, outages or one-off shocks.

## Caveats to state when they apply
- Fewer than 2 full cycles: no seasonality estimate.
- A straight-line trend cannot capture saturation, a growth curve or a recent change of direction. If the last third of the history clearly differs from the first, say the forecast may be off and compare the slopes.
- Zero or negative values: percent errors are unreliable.
- Gaps were filled by straight-line interpolation: list how many.
- Forecasts further out are less reliable than near ones; the range widens with distance.
- Ask the user for the event log (campaigns, releases, incidents) when an anomaly cannot be explained from the data.
