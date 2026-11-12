# Pulling sales and stock from an app

Use this only when the user asked for it and the app is connected. Pull data and nothing else: don't create purchase orders or bills, change stock levels or send messages in the app unless the user asks. If the app isn't connected, don't ask the user to connect it: work from their files or pasted numbers.

## What to pull

- Orders with line items over the look-back window: at least 90 days, 400 days if seasonality matters.
- Stock on hand per item or variant, per location.
- Item records for cost, price and supplier; open purchase orders or inbound stock for units on order.

Then go back to Step 2 of the skill: the numbers from an app are treated exactly like a CSV, including the data checks, and say in the reply where each figure came from.

## What to watch, by app

- **Shopify:** work at the variant level, not the product level: a shirt that sells in medium and never in XL looks healthy as a product. Exclude cancelled and refunded orders. With several locations, total them only if the user sells from one pool; otherwise stock-outs are per location and a total hides them. A bundle sale uses up component stock: if the store sells bundles, say the component rates may be understated.
- **Square:** sales come from transactions, stock from the catalog counts. Inventory tracking is often only partly switched on, so check which items actually have counts before treating a zero as a zero.
- **QuickBooks:** inventory items carry quantity on hand and cost; open purchase orders give units on order. Item costs may be averages, so say the unit costs are as recorded there.
- **Google Sheets, Excel, Airtable:** read the sheet or table the user names and treat it like a CSV: map the columns, say the mapping, and use the stock count date if the sheet has one.

Whatever the source, a stored reorder point is context, not truth. Where it differs from the computed one, say so, and never reorder an item with no sales because a stored reorder point says to.
