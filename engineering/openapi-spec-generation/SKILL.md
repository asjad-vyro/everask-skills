---
name: OpenAPI Spec Writer
description: >
  Writes a complete, valid OpenAPI 3.1 YAML spec from an API description, JSON samples or route code, with schemas, auth, pagination and error responses.
  Use it for "write an OpenAPI spec", "convert these routes to OpenAPI", "add bearer auth and error responses to my API spec", "generate swagger docs".
---

# OpenAPI Spec Writer

A good result is one OpenAPI 3.1 YAML document, in the reply in full, that parses, has every `$ref` resolving, and covers each endpoint the user described with request bodies, success responses, error responses, auth and reusable components.

## Step 1: Gather what is given

From the message, pasted code or JSON, list: the resources, each endpoint (method and path), request and response fields, auth style, and any pagination or filtering. If the user gave routes or framework code (FastAPI, Flask, Express, Spring, etc.), read the paths, methods, parameters, types and status codes from the code; do not invent endpoints that are not in it. If the user gave a JSON sample, infer types: string, integer, number, boolean, array, object; use `format: date-time`, `email`, `uuid` or `uri` only when the values clearly are one; mark a field `required` only if the user said so or it is present in every sample given, and say that was your rule.

Never stop to ask. Where something is missing, choose a sensible default (bearer JWT auth, `/v1` in the server URL, `page`/`limit` pagination on list endpoints) and record it under Assumptions.

## Step 2: Build the spec

Read `references/templates.md` once for the component patterns (error schema, pagination, shared parameters and responses, security schemes), then write the spec with this structure:

1. `openapi: 3.1.0`, `info` (title, version, one-line description), `servers` with a placeholder URL that you mark as an assumption if the user gave none (use `https://api.example.com/v1`).
2. `tags` and `paths`. Every operation has a unique camelCase `operationId`, `summary`, a tag, parameters, `requestBody` for POST, PUT and PATCH, and `responses`.
3. Responses per operation: the success code (200, 201 with a `Location` header, or 204 with no body) plus the error codes that apply: 400 on bodies and query parameters, 401 and 403 when secured, 404 on paths with an ID, 409 where uniqueness can clash, 422 if the user's API uses it, 429 if rate limits were mentioned. Errors point to shared `components/responses`.
4. `components`: `schemas` (one per resource, plus `Create...Request` and `Update...Request` variants, an `Error` schema and a `Pagination` schema if lists exist), `parameters`, `responses`, `securitySchemes`. Use `$ref` for anything used twice.
5. A global `security` entry, and `security: []` on any endpoint that is public (login, health).

Rules for 3.1 syntax: nullable is written `type: [string, "null"]`, never `nullable: true`. Use `examples` (not the old `example`) inside schemas. `readOnly: true` on `id` and timestamps. Give `minLength`, `maxLength`, `minimum`, `maximum` and `enum` only where the user's description implies them; otherwise leave them out. Quote status codes (`"200"`).

Put examples only where they come from the user's own data or are plainly labelled placeholders. Do not invent company names, real-looking emails, keys or IDs; use `user@example.com` style placeholders and say they are placeholders.

## Step 3: Check it

Do this before replying. Call `skill_view` on this skill; its result has `skill_dir`, the skill's folder in the sandbox. If `skill_view` gives no path, find `check_openapi.py` under `~/.computer/skills` with `search_files`. Save the spec with `write_file` to `/tmp/.scratch/openapi-spec-generation/openapi.yaml`, then run:

`python3 SKILL_DIR/scripts/check_openapi.py /tmp/.scratch/openapi-spec-generation/openapi.yaml`

(Use the full path in place of `SKILL_DIR`.) It reports `$ref` targets that do not exist, duplicate or missing `operationId`s, operations with no responses, secured operations missing a 401, and unused schemas. Fix every item it lists, re-run once, and use its counts (paths, operations, schemas) in your summary. If the script cannot run, check these by hand. It is a structural check, not a full validator; say so.

Linting with Spectral or Redocly, and SDK generation with openapi-generator, need tools that are not installed here. Mention the commands from `references/templates.md` only if the user asked for validation or SDKs.

## Step 4: Reply

The reply holds, in this order:

1. One or two sentences: what was covered (counts from the check script).
2. The full YAML in one fenced `yaml` block. Never abbreviate with "..." or "same as above". If the API is large, keep each schema compact rather than leaving parts out.
3. `## Assumptions`: a bullet per default you chose (auth, server URL, pagination, required fields, error codes) so the user can correct them.
4. `## Next steps`: at most three bullets, such as pasting it into an OpenAPI viewer, or the two decisions you would confirm.

Also publish the YAML with `publish_artifact` (`kind: "file"`, name like `openapi.yaml`) when the spec is longer than about 300 lines, but the full text still goes in the reply.

## Hard rules

- Only endpoints, fields and behaviour the user gave or the pasted code shows. Anything you add is labelled in Assumptions.
- No `nullable: true`, no OpenAPI 2.0 (`swagger: "2.0"`, `definitions`, `securityDefinitions`) syntax.
- Every `$ref` must resolve. Every secured endpoint documents 401.
- Consistent naming: one casing style for properties (match the user's), plural nouns for collections, no verbs in paths unless the user's API already has them.
- Never put real secrets in examples. No invented URLs presented as the user's.
- This is a draft contract for the user to review, not a statement of how their API actually behaves.
