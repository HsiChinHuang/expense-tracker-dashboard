# Chapter 12: Security and Audit

## 12.1 Overview

This chapter covers the security posture of the application, the audit
artifacts produced, and the policies that govern AI tool usage. It maps
to Final Project Criterion 13.

### 12.1.1 Criterion 13 Requirements

Criterion 13 states that a full-credit submission must include:

- PR audit output
- Deterministic security scan findings
- Agent/extension security notes
- Operational diagnosis output
- AI tool/data policy

The mapping:

| Requirement | Artifact |
|---|---|
| PR audit output | `security/pr-audit.md` |
| Deterministic security scan findings | `security/gitleaks-report.json`, `security/semgrep-report.json`, `security/trivy-report.json`, `security/pip-audit-report.txt`, `security/npm-audit-report.txt` |
| Agent/extension security notes | `security/agent-security-notes.md` |
| Operational diagnosis output | `ops/diagnosis.md` (Chapter 13) |
| AI tool/data policy | `security/ai-tool-data-policy.md` |

### 12.1.2 Security Layers

The application has multiple layers of security controls:

| Layer | Controls |
|---|---|
| Network | HTTPS via Render, CORS restricted to known origins |
| Authentication | JWT with HS256, fixed algorithm, 24-hour expiry |
| Password | bcrypt with rounds=12, salted, never stored plain |
| Authorization | Every query filtered by user_id |
| Data isolation | Cross-user access returns 404 |
| Input validation | Pydantic schemas with strict types |
| Amount integrity | Decimal everywhere, NUMERIC(12,2) in database |
| Audit | All writes logged in the same transaction |
| Secrets | Environment variables, never committed |
| Dependencies | Scanned with pip-audit, npm audit, trivy |
| Agent | Hooks, JWT, permissions, read-only analysis agents |
| Data policy | Local model, no cloud LLM calls |

### 12.1.3 Security Directory Layout

```
security/
├── pr-audit.md
├── gitleaks-report.json
├── semgrep-report.json
├── trivy-report.json
├── pip-audit-report.txt
├── npm-audit-report.txt
├── agent-security-notes.md
└── ai-tool-data-policy.md
```

## 12.2 Threat Model

### 12.2.1 Assets

| Asset | Sensitivity |
|---|---|
| User credentials | High |
| JWT secret | High |
| User expense data | Medium (financial privacy) |
| User budget data | Medium |
| Audit logs | Medium |
| Source code | Low |
| Configuration | Medium |

### 12.2.2 Threat Actors

| Actor | Motivation | Capability |
|---|---|---|
| Unauthenticated attacker | Data theft, abuse | Medium |
| Authenticated malicious user | Access other users' data | Medium |
| Compromised dependency | Supply chain attack | High |
| Misconfigured deployment | Accidental exposure | Low |
| Malicious agent input | Prompt injection, data exfiltration | Medium |

### 12.2.3 Threats and Mitigations

| Threat | Mitigation |
|---|---|
| Password brute force | bcrypt with rounds=12 (slow) |
| Token forgery | HS256 with secret from env, validated on every request |
| Token replay after expiry | 24-hour expiry, validated |
| Cross-user data access | user_id filter in every query, 404 response |
| SQL injection | SQLAlchemy parameterized queries |
| XSS | No third-party scripts, React escapes by default |
| CSRF | Bearer token in header, not cookie |
| Secret leakage | .env in .gitignore, gitleaks scan |
| Dependency vulnerability | pip-audit, npm audit, trivy |
| Agent data exfiltration | Local model, no cloud calls |
| Prompt injection | Agent restricted by hooks and permissions |
| Audit log tampering | Same transaction, no API access |
| Amount precision attack | Decimal only, NUMERIC(12,2) |
| Enumeration | 404 for missing and not-owned |
| Denial of service | Render free tier limits; no rate limiting in MVP |

### 12.2.4 Out of Scope Threats

| Threat | Reason |
|---|---|
| Nation-state attacker | Out of scope for a demo project |
| Physical access | Hosted on Render |
| Insider threat | Single-user project |
| DDoS | Render provides basic protection |
| Zero-day in dependencies | Mitigated by scanning, not eliminated |
| Social engineering | Out of scope |

## 12.3 Authentication Security

### 12.3.1 Password Storage

