# Chapter 7: API Contract (OpenAPI)

## 7.1 Overview

The API contract is defined in `openapi.yaml` at the repository root.
It is the single source of truth for frontend-backend communication.

The backend is implemented against this contract. The frontend mocks
against this contract during initial development. Integration tests
verify the backend matches the contract.

### 7.1.1 OpenAPI Version

| Field | Value |
|---|---|
| OpenAPI version | 3.1.0 |
| API version | 1.0.0 |
| Title | Expense Tracker & Budget Dashboard API |

### 7.1.2 Base URLs

| Environment | URL |
|---|---|
| Local backend (direct) | http://localhost:8000/api/v1 |
| Local full stack (Docker) | http://localhost:8000/api/v1 |
| Production (Render) | https://expense-tracker-dashboard.onrender.com/api/v1 |

### 7.1.3 Content Types

| Direction | Content Type |
|---|---|
| Request body | application/json |
| Response body | application/json |
| Error response | application/json |
| Authentication | Authorization: Bearer <token> |

### 7.1.4 Top-Level Structure

```yaml
openapi: 3.1.0
info:
  title: Expense Tracker & Budget Dashboard API
  version: 1.0.0
  description: |
    API for tracking personal expenses and managing monthly budgets.
servers:
  - url: http://localhost:8000/api/v1
    description: Local development
  - url: https://expense-tracker-dashboard.onrender.com/api/v1
    description: Production
tags:
  - name: health
  - name: auth
  - name: categories
  - name: expenses
  - name: budgets
  - name: dashboard
security:
  - bearerAuth: []
paths:
  # ...
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    # ...
```

### 7.1.5 Authentication Scheme

```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |
        JWT access token. Obtain via POST /auth/login.
        Include as: Authorization: Bearer <token>
```

Global security applies `bearerAuth` to all endpoints. Endpoints that do
not require authentication override this with `security: []`.

| Endpoint | Requires Auth |
|---|---|
| GET /health | No |
| POST /auth/register | No |
| POST /auth/login | No |
| All other endpoints | Yes |

## 7.2 Health Endpoints

### 7.2.1 GET /health

```yaml
/health:
  get:
    tags: [health]
    summary: Health check
    description: |
      Returns application status and database information.
      No authentication required.
    security: []
    operationId: getHealth
    responses:
      "200":
        description: Application status
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/HealthResponse"
```

**HealthResponse schema**:

```yaml
HealthResponse:
  type: object
  required: [status, database, fallback_active, version]
  properties:
    status:
      type: string
      enum: [ok, degraded]
      description: ok when primary database is connected, degraded when fallback is active
    database:
      type: string
      enum: [postgresql, sqlite]
    fallback_active:
      type: boolean
    version:
      type: string
      example: "1.0.0"
```

**Example response (healthy)**:

```json
{
  "status": "ok",
  "database": "postgresql",
  "fallback_active": false,
  "version": "1.0.0"
}
```

**Example response (fallback)**:

```json
{
  "status": "degraded",
  "database": "sqlite",
  "fallback_active": true,
  "version": "1.0.0"
}
```

## 7.3 Auth Endpoints

### 7.3.1 POST /auth/register

```yaml
/auth/register:
  post:
    tags: [auth]
    summary: Register a new user
    security: []
    operationId: registerUser
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/RegisterRequest"
    responses:
      "201":
        description: User created
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/UserResponse"
      "409":
        description: Email or username already exists
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
      "422":
        description: Validation error
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
```

**RegisterRequest schema**:

```yaml
RegisterRequest:
  type: object
  required: [email, username, password]
  properties:
    email:
      type: string
      format: email
      maxLength: 255
      example: "user@example.com"
    username:
      type: string
      minLength: 3
      maxLength: 50
      pattern: "^[a-zA-Z0-9_]+$"
      example: "johndoe"
    password:
      type: string
      minLength: 8
      maxLength: 72
      format: password
      example: "securepass123"
```

**Example request**:

```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepass123"
}
```

