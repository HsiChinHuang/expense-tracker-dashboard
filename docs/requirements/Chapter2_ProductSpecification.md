# Chapter 2: Product Specification

## 2.1 Problem Statement

Individuals who want to manage personal finances face two common problems:

1. **Spreadsheets are tedious.** They require manual formulas, break easily,
   and provide no visual feedback. Users spend more time maintaining the
   spreadsheet than understanding their spending.

2. **Full accounting software is overwhelming.** It includes features for
   invoicing, tax reporting, payroll, and multi-account reconciliation that
   individual users do not need.

There is a gap for a focused tool that answers three questions:

- How much have I spent this month?
- How much of my budget is left?
- Where is my money going?

Expense Tracker & Budget Dashboard fills this gap. It provides a simple
expense recording flow, a monthly budget, and a visual dashboard that makes
spending patterns immediately clear.

## 2.2 User Stories

### Authentication

| ID | Story | Priority |
|---|---|---|
| AUTH-1 | As a new user, I can register with email, username, and password so that I can start tracking expenses | Must |
| AUTH-2 | As a registered user, I can log in with email and password so that I can access my data | Must |
| AUTH-3 | As a logged-in user, I can view my profile so that I can confirm which account I am using | Must |
| AUTH-4 | As a logged-in user, I can log out so that my session ends | Must |
| AUTH-5 | As a user, I cannot access another user's data so that my finances stay private | Must |

### Expenses

| ID | Story | Priority |
|---|---|---|
| EXP-1 | As a user, I can create an expense with amount, category, date, and optional note | Must |
| EXP-2 | As a user, I can view a paginated list of my expenses | Must |
| EXP-3 | As a user, I can filter my expenses by month and category | Must |
| EXP-4 | As a user, I can update an expense I created | Must |
| EXP-5 | As a user, I can delete an expense I created | Must |
| EXP-6 | As a user, I cannot see, update, or delete another user's expenses | Must |
| EXP-7 | As a user, I receive a clear error when I enter an invalid amount | Must |

### Budgets

| ID | Story | Priority |
|---|---|---|
| BUD-1 | As a user, I can set a monthly total budget | Must |
| BUD-2 | As a user, I can update my budget for a month | Must |
| BUD-3 | As a user, I can delete my budget for a month | Must |
| BUD-4 | As a user, I can view my budget status for any month | Must |
| BUD-5 | As a user, I receive a conflict error when I try to create a duplicate budget for the same month | Must |

### Categories

| ID | Story | Priority |
|---|---|---|
| CAT-1 | As a user, I can see 10 system-preset categories with distinct colors | Must |
| CAT-2 | As a user, I can create a custom category with a name and color | Must |
| CAT-3 | As a user, I can view my custom categories alongside system categories | Must |
| CAT-4 | As a user, I cannot delete or modify system categories | Must |
| CAT-5 | As a user, I cannot create a custom category with a duplicate name | Should |

### Dashboard

| ID | Story | Priority |
|---|---|---|
| DASH-1 | As a user, I can see KPI cards: total spent, budget remaining, usage percentage, transaction count | Must |
| DASH-2 | As a user, I can see a category pie chart for the selected month | Must |
| DASH-3 | As a user, I can see a monthly trend bar chart for the last 6 months | Must |
| DASH-4 | As a user, I can see a cumulative spending line chart with a budget line | Must |
| DASH-5 | As a user, I can see the line chart turn red when spending exceeds budget | Must |
| DASH-6 | As a user, I can see a weekly spending heatmap for the last 12 weeks | Must |
| DASH-7 | As a user, I can see my 10 most recent transactions | Must |
| DASH-8 | As a user, I can see a budget progress bar with color coding | Must |
| DASH-9 | As a user, I can switch months and all charts update together | Must |
| DASH-10 | As a user, I see a friendly empty state when there is no data | Must |

### Audit

| ID | Story | Priority |
|---|---|---|
| AUD-1 | As a system operator, I can trust that every expense create/update/delete is logged | Must |
| AUD-2 | As a system operator, I can trust that every budget create/update/delete is logged | Must |
| AUD-3 | As a user, I cannot access audit logs through the API | Must |

