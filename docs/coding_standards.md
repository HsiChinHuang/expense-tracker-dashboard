# Coding Standards

All code MUST follow this standard. Violation = Verifier FAIL.

## General Principles

- All code, comments, and documentation MUST be in **English**.
- Use **snake_case** for files, variables, and functions.
- Use **PascalCase** for classes.
- Use **UPPER_SNAKE_CASE** for constants.
- Indentation: 2 spaces (TypeScript / YAML / JSON), 4 spaces (Python).
- Line length: max 100 characters.
- File encoding: UTF-8, no BOM.
- Line endings: LF.

## Python

### Toolchain

| Purpose | Command |
|---|---|
| Install deps | `uv sync` |
| Run tests | `uv run pytest` |
| Lint + fix | `ruff check --fix` |
| Lint JSON | `ruff check --output-format=json` |
| Type check | `uv run mypy .` |

### Naming

- Modules: `snake_case` (`user_model.py`)
- Classes: `PascalCase` (`UserModel`)
- Functions: `snake_case` (`get_user_by_email`)
- Constants: `UPPER_SNAKE_CASE` (`MAX_RETRY_COUNT`)
- Private: prefix `_` (`_internal_helper`)

### Style

- Follow PEP 8.
- Function docstrings in Google style.
- Type annotations MUST be complete.
- Avoid `*args` / `**kwargs` unless necessary.
- Exception handling MUST be specific. `except Exception` is forbidden.

### Testing

- At least 1 test per AC.
- Test file name: `test_<module>.py`.
- Test function name: `test_<action>_<expected>`.
- Group: `class Test<Module>`.
- Assertions MUST be meaningful. `assert True` is forbidden.

## TypeScript

### Toolchain

| Purpose | Command |
|---|---|
| Install deps | `npm install` |
| Compile | `tsc` |
| Run | `tsx <file>` |
| Lint | `eslint .` |
| Type check | `tsc --noEmit` |

### Naming

- Files: `snake_case` (`state_machine.ts`)
- Classes / Interfaces: `PascalCase` (`Handoff`, `IssueState`)
- Functions: `camelCase` (`validateTransition`)
- Constants: `UPPER_SNAKE_CASE` (`MAX_RETRIES`)
- Type aliases: `PascalCase`

### Style

- Use `const` / `let`. `var` is forbidden.
- Prefer arrow functions.
- Use `async` / `await`. Callbacks are forbidden.
- `any` is forbidden. Use `unknown` or explicit types.
- Imports use ES modules.

### Error Handling

- Use `try` / `catch`. Catch MUST handle or re-throw.
- Custom errors MUST extend `Error`.

## YAML

- Indentation: 2 spaces.
- Booleans: `true` / `false` only. `yes` / `no` are forbidden.
- Strings: no quotes unless containing special characters.
- Comments: `#` at start, followed by 1 space.

## JSON

- Indentation: 2 spaces.
- All keys use double quotes.
- Trailing commas are forbidden.
- Comments are forbidden (except `.jsonc`).

## Git

### Commit Message

Use Conventional Commits:

```
<type>(<scope>): <description>

<body>

<footer>
```

Types:

| Type | Purpose |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `test` | Add or modify tests |
| `refactor` | Refactor |
| `docs` | Documentation |
| `chore` | Chores |
| `merge` | Merge |
| `revert` | Revert |

Scope: issue ID, e.g. `t42`.

Example:

```
feat(t42): add signup with invite code

- Add POST /signup endpoint
- Add invite code validation
- Add tests for duplicate email

Closes: t42
```

### Branch

- Naming: `issue/<id>-<slug>`
- Merge conflict fix: `issue/MERGE-FIX-<id>-<slug>`
- Regression fix: `issue/REG-FIX-<id>-<slug>`

### Force Push

Force push to ANY branch is **forbidden**. Detection = BLOCKER.

## Forbidden Actions

| Forbidden | Reason |
|---|---|
| `sudo` / `su` | Privilege escalation |
| `rm -rf /` | System destruction |
| `git push --force` | History rewrite |
| `git push` to main | Bypass process |
| Read `~/.ssh/` | Secret |
| Read `.env` | Secret |
| `env` / `printenv` | Possible leak |
| `curl` / `wget` to non-Platform API | Data exfiltration |
| `dd` / `mkfs` / `fdisk` | Disk operations |
| `chmod 777 /` | Permission destruction |
## Security coding rules

Injection and escaping are prevented by construction, not by review
memory.

**SQL injection (REQ-SEC-042)**: all database access goes through the
SQLAlchemy 2.0 ORM with parameterized queries. No raw SQL string is
built in application code, and no user-supplied value is ever
concatenated into a statement; the services in
`backend/app/services/` compose `select()` expressions and bind
parameters. The Alembic migrations under `backend/alembic/versions/`
are the one place a literal SQL fragment is allowed, because they are
authored, reviewed, and versioned rather than assembled from input.

**XSS (REQ-SEC-043)**: React escapes interpolated text by default, so
the rule is to keep it that way - `dangerouslySetInnerHTML` is
forbidden in `frontend/src` and no third-party script tag is injected
into the document. The API returns plain data, never HTML, so there is
no trusted-HTML path that would justify an exception. A Content
Security Policy is not configured in the MVP; that gap is documented
here rather than claimed as done.

## Naming: files and directories

The per-language naming tables above cover identifiers. File and
directory naming (REQ-STRUCT-050, REQ-STRUCT-051) is:

| Surface | Rule | Example |
|---|---|---|
| React component file | `PascalCase.tsx` per the spec; merged code ships `snake_case.tsx` with a PascalCase exported symbol (disclosed deviation) | `budget_progress.tsx` exports `BudgetProgress` |
| Hook file | `camelCase.ts`/`.tsx` with a `use` prefix | `use_dashboard.ts` |
| TypeScript module | `camelCase.ts` per the spec; merged modules use `snake_case.ts` (disclosed deviation) | `chart_data.ts` |
| Backend test file | `test_<module>.py` | `test_budget_service.py` |
| Frontend test file | colocated `<source>.test.ts(x)` | `login_page.test.tsx` |
| Python package / module | `snake_case` | `backend/app/services/` |
| Feature directory | lowercase | `frontend/src/components/charts/` |
| Agent tool directory | `kebab-case` | `agent-hooks/validate-amount.py` |
| Docs subdirectory | lowercase, hyphen-free where possible | `docs/team/` |

Where the requirement's casing rule and the merged file names differ,
the table records both rather than pretending the code matches: the
requirement text is the spec, the file names are the measured state,
and a rename is a card of its own with the test-title greps it implies.