| Control | Implementation |
|---|---|
| Algorithm | bcrypt |
| Rounds | 12 |
| Salt | Automatic, unique per password |
| Storage | `hashed_password` column |
| Transmission | HTTPS only in production |
| Logging | Never logged |
| Validation | Min 8 chars, max 72 (bcrypt limit) |

### 12.3.2 JWT Security

| Control | Implementation |
|---|---|
| Algorithm | HS256, fixed in code |
| Algorithm confusion | `algorithms=[settings.JWT_ALGORITHM]` — never from token |
| alg=none | Rejected by python-jose when algorithms is fixed |
| Expiry | 24 hours, validated on every request |
| Audience | `expense-tracker-api`, validated |
| Issuer | `expense-tracker`, validated |
| Type | `access`, validated |
| Secret | From `JWT_SECRET` env var |
| Secret length | Recommended 32+ characters |
| Secret rotation | Not automated in MVP |
| Token storage | localStorage (documented trade-off) |

### 12.3.3 Authentication Failures

| Failure | Response |
|---|---|
| Missing token | 401 UNAUTHORIZED |
| Malformed token | 401 TOKEN_INVALID |
| Expired token | 401 TOKEN_EXPIRED |
| Wrong audience | 401 TOKEN_INVALID |
| Wrong issuer | 401 TOKEN_INVALID |
| Wrong type | 401 TOKEN_INVALID |
| User not found | 401 TOKEN_INVALID |
| User inactive | 401 USER_INACTIVE |
| Wrong password | 401 INVALID_CREDENTIALS |
| Nonexistent email | 401 INVALID_CREDENTIALS (same as wrong password) |

### 12.3.4 Timing Attack Mitigation

When a login is attempted with a nonexistent email, the backend runs a
dummy bcrypt verification. This ensures the response time is similar to
a real password check, preventing email enumeration through timing.

```python
DUMMY_HASH = hash_password("dummy-password-for-timing")


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email.lower()).first()
    if user is None:
        verify_password(password, DUMMY_HASH)
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
```

## 12.4 Authorization Security

### 12.4.1 User Isolation

Every query that reads or writes user data includes a `user_id` filter.

```python
# Every expense query
db.query(Expense).filter(Expense.user_id == current_user.id)

# Every budget query
db.query(Budget).filter(Budget.user_id == current_user.id)

# Every category query (user's own, plus system)
db.query(Category).filter(
    or_(Category.user_id.is_(None), Category.user_id == current_user.id)
)
```

### 12.4.2 Cross-User Access Returns 404

When a user tries to access another user's resource, the response is
404 Not Found, not 403 Forbidden. This prevents the attacker from
confirming that the resource exists.

| Scenario | Response |
|---|---|
| Resource exists and belongs to user | 200 |
| Resource does not exist | 404 |
| Resource exists but belongs to another user | 404 |
| Resource exists but user is not authenticated | 401 |

### 12.4.3 Category Access Validation

Categories are shared between system and user scope. Access validation
checks both:

```python
def validate_category_access(db, user, category_id):
    category = db.query(Category).filter(
        Category.id == category_id,
        or_(
            Category.user_id.is_(None),       # system category
            Category.user_id == user.id,       # user's own category
        ),
    ).first()
    if category is None:
        raise AppError("CATEGORY_NOT_FOUND", "Category not found", 404)
    return category
```

### 12.4.4 System Category Protection

System categories cannot be modified or deleted:

| Action | Result |
|---|---|
| List system categories | Allowed |
| Use system category in expense | Allowed |
| Update system category | 404 (not returned by query filter) |
| Delete system category | 404 |
| Create system category | Not exposed via API |

### 12.4.5 Test Coverage

`backend/tests/integration/test_isolation.py` verifies:

- User A cannot read user B's expense (404)
- User A cannot update user B's expense (404)
- User A cannot delete user B's expense (404)
- User A's expense list contains only their own
- User A cannot read user B's budget (returns 0.00)
- User A cannot set a budget on behalf of user B

## 12.5 Input Validation

### 12.5.1 Pydantic Schemas

All request bodies are validated by Pydantic v2 schemas with strict
constraints.

```python
class CreateExpenseRequest(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category_id: UUID
    date: date
    note: str | None = Field(None, max_length=500)
```

### 12.5.2 Validation Rules