**Example response (201)**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "created_at": "2026-10-15T12:34:56Z"
}
```

**Error responses**:

```json
// 409 DUPLICATE_EMAIL
{
  "detail": "Email already registered",
  "code": "DUPLICATE_EMAIL",
  "field": "email"
}
```

```json
// 422 VALIDATION_ERROR
{
  "detail": "Password must be at least 8 characters",
  "code": "VALIDATION_ERROR",
  "field": "password"
}
```

### 7.3.2 POST /auth/login

```yaml
/auth/login:
  post:
    tags: [auth]
    summary: Log in and obtain an access token
    security: []
    operationId: loginUser
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/LoginRequest"
    responses:
      "200":
        description: Login successful
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/LoginResponse"
      "401":
        description: Invalid credentials
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
```

**LoginRequest schema**:

```yaml
LoginRequest:
  type: object
  required: [email, password]
  properties:
    email:
      type: string
      format: email
    password:
      type: string
      format: password
```

**LoginResponse schema**:

```yaml
LoginResponse:
  type: object
  required: [access_token, token_type, user]
  properties:
    access_token:
      type: string
      example: "eyJhbGciOiJIUzI1NiIs..."
    token_type:
      type: string
      enum: [bearer]
    user:
      $ref: "#/components/schemas/UserResponse"
```

**Example response (200)**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "username": "johndoe",
    "is_active": true,
    "created_at": "2026-10-15T12:34:56Z"
  }
}
```

### 7.3.3 GET /auth/me

```yaml
/auth/me:
  get:
    tags: [auth]
    summary: Get current user profile
    operationId: getCurrentUser
    responses:
      "200":
        description: Current user
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/UserResponse"
      "401":
        description: Not authenticated
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
```

**UserResponse schema**:

```yaml
UserResponse:
  type: object
  required: [id, email, username, is_active, created_at]
  properties:
    id:
      type: string
      format: uuid
    email:
      type: string
      format: email
    username:
      type: string
    is_active:
      type: boolean
    created_at:
      type: string
      format: date-time
```

## 7.4 Category Endpoints

### 7.4.1 GET /categories

```yaml
/categories:
  get:
    tags: [categories]
    summary: List system and user categories
    operationId: listCategories
    responses:
      "200":
        description: List of categories
        content:
          application/json:
            schema:
              type: object
              required: [categories]
              properties:
                categories:
                  type: array
                  items:
                    $ref: "#/components/schemas/CategoryResponse"
```

**CategoryResponse schema**:

```yaml
CategoryResponse:
  type: object
  required: [id, name, color, is_system, created_at]
  properties:
    id:
      type: string
      format: uuid
    name:
      type: string
      maxLength: 100
    color:
      type: string
      pattern: "^#[0-9A-Fa-f]{6}$"
      example: "#EF4444"
    icon:
      type: string
      nullable: true
    is_system:
      type: boolean
    created_at:
      type: string
      format: date-time
```

**Example response (200)**:

```json
{
  "categories": [
    {
      "id": "11111111-1111-1111-1111-111111111111",
      "name": "Food & Dining",
      "color": "#EF4444",
      "icon": "utensils",
      "is_system": true,
      "created_at": "2026-10-01T00:00:00Z"
    },
    {
      "id": "22222222-2222-2222-2222-222222222222",
      "name": "My Side Project",
      "color": "#A855F7",
      "icon": null,
      "is_system": false,
      "created_at": "2026-10-15T12:34:56Z"
    }
  ]
}
```

### 7.4.2 POST /categories

```yaml
/categories:
  post:
    tags: [categories]
    summary: Create a custom category
    operationId: createCategory
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/CreateCategoryRequest"
    responses:
      "201":
        description: Category created
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CategoryResponse"
      "409":
        description: Category name already exists
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
      "422":
        description: Validation error
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
```

**CreateCategoryRequest schema**:

```yaml
CreateCategoryRequest:
  type: object
  required: [name, color]
  properties:
    name:
      type: string
      minLength: 1
      maxLength: 100
    color:
      type: string
      pattern: "^#[0-9A-Fa-f]{6}$"
    icon:
      type: string
      maxLength: 50
      nullable: true
```

