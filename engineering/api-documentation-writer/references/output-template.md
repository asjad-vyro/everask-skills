# REST reference: output shape

Fill each `<...>` from the user's input. Where the input is silent, write `not given` or mark `(assumed)`. Never keep a placeholder in the final text.

````markdown
# <API name> Documentation

## Overview
<one or two sentences on what the API does, from the input>

**Base URL**: `<base URL, or not given>`
**Version**: `<version, or not given>`
**Authentication**: <method, or not given>

## Quick Start
1. <get credentials: where, or not given>
2. <make the first call: the simplest endpoint, as a curl command>
3. <what a successful response looks like>

## Authentication
<where the credential goes, with an example header using <YOUR_API_KEY>; token refresh only if the input has one>

## Endpoints

### <METHOD> <path>
<what it does, one sentence>

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `<name>` | path / query / header / body | `<type>` | yes / no | <meaning, default, limits if given> |

**Request**
```bash
curl -X <METHOD> "<base URL><path>" \
  -H "Authorization: Bearer <YOUR_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '<sample body using the real field names>'
```

**Response** (`<status> <reason>`)
```json
<sample body using the real field names, sample values>
```

**Errors**
| Status | Code or meaning | When |
|---|---|---|
| `<status>` | `<code>` | <cause, from the input> |

(repeat for each endpoint)

## Errors
<the standard error body if the input shows one, else a minimal one marked (assumed)>

| Status | Meaning |
|---|---|

## Rate Limits
<limits and headers if given, else: not given. How to handle 429 only if limits apply: wait, then retry with backoff.>

## Code Examples
### JavaScript (Node.js)
### Python
<one call each, for the most useful endpoint>

## Assumptions and gaps
- <what was inferred, what is not given, what to confirm>
````

GraphQL: replace Endpoints with Schema, Queries, Mutations (and Subscriptions if present), each with a variables example and a response.
Webhooks: list each event, its payload, and how to verify the signature, only if the input describes them.
