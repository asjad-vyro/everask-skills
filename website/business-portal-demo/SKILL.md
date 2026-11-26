---
name: Business Portal Demo
description: >
  Turns a list of modules and user roles into a clickable demo of a business portal or admin panel, one HTML file with login, menu, lists, forms and dashboard.
  Use it for "demo of an admin panel", "clickable prototype of a CRM", "ERP demo for a client", "school portal mockup", "clinic management screens".
---

# Business Portal Demo

The user gets one self-contained HTML file, shown live in the chat, that behaves like an internal business app: a login screen with a role picker, a menu built from their modules, role-based menu visibility, a list per module with search and sort, add, edit and delete in a form, a detail view, and a dashboard whose counts come from the data. It is a front-end prototype to show a client or team, not a working system.

**Never invent** a real company, product, person, price, regulation or customer. All data in the demo is clearly fake sample data. Modules, roles and fields the user did not give are your assumptions, and the reply lists them.

**Language.** Build the labels, menu and sample records in the language the user wrote in, unless they ask for another, and keep their module, role and field names exactly as given. Right-to-left languages (Arabic, Hebrew, Persian, Urdu) set `rtl`. The first words of the reply are the result: never "I'll load the skill", "I'll build it" or any other narration of tool use, and no English sentence before a reply in another language.

## Step 1: Read the request

Collect from the message (and any pasted list or attached file):

- **Modules**: the menu entries (Patients, Invoices, Courses...). Keep the user's order.
- **Roles** and what each can see. A role the user says "cannot see X" must have X left out of its `modules`. A role that "can only view" gets `readonly`. With no roles given, use Admin (everything) and one limited user role, and say so as an assumption. When the user names roles but not what they see or may edit, decide a simple rule and list each such rule in the reply under assumptions (for example "Teacher: cannot see Teachers, view only on Students"); never present it as something they asked for.
- **Fields per module**, if given. If not, propose 3 to 5 plain fields that fit each module's name and list them in the reply as assumptions.
- **Language** and any colour or title they asked for.

Do not open with questions. If only a type of business is given with no modules ("a school portal"), propose 4 to 6 common modules and 2 to 3 roles for that kind of business and list them as assumptions. Ask once with `clarify` only if the message gives nothing to build from at all.

At most 8 modules are fully working. For a longer list, build the first 8 in the user's order; the rest become menu items marked "next step", and the reply says so.

## Step 2: Write the config

Read `references/config-format.md`. Write `/tmp/.scratch/business-portal-demo/config.json` (run `mkdir -p /tmp/.scratch/business-portal-demo` first) with `write_file`. For a language other than English, translate every label key into `labels`. Do not write the HTML yourself: one generic engine renders every module from the config, so the screens cannot drift apart.

## Step 3: Build and check

Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox, and the scripts are in its `scripts/` folder. Use the full path in every command below, where it says `SKILL_DIR`. If `skill_view` gives no path, find `build_portal.py` under `~/.computer/skills` with `search_files`.

```
python3 SKILL_DIR/scripts/build_portal.py /tmp/.scratch/business-portal-demo/config.json /tmp/.scratch/business-portal-demo/<meaningful-name>.html
```

The script validates the config, makes the sample data, writes the file, runs `node --check` on the page script and looks for external URLs. Read its JSON:

- `ok` is false, or `syntax_check` says FAILED, or `external_urls` is not empty: fix the config (never the template) and run it again. Do not publish a failing page.
- `error`: the message names the config problem; fix it and run again.
- `untranslated_labels` not empty for a non-English page: add those translations and run again.
- Check `modules_working`, `modules_next_step` and each role's `sees` and `view_only` against what the user asked for, especially every "cannot see" rule.

## Step 4: Publish

Publish the .html with `publish_artifact` with `kind: "html_preview"` and a meaningful filename. The file calls no server, needs no network and loads nothing from a CDN.

## Step 5: Reply

In the user's language, short:

1. **What was built**: the modules that work, the "next step" modules if any, and each role with what it sees and whether it is view only. Include the demo account shown on the login screen for each role (`demo.<role id>`, password `demo`: these are labels, not real accounts).
2. **How to try it**: pick a role on the login screen, open a module, search, click a column title to sort, add or edit a record, delete one, and use "Reset demo data" to start over. Changes are kept in the browser (localStorage) only; if the preview blocks storage they last until the page is reloaded.
3. **Assumptions** you made (modules, fields, roles, options).
4. **What it is not**, in three lines: there is no server, no real login or security (anyone can pick any role), no database and no sync between users. A real build needs: a backend and database for the records, real authentication and permissions checked on the server, and the integrations, validation rules and reports the business needs.

Never claim that anything is secure, compliant or production-ready.

## When the user asks for a change

Typical: "add a Suppliers module", "Reception cannot delete", "rename Staff to Team", "make it Spanish". Edit the same `config.json`, change only what was asked and keep every other module, role, field and label as it was, rebuild the same file name with the script, publish it again, and say in one line what changed. The sample data comes back to its starting state in the rebuilt file; say so if the user had been editing records.

## Self-check before you reply

- The script printed `ok: true`, `syntax_check: passed` and no external URLs.
- Every role rule the user gave is in the config and was checked in the script's `roles` output.
- Sample data is fake and generated; no real company or person is named; the "Demo: sample data" badge is shown (the template adds it).
- The reply lists the assumptions, the "next step" modules (if any) and the three-line "what it is not".
- The file is published as `html_preview`, and the reply is in the user's language and does not start by narrating tool use.