### 7.4.3 DELETE /categories/{category_id}

```yaml
/categories/{category_id}:
  delete:
    tags: [categories]
    summary: Delete a custom category
    operationId: deleteCategory
    parameters:
      - name: category_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      "204":
        description: Category deleted
      "404":
        description: Category not found or not owned by user
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
      "409":
        description: Category has existing expenses
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
```

## 7.5 Expense Endpoints

### 7.5.1 GET /expenses

```yaml
/expenses:
  get:
    tags: [expenses]
    summary: List expenses with filters and pagination
    operationId: listExpenses
    parameters:
      - name: year_month
        in: query
        required: false
        schema:
          type: string
          pattern: "^[0-9]{4}-[0-9]{2}$"
          example: "2026-10"
      - name: category_id
        in: query
        required: false
        schema:
          type: string
          format: uuid
      - name: page
        in: query
        required: false
        schema:
          type: integer
          minimum: 1
          default: 1
      - name: page_size
        in: query
        required: false
        schema:
          type: integer
          minimum: 1
          maximum: 100
          default: 20
    responses:
      "200":
        description: Paginated list of expenses
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ExpenseListResponse"
      "422":
        description: Invalid query parameters
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
```

**ExpenseListResponse schema**:

```yaml
ExpenseListResponse:
  type: object
  required: [items, total, page, page_size]
  properties:
    items:
      type: array
      items:
        $ref: "#/components/schemas/ExpenseResponse"
    total:
      type: integer
      minimum: 0
    page:
      type: integer
      minimum: 1
    page_size:
      type: integer
      minimum: 1
```

**ExpenseResponse schema**:

```yaml
ExpenseResponse:
  type: object
  required: [id, amount, currency, category_id, category_name, category_color, date, created_at]
  properties:
    id:
      type: string
      format: uuid
    amount:
      type: string
      pattern: "^[0-9]+\\.[0-9]{2}$"
      example: "125.50"
    currency:
      type: string
      enum: [USD]
    category_id:
      type: string
      format: uuid
    category_name:
      type: string
    category_color:
      type: string
      pattern: "^#[0-9A-Fa-f]{6}$"
    date:
      type: string
      format: date
      example: "2026-10-15"
    note:
      type: string
      nullable: true
      maxLength: 500
    created_at:
      type: string
      format: date-time
    updated_at:
      type: string
      format: date-time
```

### 7.5.2 POST /expenses

```yaml
/expenses:
  post:
    tags: [expenses]
    summary: Create an expense
    operationId: createExpense
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/CreateExpenseRequest"
    responses:
      "201":
        description: Expense created
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ExpenseResponse"
      "404":
        description: Category not found
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
      "422":
        description: Validation error
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
```

**CreateExpenseRequest schema**:

```yaml
CreateExpenseRequest:
  type: object
  required: [amount, category_id, date]
  properties:
    amount:
      type: string
      pattern: "^[0-9]+(\\.[0-9]{1,2})?$"
      example: "125.50"
      description: |
        Amount in USD as a string. Must be positive.
        Maximum 2 decimal places.
    category_id:
      type: string
      format: uuid
    date:
      type: string
      format: date
      example: "2026-10-15"
    note:
      type: string
      maxLength: 500
      nullable: true
```

### 7.5.3 GET /expenses/{expense_id}

```yaml
/expenses/{expense_id}:
  get:
    tags: [expenses]
    summary: Get a single expense
    operationId: getExpense
    parameters:
      - name: expense_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      "200":
        description: Expense details
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ExpenseResponse"
      "404":
        description: Expense not found
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
```

### 7.5.4 PUT /expenses/{expense_id}

```yaml
/expenses/{expense_id}:
  put:
    tags: [expenses]
    summary: Update an expense
    operationId: updateExpense
    parameters:
      - name: expense_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/UpdateExpenseRequest"
    responses:
      "200":
        description: Expense updated
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ExpenseResponse"
      "404":
        description: Expense not found
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
      "422":
        description: Validation error
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
```

**UpdateExpenseRequest schema**:

