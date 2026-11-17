---
name: Web Form Designer and Auditor
description: >
  Designs or audits a web form and gives a field-by-field spec: which fields to cut or keep, validation rules, spam defence, accessibility fixes and the submission flow.
  Use it for "audit my contact form", "design a signup form", "which fields should I cut", "stop form spam", "my form completion rate is low".
---

# Web Form Designer and Auditor

A good result is a form spec the user can hand to a developer: a table of every field with a keep/cut/move-later decision and a reason, then validation, spam defence, accessibility and submission fixes ranked by impact. It all goes in the reply, in one pass.

## Step 1: Get the form

Work from what the user gave: a pasted field list, a description, a screenshot or a URL.
- If there is a URL, call `web_extract` once and read the fields from the page (labels, input types, required markers, any CAPTCHA, what the button says). If the page shows no form (it loads by script, or is blocked), say so and work from the user's description.
- If the user only describes a goal ("a signup form for a free trial"), you are designing, not auditing: propose the form from scratch.
- If almost nothing is given, do not stop to ask. Pick the most common case for the form type, state it as an assumption in one line, and go on.

Note the form's purpose, the downstream system (CRM, email, database) and any figures the user gave (completion rate, spam volume). Anything not given is "not given". Never invent a completion rate, spam rate, benchmark or conversion uplift. You may say that fewer fields usually help conversion, but give no percentage.

## Step 2: Decide the fields

Read `references/form-anatomy-checklist.md` before you write the field table and the audit, since it holds the per-field, accessibility and pre-launch checks.

For each field ask four questions: does the user need it to get value, does the business need it for the next step, can it be inferred (email domain, context), can it wait until later (after first contact, on a settings page)? Then give one verdict:
- **Keep (required)**: needed for the next step to happen.
- **Keep (optional)**: useful, harmless to skip.
- **Move later**: ask after first contact or on a second visit.
- **Cut**: nothing depends on it, or it can be inferred.

Defaults by form type: a B2B contact form needs name, email and message; phone, company size and role usually hurt more than they help. A checkout needs name, address, country, postal code and payment; referral source, account creation and marketing opt-in are optional or go after purchase. A trial signup needs email (and password, unless there is magic-link or SSO login). Never cut a field the user says a legal, billing or delivery process needs; keep it and say why.

## Step 3: Field design and validation

For each kept field give: label, input type (`email`, `tel`, `number`, `date`, `url`), `autocomplete` value, `inputmode` if it differs, required or optional, a hint if needed, and the validation rule with its exact error message. Rules:
- Single column, labels above inputs, not placeholders as labels. Mark either required or optional fields, not both.
- Validate on blur and again on submit, never on every keystroke. Error text is specific ("Enter an email with an @, like name@example.com"), sits next to the field, is not shown by colour alone, and the page focuses the first error.
- Phone numbers and postal codes: validate liberally, since formats vary by country.
- Validate on the server too: client checks are UX, server checks are correctness.
- Keep autocomplete on. Marketing opt-ins and terms boxes are unchecked by default.

## Step 4: Spam defence

Layer the defences in this order, cheapest and least visible first, and say which layers this form needs:
1. Honeypot field (hidden; reject silently when filled).
2. Time check (reject submissions made in under 2 to 3 seconds).
3. Rate limit per IP or session.
4. Server-side content filtering (link count, obvious spam words) and, for heavy targets, a review queue instead of direct delivery to an inbox.
5. A modern low-friction CAPTCHA (Turnstile, hCaptcha invisible, reCAPTCHA v3) only if layers 1 to 4 let too much through. Never an image-puzzle CAPTCHA, and never a CAPTCHA as the only defence.

Typical contact form: honeypot, time check, rate limit, and a CAPTCHA only when spam persists. Add logging of rejected submissions so the layers can be tuned. Do not name a vendor price or a catch rate.

## Step 5: Accessibility and submission flow

- Accessibility: every input has an associated label; errors use `aria-invalid` and `aria-describedby`; focus order matches visual order and the focus ring stays visible; contrast at least 4.5:1 for text and 3:1 for UI parts; touch targets at least 44px; works at 200% zoom.
- Submission: disable the button while sending, show a loading state, keep entered data when an error occurs, give a clear success state with a next step (not a dead end), and send a confirmation email for signups, purchases and bookings. Use double opt-in for marketing lists.
- Multi-step forms (only when there are many fields or branches): show progress ("2 of 4"), save state between steps, allow Back without losing data, validate per step.
- Privacy: a privacy notice near the form, HTTPS only, explicit consent where the user's region requires it. This is general good practice, not legal advice.

## Step 6: Write the reply

Use exactly this shape. Replace each `<...>` with real content for this form.

```
## Form spec: <form name>
**Purpose:** <what action the form drives>  **Downstream:** <where submissions go, or "not given">
**Assumptions:** <anything you assumed, or "none">

### Field table
| # | Field | Verdict | Input type / autocomplete | Required? | Validation and error message | Why |
|---|-------|---------|---------------------------|-----------|------------------------------|-----|
(one row per field; current fields first, then any field you add)

**Result:** <current count> fields becomes <new count>. Cut: <list>. Moved later: <list>.

### Top fixes, in order of impact
1. <fix> - <one-line reason>
(three to seven items)

### Spam defence plan
<layers in order, with the settings, such as the time threshold>

### Accessibility and submission
<short list of changes>

### Test before launch
<five to eight checks taken from the checklist, such as filled honeypot, very fast submit, keyboard-only submit>

### What to track
<completion rate, field drop-off, error rate, spam rate; note any figures the user gave or "not given">
```

For a design job from scratch, the field table lists the proposed fields (verdict "Keep (required)" or "Keep (optional)") and the "Result" line says how many fields you propose and which you deliberately left out.

If the user wants a mock-up and not just a spec, offer it in one line at the end; do not build it unless asked. If they ask for working HTML, load the built-in `web-design` skill with `skill_view`.

## Hard rules

- Deliver the full spec in the reply. Never say "I've prepared" without the content.
- No invented numbers: no completion rates, uplift percentages, spam rates or benchmarks. Use only the user's figures, or write "not given".
- Count fields with `execute_code` or by listing them; the "Result" counts must match the table.
- Do not open with questions. Decide, state the assumption, deliver.
- At most one `web_extract` call, and only when the user gave a URL.
