# OpenAPI 3.1 notes

Produce one YAML document. Keep it valid: consistent two-space indentation, quoted strings that contain `:` or start with a digit or special character, and every `$ref` pointing at a schema you defined.

Skeleton (replace each `<...>` from the input; never leave one in):

```yaml
openapi: 3.1.0
info:
  title: <API name>
  version: <version, or "not given" quoted>
  description: <one sentence>
servers:
  - url: <base URL, or https://api.example.com marked as a placeholder in a comment>
paths:
  /<path>:
    <method>:
      summary: <short>
      operationId: <camelCaseName>
      parameters:
        - name: <name>
          in: <path|query|header>
          required: <true|false>
          schema:
            type: <type>
          description: <meaning>
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/<Name>'
      responses:
        '<status>':
          description: <meaning>
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/<Name>'
        '<error status>':
          $ref: '#/components/responses/<Name>'
components:
  schemas:
    <Name>:
      type: object
      required: [<fields>]
      properties:
        <field>:
          type: <string|integer|number|boolean|array|object>
          description: <meaning>
  responses:
    <Name>:
      description: <meaning>
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
  securitySchemes:
    <schemeName>:
      type: http
      scheme: bearer
security:
  - <schemeName>: []
```

Rules:
- Path parameters are always `required: true`.
- Nullable fields in 3.1 use `type: [string, 'null']`, not `nullable: true`.
- Use `format: date-time`, `format: uuid`, `format: email` only where the input says so or the field name makes it clear.
- API key auth uses `type: apiKey` with `in: header` and `name: <header name>`.
- Put an `example:` on each schema only with sample data, never real data.