```yaml
UpdateExpenseRequest:
  type: object
  properties:
    amount:
      type: string
      pattern: "^[0-9]+(\\.[0-9]{1,2})?$"
    category_id:
      type: string
      format: uuid
    date:
      type: string
      format: date
    note:
      type: string
      maxLength: 500
      nullable: true
  minProperties: 1
```

### 7.5.5 DELETE /expenses/{expense_id}

```yaml
/expenses/{expense_id}:
  delete:
    tags: [expenses]
    summary: Delete an expense
    operationId: deleteExpense
    parameters:
      - name: expense_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      "204":
        description: Expense deleted
      "404":
        description: Expense not found
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
```

## 7.6 Budget Endpoints

### 7.6.1 GET /budgets/{year_month}

```yaml
/budgets/{year_month}:
  get:
    tags: [budgets]
    summary: Get budget for a month
    operationId: getBudget
    parameters:
      - name: year_month
        in: path
        required: true
        schema:
          type: string
          pattern: "^[0-9]{4}-[0-9]{2}$"
    responses:
      "200":
        description: Budget details
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/BudgetResponse"
      "422":
        description: Invalid year_month format
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
```

**BudgetResponse schema**:

```yaml
BudgetResponse:
  type: object
  required: [year_month, amount]
  properties:
    year_month:
      type: string
      pattern: "^[0-9]{4}-[0-9]{2}$"
      example: "2026-10"
    amount:
      type: string
      pattern: "^[0-9]+\\.[0-9]{2}$"
      example: "2000.00"
```

**Behavior note**: If no budget exists for the month, the endpoint
returns 200 with `amount: "0.00"`. It does not return 404.

### 7.6.2 PUT /budgets/{year_month}

```yaml
/budgets/{year_month}:
  put:
    tags: [budgets]
    summary: Set or update budget for a month
    operationId: setBudget
    parameters:
      - name: year_month
        in: path
        required: true
        schema:
          type: string
          pattern: "^[0-9]{4}-[0-9]{2}$"
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/SetBudgetRequest"
    responses:
      "200":
        description: Budget set or updated
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/BudgetResponse"
      "422":
        description: Validation error
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
```

**SetBudgetRequest schema**:

```yaml
SetBudgetRequest:
  type: object
  required: [amount]
  properties:
    amount:
      type: string
      pattern: "^[0-9]+(\\.[0-9]{1,2})?$"
      example: "2000.00"
```

### 7.6.3 DELETE /budgets/{year_month}

```yaml
/budgets/{year_month}:
  delete:
    tags: [budgets]
    summary: Delete budget for a month
    operationId: deleteBudget
    parameters:
      - name: year_month
        in: path
        required: true
        schema:
          type: string
          pattern: "^[0-9]{4}-[0-9]{2}$"
    responses:
      "204":
        description: Budget deleted
      "404":
        description: No budget for that month
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
```

## 7.7 Dashboard Endpoints

### 7.7.1 GET /dashboard/summary

```yaml
/dashboard/summary:
  get:
    tags: [dashboard]
    summary: Get monthly summary
    operationId: getDashboardSummary
    parameters:
      - name: year_month
        in: query
        required: true
        schema:
          type: string
          pattern: "^[0-9]{4}-[0-9]{2}$"
    responses:
      "200":
        description: Monthly summary
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/DashboardSummaryResponse"
```

**DashboardSummaryResponse schema**:

```yaml
DashboardSummaryResponse:
  type: object
  required:
    - year_month
    - total_spent
    - budget
    - remaining
    - percentage
    - transaction_count
    - is_over_budget
  properties:
    year_month:
      type: string
    total_spent:
      type: string
      example: "1250.50"
    budget:
      type: string
      example: "2000.00"
    remaining:
      type: string
      example: "749.50"
    percentage:
      type: number
      nullable: true
      example: 62.5
      description: null when budget is 0
    transaction_count:
      type: integer
      example: 23
    is_over_budget:
      type: boolean
      example: false
```

### 7.7.2 GET /dashboard/by-category

