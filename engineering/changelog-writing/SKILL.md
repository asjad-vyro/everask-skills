---
name: Changelog and Release Notes Writer
description: >
  Turns a pasted git log, list of merged PRs or tickets into finished release notes: a CHANGELOG.md entry, a release body, or a what's-new note, with breaking changes up front.
  Use it for "write the changelog for v2.4", "turn these commits into release notes", "what do I put in the GitHub release?", "draft the app store what's new", "our changelog reads like a git log".
---

# Changelog and Release Notes Writer

A good result lets a developer scan the notes in fifteen seconds and know whether the release costs them work. The agent adds the editorial layer a generator cannot: what to keep, what it means for the reader, and what breaks. It does not bump versions, tag, or publish.

Work only from what the user pasted or attached (a log, PR list, ticket list, diff, or a description). Do not ask questions first. Decide, state your assumptions in one line, and deliver the whole result in this reply. If the user says the material is in a GitHub repo and GitHub is connected, you may read it from there; otherwise never reach for it.

## Step 1: Fix the brief from the message

Decide these without asking, and state each assumption in one short line at the top of the reply:

- **Surface**: `CHANGELOG.md` entry, git-host release body, hosted changelog page, in-product or email "what's new", app-store text. Default when unstated: a `CHANGELOG.md` entry plus a release body.
- **Audience**: integrators upgrading a dependency (libraries, SDKs, APIs) or end users (apps). Infer from the material.
- **Format**: use the project's existing format if the user shows one. Otherwise Keep a Changelog for apps, Common Changelog for libraries. Read `references/format-specifications.md` when picking or mapping between formats.
- **Version and date**: use what the user gave. If none, use a placeholder such as `[Unreleased]` or `vX.Y.Z` and list it under open items. Never invent a version number or date.

## Step 2: Reduce to the net diff

1. List every input line with an id (PR number, hash, or its position).
2. Collapse fixups, follow-ups and reverts into the surviving outcome. An add, a revert and a re-add of the same thing is one entry or none. A change that was reverted inside the range and not re-applied has no entry.
3. If subjects are junk ("wip", "fix tests"), work from PR titles and bodies. If you cannot tell whether something is user-visible, make the more cautious choice, mark it "unconfirmed" and list it under open items.

## Step 3: Select

Keep what a consumer can observe: new features, changed defaults, error message text, timeouts and limits, runtime or platform version floors, deprecations, removals, security fixes, measured performance changes, and refactors with a behavioural side effect.

Drop what they cannot: dev-only dependency bumps, lint or formatter config, CI changes, test-only changes, internal renames, docs formatting. Decide from what the change does, not from its directory or file name. A runtime version bump or "support Python 3.13" is not tooling noise.

Every dropped change goes on the exclusion list with a reason. Never drop silently.

If the range is too big to write up in full, rank by consumer impact, set an explicit cut line, and say what fell below it.

## Step 4: Tier the release

Tier by reader impact, never by effort. Tier 1: new product (a launch, outside this job). Tier 2: noticeable impact on most users or requires user action: changelog, release body, hosted page, email, in-product note. Tier 3: noticeable for some, no action: changelog, release body, hosted page. Tier 4: little noticeable impact: changelog and release body. Any release that requires user action is at least tier 2, so recommend telling users beyond the repository. State the tier in one line. Write only the surfaces the user asked for, and say what else the tier earns.

## Step 5: Write each entry

- Say what changed, then why a reader cares, in one to three sentences. Lead with the observable effect; mechanism after it or not at all.
- Put internal vocabulary into product terms: no ticket ids in the text, no service codenames, no module names outsiders never see.
- Stay flat and specific. No "revolutionary", "blazing", "completely rebuilt". Developers stop reading at adjectives.
- Within a category, breaking items first, then by impact.
- Tense: imperative present ("Add `stream()`") for Common Changelog; past tense ("Added streaming") otherwise. Never mix within a release.
- Link each entry to its PR or commit when the user gave the links or ids. Do not invent URLs: use the ids as given (`#405`) if the repo URL is unknown.
- **No unsourced numbers.** A quantitative claim ("40% faster") appears only if a measurement is in the material. Otherwise write it qualitatively or leave it out, and add an open item.
- Do not claim more than the diff or PR text shows. Add no extra promises or outcomes ('works first time', 'no more crashes') beyond what the user stated, and no filler such as thank-you lines in notes. PR titles overstate; if the title and body disagree, write what the body shows.