| Field | Rule |
|---|---|
| Email | Valid email format, max 255 |
| Username | 3-50 chars, `^[a-zA-Z0-9_]+$` |
| Password | 8-72 chars |
| Amount | Positive, max 12 digits, 2 decimals |
| Category ID | Valid UUID |
| Date | Valid ISO date |
| Note | Max 500 chars |
| year_month | `^\d{4}-\d{2}$`, month 01-12 |
| page | Integer >= 1 |
| page_size | Integer 1-100 |
| months | Integer 1-24 |
| weeks | Integer 1-52 |
| limit | Integer 1-50 |
| Color | `^#[0-9A-Fa-f]{6}$` |

### 12.5.3 SQL Injection Prevention

All database access uses SQLAlchemy ORM with parameterized queries.
No raw SQL is used in application code. Raw SQL is only in Alembic
migrations, which are not exposed to users.

### 12.5.4 XSS Prevention

| Control | Implementation |
|---|---|
| React escaping | All dynamic content escaped by default |
| No `dangerouslySetInnerHTML` | Not used anywhere |
| No third-party scripts | Only the app's own bundle |
| Content Security Policy | Not configured in MVP (documented) |

### 12.5.5 CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,   # explicit list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

In production, `CORS_ORIGINS` is set to the Render URL only.

## 12.6 Data Integrity

### 12.6.1 Amount Precision

| Layer | Type | Example |
|---|---|---|
| Database | NUMERIC(12,2) | 125.50 |
| Python | Decimal | Decimal("125.50") |
| Pydantic | condecimal(max_digits=12, decimal_places=2) | Decimal("125.50") |
| JSON | String | "125.50" |
| Frontend | String | "125.50" |

### 12.6.2 Date Handling

| Data | Type | Timezone |
|---|---|---|
| Expense date | DATE | None |
| created_at | TIMESTAMPTZ | UTC |
| updated_at | TIMESTAMPTZ | UTC |
| year_month | CHAR(7) | None |

### 12.6.3 Database Constraints

| Table | Constraint |
|---|---|
| users | UNIQUE(email), UNIQUE(username) |
| categories | CHECK color format, CHECK system consistency |
| expenses | CHECK amount > 0, CHECK currency = 'USD' |
| budgets | UNIQUE(user_id, year_month), CHECK amount > 0, CHECK year_month format |
| audit_logs | CHECK action in (CREATE, UPDATE, DELETE), CHECK entity_type in (expense, budget) |

## 12.7 Audit Logging

### 12.7.1 Design

| Property | Value |
|---|---|
| Trigger | Expense and budget create/update/delete |
| Written in | Same transaction as the business operation |
| Accessible via API | No |
| Preserved on user delete | Yes (no cascade) |
| Fields | user_id, action, entity_type, entity_id, old_value, new_value, ip_address, created_at |

### 12.7.2 What Is Logged

| Action | old_value | new_value |
|---|---|---|
| CREATE | null | Full entity state |
| UPDATE | Previous state | New state |
| DELETE | Previous state | null |

### 12.7.3 What Is Not Logged

| Event | Reason |
|---|---|
| Login attempts | Logged to application logs, not audit_logs |
| Registration | Not a data operation on existing data |
| Read operations | Only writes are audited |
| Category operations | Not in MVP scope |
| Failed operations | Only successful commits are audited |

### 12.7.4 Audit Log Example

```json
{
  "id": "audit-uuid",
  "user_id": "user-uuid",
  "action": "UPDATE",
  "entity_type": "expense",
  "entity_id": "expense-uuid",
  "old_value": {
    "amount": "50.00",
    "category_id": "cat-uuid",
    "date": "2026-10-15",
    "note": "Lunch"
  },
  "new_value": {
    "amount": "75.00",
    "category_id": "cat-uuid",
    "date": "2026-10-15",
    "note": "Lunch with team"
  },
  "ip_address": "203.0.113.5",
  "created_at": "2026-10-15T14:22:10Z"
}
```

### 12.7.5 Atomicity

If the audit log write fails, the entire transaction is rolled back.
This guarantees that no business operation occurs without a
corresponding audit entry.

