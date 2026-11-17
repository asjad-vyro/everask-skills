# Component templates for OpenAPI 3.1

Adapt names and fields to the user's API. Values in angle brackets are placeholders to replace.

## Skeleton

```yaml
openapi: 3.1.0
info:
  title: <API title>
  version: <version>
  description: <one line>
servers:
  - url: <base URL, mark as assumption if not given>
    description: Production
tags:
  - name: <Resource>
    description: <what it covers>
security:
  - bearerAuth: []
paths:
  /<resources>:
    get:
      operationId: list<Resources>
      summary: <List ...>
      tags: [<Resource>]
      parameters:
        - $ref: "#/components/parameters/PageParam"
        - $ref: "#/components/parameters/LimitParam"
      responses:
        "200":
          description: <Successful response>
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/<Resource>ListResponse"
        "400":
          $ref: "#/components/responses/BadRequest"
        "401":
          $ref: "#/components/responses/Unauthorized"
    post:
      operationId: create<Resource>
      summary: <Create ...>
      tags: [<Resource>]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Create<Resource>Request"
      responses:
        "201":
          description: Created
          headers:
            Location:
              description: URL of the new resource
              schema:
                type: string
                format: uri
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/<Resource>"
        "400":
          $ref: "#/components/responses/BadRequest"
        "401":
          $ref: "#/components/responses/Unauthorized"
        "409":
          $ref: "#/components/responses/Conflict"
  /<resources>/{<resource>Id}:
    parameters:
      - $ref: "#/components/parameters/<Resource>IdParam"
    get:
      operationId: get<Resource>
      summary: <Get ... by ID>
      tags: [<Resource>]
      responses:
        "200":
          description: <Successful response>
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/<Resource>"
        "401":
          $ref: "#/components/responses/Unauthorized"
        "404":
          $ref: "#/components/responses/NotFound"
    delete:
      operationId: delete<Resource>
      summary: <Delete ...>
      tags: [<Resource>]
      responses:
        "204":
          description: Deleted
        "401":
          $ref: "#/components/responses/Unauthorized"
        "404":
          $ref: "#/components/responses/NotFound"
```

## Resource schema pattern

```yaml
components:
  schemas:
    <Resource>:
      type: object
      required: [id, <fields the user said are always present>]
      properties:
        id:
          type: string
          format: uuid          # only if IDs are UUIDs; otherwise plain string or integer
          readOnly: true
        <field>:
          type: string
          description: <what it is>
        <optionalNullableField>:
          type: [string, "null"]
        <enumField>:
          type: string
          enum: [<value1>, <value2>]
        createdAt:
          type: string
          format: date-time
          readOnly: true
    Create<Resource>Request:
      type: object
      required: [<fields the client must send>]
      properties: {}            # copy writable fields, leave out id and timestamps
    Update<Resource>Request:
      type: object
      minProperties: 1
      properties: {}            # same fields, none required (PATCH)
    <Resource>ListResponse:
      type: object
      required: [data, pagination]
      properties:
        data:
          type: array
          items:
            $ref: "#/components/schemas/<Resource>"
        pagination:
          $ref: "#/components/schemas/Pagination"
    Pagination:
      type: object
      required: [page, limit, total]
      properties:
        page: { type: integer, minimum: 1 }
        limit: { type: integer, minimum: 1 }
        total: { type: integer, minimum: 0 }
    Error:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
          description: Machine-readable error code
        message:
          type: string
          description: Human-readable message
        details:
          type: array
          items:
            type: object
            properties:
              field: { type: string }
              message: { type: string }
        requestId:
          type: string
```

If the user's API uses cursor pagination, replace `page` with `cursor` and `nextCursor`. If it already has an error format, use theirs instead of `Error`.

## Parameters, responses, security

```yaml
  parameters:
    PageParam:
      name: page
      in: query
      schema: { type: integer, minimum: 1, default: 1 }
    LimitParam:
      name: limit
      in: query
      schema: { type: integer, minimum: 1, maximum: 100, default: 20 }
    <Resource>IdParam:
      name: <resource>Id
      in: path
      required: true
      schema: { type: string }
  responses:
    BadRequest:
      description: Invalid request
      content:
        application/json:
          schema: { $ref: "#/components/schemas/Error" }
    Unauthorized:
      description: Missing or invalid credentials
      content:
        application/json:
          schema: { $ref: "#/components/schemas/Error" }
    Forbidden:
      description: Not allowed to perform this action
      content:
        application/json:
          schema: { $ref: "#/components/schemas/Error" }
    NotFound:
      description: Resource not found
      content:
        application/json:
          schema: { $ref: "#/components/schemas/Error" }
    Conflict:
      description: Conflicts with existing data
      content:
        application/json:
          schema: { $ref: "#/components/schemas/Error" }
    RateLimited:
      description: Too many requests
      headers:
        Retry-After:
          description: Seconds until the limit resets
          schema: { type: integer }
      content:
        application/json:
          schema: { $ref: "#/components/schemas/Error" }
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    apiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
    # OAuth2 only if the user asks:
    # oauth2:
    #   type: oauth2
    #   flows:
    #     authorizationCode:
    #       authorizationUrl: <url>
    #       tokenUrl: <url>
    #       scopes: { "<scope>": "<description>" }
```

Public endpoints (login, health): add `security: []` on the operation.

## Reading code instead of a description

- FastAPI / Pydantic: model fields become schema properties; `Optional[X]` becomes `type: [X, "null"]` and not required; `Field(ge=, le=, min_length=)` become `minimum`, `maximum`, `minLength`; `status_code=` is the success code; `responses={...}` lists extra codes.
- Flask / Express / Spring: take method and path from the route decorator or call, `<int:id>` or `:id` as a path parameter, request body fields from the validation or parsing code, status codes from `return ..., 201` or `res.status(...)`. Where types are not visible, use `type: string` and say so in Assumptions.
- If the project can export its own spec (FastAPI: `app.openapi()`), mention that as a way to cross-check, but still write the spec from the code shown.

## Optional tooling (not installed in the agent sandbox; mention only if asked)

- Lint: `npx @stoplight/spectral-cli lint openapi.yaml` or `npx @redocly/cli lint openapi.yaml`.
- Preview docs: `npx @redocly/cli preview-docs openapi.yaml`.
- Client SDKs: `npx @openapitools/openapi-generator-cli generate -i openapi.yaml -g <typescript-fetch|python|go> -o ./generated`.