## Step 6: Breaking changes and deprecations

Every breaking entry has three parts, in the entry itself:

1. **What breaks**: the observable behaviour, not the internal cause.
2. **Who it hits**: the affected subset. "Everyone" is rarely true.
3. **What to do**: one line of action, plus a link if the user gave a migration doc. If no migration link exists, say so in open items.

Shape (illustrative only; the names in it are made up):
`**Breaking:** \`client.send()\` now rejects payloads over 1 MB instead of truncating them. Affects callers that relied on silent truncation: send smaller payloads.`

Name an exception class, flag, function signature or config key in an entry only if it appears in the user's material. If the material does not say what the new error is, write "rejects ... with an error" and put the exact error name under open items. The action line must be something the material supports; if it does not say how to migrate, give the generic action (for example "send smaller payloads") and flag it as unconfirmed.

Breaking entries go first in the file, and in the release body get their own `### Breaking` section at the top. Version honesty: major means breaking, minor additive, patch fixes. If the entry set contradicts the version the user gave (a removal in a minor, a breaking change in a patch), say so plainly in open items instead of quietly shipping it. Do not choose the version number for the user, but you may say which bump the contents imply.

A deprecation names the replacement and the earliest removal version if the material gives it; otherwise leave the removal version as an open item. A removal entry points back to the earlier deprecation.

## Step 7: Assemble per surface

Read `references/surface-templates.md` for the shape of `CHANGELOG.md`, release body, hosted page and in-product or email notes, and for the derive order (write the changelog first, derive the others). Read `references/non-git-surfaces.md` before writing app-store text (character caps, review rules, localization), enterprise advisories, hosted API changelogs or browser-extension notes. Read `references/worked-examples.md` when the history is messy or the release is breaking and you want a model.

Store caps: count characters with `execute_code` and report the count. Do not eyeball it. Apple's limit is reported by third parties, not verified: say so.

For consumer-facing text (what's new, email) write three to five benefit-led items with no version numbers, and a link line back to the full notes.

## Step 8: Verification gate

Before the reply, check each of the four points against the input, and fix before sending:

1. **Traceability**: every entry maps to at least one id in the input and the claim is supported by it.
2. **Coverage**: every input line is either in an entry or on the exclusion list.
3. **No unsourced numbers, versions, dates, names, URLs or CVE ids.**
4. **Breaking completeness**: all three parts present on every breaking entry.

If there are many input lines, count them in `execute_code` and confirm entries plus exclusions account for all of them.

## Output shape

Deliver all of this in the reply, in this order:

1. **Assumptions**: one to three lines (surface, audience, format, tier).
2. **The notes**: one fenced Markdown block per requested surface, ready to paste.
3. **Traceability**: table, one row per entry, with the id(s) it maps to.
4. **Excluded**: table of every change left out, with the reason.
5. **Open items for a human**: unmeasured performance claims, missing migration link, a security entry needing a CVE or advisory id, unconfirmed visibility, a version or date placeholder, anything you could not verify.

Add, once, only if the user's setup suggests it: recommend writing each entry as a small note file in the same PR as the code, so entries are not reconstructed from memory at release time.

## Hard rules

- Finish in one reply. Never end with a promise or a question; put doubts under open items.
- Facts only from the material the user gave. Do not invent versions, dates, PR numbers, authors, benchmarks, URLs or quotes. Mark every assumption.
- Never rewrite old releases when switching format: start the new format at the next release.
- Do not write the full upgrade guide with code and codemods. Write the notes and link to the guide, or list its absence as an open item.
- Notes are drafts for the user to publish. Do not push, tag, or publish anything.