```python
def update_expense(db, user, expense_id, updates, ip_address):
    expense = get_expense(db, user, expense_id)
    old_value = expense_to_dict(expense)

    for key, value in updates.items():
        setattr(expense, key, value)

    db.flush()

    write_audit_log(
        db=db,
        user_id=user.id,
        action="UPDATE",
        entity_type="expense",
        entity_id=expense.id,
        old_value=old_value,
        new_value=expense_to_dict(expense),
        ip_address=ip_address,
    )

    db.commit()  # Both expense update and audit log commit together
    return expense
```

## 12.8 Security Scan Artifacts

### 12.8.1 Scan Tools

| Tool | Purpose | Output |
|---|---|---|
| gitleaks | Detect secrets in git history and working tree | `security/gitleaks-report.json` |
| semgrep | Static analysis for security issues | `security/semgrep-report.json` |
| trivy | Scan dependencies and Docker images | `security/trivy-report.json` |
| pip-audit | Audit Python dependencies | `security/pip-audit-report.txt` |
| npm audit | Audit Node dependencies | `security/npm-audit-report.txt` |

### 12.8.2 Scan Commands

```bash
# 1. Secret scanning
gitleaks detect --source . --report-format json \
  --report-path security/gitleaks-report.json

# 2. Static analysis
semgrep --config=auto --json \
  --output=security/semgrep-report.json

# 3. Dependency and image scanning
trivy fs --format json \
  --output security/trivy-report.json .

trivy image --format json \
  --output security/trivy-image-report.json \
  expense-tracker:latest

# 4. Python dependencies
cd backend && pip-audit --format json \
  > ../security/pip-audit-report.txt

# 5. Node dependencies
cd frontend && npm audit --json \
  > ../security/npm-audit-report.txt
```

### 12.8.3 When Scans Run

| Phase | Scans |
|---|---|
| After Phase 2 (auth) | gitleaks, semgrep |
| After Phase 3 (CRUD) | gitleaks, semgrep, pip-audit, npm audit |
| After Phase 4 (dashboard) | all scans |
| Before deployment | all scans + trivy image |
| After final changes | all scans |

Scans are run locally and results are committed to `security/`. They
are not run in CI, per the project decision.

### 12.8.4 Expected Findings and Handling

| Tool | Expected Finding | Action |
|---|---|---|
| gitleaks | `.env.example` placeholders | Document as template, not real secrets |
| gitleaks | No real secrets | Confirm clean |
| semgrep | Possible `subprocess` usage in MCP | Document as expected |
| semgrep | No high-severity findings | Confirm clean |
| trivy | Low-severity base image CVEs | Document, upgrade when possible |
| pip-audit | Possibly `python-jose` CVE | Upgrade or replace if found |
| npm audit | Dev dependency findings | `npm audit fix` or document |

### 12.8.5 Accepted Findings

Any finding that is not fixed is documented in
`security/agent-security-notes.md` with:

- The finding
- Why it is accepted
- The mitigating control
- The plan to address it (if any)

## 12.9 PR Audit

### 12.9.1 Purpose

`security/pr-audit.md` records at least one pull request reviewed with
AI assistance. It demonstrates that AI-generated code was reviewed
before merging.

### 12.9.2 Template

```markdown
# PR Audit: <PR Title>

## PR Details

- Number: #12
- Title: feat(expenses): implement CRUD endpoints
- Author: <author>
- AI tool used: pi-agent + qwen3.8-27b
- Date: 2026-10-09

## AI Review Output

The PR was reviewed by an independent QA agent. The agent checked:

- All endpoints match openapi.yaml
- All queries filter by user_id
- Amount uses Decimal
- Tests cover the acceptance criteria

## Issues Found

| # | Severity | Description | Fixed |
|---|---|---|---|
| 1 | High | `delete_expense` missing user_id filter | Yes |
| 2 | Medium | Pagination allowed page=0 | Yes |
| 3 | Low | Log message missing expense_id | Yes |

## Verification

- Tests added: `test_delete_other_user_expense_returns_404`
- Manual check: User A cannot access User B's data
- Test suite: 46 passed, 0 failed

## Verdict

Approved after fixes.
```

### 12.9.3 What the Audit Covers

| Category | Checks |
|---|---|
| API contract | Endpoints match openapi.yaml |
| Security | user_id filter, Decimal, no raw SQL |
| Tests | Acceptance criteria covered |
| Code quality | Naming, structure, no dead code |
| Error handling | Error codes, status codes |
| Documentation | Comments, docstrings where needed |

## 12.10 Agent and Extension Security

### 12.10.1 Threat Model for Agents