```yaml
/dashboard/by-category:
  get:
    tags: [dashboard]
    summary: Get category breakdown
    operationId: getDashboardByCategory
    parameters:
      - name: year_month
        in: query
        required: true
        schema:
          type: string
          pattern: "^[0-9]{4}-[0-9]{2}$"
    responses:
      "200":
        description: Category breakdown
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/DashboardByCategoryResponse"
```

**DashboardByCategoryResponse schema**:

```yaml
DashboardByCategoryResponse:
  type: object
  required: [year_month, total, categories]
  properties:
    year_month:
      type: string
    total:
      type: string
    categories:
      type: array
      items:
        type: object
        required: [category_id, name, color, amount, percentage]
        properties:
          category_id:
            type: string
            format: uuid
          name:
            type: string
          color:
            type: string
          amount:
            type: string
          percentage:
            type: number
```

### 7.7.3 GET /dashboard/trend

```yaml
/dashboard/trend:
  get:
    tags: [dashboard]
    summary: Get monthly trend
    operationId: getDashboardTrend
    parameters:
      - name: months
        in: query
        required: false
        schema:
          type: integer
          minimum: 1
          maximum: 24
          default: 6
    responses:
      "200":
        description: Monthly trend
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/DashboardTrendResponse"
```

**DashboardTrendResponse schema**:

```yaml
DashboardTrendResponse:
  type: object
  required: [months]
  properties:
    months:
      type: array
      items:
        type: object
        required: [year_month, total]
        properties:
          year_month:
            type: string
          total:
            type: string
```

### 7.7.4 GET /dashboard/cumulative

```yaml
/dashboard/cumulative:
  get:
    tags: [dashboard]
    summary: Get cumulative spending for a month
    operationId: getDashboardCumulative
    parameters:
      - name: year_month
        in: query
        required: true
        schema:
          type: string
          pattern: "^[0-9]{4}-[0-9]{2}$"
    responses:
      "200":
        description: Cumulative spending
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/DashboardCumulativeResponse"
```

**DashboardCumulativeResponse schema**:

```yaml
DashboardCumulativeResponse:
  type: object
  required: [year_month, budget, days]
  properties:
    year_month:
      type: string
    budget:
      type: string
    days:
      type: array
      items:
        type: object
        required: [date, daily, cumulative]
        properties:
          date:
            type: string
            format: date
          daily:
            type: string
          cumulative:
            type: string
```

### 7.7.5 GET /dashboard/heatmap

```yaml
/dashboard/heatmap:
  get:
    tags: [dashboard]
    summary: Get weekly spending heatmap
    operationId: getDashboardHeatmap
    parameters:
      - name: weeks
        in: query
        required: false
        schema:
          type: integer
          minimum: 1
          maximum: 52
          default: 12
    responses:
      "200":
        description: Weekly heatmap data
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/DashboardHeatmapResponse"
```

**DashboardHeatmapResponse schema**:

```yaml
DashboardHeatmapResponse:
  type: object
  required: [max_amount, weeks]
  properties:
    max_amount:
      type: string
    weeks:
      type: array
      items:
        type: object
        required: [week_start, days]
        properties:
          week_start:
            type: string
            format: date
          days:
            type: array
            minItems: 7
            maxItems: 7
            items:
              type: object
              required: [date, amount]
              properties:
                date:
                  type: string
                  format: date
                amount:
                  type: string
```

### 7.7.6 GET /dashboard/recent

```yaml
/dashboard/recent:
  get:
    tags: [dashboard]
    summary: Get recent transactions
    operationId: getDashboardRecent
    parameters:
      - name: limit
        in: query
        required: false
        schema:
          type: integer
          minimum: 1
          maximum: 50
          default: 10
    responses:
      "200":
        description: Recent transactions
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/DashboardRecentResponse"
```

**DashboardRecentResponse schema**:

```yaml
DashboardRecentResponse:
  type: object
  required: [items]
  properties:
    items:
      type: array
      items:
        $ref: "#/components/schemas/ExpenseResponse"
```

## 7.8 Error Response Format

### 7.8.1 ErrorResponse Schema

