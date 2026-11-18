# Templates

Fill every <placeholder> from real data. If a fact is missing, leave it out; never
make one up.

## Run folder (`close-<YYYY-MM>/`)

| File | Made at | Shape |
|---|---|---|
| `receipts.json` | Step 1 | `[{"id", "merchant", "date", "amount", "currency", "tax", "sender", "file"}]` |
| `txns.json` | Step 2 | `[{"id", "date", "merchant", "amount", "currency", "spender"}]` (QuickBooks id) |
| `rules.txt` | Step 2 | One rule per line: `Uber -> Travel` |
| `history.json` | Step 2, only without rules | `[{"merchant", "category"}]`, last 3 months |
| `match.json` | Step 2 | Output of `match_receipts.py` |
| `payouts.json` | Step 3 | Stripe payouts as returned, each with `"balance_transactions": [...]` |
| `deposits.json` / `.csv` | Step 3 | Mercury credits (API JSON or the CSV export) |
| `recon.json` | Step 3 | Output of `reconcile_payouts.py` |
| `last_month.json` | Step 4 | `{"<expense account>": <total>, ...}` from last month's Profit and Loss |
| `close-pack-<YYYY-MM>.xlsx` | Step 4 | Output of `build_close_pack.py` |
| `memo_inputs.json` | Step 7 | See `allowance_review.py` |

Dates are `YYYY-MM-DD`. Amounts are plain numbers; money out may be negative.

## Receipt reading prompt (for `media_analyze`)

```
This is a purchase receipt or invoice. Return JSON only:
{"merchant": "<business name as printed>", "date": "<YYYY-MM-DD>",
 "amount": <grand total paid, number>, "currency": "<ISO code, from the symbol or
 country>", "tax": <VAT/sales tax total, number, or null>}
Use only what is printed. If a field is not visible or not readable, use null.
If this is not a receipt or invoice, return {"not_a_receipt": true}.
```

Add `"id"` (r-01, r-02 …), `"sender"` (the WhatsApp contact name) and `"file"`
yourself.

## QuickBooks pulls

- Uncategorised: Purchases (expenses, card charges, cheques) dated in the month whose
  line account is "Uncategorized Expense", or with no account.
- History: Purchases from the 3 months before, with their line account as category.
- Last month: the Profit and Loss report for the previous month, expense accounts
  only, account name → total.

## Close pack tabs (built by `build_close_pack.py`)

| Tab | What it shows |
|---|---|
| Summary | Counts, spend with and without receipts, Stripe gross/refunds/fees/paid out, deposits, reconciled payouts, exception decisions and a close status, all formulas |
| Receipts matched | One row per transaction: receipt, difference (formula), confidence, proposed category and its rule |
| Stripe reconciliation | One row per payout: gross, refunds, fees, net (formula), deposit, difference and status (formulas), totals |
| Category totals | This month (SUMIFS over Receipts matched), last month, change, change %, flag |
| Exceptions | Type, reference, date, description, amount, person, detail, Decision (Approve / Fix / Exclude) |

## Exceptions review (the step 4 Stop message)

```
<Month> close pack: <link>
<n> transactions, <n> matched, <n> to check, <n> missing a receipt.
Stripe: <n> payouts, <n> reconciled, <n> to look at.

Please decide each exception (Approve / Fix: <change> / Exclude):
1. <type> · <reference> · <date> · <description> · <amount> · <detail>
2. ...

Proposed category rules (only if you gave none): <rule list>
Reply like "1 approve, 2 fix: Travel, 3 exclude", or fill in the Decision column and
send the file back.
```

## Slack chase (direct message, under 80 words)

```
Hi <first name>, I'm closing the books for <Month> and can't find a receipt for:
- <date> · <merchant> · <amount>
- <date> · <merchant> · <amount>
Could you send a photo of each on WhatsApp to <the number they used for receipts>
by <date, 3 working days from now>? Thanks!
<user's first name>
```

## Slack reminder (once, 3 working days later, under 50 words)

```
Hi <first name>, a quick reminder about the <Month> receipt(s) for <merchant>
<amount> (<date>). A photo on WhatsApp is all I need. Thanks!
```

## CFO summary (Outlook draft, under 200 words)

```
To: <CFO email>
Subject: <Company> · <Month Year> close: <Ready to post / Open items>

Hi <CFO first name>,

The <Month> close is <done / nearly done>. Close pack attached.

- Spend: <total spend> across <n> transactions; <n> with receipts.
- Posted to QuickBooks: <n> entries, <total>. Held back: <n>, <total>.
- Stripe: <n> payouts, <paid out> paid out (gross <gross>, fees <fees>, refunds
  <refunds>); <n> reconciled to Mercury<, <n> still open: one line each>.
- Open exceptions: <n> (<one line each, or "none">).
- Missing receipts: <n> people chased on <date>.
<Only with a memo:> The memo you asked for, <title>, is attached.

<user's name>
```

All numbers from the close pack's Summary tab and the push report; nothing else.

## Memo outline (e.g. travel allowance review, about one page)

1. Purpose: the CFO's question, in one sentence.
2. Current allowances: each one and its amount (from the user or the policy doc).
3. Inflation: the index used, the period, the rate, source and date.
4. Allowances uplifted for inflation: table from `allowance_review.py`.
5. FX: each rate used, its date and source, and converted amounts.
6. This month's actual spend in the related categories (from the close pack).
7. Options for the CFO to decide (keep, uplift, other); no recommendation the data
   does not support.
8. Sources: every URL with the date it was read.