## 2.3 Functional Requirements

### 2.3.1 Authentication

**FR-AUTH-1: Registration**
- Input: email, username, password
- Validation:
  - Email must match standard email format
  - Username must be 3-50 characters, alphanumeric and underscore only
  - Password must be at least 8 characters
- Behavior:
  - Reject if email already exists (409 DUPLICATE_EMAIL)
  - Reject if username already exists (409 DUPLICATE_USERNAME)
  - Hash password with bcrypt
  - Create user with is_active = true
  - Return 201 with user object (no password field)
- Audit: not logged (registration is not a sensitive data operation)

**FR-AUTH-2: Login**
- Input: email, password
- Behavior:
  - Look up user by email
  - Verify password with bcrypt
  - Generate JWT access token with 24-hour expiry
  - Return 200 with access_token, token_type, and user object
  - On failure, return 401 INVALID_CREDENTIALS
  - Do not reveal whether email exists
- Audit: log successful and failed login attempts

**FR-AUTH-3: Current User**
- Input: Bearer token
- Behavior:
  - Validate token signature, expiry, audience, issuer
  - Extract user_id from sub claim
  - Return 200 with user object
  - Return 401 if token invalid, expired, or user inactive

**FR-AUTH-4: Logout**
- Frontend-only: remove token from local storage
- No backend endpoint required

### 2.3.2 Expenses

**FR-EXP-1: Create Expense**
- Input: amount, category_id, date, note (optional)
- Validation:
  - amount: positive, max 2 decimal places, max 9,999,999,999.99
  - category_id: must exist and belong to user or be a system category
  - date: valid ISO date
  - note: max 500 characters
- Behavior:
  - Create expense with user_id from token
  - Write audit log entry (CREATE)
  - Return 201 with created expense
- Errors:
  - 422 INVALID_AMOUNT if amount invalid
  - 404 CATEGORY_NOT_FOUND if category invalid or belongs to another user

**FR-EXP-2: List Expenses**
- Input: year_month (optional), category_id (optional), page (default 1), page_size (default 20, max 100)
- Behavior:
  - Filter by user_id from token
  - Apply year_month filter using date range
  - Apply category_id filter if provided
  - Order by date descending, then created_at descending
  - Return paginated result with items, total, page, page_size
- Errors:
  - 422 if page < 1 or page_size > 100

**FR-EXP-3: Get Expense**
- Input: expense id
- Behavior:
  - Return expense if it belongs to the user
  - Return 404 if not found or belongs to another user

**FR-EXP-4: Update Expense**
- Input: expense id, fields to update
- Behavior:
  - Verify expense belongs to user
  - Apply updates with same validation as create
  - Write audit log entry (UPDATE) with old and new values
  - Return 200 with updated expense
- Errors:
  - 404 if not found or belongs to another user
  - 422 for invalid fields

**FR-EXP-5: Delete Expense**
- Input: expense id
- Behavior:
  - Verify expense belongs to user
  - Delete expense
  - Write audit log entry (DELETE) with old value
  - Return 204
- Errors:
  - 404 if not found or belongs to another user

### 2.3.3 Budgets

**FR-BUD-1: Set Budget**
- Input: year_month, amount
- Validation:
  - year_month: format YYYY-MM
  - amount: positive, max 2 decimal places
- Behavior:
  - Upsert budget for the user and month
  - Write audit log entry (CREATE or UPDATE)
  - Return 200 with budget object

**FR-BUD-2: Get Budget**
- Input: year_month
- Behavior:
  - Return budget if exists
  - Return 200 with budget = 0 if not exists (not 404)

**FR-BUD-3: Delete Budget**
- Input: year_month
- Behavior:
  - Delete budget if exists
  - Write audit log entry (DELETE)
  - Return 204
  - Return 404 if no budget exists

### 2.3.4 Categories

**FR-CAT-1: List Categories**
- Behavior:
  - Return all system categories (user_id IS NULL)
  - Plus all user categories (user_id = current user)
  - Order: system first, then user, then by name