```yaml
ErrorResponse:
  type: object
  required: [detail, code]
  properties:
    detail:
      type: string
      description: Human-readable error message
      example: "Amount must be positive"
    code:
      type: string
      description: Machine-readable error code
      example: "INVALID_AMOUNT"
    field:
      type: string
      nullable: true
      description: Field name for validation errors
      example: "amount"
```

### 7.8.2 Validation Error (422)

For Pydantic validation errors, the format is normalized:

```json
{
  "detail": "ensure this value is greater than 0",
  "code": "VALIDATION_ERROR",
  "field": "amount"
}
```

If multiple fields fail, only the first error is returned. This keeps
the response shape consistent. Frontend can submit and correct one
field at a time.

### 7.8.3 Error Code Reference

| Code | HTTP | When |
|---|---|---|
| VALIDATION_ERROR | 422 | Request body or query invalid |
| INVALID_CREDENTIALS | 401 | Login failed |
| TOKEN_EXPIRED | 401 | JWT expired |
| TOKEN_INVALID | 401 | JWT malformed or wrong claims |
| UNAUTHORIZED | 401 | Missing token |
| USER_INACTIVE | 401 | Account disabled |
| FORBIDDEN | 403 | Action not permitted |
| NOT_FOUND | 404 | Resource not found |
| CATEGORY_NOT_FOUND | 404 | Category missing or not owned |
| DUPLICATE_EMAIL | 409 | Email registered |
| DUPLICATE_USERNAME | 409 | Username taken |
| DUPLICATE_CATEGORY | 409 | Category name exists |
| DUPLICATE_BUDGET | 409 | Budget exists for month |
| CATEGORY_IN_USE | 409 | Category has expenses |
| INVALID_AMOUNT | 422 | Amount invalid |
| INVALID_MONTH | 422 | year_month invalid |
| DATABASE_UNAVAILABLE | 503 | Database error |
| INTERNAL_ERROR | 500 | Unexpected error |

### 7.8.4 HTTP Status Code Usage

| Status | Meaning | Used For |
|---|---|---|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST (register, create) |
| 204 | No Content | Successful DELETE |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Action not allowed for this user |
| 404 | Not Found | Resource missing or not owned |
| 409 | Conflict | Duplicate resource |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Unexpected error |
| 503 | Service Unavailable | Database error |

## 7.9 Pagination Specification

### 7.9.1 Request Parameters

| Parameter | Type | Default | Min | Max |
|---|---|---|---|---|
| page | integer | 1 | 1 | - |
| page_size | integer | 20 | 1 | 100 |

### 7.9.2 Response Shape

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

### 7.9.3 Rules

- `total` is the total count of matching records, not the page size
- `items` may be empty when `page` exceeds total pages
- Frontend computes total pages as `ceil(total / page_size)`
- Invalid `page` or `page_size` returns 422

### 7.9.4 Example

Request:

```
GET /api/v1/expenses?year_month=2026-10&page=2&page_size=10
```

