# Config format for `scripts/build_portal.py`

Write one JSON file. Names, modules, roles and fields come from the user; anything you add yourself is an assumption you will list in the reply.

```json
{
  "title": "<portal name>",
  "key": "<short ascii id, used for the saved-data key>",
  "lang": "<language code of the user's language>",
  "rtl": false,
  "accent": "#2457c5",
  "labels": { "dashboard": "<translation>", "...": "..." },
  "roles": [
    {"id": "<ascii id>", "name": "<role name>", "modules": "*"},
    {"id": "<ascii id>", "name": "<role name>", "modules": ["<module id>", "<module id>"], "readonly": ["<module id>"]}
  ],
  "modules": [
    {"id": "<ascii id>", "name": "<module name>", "singular": "<one record, for sample names>", "seed": 6,
     "fields": [
       {"key": "<ascii key>", "label": "<field label>", "type": "text", "required": true},
       {"key": "<ascii key>", "label": "<label>", "type": "select", "options": ["<option>", "<option>"]}
     ]}
  ]
}
```

## Rules

- `roles[].modules`: `"*"` (all modules) or a list of module ids. A role does not see the other modules at all (no menu item). `readonly`: modules the role can open but not add to, edit or delete (`"*"` for all).
- Give every module and role an ascii `id` (the script makes one from the name, or `m1`, `m2` and so on for a name without Latin letters, when you leave it out). Field `key` likewise.
- Field `type`: `text`, `number`, `date`, `select` (needs `options`), `email`, `phone`, `textarea`, `boolean`. The first field is the record's title: make it the name or number. At most six non-textarea fields show as table columns; all fields appear in the detail view and the form. Aim for 3 to 6 fields per module.
- Fields the user named are used as given. For a module with none, propose 3 to 5 plain fields that fit the module's name and list them as assumptions.
- Select options the user did not give: two to four neutral ones such as a status list, listed as assumptions.
- Seed data is generated: 5 to 8 rows per module (`seed`, clamped), named `<labels.sample> <singular> <n>`, round numbers, `sampleN@example.com`, `555-01NN`. Do not pass your own `rows` unless the user supplied sample records; if you do, they must be clearly fake.
- At most 8 modules are built; the script marks module 9 onward as "next step" menu items. Modules past 8 need only a `name`.
- `lang`, `rtl` and `labels`: for any language other than English translate every key below into the user's language and pass them all in `labels`; the script prints `untranslated_labels` for what is still English. `rtl: true` for Arabic, Hebrew, Persian and Urdu.

Label keys (English defaults): `demo_badge` "Demo: sample data", `demo_note`, `pick_role`, `demo_accounts`, `sign_in`, `sign_out`, `dashboard`, `search`, `add`, `edit`, `delete`, `save`, `cancel`, `back`, `details`, `actions`, `no_rows`, `confirm_delete`, `reset`, `confirm_reset`, `records`, `total_of`, `by`, `next_step`, `next_step_note`, `required`, `role`, `yes`, `no`, `sample`, `menu`, `read_only`.

## What the script prints

JSON with `ok`, `file`, `modules_working`, `modules_next_step`, `roles`, `rows_per_module`, `external_urls` (must be empty), `syntax_check` (`passed`, or `FAILED` with the error, or skipped when node is missing) and, for non-English pages, `untranslated_labels`. `ok` is false when there is an external URL or a failed syntax check; fix the config or report it, never publish a page with `ok` false.