| Threat | Mitigation |
|---|---|
| Agent accesses another user's data | JWT verification, user_id filter |
| Agent modifies data it should not | Read-only agents (finance-analyst) |
| Agent bypasses backend | MCP calls API, not database |
| Prompt injection | Hooks, permissions, restricted tools |
| Agent leaks secrets | Never in context, never in output |
| Agent executes arbitrary code | File operations restricted to project |
| Agent creates invalid data | Hooks validate before API calls |

### 12.10.2 Agent Security Controls

| Control | Implementation |
|---|---|
| Authentication | JWT via `MCP_USER_TOKEN` |
| Authorization | Backend enforces user_id filter |
| Input validation | Hooks run before API calls |
| Output filtering | No raw IDs, no secrets |
| Tool restriction | MCP exposes only 4 tools |
| Context isolation | Subagents have separate contexts |
| Read-only roles | finance-analyst cannot modify |
| Audit | All MCP writes go through the backend |

### 12.10.3 MCP Security

| Control | Implementation |
|---|---|
| JWT verification | Signature, exp, aud, iss |
| Token source | Environment variable |
| No database access | MCP calls backend API |
| Tool schemas | Strict types, required fields |
| Error handling | Raises exceptions with clear messages |
| No token logging | Token never printed or logged |

### 12.10.4 Hook Security

| Hook | Prevents |
|---|---|
| validate_amount | Negative, zero, three decimals, over max |
| validate_ownership | Access to another user's resource |

Hooks are also enforced in the backend for defense in depth. If a hook
is bypassed, the backend still rejects the operation.

### 12.10.5 Prompt Injection Considerations

| Scenario | Mitigation |
|---|---|
| User input contains instructions | Agent treats user input as data, not commands |
| Skill content is malicious | Skills are project files, not user input |
| MCP tool output is malicious | Tool output is structured JSON, validated |
| Agent is asked to exfiltrate data | No cloud calls, no external requests |
| Agent is asked to bypass auth | MCP verifies JWT, backend enforces |

### 12.10.6 Agent Security Notes Document

`security/agent-security-notes.md` covers:

- Agent architecture and data flow
- Authentication and authorization
- Hooks and guardrails
- Permissions matrix
- Known limitations
- Accepted risks
- Future improvements

## 12.11 AI Tool and Data Policy

### 12.11.1 Policy Summary

`security/ai-tool-data-policy.md` states:

- All AI processing happens locally
- No code, prompts, or context leaves the machine
- No cloud LLM APIs are used
- No production data is used in development
- No secrets are included in agent context

### 12.11.2 Data Categories

| Data | In Agent Context | Reason |
|---|---|---|
| Source code | Yes | Needed for implementation |
| Documentation | Yes | Needed for context |
| Test files | Yes | Needed for test writing |
| Seed data | Yes | Non-sensitive |
| OpenAPI spec | Yes | Needed for backend work |
| Real user data | No | Privacy |
| Production database | No | Not accessible |
| .env file | No | Contains secrets |
| JWT tokens | No | Sensitive |
| JWT secret | No | Sensitive |

### 12.11.3 AI Tool Inventory

| Tool | Purpose | Data Sent |
|---|---|---|
| pi-agent | Coding agent | None (local) |
| qwen3.8-27b | Language model | None (local) |
| Plugins | Extend pi-agent | None (local) |

### 12.11.4 Compliance Considerations

| Concern | Handling |
|---|---|
| Data residency | Local only |
| PII | Not in development data |
| Secrets | Never in context |
| Audit | Session records in docs/ai-workflow.md |
| Reproducibility | Same model version |
| Retention | Session records kept in repo |

### 12.11.5 Policy Document

`security/ai-tool-data-policy.md` contains the full policy with:

- Tool inventory
- Data classification
- Data flow diagram
- Permitted and forbidden uses
- Review requirements
- Incident response

## 12.12 Known Security Limitations

### 12.12.1 Accepted Limitations