Response:

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440010",
      "amount": "45.00",
      "currency": "USD",
      "category_id": "11111111-1111-1111-1111-111111111111",
      "category_name": "Food & Dining",
      "category_color": "#EF4444",
      "date": "2026-10-10",
      "note": null,
      "created_at": "2026-10-10T08:15:00Z",
      "updated_at": "2026-10-10T08:15:00Z"
    }
  ],
  "total": 23,
  "page": 2,
  "page_size": 10
}
```

## 7.10 Amount and Date Format

### 7.10.1 Amount Format

| Aspect | Rule |
|---|---|
| JSON type | String |
| Pattern | `^[0-9]+(\.[0-9]{1,2})?$` |
| Examples | `"125"`, `"125.5"`, `"125.50"` |
| Invalid | `125.505`, `-125`, `"abc"`, `""` |
| Precision | Max 2 decimal places |
| Max value | 9999999999.99 |
| Min value | 0.01 |
| Currency | Always USD |

**Why string not number**: JSON numbers are floating-point. Transmitting
`125.50` as a number can lose precision. Strings preserve exact value.

### 7.10.2 Date Format

| Aspect | Rule |
|---|---|
| Format | ISO 8601 date |
| Pattern | `YYYY-MM-DD` |
| Example | `"2026-10-15"` |
| No time component | Date only |
| No timezone | Interpreted as a local date |

### 7.10.3 DateTime Format

| Aspect | Rule |
|---|---|
| Format | ISO 8601 with timezone |
| Example | `"2026-10-15T12:34:56Z"` |
| Timezone | Always UTC (Z suffix) |
| Used for | `created_at`, `updated_at` |

### 7.10.4 Year-Month Format

| Aspect | Rule |
|---|---|
| Format | `YYYY-MM` |
| Pattern | `^[0-9]{4}-[0-9]{2}$` |
| Example | `"2026-10"` |
| Used for | Budget keys, dashboard filters |
| Invalid | `"2026-1"`, `"26-01"`, `"2026/10"` |

## 7.11 Response Examples

### 7.11.1 Dashboard Summary

```json
{
  "year_month": "2026-10",
  "total_spent": "1250.50",
  "budget": "2000.00",
  "remaining": "749.50",
  "percentage": 62.5,
  "transaction_count": 23,
  "is_over_budget": false
}
```

### 7.11.2 Dashboard By Category

```json
{
  "year_month": "2026-10",
  "total": "1250.50",
  "categories": [
    {
      "category_id": "11111111-1111-1111-1111-111111111111",
      "name": "Food & Dining",
      "color": "#EF4444",
      "amount": "450.00",
      "percentage": 36.0
    },
    {
      "category_id": "22222222-2222-2222-2222-222222222222",
      "name": "Groceries",
      "color": "#F97316",
      "amount": "300.00",
      "percentage": 24.0
    },
    {
      "category_id": "33333333-3333-3333-3333-333333333333",
      "name": "Transportation",
      "color": "#EAB308",
      "amount": "200.00",
      "percentage": 16.0
    }
  ]
}
```

### 7.11.3 Dashboard Trend

```json
{
  "months": [
    {"year_month": "2026-05", "total": "980.00"},
    {"year_month": "2026-06", "total": "1100.50"},
    {"year_month": "2026-07", "total": "870.25"},
    {"year_month": "2026-08", "total": "1320.00"},
    {"year_month": "2026-09", "total": "1450.75"},
    {"year_month": "2026-10", "total": "1250.50"}
  ]
}
```

### 7.11.4 Dashboard Cumulative

```json
{
  "year_month": "2026-10",
  "budget": "2000.00",
  "days": [
    {"date": "2026-10-01", "daily": "45.00", "cumulative": "45.00"},
    {"date": "2026-10-02", "daily": "0.00", "cumulative": "45.00"},
    {"date": "2026-10-03", "daily": "25.50", "cumulative": "70.50"},
    {"date": "2026-10-04", "daily": "0.00", "cumulative": "70.50"}
  ]
}
```

### 7.11.5 Dashboard Heatmap

```json
{
  "max_amount": "150.00",
  "weeks": [
    {
      "week_start": "2026-10-13",
      "days": [
        {"date": "2026-10-13", "amount": "0.00"},
        {"date": "2026-10-14", "amount": "25.00"},
        {"date": "2026-10-15", "amount": "125.50"},
        {"date": "2026-10-16", "amount": "0.00"},
        {"date": "2026-10-17", "amount": "45.00"},
        {"date": "2026-10-18", "amount": "0.00"},
        {"date": "2026-10-19", "amount": "30.00"}
      ]
    }
  ]
}
```

## 7.12 OpenAPI Schema Components

### 7.12.1 Complete Schema List

| Schema | Used By |
|---|---|
| HealthResponse | GET /health |
| RegisterRequest | POST /auth/register |
| LoginRequest | POST /auth/login |
| LoginResponse | POST /auth/login |
| UserResponse | GET /auth/me, POST /auth/register, POST /auth/login |
| CategoryResponse | GET /categories, POST /categories |
| CreateCategoryRequest | POST /categories |
| ExpenseResponse | GET /expenses, POST /expenses, GET /expenses/{id}, PUT /expenses/{id} |
| ExpenseListResponse | GET /expenses |
| CreateExpenseRequest | POST /expenses |
| UpdateExpenseRequest | PUT /expenses/{id} |
| BudgetResponse | GET /budgets/{ym}, PUT /budgets/{ym} |
| SetBudgetRequest | PUT /budgets/{ym} |
| DashboardSummaryResponse | GET /dashboard/summary |
| DashboardByCategoryResponse | GET /dashboard/by-category |
| DashboardTrendResponse | GET /dashboard/trend |
| DashboardCumulativeResponse | GET /dashboard/cumulative |
| DashboardHeatmapResponse | GET /dashboard/heatmap |
| DashboardRecentResponse | GET /dashboard/recent |
| ErrorResponse | All error responses |

### 7.12.2 Common Patterns

**All IDs are UUID strings**:

```yaml
id:
  type: string
  format: uuid
