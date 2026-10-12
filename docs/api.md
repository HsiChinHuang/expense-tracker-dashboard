# API Reference

The HTTP API of the Expense Tracker Dashboard, documented against the
merged backend and the exported contract `openapi.yaml` (16 paths). The
contract that ships is the one described here: the committed
`openapi.yaml` path set equals the merged app's runtime
`app.openapi()["paths"]` set. See also
[architecture.md](architecture.md) and
[testing-guidelines.md](testing-guidelines.md).

## Base URL

All API endpoints share the base URL `/api/v1` (the routers in
`backend/app/routers` mount under this prefix). Two exceptions answer at
the root: `GET /` (a static `{"status": "ok"}` skeleton probe) and the
SPA asset/fallback routes served by `backend/app/main.py` when the built
frontend is present.

Examples in this document use the local development origin
`http://localhost:8000`.

## Authentication

The API uses **bearer** authentication (JWT): the `HTTPBearer` scheme
declared in `openapi.yaml` under `components.securitySchemes`
(`scheme: bearer`, `type: http`). Clients send:

```text
Authorization: Bearer <access_token>
```

- `POST /api/v1/auth/register` creates an account (no token required).
- `POST /api/v1/auth/login` returns `{access_token, token_type, user}`;
  the token is a 24-hour HS256 JWT (issuer and audience are fixed by
  `backend/app/config.py`).
- Every other `/api/v1/*` endpoint requires the bearer token; all
  queries are scoped to the authenticated user, so one user never sees
  another user's rows.
- Missing or invalid credentials answer `401 UNAUTHORIZED`; an expired
  token answers `TOKEN_EXPIRED` and a malformed or forged one
  `TOKEN_INVALID`. Disabled accounts are rejected with `USER_INACTIVE`.

## Common patterns

- **Pagination envelope**: collection endpoints return exactly the four
  keys `{"items": [...], "total": <int>, "page": <int>,
  "page_size": <int>}` (the W6 envelope, defined in
  `backend/app/schemas/expense.py`).
- **Money as strings**: amounts serialize as 2-decimal strings matching
  `^[0-9]+\.[0-9]{2}$` (Decimal in, string out - never a JSON float).
  Dates are plain `YYYY-MM-DD` with no timezone; budget months use
  `YYYY-MM`.
- **Error envelope**: every error renders exactly three keys
  `{"detail": "...", "code": "...", "field": "..."}`; `field` is
  present (possibly `null`) always so clients can read one shape.
- **Ownership without 403**: a resource owned by someone else answers
  404 (or, for budgets, the `0.00` body), never 403 - existence itself
  is private.

## Endpoint reference

The sixteen paths below are the complete contract (identical to
`openapi.yaml`):

| Method(s) | Path | Purpose |
|---|---|---|
| GET | `/` | Static root probe `{"status": "ok"}` |
| POST | `/api/v1/auth/register` | Create an account (201) |
| POST | `/api/v1/auth/login` | Exchange credentials for a bearer token (200) |
| GET | `/api/v1/auth/me` | Current user (five public fields) |
| GET | `/api/v1/categories` | System categories first, then the caller's custom rows |
| POST | `/api/v1/categories` | Create a custom category (201) |
| DELETE | `/api/v1/categories/{category_id}` | Delete an unused custom category (204) |
| GET | `/api/v1/expenses` | Paginated expense list (`items`/`total`/`page`/`page_size`) with `category_id`, `date_from`, `date_to`, `year_month` filters |
| POST | `/api/v1/expenses` | Create an expense (201) |
| PUT | `/api/v1/expenses/{expense_id}` | Update an expense (partial body, at least one key) |
| DELETE | `/api/v1/expenses/{expense_id}` | Delete an expense (204) |
| GET | `/api/v1/budgets/{year_month}` | Budget for one month (absent month answers `"0.00"`, never 404) |
| PUT | `/api/v1/budgets/{year_month}` | Upsert the month budget (always 200, never 201) |
| GET | `/api/v1/dashboard/summary` | Month totals (spend, budget, remaining, percentage) |
| GET | `/api/v1/dashboard/trend` | Six-month spend trend |
| GET | `/api/v1/dashboard/by-category` | Category breakdown for one month |
| GET | `/api/v1/dashboard/heatmap` | Weekday-by-hour activity grid |
| GET | `/api/v1/dashboard/cumulative` | Per-day cumulative spend versus budget |
| GET | `/api/v1/dashboard/recent` | Most recent expense rows |
| GET | `/api/v1/health` | Database health probe (reports the fallback state) |

The dashboard endpoints take a required `year_month` query parameter in
`YYYY-MM` form; a malformed value answers 422.

## Examples

Register, then log in:

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","email":"alice@example.com","password":"S3cure-pass"}'
```

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"login":"alice","password":"S3cure-pass"}'
```

Create an expense with the token:

```bash
curl -s -X POST http://localhost:8000/api/v1/expenses \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"amount":"12.50","category_id":"<uuid>","date":"2026-10-13","note":"lunch"}'
```

A successful expense list answers the W6 envelope:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

## Error codes

Codes are the Appendix B constants defined in
`backend/app/core/errors.py`, rendered inside the three-key envelope:

| Code | Typical status | Meaning |
|---|---|---|
| `VALIDATION_ERROR` | 422 | Request body/params failed structural validation |
| `DUPLICATE_EMAIL` | 409 | Email already registered |
| `DUPLICATE_USERNAME` | 409 | Username already taken |
| `INVALID_CREDENTIALS` | 401 | Wrong login or password |
| `UNAUTHORIZED` | 401 | Missing or unusable bearer token |
| `TOKEN_INVALID` | 401 | Token failed signature/type checks |
| `TOKEN_EXPIRED` | 401 | Token past its `exp` claim |
| `USER_INACTIVE` | 401 | Account is deactivated |
| `DATABASE_UNAVAILABLE` | 503 | Neither primary nor fallback answered |
| `DUPLICATE_CATEGORY` | 409 | Category name already used (field `name`) |
| `CATEGORY_NOT_FOUND` | 404 | Unknown, foreign, or system category id |
| `CATEGORY_IN_USE` | 409 | Category still referenced by expenses (field `category_id`) |
| `INVALID_AMOUNT` | 422 | Amount VALUE cases: zero, negative, 3 decimals, over max, empty (field `amount`) |
