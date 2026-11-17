---
name: API Documentation Writer
description: >
  Turns routes, code, a JSON payload or a plain description into a finished API reference: endpoints, parameters, example requests and responses, auth, errors, and an OpenAPI spec if wanted.
  Use it for "document these endpoints", "write API docs for this code", "create an OpenAPI spec", "write an auth and error codes page".
---

# API Documentation Writer

A good result is documentation a developer can use without asking anyone: every endpoint has its parameters explained, a copy-paste request, a realistic response and its error cases, and nothing in it contradicts what the user gave.

## Step 1: Read what the user gave

Work only from the message, pasted code or specs, and attached files. Do not ask questions: decide, and list your assumptions at the end. From the input, extract:

- API type (REST unless the input shows GraphQL, WebSocket or gRPC), base URL, version, auth method.
- Every endpoint: method, path, path/query/header parameters, body fields, response shape, status codes. For code (Express, FastAPI, Flask, Rails and so on), read the route handlers, validators and thrown errors to get these.
- Rate limits, pagination and webhooks, only if the input mentions them.

## Step 2: Decide what is known and what is not

Facts come only from the user's input. Where the input is silent, do one of two things:

- Write `not given` (for example the rate limit, the base URL, the token lifetime) and say what the user should fill in.
- Mark a reasonable inference as `(assumed)`, for example a field type inferred from a name.

Never invent limits, URLs, SDK names, error codes, status codes or support contacts. Example values in requests and responses are fine when they are plainly sample data (`"name": "Example item"`, `<YOUR_API_KEY>`), and an example response must use exactly the field names the input defines. If the user asked you to design a small API from a description, the design is yours to make: say so, and list the choices under assumptions.

## Step 3: Write the reference

Read `references/output-template.md` for the exact shape and follow it. Order endpoints by how commonly they are used (or as the user listed them). For each endpoint include:

1. Method and path, and one sentence on what it does.
2. A parameters table: name, where (path, query, header, body), type, required or optional, description, default if given.
3. A request example in curl, and in JavaScript and Python when the user wants multi-language samples or there are three or fewer endpoints. Do not repeat all three languages for every endpoint of a large API: show curl for each and JavaScript and Python once in a Code Examples section.
4. A success response with a realistic body, and the status code.
5. Error responses that the input supports (validation, not found, auth). Add `401` or `429` only if the auth or limits in the input make them apply.

Then add, in this order: Quick Start (a working first call), Authentication, Errors (the standard error body and a table of codes), Rate Limits (or `not given`), Pagination and Webhooks only when relevant.

## Step 4: OpenAPI, when asked or when the input is a spec

If the user asks for OpenAPI or Swagger, read `references/openapi-notes.md`, then produce a complete OpenAPI 3.1 YAML in one code block: `info`, `servers`, `paths`, `components/schemas`, `components/securitySchemes`. Every path in the reference must appear in the spec with the same parameters and responses. If the user did not ask for OpenAPI, do not produce one: offer it in one closing line.

## Step 5: Check, then deliver

Before replying, check each item and fix what fails:

- Every endpoint in the input is documented, none added.
- Every parameter and body field is explained, and the examples match the tables.
- Each request example is valid (quotes closed, JSON parses, headers present).
- Nothing in the doc is a number, URL or name the user never gave, apart from marked sample values.

## Output

The documentation goes in the reply itself, in full, as Markdown (and the OpenAPI YAML after it when asked). Do not build a file unless the user asks for one. End with a short `## Assumptions and gaps` list: what you inferred, what is `not given`, and what the user should confirm. Say nothing about how you worked.

## Hard rules

- No invented facts (see Step 2).
- Never paste real secrets: use `<YOUR_API_KEY>` style placeholders.
- Keep the user's names for resources and fields exactly as given.
- Do not stop to ask or to wait for approval: deliver the whole result in one reply.