| Limitation | Impact | Mitigation | Documented In |
|---|---|---|---|
| No rate limiting | Brute force possible | bcrypt slowness, strong passwords | `security/agent-security-notes.md` |
| JWT in localStorage | XSS could steal token | No third-party scripts | Same |
| No refresh token | User must re-login after 24h | Documented trade-off | Same |
| No CSP header | Reduced XSS protection | No third-party scripts | Same |
| No CSRF token | Bearer token in header mitigates | Standard SPA pattern | Same |
| HTTP in local dev | Not encrypted | HTTPS in production | Same |
| No secret rotation | Secret stays constant | Simple for demo | Same |
| SQLite fallback has no encryption | Data readable if container compromised | Temporary data only | Same |
| Render free tier shared | Noisy neighbor risk | Acceptable for demo | Same |
| No WAF | Basic attacks possible | Render provides basic protection | Same |
| Audit logs not encrypted | Readable in database | Access restricted | Same |
| No 2FA | Account takeover if password leaked | Documented | Same |

### 12.12.2 Why These Are Accepted

The project is a demonstration and learning artifact, not a production
financial application. The security posture is appropriate for:

- A single-user or small-group deployment
- Non-critical data
- Peer review context
- Educational purposes

For production use, the limitations above would need to be addressed.

### 12.12.3 Future Improvements

| Improvement | Priority |
|---|---|
| Rate limiting on auth endpoints | High |
| HttpOnly cookie for token | High |
| Refresh token rotation | Medium |
| Content Security Policy | Medium |
| 2FA | Medium |
| Secret rotation | Medium |
| Audit log encryption | Low |
| WAF | Low |
| Penetration testing | Low |

## 12.13 Operational Security

### 12.13.1 Secrets Management

| Secret | Storage | Rotation |
|---|---|---|
| JWT_SECRET | Environment variable | Manual |
| DATABASE_URL | Environment variable | Managed by Render |
| RENDER_DEPLOY_HOOK | GitHub Actions secret | Manual |

### 12.13.2 .gitignore

```
.env
.env.local
.env.*.local
*.db
*.sqlite
__pycache__/
*.pyc
node_modules/
dist/
build/
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.DS_Store
*.log
```

### 12.13.3 Git History

gitleaks scans the full git history. If a secret was ever committed,
it is flagged. The project starts with a clean history.

### 12.13.4 Environment Separation

| Environment | Database | JWT Secret | CORS |
|---|---|---|---|
| Local dev | SQLite | Dev default | localhost:5173 |
| Docker Compose | PostgreSQL | Dev default | localhost:5173 |
| Production | Render PostgreSQL | Generated by Render | Render URL |

## 12.14 Incident Response

### 12.14.1 Detection

| Event | Detection |
|---|---|
| Failed login spike | Application logs (`auth.login_failed`) |
| Cross-user access attempt | Not possible; returns 404 |
| Database unavailable | Health check (`fallback_active: true`) |
| Secret leak | gitleaks scan |
| Dependency vulnerability | pip-audit, npm audit, trivy |

### 12.14.2 Response Steps

| Step | Action |
|---|---|
| 1 | Identify the event from logs or alerts |
| 2 | Assess severity and scope |
| 3 | Contain: disable affected feature or rotate secret |
| 4 | Eradicate: fix the root cause |
| 5 | Recover: redeploy with the fix |
| 6 | Document: update `ops/diagnosis.md` |

### 12.14.3 Rollback

| Scenario | Action |
|---|---|
| Bad deployment | Render Dashboard → Deploys → Redeploy previous |
| Secret leaked | Rotate `JWT_SECRET`, redeploy |
| Database compromised | Not applicable (free tier expires) |
| Dependency vulnerability | Update dependency, redeploy |

## 12.15 Security Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Password hashing | bcrypt rounds=12 | Industry standard, slow enough |
| JWT algorithm | HS256 | Symmetric, simple, no key management |
| Token storage | localStorage | Simpler than cookies for SPA |
| Token expiry | 24 hours | Balance security and usability |
| No refresh token | MVP scope | Reduces complexity |
| Cross-user response | 404 not 403 | Does not reveal existence |
| Audit write | Same transaction | Atomicity guarantee |
| Audit access | No API | Reduces attack surface |
| Secrets | Environment variables | Never in code or git |
| Security scans | Local, committed | Per project decision |
| Agent auth | JWT | Same as backend |
| Agent data access | Via API | Single permission layer |
| Hooks | Pure functions | Testable, no side effects |
| Read-only agents | finance-analyst | Safety |
| AI data policy | Local only | Privacy, no cloud dependency |
| Known limitations | Documented | Transparency |
| Future improvements | Listed | Shows awareness |
```

---