**FR-CAT-2: Create Category**
- Input: name, color
- Validation:
  - name: 1-100 characters, unique within user's categories
  - color: valid HEX color (#RRGGBB)
- Behavior:
  - Create category with user_id = current user
  - is_system = false
  - Return 201

**FR-CAT-3: System Categories**
- Cannot be created, updated, or deleted by users
- Seeded during migration or fallback initialization
- 10 categories with fixed colors

### 2.3.5 Dashboard

**FR-DASH-1: Summary**
- Input: year_month
- Returns: total_spent, budget, remaining, percentage, transaction_count, is_over_budget
- Behavior:
  - Sum all expenses in the month for the user
  - Look up budget for the month
  - Compute remaining and percentage
  - percentage is null if budget is 0

**FR-DASH-2: By Category**
- Input: year_month
- Returns: array of {category_id, name, color, amount, percentage}
- Behavior:
  - Group expenses by category
  - Order by amount descending
  - Return all categories (frontend merges to top 6 + Other)

**FR-DASH-3: Trend**
- Input: months (default 6, max 24)
- Returns: array of {year_month, total}
- Behavior:
  - Aggregate expenses by month for the last N months
  - Include months with zero expenses
  - Handle year boundary correctly

**FR-DASH-4: Cumulative**
- Input: year_month
- Returns: {year_month, budget, days: [{date, daily, cumulative}]}
- Behavior:
  - Generate all days in the month
  - Compute daily total and running cumulative
  - Include days with zero expenses

**FR-DASH-5: Heatmap**
- Input: weeks (default 12, max 52)
- Returns: {max_amount, weeks: [{week_start, days: [{date, amount}]}]}
- Behavior:
  - Generate week matrix starting on Monday
  - Fill missing days with 0
  - Compute max_amount for color scaling

**FR-DASH-6: Recent**
- Input: limit (default 10, max 50)
- Returns: array of expenses ordered by date desc, created_at desc
- Behavior:
  - Only user's expenses

### 2.3.6 Audit Logging

**FR-AUD-1: Write Audit Log**
- Trigger: any expense or budget CREATE, UPDATE, DELETE
- Fields: user_id, action, entity_type, entity_id, old_value, new_value, ip_address
- Behavior:
  - Written in the same transaction as the business operation
  - If audit write fails, the business operation fails

**FR-AUD-2: Audit Log Access**
- No API endpoint exposed
- Only accessible directly via database

### 2.3.7 Health Check

**FR-HEALTH-1: Health Endpoint**
- Input: none
- Returns: {status, database, fallback_active, version}
- Behavior:
  - status = "ok" if database is reachable
  - status = "degraded" if fallback is active
  - database reports "postgresql" or "sqlite"
  - No authentication required

### 2.3.8 Database Fallback

**FR-DB-1: Automatic Fallback**
- Trigger: PostgreSQL connection failure on startup
- Behavior:
  - Wait up to 5 seconds for connection
  - On failure, switch to SQLite
  - Create tables with Base.metadata.create_all()
  - Seed system categories
  - Log WARNING
  - Continue serving requests
- Limitations:
  - Data written during fallback is temporary
  - No automatic switch back to PostgreSQL without restart

## 2.4 Non-Functional Requirements

### 2.4.1 Performance

| Requirement | Target |
|---|---|
| Dashboard load (all 5 charts) | < 2 seconds on warm cache |
| API response time (simple query) | < 200ms |
| API response time (dashboard aggregation) | < 500ms |
| Cold start (Render free tier) | < 60 seconds |
| Frontend initial load | < 3 seconds |

### 2.4.2 Reliability

- SQLite fallback ensures functionality when PostgreSQL is unavailable
- Health check endpoint reports database status
- No data loss on graceful restart when using PostgreSQL
- Audit log written atomically with business operation

### 2.4.3 Security

- Passwords hashed with bcrypt, never stored in plain text
- JWT signed with HS256, algorithm fixed, never accepts alg=none
- JWT validated on signature, expiry, audience, issuer
- All database queries filter by user_id
- Cross-user access returns 404, not 403 (does not reveal existence)
- SECRET_KEY read from environment variable, never committed
- .env file in .gitignore
- Audit log records all write operations
- Known limitation: no rate limiting (documented)

### 2.4.4 Data Integrity

- Amount stored as NUMERIC(12,2), handled as Decimal in Python
- Amount transmitted as string in JSON
- Date stored as DATE, no timezone
- Month attribution based on date field, not timestamp
- Budget unique constraint on (user_id, year_month)
- Foreign keys enforced
- CHECK constraints for amount > 0 and valid action/entity types

### 2.4.5 Usability

- Dashboard loads in under 2 seconds
- Empty states shown when no data
- Loading states shown during fetch
- Error messages are specific and actionable
- Month selector updates all charts simultaneously
- Forms validate before submission
- Confirmation dialogs for destructive actions
- Responsive layout: single column on mobile, two columns on desktop

### 2.4.6 Accessibility

- All form inputs have associated labels
- All buttons have visible text or aria-label
- Modal has role="dialog", aria-modal="true", focus trap, Esc to close
- Charts have title and description or adjacent text
- Color contrast ratio >= 4.5:1
- Keyboard navigation works without traps
- Skip to main content link
- Each route has a unique page title
- html lang="en"

### 2.4.7 Maintainability

- Backend split into routers, services, models, schemas
- Frontend split into api, components, pages, hooks, context, utils
- All API calls centralized in frontend/src/api/
- All business logic in backend/app/services/
- Tests at unit, integration, and E2E levels
- Documentation in docs/
- AGENTS.md provides agent context

### 2.4.8 Portability

- Docker Compose runs the full stack on any platform
- SQLite for local development, PostgreSQL for production
- Environment variables for all configuration
- No hardcoded paths or credentials

### 2.4.9 Observability

- Structured JSON logs
- Key events logged: auth, expense, budget, db fallback
- Health check endpoint
- Audit log in database
- Render logs accessible via dashboard

## 2.5 Edge Cases

### 2.5.1 Authentication Edge Cases

| Case | Expected Behavior |
|---|---|
| Email format invalid | 422 with field=email |
| Password less than 8 characters | 422 with field=password |
| Username less than 3 characters | 422 with field=username |
| Username contains spaces | 422 with field=username |
| Email already registered | 409 DUPLICATE_EMAIL |
| Username already taken | 409 DUPLICATE_USERNAME |
| Wrong password | 401 INVALID_CREDENTIALS |
| Nonexistent email | 401 INVALID_CREDENTIALS (same as wrong password) |
| Token expired | 401 TOKEN_EXPIRED |
| Token signature invalid | 401 TOKEN_INVALID |
| Token algorithm is none | 401, rejected |
| No token on protected endpoint | 401 |
| Disabled user with valid token | 401 |

### 2.5.2 Expense Edge Cases

| Case | Expected Behavior |
|---|---|
| Amount is 0 | 422 INVALID_AMOUNT |
| Amount is negative | 422 INVALID_AMOUNT |
| Amount has 3 decimal places | 422 INVALID_AMOUNT |
| Amount exceeds 9,999,999,999.99 | 422 INVALID_AMOUNT |
| Amount is empty string | 422 INVALID_AMOUNT |
| Category does not exist | 404 CATEGORY_NOT_FOUND |
| Category belongs to another user | 404 CATEGORY_NOT_FOUND |
| Date format invalid | 422 |
| Note exceeds 500 characters | 422 |
| Update another user's expense | 404 |
| Delete another user's expense | 404 |
| page = 0 | 422 |
| page_size = 1000 | 422 |
| Filter by month with no expenses | 200 with empty items |
| Filter by category with no expenses | 200 with empty items |

### 2.5.3 Budget Edge Cases

| Case | Expected Behavior |
|---|---|
| year_month format invalid | 422 INVALID_MONTH |
| Duplicate budget for same month | 409 DUPLICATE_BUDGET |
| Update nonexistent budget | Creates it (upsert) |
| Query month with no budget | 200 with budget = 0 |
| Amount is negative | 422 INVALID_AMOUNT |
| Delete nonexistent budget | 404 |

### 2.5.4 Dashboard Edge Cases

| Case | Expected Behavior |
|---|---|
| Month with no expenses | 200, total = 0, charts show empty state |
| Month with no budget | 200, budget = 0, percentage = null |
| Month with expenses but no budget | 200, is_over_budget = true (since budget = 0) |
| Spending exactly equals budget | is_over_budget = false, percentage = 100 |
| Month boundary (Oct 31 to Nov 1) | No bleed between months |
| Year boundary (Dec to Jan) | Trend chart handles correctly |
| Heatmap spanning year boundary | Week matrix aligns correctly to Monday |
| More than 6 categories | Pie chart merges to top 6 + Other |
| Exactly 6 categories | No Other slice |
| Zero expenses in trend range | All months show 0 |
| Cumulative last point | Equals total spent for the month |
| Recent transactions with fewer than 10 | Returns all available |
| Recent transactions with more than 10 | Returns exactly 10 |

### 2.5.5 Category Edge Cases

| Case | Expected Behavior |
|---|---|
| Custom category name duplicates system category | Allowed (different user_id scope) |
| Custom category name duplicates own category | 409 DUPLICATE_CATEGORY |
| Custom category name exceeds 100 characters | 422 |
| Invalid HEX color | 422 |
| Delete system category | 403 or 404 (not allowed) |
| Update system category | 403 or 404 (not allowed) |

### 2.5.6 Database Edge Cases

| Case | Expected Behavior |
|---|---|
| PostgreSQL unreachable on startup | Fallback to SQLite within 5 seconds |
| PostgreSQL becomes unreachable at runtime | Existing connections fail, return 503 |
| PostgreSQL recovers after fallback | Requires backend restart to reconnect |
| SQLite file not writable | Startup fails with clear log |
| Migration fails | Startup fails with clear log |
| Concurrent budget creation for same month | One succeeds, other gets 409 |

### 2.5.7 Frontend Edge Cases

| Case | Expected Behavior |
|---|---|
| Token expires during session | 401 triggers redirect to login |
| Network error during fetch | Toast shown, retry option |
| Empty dashboard | Friendly empty state per chart |
| Chart data is loading | Skeleton shown |
| Form submitted with invalid data | Field-level error messages |
| User navigates to protected route without login | Redirect to login, then back |
| User switches month rapidly | React Query cancels previous request |
| Browser back button after logout | Redirect to login |
| Long note text | Truncated in list, full in detail |

## 2.6 Success Criteria

### 2.6.1 Functional Success

- A new user can register, log in, record expenses, set a budget,
  and view the dashboard without errors
- All 5 dashboard charts render correctly with data
- Month switching updates all charts simultaneously
- User A cannot see, update, or delete user B's data
- System categories are always available
- Custom categories can be created and used
- Audit log records all write operations

### 2.6.2 Technical Success

- All unit tests pass
- All integration tests pass
- All E2E tests pass
- SQLite fallback works when PostgreSQL is unavailable
- Health check accurately reports database state
- CI pipeline runs on every PR
- CD pipeline deploys on merge to main
- Application is accessible via a public URL

### 2.6.3 Quality Success

- README provides a 5-minute verification path
- All 14 Final Project criteria have evidence
- Security scan artifacts are present
- Agent Extension Pack is functional
- AI workflow is documented with real sessions
- Peer reviewer can reproduce setup in under 10 minutes

### 2.6.4 Measurable Targets

| Metric | Target |
|---|---|
| Backend test count | >= 50 |
| Frontend test count | >= 20 |
| E2E test count | >= 3 |
| API endpoints | >= 15 |
| Dashboard charts | 5 |
| System categories | 10 |
| Security artifacts | 8 |
| Ops artifacts | 5 |
| Agent skills | 3 |
| Agent subagents | 2 |
| MCP tools | 4 |
| Agent hooks | 2 |
| Documentation files | >= 20 |
| README length | < 500 lines |
| Setup time (new developer) | < 10 minutes |
| Cold start time (Render) | < 60 seconds |