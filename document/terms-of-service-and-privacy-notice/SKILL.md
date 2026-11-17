---
name: Terms of Service and Privacy Notice Drafter
description: >
  Drafts terms of service plus a matching privacy notice for your app, website or SaaS, with a chapter for each feature you offer.
  Use it for "write terms of service for our app", "draft the user agreement", "I need a ToS and privacy policy", "terms for a store that sells digital downloads".
---

# Terms of Service and Privacy Notice Drafter

A good result is a complete reference draft of the terms and a privacy notice, built from the product's own features: every feature the user has gets its own chapter, and no chapter exists for a feature they lack. The drafts are not legal advice.

## Step 1: Work out the product

From the user's message, list the product's form (app, website, SaaS, mini-program, open-source tool) and its feature modules. Look for: accounts, user-generated content (UGC), community interaction, payments, subscriptions or auto-renewal, virtual goods or digital downloads, third-party login, third-party services, an API, users who are minors, business customers.

Do not ask questions. Where something is missing (operating entity, user base, refund rules, regions), use a bracketed placeholder or write one stated assumption, and carry on to the full draft. Never invent a company name, address, price, refund window, cap amount, court or law: use `[Operating Entity]`, `[Contact Email]`, `[Effective Date]`, `[Refund Window]`, `[Liability Cap Amount]`, `[Governing Law]`, `[Competent Court]`.

## Step 2: Write the terms

Start with the level-1 heading `# <Product Name> Terms of Service` (use `[Product Name]` if not given), then directly under it this exact italic line:

*This is a reference draft, not legal advice. Have a licensed lawyer review it before signing.*

Chapters are numbered with Roman numerals (I, II, III), clauses "Article 1", "Article 2" and so on, running on through the document. Each chapter opens with one sentence saying what it covers.

Fixed chapters, in this order:
1. Acceptance and Updates
2. Definitions
3. Account Registration and Security
4. The Service and Changes to It
5. User Conduct
6. Intellectual Property
7. Disclaimers and Limitation of Liability
8. Termination
9. Governing Law and Dispute Resolution
10. Contact

Insert one dedicated chapter per feature module the user has, after "The Service and Changes to It" and before "User Conduct", with the feature name in the title (for example "Payments and Auto-Renewal"). Renumber so the numerals run in order. Each covers only that feature:
- **User-generated content**: licence the user grants, who owns it, moderation, removal, appeals.
- **Payments**: price display, payment, taxes, invoices, refunds (`[Refund Window]`), failed payments.
- **Subscriptions and auto-renewal**: renewal term, a reminder sent before each charge (with `[Reminder Days]` as the lead time), the exact cancellation path, what happens at cancellation.
- **Virtual goods or digital downloads**: licence scope (not a sale of ownership), delivery, no resale, refund limits.
- **Third-party login and services**: the boundary of responsibility; the product does not control their terms.
- **API**: keys, rate limits, permitted use, revocation.
- **Minors**: age threshold `[Minimum Age]`, guardian consent, spending limits, what the product does if it learns a user is under age.
- **Business customers**: authority to bind the company, admin responsibilities, data ownership.

Writing rules:
- Write each rule as "the user may / may not + specific behaviour + consequence". Never use open-ended wording like "any measures it deems necessary".
- Keep user obligations and platform rights in separate clauses, never mixed in one.
- Updates clause: state how users are notified (for example email or in-product notice), and a waiting period (`[Notice Period]`) before changes take effect. "Continued use means acceptance" alone is not enough.
- Limitation of liability: state both the situations excluded and the cap, and put the cap placeholder in bold: **[Liability Cap Amount]**.
- Do not cite statute numbers or named laws; where law matters write "under applicable law".
- Do not write clauses for features the user did not mention. If the product has no payments, there is no payment chapter and no refund text anywhere.
- Do not copy sections from another company's terms.

## Step 3: Write the privacy notice

Under the heading `# <Product Name> Privacy Notice`, repeat the italic not-legal-advice line directly below it. Sections: Information We Collect, Why We Use It, Who We Share It With, Storage and Retention, Your Rights, Minors, Changes to This Notice, Contact.

Under "Information We Collect", list each category of data against the feature that triggers it (for example accounts: email and password; payments: billing details handled by the payment provider; UGC: posts and uploads). Collect nothing for features the product lacks. Use placeholders for retention periods (`[Retention Period]`) and the data contact (`[Contact Email]`). Include the Minors section only if the product has minors or the user base is unclear (then say it is an assumption).

## Step 4: Reply

The reply itself holds the full deliverable: the terms, then the privacy notice, then a closing block. Do not say it is prepared without including it. Build a Word file only if the user asks for one or for a document file; then load the built-in `docx` skill with `skill_view`, follow it, and publish the file with `publish_artifact` (`kind: "document"`), still giving the draft in the reply.

Closing block, after the privacy notice:
- **Features found** and the chapter matched to each.
- **Assumptions I made**, one line each.
- **Facts to confirm** before launch: the placeholders you left (refund window, liability cap, moderation turnaround, governing law and so on), two or three most important first.
- One plain line: this is a reference draft, not legal advice, and a licensed lawyer should review it before launch, especially for the user's regions and for any minors.

## Hard rules

- The italic not-legal-advice line sits directly under each document title.
- No invented facts: no company details, prices, windows, amounts, law names or jurisdictions the user did not give. Use placeholders.
- Only chapters for features that exist.
- Finish in one reply.