```

**All amounts are strings**:

```yaml
amount:
  type: string
  pattern: "^[0-9]+\\.[0-9]{2}$"
```

**All dates are ISO strings**:

```yaml
date:
  type: string
  format: date
```

**All timestamps are ISO strings with UTC**:

```yaml
created_at:
  type: string
  format: date-time
```

## 7.13 Contract Testing

### 7.13.1 How the Contract Is Verified

| Layer | How |
|---|---|
| Backend implementation | FastAPI generates OpenAPI from code; compared against `openapi.yaml` |
| Frontend integration | Frontend mocks against `openapi.yaml` shapes |
| Integration tests | httpx tests assert response shapes match schemas |
| E2E tests | Playwright exercises full flows against the real backend |

### 7.13.2 FastAPI Auto-Generated OpenAPI

FastAPI generates an OpenAPI document at `/openapi.json`. The repository
`openapi.yaml` is the hand-authored contract. They should match.

A CI step compares key fields:

```bash
# In CI
curl http://localhost:8000/openapi.json > /tmp/generated.json
python scripts/compare_openapi.py openapi.yaml /tmp/generated.json
```

The comparison checks:

- All paths in `openapi.yaml` exist in the generated spec
- All required schemas exist
- All response shapes match

### 7.13.3 Schema Validation in Tests

```python
def test_create_expense_response_shape(client, auth_headers, category_id):
    response = client.post("/api/v1/expenses", json={
        "amount": "125.50",
        "category_id": str(category_id),
        "date": "2026-10-15",
        "note": "Lunch",
    }, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()

    assert set(data.keys()) >= {
        "id", "amount", "currency", "category_id", "category_name",
        "category_color", "date", "note", "created_at", "updated_at",
    }
    assert data["amount"] == "125.50"
    assert data["currency"] == "USD"
    assert isinstance(data["id"], str)
```

## 7.14 OpenAPI Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| OpenAPI version | 3.1.0 | Latest, supports JSON Schema 2020-12 |
| Amount type | String | Avoids float precision loss |
| ID type | UUID string | Portable, no integer overflow |
| Date type | ISO date string | No timezone ambiguity |
| Error format | `{detail, code, field}` | Consistent, machine-readable |
| Pagination | page + page_size | Simple, predictable |
| Auth scheme | Bearer JWT | Standard, works with SPA |
| Global security | Applied by default | Fewer repetitions |
| Health endpoint | No auth | Needed for monitoring |
| Register/login | No auth | Bootstrap endpoints |
| 404 for cross-user | Not 403 | Does not reveal existence |
| Budget missing | 200 with amount=0 | Simplifies frontend |
| Percentage null | When budget=0 | Avoids division by zero |
| Trend months | 1-24, default 6 | Bounded, sensible default |
| Heatmap weeks | 1-52, default 12 | Bounded, sensible default |
| Recent limit | 1-50, default 10 | Bounded, sensible default |
| Page size max | 100 | Prevents abuse |
| Note max length | 500 | Reasonable limit |
| Username pattern | `^[a-zA-Z0-9_]+$` | Safe, readable |
| Password max | 72 | bcrypt limit |
```

---
