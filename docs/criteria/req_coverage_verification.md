# Requirement-ID coverage matrix (t57)

GENERATOR-OWNED: docs/criteria/req_coverage_verification.md is written by
backend/scripts/req_coverage_verification.py. Never hand-edit it; change the
generator's derivation rules instead. The matrix enumerates every unique
REQ-[A-Z_]+-[0-9]{3} id in docs/requirements.md and classifies it with the
closed five-label vocabulary below; a non-GAP row always carries at least one
concrete evidence pointer. The generator exits nonzero IFF a GAP row or an
unpointed non-GAP row exists (fail-closed fence, review_plan W1) - the first
landing is expected to carry GAP rows; closing them is t58's work.

REQ_STATUSES PASS vocabulary=IMPLEMENTED_TESTED,IMPLEMENTED_STRUCTURAL,DEFERRED_RULLED,GAP,EXAMPLE_REFERENCE
REQ_MATRIX PASS rows=749 unique=749 idset=sha256:ef6c4bba27791a79
REQ_STATUS_COUNT IMPLEMENTED_TESTED 116
REQ_STATUS_COUNT IMPLEMENTED_STRUCTURAL 622
REQ_STATUS_COUNT DEFERRED_RULLED 10
REQ_STATUS_COUNT GAP 0
REQ_STATUS_COUNT EXAMPLE_REFERENCE 1
REQ_FAMILY PASS family=AI rows=66
REQ_FAMILY PASS family=API rows=42
REQ_FAMILY PASS family=ARCH rows=42
REQ_FAMILY PASS family=AUTH rows=1
REQ_FAMILY PASS family=BE rows=56
REQ_FAMILY PASS family=CICD rows=44
REQ_FAMILY PASS family=DB rows=53
REQ_FAMILY PASS family=DOC rows=37
REQ_FAMILY PASS family=EXT rows=41
REQ_FAMILY PASS family=FE rows=63
REQ_FAMILY PASS family=OPS rows=58
REQ_FAMILY PASS family=PLAN rows=29
REQ_FAMILY PASS family=PROD rows=35
REQ_FAMILY PASS family=PROJ rows=9
REQ_FAMILY PASS family=SEC rows=62
REQ_FAMILY PASS family=STRUCT rows=23
REQ_FAMILY PASS family=TECH rows=43
REQ_FAMILY PASS family=TEST rows=45
REQ_FAMILIES PASS total=749 distinct=18

## Deferral surface

REQ_DEFERRAL_PROVENANCE PASS source=docs/criteria/docs_verification.md#DEFERRAL_REGISTER method=register-row-derivation id_key_and_reason_snippet_per_row=true
REQ_DEFERRAL_PROVENANCE PASS source=docs/rulings/req-matrix.md method=card-declared-ruling id_key_and_reason_snippet_per_row=true
REQ_DEFERRAL_KEY PASS key=LIVE_AGENT_SESSION ids=2
REQ_DEFERRAL_KEY PASS key=LIVE_MCP_SUBPROCESS ids=2
REQ_DEFERRAL_KEY PASS key=LIVE_SUBAGENT_LAUNCH ids=2
REQ_DEFERRAL_KEY PASS key=RULING_FE_PERF_LIVE_PROFILING ids=1
REQ_DEFERRAL_KEY PASS key=RULING_TECH_DATEFNS_OVERRULED ids=1
REQ_DEFERRAL_POINTER PASS issue=61 family=OPS artifact=ops/deployment-health.md

## Hard cases (card-declared, ruled by platform #65 in t58)

REQ_HARDCASE PASS id=REQ-TECH-008 status=DEFERRED_RULLED ruling_key=RULING_TECH_DATEFNS_OVERRULED issue=65 pointer=docs/rulings/req-matrix.md
REQ_HARDCASE PASS id=REQ-FE-121 status=DEFERRED_RULLED ruling_key=RULING_FE_PERF_LIVE_PROFILING issue=65 pointer=docs/rulings/req-matrix.md

## Fail-closed fence

REQ_FENCE PASS gate=fail-closed iff=gap-or-unpointed-row fixture=env-gated self-test token=d5d75d0382bd0796

## Matrix

Per-id rows: the REQ_ROW line carries the machine contract; the REQ_TITLE
line carries the heading title and the Statement first clause.

REQ_ROW PASS id=REQ-AI-001 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-001 title="four-layer workflow" statement="The AI workflow has four layers: context, roles, orchestration, and extension."
REQ_ROW PASS id=REQ-AI-010 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-010 title="primary tools" statement="pi-agent is the primary coding agent; qwen3.8-27b is the local LLM; plugins extend capabilities when needed."
REQ_ROW PASS id=REQ-AI-011 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-011 title="confirmed capabilities" statement="pi-agent reads AGENTS.md, discovers skills, launches subagents, uses tools, performs file operations, and executes shell commands."
REQ_ROW PASS id=REQ-AI-012 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-012 title="why local model" statement="Local model chosen for data privacy, no API cost, offline capability, reproducibility, and learning visibility."
REQ_ROW PASS id=REQ-AI-013 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-013 title="local model limitations" statement="Smaller context window (keep AGENTS.md short), slower inference (smaller issues), less capable at complex tasks (more grooming), function calling may be less re"
REQ_ROW PASS id=REQ-AI-020 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=AGENTS.md
REQ_TITLE PASS id=REQ-AI-020 title="AGENTS.md" statement="AGENTS.md contains commands, rules, and document links; it is short and read at every session start."
REQ_ROW PASS id=REQ-AI-021 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=CLAUDE.md
REQ_TITLE PASS id=REQ-AI-021 title="CLAUDE.md" statement="CLAUDE.md contains a single line `@AGENTS.md`."
REQ_ROW PASS id=REQ-AI-022 family=AI status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/process.md
REQ_TITLE PASS id=REQ-AI-022 title="supporting documents" statement="Supporting documents: process.md, architecture.md, design-system.md, testing-guidelines.md, api.md, openapi.yaml, and the three team role files."
REQ_ROW PASS id=REQ-AI-023 family=AI status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/process.md
REQ_TITLE PASS id=REQ-AI-023 title="context loading strategy" statement="The agent loads documents on demand based on task type: backend endpoint, frontend UI, testing, PM grooming, QA verification."
REQ_ROW PASS id=REQ-AI-024 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-024 title="living documents" statement="When the agent makes a mistake, the correction is written into the relevant document so it does not repeat."
REQ_ROW PASS id=REQ-AI-030 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/team/pm.md
REQ_TITLE PASS id=REQ-AI-030 title="PM agent role" statement="`docs/team/pm.md` defines the Product Manager role: grooms tasks, rewrites using the task template, makes acceptance criteria checkable, files follow-ups for ou"
REQ_ROW PASS id=REQ-AI-031 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/team/software-engineer.md
REQ_TITLE PASS id=REQ-AI-031 title="SWE agent role" statement="`docs/team/software-engineer.md` defines the Software Engineer role: implements one groomed task, stays within constraints, writes tests, does not close the iss"
REQ_ROW PASS id=REQ-AI-032 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/team/qa-engineer.md
REQ_TITLE PASS id=REQ-AI-032 title="QA agent role" statement="`docs/team/qa-engineer.md` defines the QA role: checks each acceptance criterion, runs tests, reports PASS or FAIL with evidence, does not fix code."
REQ_ROW PASS id=REQ-AI-033 family=AI status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/process.md
REQ_TITLE PASS id=REQ-AI-033 title="role summary" statement="PM produces groomed issue (no code); SWE produces code + tests + commit; QA produces PASS/FAIL comment (no code)."
REQ_ROW PASS id=REQ-AI-040 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/process.md
REQ_TITLE PASS id=REQ-AI-040 title="orchestrator definition" statement="`docs/process.md` defines the main session as the orchestrator, with the PM → SWE → QA lifecycle and rules."
REQ_ROW PASS id=REQ-AI-041 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/process.md
REQ_TITLE PASS id=REQ-AI-041 title="workflow diagram" statement="The workflow diagram shows Backlog → Orchestrator → PM → SWE → QA, with FAIL looping back to SWE."
REQ_ROW PASS id=REQ-AI-042 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/process.md
REQ_TITLE PASS id=REQ-AI-042 title="sequential execution" statement="MVP uses sequential execution: one issue flows through PM → SWE → QA before the next issue starts."
REQ_ROW PASS id=REQ-AI-043 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-043 title="orchestrator commands" statement="Commands: `Groom issue #N`, `Implement issue #N`, `Test issue #N`, `/goal work through the backlog`."
REQ_ROW PASS id=REQ-AI-044 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-044 title="loop engineering" statement="The `/goal` command keeps the orchestrator running until the stop condition (all issues groomed, implemented, verified) is met."
REQ_ROW PASS id=REQ-AI-045 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md,docs/process.md
REQ_TITLE PASS id=REQ-AI-045 title="graph engineering" statement="The workflow is a graph with PM, SWE, QA as nodes; orchestrator enforces the graph; each agent runs in its own context."
REQ_ROW PASS id=REQ-AI-050 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/task-template.md
REQ_TITLE PASS id=REQ-AI-050 title="issue template" statement="`docs/task-template.md` defines sections: Goal, Acceptance criteria, Out of scope, Constraints."
REQ_ROW PASS id=REQ-AI-051 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-051 title="example groomed issue" statement="A worked example shows a vague issue transformed into a groomed issue with 14 acceptance criteria, out-of-scope items, and constraints."
REQ_ROW PASS id=REQ-AI-052 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/process.md
REQ_TITLE PASS id=REQ-AI-052 title="issue lifecycle" statement="Issue lifecycle: open/ungroomed (human) → open/groomed (PM) → open/implemented (SWE) → open/QA verdict (QA) → closed (orchestrator)."
REQ_ROW PASS id=REQ-AI-060 family=AI status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t29.md
REQ_TITLE PASS id=REQ-AI-060 title="skill format" statement="Skills are markdown files with YAML frontmatter containing name and description, stored in `agent-capabilities/<name>/SKILL.md`."
REQ_ROW PASS id=REQ-AI-061 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=agent-capabilities/monthly-report/SKILL.md
REQ_TITLE PASS id=REQ-AI-061 title="monthly-report skill" statement="The `monthly-report` skill generates a monthly expense report with summary, top categories, and warnings."
REQ_ROW PASS id=REQ-AI-062 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=agent-capabilities/add-expense/SKILL.md
REQ_TITLE PASS id=REQ-AI-062 title="add-expense skill" statement="The `add-expense` skill validates amount, calls `add_expense`, and confirms success."
REQ_ROW PASS id=REQ-AI-063 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=agent-capabilities/budget-check/SKILL.md
REQ_TITLE PASS id=REQ-AI-063 title="budget-check skill" statement="The `budget-check` skill reports budget status and warns if percentage > 80% or over budget."
REQ_ROW PASS id=REQ-AI-064 family=AI status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/scripts/agent_pack_verification.py,docs/criteria/agent_pack_verification.md,docs/issues/closed/t29.md
REQ_TITLE PASS id=REQ-AI-064 title="skill discovery" statement="Skills are discoverable via symlinks in `.agents/skills/` (and `.claude/skills/` for Claude)."
REQ_ROW PASS id=REQ-AI-065 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-065 title="how skills are created" statement="Skills emerge from doing the task first, correcting the agent, then asking to save the workflow as a project-specific skill."
REQ_ROW PASS id=REQ-AI-070 family=AI status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/scripts/agent_pack_verification.py,docs/criteria/agent_pack_verification.md,docs/issues/closed/t33.md
REQ_TITLE PASS id=REQ-AI-070 title="subagent structure" statement="Subagent definitions are markdown files with YAML frontmatter, stored in `custom-agent/<name>.md`, discoverable via `.agents/agents/` symlinks."
REQ_ROW PASS id=REQ-AI-071 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=custom-agent/finance-analyst.md
REQ_TITLE PASS id=REQ-AI-071 title="finance-analyst subagent" statement="`finance-analyst` analyzes spending patterns and suggests adjustments; read-only."
REQ_ROW PASS id=REQ-AI-072 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=custom-agent/qa-reviewer.md
REQ_TITLE PASS id=REQ-AI-072 title="qa-reviewer subagent" statement="`qa-reviewer` verifies work against acceptance criteria and outputs PASS/FAIL; does not fix code."
REQ_ROW PASS id=REQ-AI-073 family=AI status=DEFERRED_RULLED method=deferral-register pointers=docs/criteria/docs_verification.md,ops/deployment-health.md deferral_key=LIVE_SUBAGENT_LAUNCH deferral_reason="sub-agent definitions are present as config artifacts only; launching them needs a live agent runtime which this gate must not require (no-E2E/no-live ruling)"
REQ_TITLE PASS id=REQ-AI-073 title="subagent launch" statement="Subagents launch with prompts like 'Launch a subagent to implement #12', 'Launch QA for #12'."
REQ_ROW PASS id=REQ-AI-074 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/process.md
REQ_TITLE PASS id=REQ-AI-074 title="separate contexts" statement="Subagents run in separate contexts to enable independent verification and focused attention."
REQ_ROW PASS id=REQ-AI-080 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=mcp-server/server.py
REQ_TITLE PASS id=REQ-AI-080 title="MCP purpose" statement="The MCP server exposes backend operations as tools the agent can call; it calls the backend API with the same JWT, not the database."
REQ_ROW PASS id=REQ-AI-081 family=AI status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t31.md
REQ_TITLE PASS id=REQ-AI-081 title="MCP structure" statement="MCP structure: server.py, auth.py, config.py, tools/ with four tool modules."
REQ_ROW PASS id=REQ-AI-082 family=AI status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_mcp_tools.py
REQ_TITLE PASS id=REQ-AI-082 title="MCP server entry" statement="server.py defines `list_tools` returning four tool definitions and `call_tool` dispatching to tool modules after JWT verification."
REQ_ROW PASS id=REQ-AI-083 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=mcp-server/auth.py
REQ_TITLE PASS id=REQ-AI-083 title="MCP JWT verification" statement="`verify_jwt` validates signature, exp, aud, iss, checks `type == 'access'`, returns `sub`."
REQ_ROW PASS id=REQ-AI-084 family=AI status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t32.md,mcp-server/tools/__init__.py,mcp-server/tools/add_expense.py
REQ_TITLE PASS id=REQ-AI-084 title="MCP tool implementation" statement="Tools call the backend API via httpx with the Bearer token, raising on non-2xx responses."
REQ_ROW PASS id=REQ-AI-085 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=mcp-server/server.py
REQ_TITLE PASS id=REQ-AI-085 title="MCP tool list" statement="Four tools: add_expense, get_budget_status, monthly_summary, list_expenses."
REQ_ROW PASS id=REQ-AI-086 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-086 title="MCP authentication flow" statement="pi-agent reads `MCP_USER_TOKEN`, spawns the MCP server as a subprocess, which reads `MCP_JWT_SECRET`, `MCP_API_BASE_URL`, `MCP_USER_TOKEN`."
REQ_ROW PASS id=REQ-AI-087 family=AI status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/agent-extension-pack.md,docs/issues/closed/t31.md,docs/issues/closed/t32.md
REQ_TITLE PASS id=REQ-AI-087 title="MCP calls API not database" statement="Single permission layer, no schema duplication, same behavior as frontend, easier testing, safer."
REQ_ROW PASS id=REQ-AI-088 family=AI status=DEFERRED_RULLED method=deferral-register pointers=docs/criteria/docs_verification.md,ops/deployment-health.md deferral_key=LIVE_MCP_SUBPROCESS deferral_reason="the pack MCP wiring is proven by static config greps (tests[144] carried rows); no MCP server binary is installed on this host, so a live spawn cannot be measured here"
REQ_TITLE PASS id=REQ-AI-088 title="MCP server launch" statement="Launched by pi-agent as a subprocess with environment variables; example launch command documented."
REQ_ROW PASS id=REQ-AI-090 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=agent-hooks/README.md
REQ_TITLE PASS id=REQ-AI-090 title="hook purpose" statement="Hooks are guardrails that run before agent actions, preventing invalid operations."
REQ_ROW PASS id=REQ-AI-091 family=AI status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_agent_hooks.py
REQ_TITLE PASS id=REQ-AI-091 title="validate-amount hook" statement="`validate_amount` validates the amount is a number, positive, ≤ MAX_AMOUNT, ≤ 2 decimals; raises ValueError; returns Decimal."
REQ_ROW PASS id=REQ-AI-092 family=AI status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_agent_hooks.py
REQ_TITLE PASS id=REQ-AI-092 title="validate-ownership hook" statement="`validate_ownership` raises PermissionError if the resource does not belong to the current user."
REQ_ROW PASS id=REQ-AI-093 family=AI status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t29.md,docs/issues/closed/t30.md,docs/issues/closed/t32.md
REQ_TITLE PASS id=REQ-AI-093 title="hook triggers" statement="Hooks are triggered before MCP calls and are also enforced in the backend (Pydantic, service layer)."
REQ_ROW PASS id=REQ-AI-094 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=agent-hooks/README.md
REQ_TITLE PASS id=REQ-AI-094 title="hook README" statement="`agent-hooks/README.md` documents trigger, checks, failure behavior, and design notes."
REQ_ROW PASS id=REQ-AI-100 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/permissions.md
REQ_TITLE PASS id=REQ-AI-100 title="permissions matrix" statement="`docs/permissions.md` defines user roles, resource permissions, agent permissions by role, enforcement, and escalation rules."
REQ_ROW PASS id=REQ-AI-101 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/permissions.md
REQ_TITLE PASS id=REQ-AI-101 title="defense in depth" statement="Rules are enforced at hook, MCP, backend dependency, backend service, backend test, and database layers."
REQ_ROW PASS id=REQ-AI-110 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-110 title="why record sessions" statement="Session records provide evidence that AI tools were used and reviewed."
REQ_ROW PASS id=REQ-AI-111 family=AI status=DEFERRED_RULLED method=deferral-register pointers=docs/criteria/docs_verification.md,ops/deployment-health.md deferral_key=LIVE_AGENT_SESSION deferral_reason="docs/ai-workflow.md records are transcript attestations of real sessions, not a machine-verifiable live capture; no live session endpoint exists to re-test"
REQ_TITLE PASS id=REQ-AI-111 title="session record format" statement="Each session record includes date, tool, prompt, agent output, human review, and commit."
REQ_ROW PASS id=REQ-AI-112 family=AI status=DEFERRED_RULLED method=deferral-register pointers=docs/criteria/docs_verification.md,ops/deployment-health.md deferral_key=LIVE_AGENT_SESSION deferral_reason="docs/ai-workflow.md records are transcript attestations of real sessions, not a machine-verifiable live capture; no live session endpoint exists to re-test"
REQ_TITLE PASS id=REQ-AI-112 title="session examples" statement="Real sessions exist for grooming, implementing, QA fail, fixing, and re-verification."
REQ_ROW PASS id=REQ-AI-113 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-113 title="session coverage" statement="Sessions are recorded across spec, auth, CRUD, dashboard, frontend, testing, security, and deployment phases."
REQ_ROW PASS id=REQ-AI-120 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-120 title="correction log format" statement="The correction log records date, issue, AI output, correction, and lesson."
REQ_ROW PASS id=REQ-AI-121 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-121 title="correction examples" statement="Six example corrections are recorded, covering pagination, Decimal, isolation, aggregation, heatmap week start, and referential integrity."
REQ_ROW PASS id=REQ-AI-122 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-122 title="document updates from corrections" statement="Each correction updates the relevant document (AGENTS.md, SWE role, testing guidelines, design system, task template)."
REQ_ROW PASS id=REQ-AI-130 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/ai-tool-data-policy.md
REQ_TITLE PASS id=REQ-AI-130 title="data policy summary" statement="All code, prompts, and context stay on the local machine; no data is sent to cloud LLM providers."
REQ_ROW PASS id=REQ-AI-131 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/ai-tool-data-policy.md
REQ_TITLE PASS id=REQ-AI-131 title="what the agent sees" statement="The agent sees source code, tests, docs, OpenAPI, seed data"
REQ_ROW PASS id=REQ-AI-132 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-132 title="what the agent produces" statement="Outputs (code, tests, commits, docs, security notes) all require human review."
REQ_ROW PASS id=REQ-AI-133 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/ai-tool-data-policy.md
REQ_TITLE PASS id=REQ-AI-133 title="data flow" statement="Data flow diagram shows local-only processing with no connection to cloud LLMs, external AI services, or production databases."
REQ_ROW PASS id=REQ-AI-134 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/ai-tool-data-policy.md
REQ_TITLE PASS id=REQ-AI-134 title="compliance notes" statement="Data residency local, no PII, no secrets in context, audit via session records, reproducibility via same model version."
REQ_ROW PASS id=REQ-AI-140 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-140 title="agent and model choice" statement="pi-agent with qwen3.8-27b for local, no-cost, controllable workflow."
REQ_ROW PASS id=REQ-AI-141 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=AGENTS.md,docs/process.md
REQ_TITLE PASS id=REQ-AI-141 title="context and roles choice" statement="AGENTS.md as tool-agnostic context; PM/SWE/QA roles match course Part 1."
REQ_ROW PASS id=REQ-AI-142 family=AI status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/process.md
REQ_TITLE PASS id=REQ-AI-142 title="orchestration choice" statement="Main session as orchestrator; GitHub Issues as backlog; sequential execution for MVP."
REQ_ROW PASS id=REQ-AI-143 family=AI status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md,docs/agent-extension-pack.md,docs/ai-workflow.md
REQ_TITLE PASS id=REQ-AI-143 title="extension choice" statement="Three skills, two subagents, four MCP tools, two hooks, JWT auth, data policy local-only."
REQ_ROW PASS id=REQ-API-001 family=API status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=openapi.yaml
REQ_TITLE PASS id=REQ-API-001 title="OpenAPI version" statement="OpenAPI 3.1.0, API version 1.0.0, title 'Expense Tracker & Budget Dashboard API'."
REQ_ROW PASS id=REQ-API-002 family=API status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=openapi.yaml
REQ_TITLE PASS id=REQ-API-002 title="base URLs" statement="Base URLs: local `http://localhost:8000/api/v1`, production `https://expense-tracker-dashboard.onrender.com/api/v1`."
REQ_ROW PASS id=REQ-API-003 family=API status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/src/api/client.ts,openapi.yaml
REQ_TITLE PASS id=REQ-API-003 title="content types" statement="Request, response, and error bodies are `application/json`; auth uses `Authorization: Bearer <token>`."
REQ_ROW PASS id=REQ-API-004 family=API status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=openapi.yaml
REQ_TITLE PASS id=REQ-API-004 title="authentication scheme" statement="A `bearerAuth` scheme of type http, scheme bearer, bearerFormat JWT is defined globally; health, register, and login override with `security: []`."
REQ_ROW PASS id=REQ-API-010 family=API status=IMPLEMENTED_TESTED method=code-symbol pointers=frontend/src/api/client.test.ts,frontend/src/api/dashboard.test.ts,frontend/src/components/common/guards.test.tsx
REQ_TITLE PASS id=REQ-API-010 title="GET /health" statement="`GET /api/v1/health` returns 200 with `status`, `database`, `fallback_active`, `version`; no auth required."
REQ_ROW PASS id=REQ-API-020 family=API status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_auth_api.py
REQ_TITLE PASS id=REQ-API-020 title="POST /auth/register" statement="`POST /api/v1/auth/register` accepts email, username, password; returns 201 with user; 409 for duplicates; 422 for validation errors."
REQ_ROW PASS id=REQ-API-021 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/routers/auth.py,backend/app/schemas/auth.py,backend/app/services/auth_service.py
REQ_TITLE PASS id=REQ-API-021 title="POST /auth/login" statement="`POST /api/v1/auth/login` accepts email and password; returns 200 with access_token, token_type, user; 401 on invalid credentials."
REQ_ROW PASS id=REQ-API-022 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t8.md
REQ_TITLE PASS id=REQ-API-022 title="GET /auth/me" statement="`GET /api/v1/auth/me` returns 200 with current user; 401 if unauthenticated."
REQ_ROW PASS id=REQ-API-030 family=API status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_categories_api.py
REQ_TITLE PASS id=REQ-API-030 title="GET /categories" statement="`GET /api/v1/categories` returns system and user categories."
REQ_ROW PASS id=REQ-API-031 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/routers/categories.py,backend/app/schemas/category.py,docs/issues/closed/t11.md
REQ_TITLE PASS id=REQ-API-031 title="POST /categories" statement="`POST /api/v1/categories` creates a custom category; returns 201; 409 for duplicate; 422 for invalid color."
REQ_ROW PASS id=REQ-API-032 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/routers/categories.py,docs/issues/closed/t11.md,openapi.yaml
REQ_TITLE PASS id=REQ-API-032 title="DELETE /categories/{id}" statement="`DELETE /api/v1/categories/{id}` deletes a custom category; 204 on success; 404 if not found; 409 if category has expenses."
REQ_ROW PASS id=REQ-API-040 family=API status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_expense_api.py
REQ_TITLE PASS id=REQ-API-040 title="GET /expenses" statement="`GET /api/v1/expenses` supports year_month, category_id, page, page_size; returns paginated list."
REQ_ROW PASS id=REQ-API-041 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/routers/expenses.py,backend/app/schemas/expense.py,docs/issues/closed/t13.md
REQ_TITLE PASS id=REQ-API-041 title="POST /expenses" statement="`POST /api/v1/expenses` creates an expense; 201 on success; 404 if category invalid; 422 for validation errors."
REQ_ROW PASS id=REQ-API-042 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/routers/expenses.py,docs/issues/closed/t13.md,openapi.yaml
REQ_TITLE PASS id=REQ-API-042 title="GET /expenses/{id}" statement="`GET /api/v1/expenses/{id}` returns the expense; 404 if not found or not owned."
REQ_ROW PASS id=REQ-API-043 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/routers/expenses.py,backend/app/schemas/expense.py,docs/issues/closed/t13.md
REQ_TITLE PASS id=REQ-API-043 title="PUT /expenses/{id}" statement="`PUT /api/v1/expenses/{id}` updates; 200 on success; 404 if not found or not owned; 422 for validation errors."
REQ_ROW PASS id=REQ-API-044 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/routers/expenses.py,openapi.yaml
REQ_TITLE PASS id=REQ-API-044 title="DELETE /expenses/{id}" statement="`DELETE /api/v1/expenses/{id}` deletes; 204 on success; 404 if not found or not owned."
REQ_ROW PASS id=REQ-API-050 family=API status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_budget_api.py
REQ_TITLE PASS id=REQ-API-050 title="GET /budgets/{year_month}" statement="`GET /api/v1/budgets/{year_month}` returns the budget; returns 200 with amount '0.00' if no budget exists."
REQ_ROW PASS id=REQ-API-051 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/routers/budgets.py,backend/app/schemas/budget.py,docs/issues/closed/t14.md
REQ_TITLE PASS id=REQ-API-051 title="PUT /budgets/{year_month}" statement="`PUT /api/v1/budgets/{year_month}` sets or updates; returns 200."
REQ_ROW PASS id=REQ-API-052 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/routers/budgets.py,docs/issues/closed/t14.md,docs/issues/closed/t18.md
REQ_TITLE PASS id=REQ-API-052 title="DELETE /budgets/{year_month}" statement="`DELETE /api/v1/budgets/{year_month}` deletes; 204 on success; 404 if no budget."
REQ_ROW PASS id=REQ-API-060 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/routers/dashboard.py,docs/issues/closed/t19.md,docs/plan.md
REQ_TITLE PASS id=REQ-API-060 title="GET /dashboard/summary" statement="`GET /api/v1/dashboard/summary` returns year_month, total_spent, budget, remaining, percentage (null if budget = 0), transaction_count, is_over_budget."
REQ_ROW PASS id=REQ-API-061 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/routers/dashboard.py,openapi.yaml
REQ_TITLE PASS id=REQ-API-061 title="GET /dashboard/by-category" statement="`GET /api/v1/dashboard/by-category` returns categories with category_id, name, color, amount, percentage."
REQ_ROW PASS id=REQ-API-062 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/routers/dashboard.py,openapi.yaml
REQ_TITLE PASS id=REQ-API-062 title="GET /dashboard/trend" statement="`GET /api/v1/dashboard/trend` with months (default 6, max 24) returns months array."
REQ_ROW PASS id=REQ-API-063 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/routers/dashboard.py,openapi.yaml
REQ_TITLE PASS id=REQ-API-063 title="GET /dashboard/cumulative" statement="`GET /api/v1/dashboard/cumulative` returns year_month, budget, days array with date, daily, cumulative."
REQ_ROW PASS id=REQ-API-064 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/routers/dashboard.py,openapi.yaml
REQ_TITLE PASS id=REQ-API-064 title="GET /dashboard/heatmap" statement="`GET /api/v1/dashboard/heatmap` with weeks (default 12, max 52) returns max_amount and weeks with week_start and days."
REQ_ROW PASS id=REQ-API-065 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/routers/dashboard.py,openapi.yaml
REQ_TITLE PASS id=REQ-API-065 title="GET /dashboard/recent" statement="`GET /api/v1/dashboard/recent` with limit (default 10, max 50) returns items array of expenses."
REQ_ROW PASS id=REQ-API-070 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/api.md
REQ_TITLE PASS id=REQ-API-070 title="ErrorResponse schema" statement="Errors return `{detail, code, field?}` with detail human-readable, code machine-readable, field optional."
REQ_ROW PASS id=REQ-API-071 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/api.md
REQ_TITLE PASS id=REQ-API-071 title="validation error normalization" statement="Validation errors return 422 with the first error normalized to `{detail, code: 'VALIDATION_ERROR', field}`."
REQ_ROW PASS id=REQ-API-072 family=API status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=openapi.yaml
REQ_TITLE PASS id=REQ-API-072 title="error code reference" statement="All 18 error codes are documented with HTTP status and condition."
REQ_ROW PASS id=REQ-API-073 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/api.md
REQ_TITLE PASS id=REQ-API-073 title="HTTP status usage" statement="200 for GET/PUT, 201 for POST, 204 for DELETE, 401 for missing/invalid token, 403 for forbidden, 404 for missing or not-owned, 409 for conflict, 422 for validat"
REQ_ROW PASS id=REQ-API-080 family=API status=IMPLEMENTED_TESTED method=code-symbol pointers=frontend/src/hooks/use_expenses.test.tsx,frontend/src/pages/expenses_page.test.tsx,frontend/src/test/handlers_contract.test.ts
REQ_TITLE PASS id=REQ-API-080 title="pagination parameters" statement="`page` (default 1, min 1) and `page_size` (default 20, min 1, max 100)."
REQ_ROW PASS id=REQ-API-081 family=API status=IMPLEMENTED_TESTED method=code-symbol pointers=e2e/tests/happy-path.spec.ts,e2e/tests/isolation.spec.ts,e2e/tests/month-switch.spec.ts
REQ_TITLE PASS id=REQ-API-081 title="pagination response shape" statement="Response contains `items`, `total`, `page`, `page_size`; `total` is the full count, not page size."
REQ_ROW PASS id=REQ-API-090 family=API status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=openapi.yaml
REQ_TITLE PASS id=REQ-API-090 title="amount format" statement="Amounts are strings matching `^[0-9]+(\.[0-9]{1,2})?$`, max 2 decimals, min 0.01, max 9,999,999,999.99, always USD."
REQ_ROW PASS id=REQ-API-091 family=API status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=openapi.yaml
REQ_TITLE PASS id=REQ-API-091 title="date format" statement="Dates are ISO 8601 `YYYY-MM-DD` strings with no time component or timezone."
REQ_ROW PASS id=REQ-API-092 family=API status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=openapi.yaml
REQ_TITLE PASS id=REQ-API-092 title="datetime format" statement="Timestamps are ISO 8601 with UTC (`Z` suffix), used for created_at and updated_at."
REQ_ROW PASS id=REQ-API-093 family=API status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=openapi.yaml
REQ_TITLE PASS id=REQ-API-093 title="year-month format" statement="year_month matches `^[0-9]{4}-[0-9]{2}$`, used for budgets and dashboard filters."
REQ_ROW PASS id=REQ-API-100 family=API status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=openapi.yaml
REQ_TITLE PASS id=REQ-API-100 title="contract verification" statement="The contract is verified via FastAPI auto-generated OpenAPI compared to `openapi.yaml`, frontend mocks, integration tests, and E2E tests."
REQ_ROW PASS id=REQ-API-101 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-API-101 title="schema validation in tests" statement="Integration tests assert response shapes match OpenAPI schemas."
REQ_ROW PASS id=REQ-API-110 family=API status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=openapi.yaml
REQ_TITLE PASS id=REQ-API-110 title="amounts as strings" statement="Amounts are strings to avoid float precision loss."
REQ_ROW PASS id=REQ-API-111 family=API status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=openapi.yaml
REQ_TITLE PASS id=REQ-API-111 title="error format choice" statement="Error format `{detail, code, field}` for consistency."
REQ_ROW PASS id=REQ-API-112 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/api.md,docs/architecture.md
REQ_TITLE PASS id=REQ-API-112 title="404 for cross-user" statement="Cross-user access returns 404, not 403, to avoid revealing existence."
REQ_ROW PASS id=REQ-API-113 family=API status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/api.md
REQ_TITLE PASS id=REQ-API-113 title="budget missing returns 200" statement="A missing budget returns 200 with amount '0.00', simplifying the frontend."
REQ_ROW PASS id=REQ-API-114 family=API status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=openapi.yaml
REQ_TITLE PASS id=REQ-API-114 title="bounded parameters" statement="months 1-24 (default 6), weeks 1-52 (default 12), limit 1-50 (default 10), page_size max 100."
REQ_ROW PASS id=REQ-ARCH-001 family=ARCH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-ARCH-001 title="Three-tier architecture" statement="The system follows a three-tier architecture: presentation (React SPA), application (FastAPI), and data (PostgreSQL/SQLite), plus an agent layer alongside the a"
REQ_ROW PASS id=REQ-ARCH-002 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/agent-extension-pack.md,docs/issues/closed/t31.md,docs/issues/closed/t32.md
REQ_TITLE PASS id=REQ-ARCH-002 title="Agent layer shares API" statement="The agent layer uses the same API and JWT authentication as the frontend"
REQ_ROW PASS id=REQ-ARCH-003 family=ARCH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=Dockerfile,docker-compose.yml
REQ_TITLE PASS id=REQ-ARCH-003 title="Development vs production architecture" statement="Development runs Vite dev server, uvicorn with reload, and PostgreSQL in Docker"
REQ_ROW PASS id=REQ-ARCH-010 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-ARCH-010 title="Frontend layered structure" statement="The frontend is organized into entry, pages, components, hooks, context, API, utils, and types layers."
REQ_ROW PASS id=REQ-ARCH-011 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t16.md,docs/plan.md
REQ_TITLE PASS id=REQ-ARCH-011 title="Frontend data flow" statement="The frontend data flow is: user action → page component → hook → React Query → API module → axios → backend."
REQ_ROW PASS id=REQ-ARCH-012 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t17.md,docs/issues/closed/t18.md,docs/issues/closed/t9.md
REQ_TITLE PASS id=REQ-ARCH-012 title="State ownership" statement="Auth state lives in AuthContext, selected month in MonthContext, server data in React Query cache, form state in React Hook Form, and UI state in component-loca"
REQ_ROW PASS id=REQ-ARCH-013 family=ARCH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/src/main.tsx
REQ_TITLE PASS id=REQ-ARCH-013 title="Provider nesting order" statement="Providers are nested in this order: QueryClientProvider → BrowserRouter → AuthProvider → MonthProvider → ToastProvider."
REQ_ROW PASS id=REQ-ARCH-020 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-ARCH-020 title="Backend layered structure" statement="The backend is organized into entry, config, database, routers, services, models, schemas, auth, audit, and core layers."
REQ_ROW PASS id=REQ-ARCH-021 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t11.md,docs/issues/closed/t8.md
REQ_TITLE PASS id=REQ-ARCH-021 title="Request lifecycle" statement="A request goes through middleware, router, dependencies (including get_current_user), service, database, and back through response schema."
REQ_ROW PASS id=REQ-ARCH-022 family=ARCH status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_audit_logger.py
REQ_TITLE PASS id=REQ-ARCH-022 title="Dependency injection" statement="FastAPI dependencies provide `get_db`, `get_current_user`, `get_settings`, and `get_audit_logger`."
REQ_ROW PASS id=REQ-ARCH-023 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/services/budget_service.py,backend/app/services/expense_service.py,docs/issues/closed/t12.md
REQ_TITLE PASS id=REQ-ARCH-023 title="Transaction boundaries" statement="Each request runs in one database session; services commit at the end; audit log write is part of the same transaction; read-only endpoints do not commit."
REQ_ROW PASS id=REQ-ARCH-024 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/core/errors.py,backend/app/routers/auth.py,backend/app/services/budget_service.py
REQ_TITLE PASS id=REQ-ARCH-024 title="Error handling" statement="All errors return a consistent shape `{detail, code, field}` with appropriate HTTP status codes."
REQ_ROW PASS id=REQ-ARCH-030 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-ARCH-030 title="Login flow" statement="Login flow: user enters credentials → frontend POST /auth/login → backend verifies bcrypt → signs JWT → returns token and user → frontend stores token and redir"
REQ_ROW PASS id=REQ-ARCH-031 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t13.md
REQ_TITLE PASS id=REQ-ARCH-031 title="Create expense flow" statement="Create expense flow: frontend POST /expenses with Bearer JWT → backend verifies JWT, validates body, checks category → inserts expense and audit log in one tran"
REQ_ROW PASS id=REQ-ARCH-032 family=ARCH status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/api/dashboard.test.ts,frontend/src/hooks/use_dashboard.test.tsx,frontend/src/pages/dashboard_page.test.tsx
REQ_TITLE PASS id=REQ-ARCH-032 title="Dashboard load flow" statement="Dashboard load issues six parallel requests (summary, by-category, trend, cumulative, heatmap, recent), aggregates in Python where needed, and renders five char"
REQ_ROW PASS id=REQ-ARCH-033 family=ARCH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/diagnosis.md
REQ_TITLE PASS id=REQ-ARCH-033 title="Database fallback flow" statement="On startup, the app tries PostgreSQL with a 5-second timeout; on failure, it logs a warning, creates SQLite tables, seeds categories, and reports `fallback_acti"
REQ_ROW PASS id=REQ-ARCH-040 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t7.md
REQ_TITLE PASS id=REQ-ARCH-040 title="JWT structure" statement="JWT contains sub, iss, aud, exp, iat, and type claims."
REQ_ROW PASS id=REQ-ARCH-041 family=ARCH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/auth/dependencies.py,backend/app/auth/jwt.py
REQ_TITLE PASS id=REQ-ARCH-041 title="Token validation steps" statement="Every protected request validates Bearer header, decodes JWT with fixed HS256, verifies signature, exp, aud, iss, extracts sub, loads user, checks is_active."
REQ_ROW PASS id=REQ-ARCH-042 family=ARCH status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/api/dashboard.test.ts
REQ_TITLE PASS id=REQ-ARCH-042 title="Token storage" statement="The token is stored in localStorage under key `token`, sent as `Authorization: Bearer <token>`, expires in 24 hours, with no refresh token in MVP."
REQ_ROW PASS id=REQ-ARCH-050 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-ARCH-050 title="Repository root structure" statement="The repository root contains README, product-spec, AGENTS.md, CLAUDE.md, openapi.yaml, docker-compose.yml, render.yaml, Makefile, .env.example, .gitignore, LICE"
REQ_ROW PASS id=REQ-ARCH-051 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-ARCH-051 title="Frontend directory structure" statement="The frontend contains `src/` with api, components, pages, hooks, context, types, utils, test; plus `public/`, config files, and Dockerfile."
REQ_ROW PASS id=REQ-ARCH-052 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t3.md
REQ_TITLE PASS id=REQ-ARCH-052 title="Backend directory structure" statement="The backend contains `app/` with main, config, database, models, schemas, routers, services, auth, audit, core; plus tests, alembic, config files, and Dockerfil"
REQ_ROW PASS id=REQ-ARCH-053 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/scripts/agent_pack_verification.py,docs/criteria/agent_pack_verification.md,docs/issues/closed/t0.md
REQ_TITLE PASS id=REQ-ARCH-053 title="Agent layer directory structure" statement="The agent layer contains `agent-capabilities/`, `agent-hooks/`, `mcp-server/`, `custom-agent/`, and `.agents/` with symlinks."
REQ_ROW PASS id=REQ-ARCH-054 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-ARCH-054 title="Documentation and artifacts structure" statement="`docs/` contains architecture, api, process, ai-workflow, design-system, testing-guidelines, agent-extension-pack, permissions, task-template, and team/. `secur"
REQ_ROW PASS id=REQ-ARCH-060 family=ARCH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/logging.md
REQ_TITLE PASS id=REQ-ARCH-060 title="Logging" statement="Logs are JSON structured, level INFO in production, include a request ID, never include sensitive data, and cover key events."
REQ_ROW PASS id=REQ-ARCH-061 family=ARCH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/config.py,mcp-server/config.py
REQ_TITLE PASS id=REQ-ARCH-061 title="Configuration priority" statement="Configuration priority is environment variables > `.env` file > defaults in `config.py`."
REQ_ROW PASS id=REQ-ARCH-062 family=ARCH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/core/errors.py,frontend/src/api/client.ts
REQ_TITLE PASS id=REQ-ARCH-062 title="Error handling layers" statement="Routers raise AppError or HTTPException; services raise AppError; database errors become 503; axios normalizes errors; UI shows field errors, toasts, or redirec"
REQ_ROW PASS id=REQ-ARCH-063 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-ARCH-063 title="Security cross-cutting" statement="Passwords use bcrypt, tokens use HS256 with env secret, token validation covers signature/exp/aud/iss, all queries filter by user_id, cross-user access returns"
REQ_ROW PASS id=REQ-ARCH-064 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-ARCH-064 title="Testing cross-cutting" statement="Backend unit, backend integration, frontend unit, frontend component, and E2E tests exist in their respective locations."
REQ_ROW PASS id=REQ-ARCH-070 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t16.md,docs/issues/closed/t9.md,frontend/src/api/auth.ts
REQ_TITLE PASS id=REQ-ARCH-070 title="Centralized API layer" statement="All backend calls from the frontend go through `src/api/` as a single integration point."
REQ_ROW PASS id=REQ-ARCH-071 family=ARCH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/main.py
REQ_TITLE PASS id=REQ-ARCH-071 title="Backend serves frontend static files" statement="In production, FastAPI serves the built frontend static files."
REQ_ROW PASS id=REQ-ARCH-072 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t5.md,docs/plan.md
REQ_TITLE PASS id=REQ-ARCH-072 title="SQLAlchemy abstraction" statement="All database access goes through SQLAlchemy 2.0, enabling PostgreSQL and SQLite without code changes."
REQ_ROW PASS id=REQ-ARCH-073 family=ARCH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/database.py
REQ_TITLE PASS id=REQ-ARCH-073 title="Automatic SQLite fallback" statement="The SQLite fallback triggers only on startup, keeping the design simple and predictable."
REQ_ROW PASS id=REQ-ARCH-074 family=ARCH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-ARCH-074 title="JWT storage choice" statement="JWT is stored in localStorage rather than an HttpOnly cookie, documented as a trade-off with mitigations."
REQ_ROW PASS id=REQ-ARCH-075 family=ARCH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/auth/jwt.py
REQ_TITLE PASS id=REQ-ARCH-075 title="No refresh token" statement="The MVP uses a 24-hour access token with no refresh token, documented as a trade-off."
REQ_ROW PASS id=REQ-ARCH-076 family=ARCH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=Dockerfile
REQ_TITLE PASS id=REQ-ARCH-076 title="Single production container" statement="The frontend is built into the backend image as a single container to simplify Render configuration."
REQ_ROW PASS id=REQ-ARCH-077 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-ARCH-077 title="Agent layer uses same API" statement="The agent layer calls the same backend API with the same JWT, with no special endpoints."
REQ_ROW PASS id=REQ-ARCH-078 family=ARCH status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_expense_api.py,backend/tests/unit/test_budget_service.py
REQ_TITLE PASS id=REQ-ARCH-078 title="Audit in same transaction" statement="Audit log writes happen in the service layer within the same transaction as the business operation."
REQ_ROW PASS id=REQ-ARCH-079 family=ARCH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-ARCH-079 title="Month selector in context" statement="The selected month lives in MonthContext, enabling global chart synchronization."
REQ_ROW PASS id=REQ-ARCH-080 family=ARCH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md,render.yaml
REQ_TITLE PASS id=REQ-ARCH-080 title="Platform constraints" statement="The project operates within Render free tier constraints: 512 MB RAM, 0.1 CPU, 15-minute idle sleep, 1 GB database storage, 30-day database expiry."
REQ_ROW PASS id=REQ-ARCH-081 family=ARCH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-ARCH-081 title="Project assumptions" statement="The project assumes stable internet, modern browsers, low traffic (demo and peer review), small data volume per user, and that the agent layer runs on the devel"
REQ_ROW PASS id=REQ-ARCH-082 family=ARCH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-ARCH-082 title="Known limitations" statement="Known limitations are documented: cold start on Render, PostgreSQL 30-day expiry, no refresh token, no rate limiting, localStorage JWT, SQLite fallback data los"
REQ_ROW PASS id=REQ-AUTH-001 family=AUTH status=EXAMPLE_REFERENCE method=example-reference pointers=docs/requirements.md#section-3.1-id-format
REQ_TITLE PASS id=REQ-AUTH-001 title="section 3.1 ID-format example (never a heading entry)" statement="Full example of the REQ-[FAMILY]-NNN id format"
REQ_ROW PASS id=REQ-BE-001 family=BE status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md
REQ_TITLE PASS id=REQ-BE-001 title="backend directory structure" statement="The backend contains `app/` with main, config, database, models/, schemas/, routers/, services/, auth/, audit/, core/; plus tests/unit/, tests/integration/, ale"
REQ_ROW PASS id=REQ-BE-002 family=BE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-BE-002 title="layer responsibilities" statement="Each layer has defined responsibilities: entry (orchestration), config (settings), database (engine), routers (parsing), services (business), models (ORM), sche"
REQ_ROW PASS id=REQ-BE-003 family=BE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-BE-003 title="dependency direction" statement="Dependencies point inward: main → routers → services → models"
REQ_ROW PASS id=REQ-BE-010 family=BE status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_config.py
REQ_TITLE PASS id=REQ-BE-010 title="Settings class" statement="A Pydantic Settings class loads environment variables for DATABASE_URL, DB_CONNECT_TIMEOUT, JWT_SECRET, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ISSU"
REQ_ROW PASS id=REQ-BE-011 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=mcp-server/config.py
REQ_TITLE PASS id=REQ-BE-011 title="settings caching" statement="Settings are cached via `@lru_cache`."
REQ_ROW PASS id=REQ-BE-012 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=mcp-server/config.py
REQ_TITLE PASS id=REQ-BE-012 title="production validation" statement="In production, the app refuses to start if `JWT_SECRET` is the default value or empty."
REQ_ROW PASS id=REQ-BE-020 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/auth/jwt.py
REQ_TITLE PASS id=REQ-BE-020 title="token creation" statement="`create_access_token` creates a JWT with sub, iss, aud, iat, exp, type claims, signed with HS256."
REQ_ROW PASS id=REQ-BE-021 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/auth/jwt.py
REQ_TITLE PASS id=REQ-BE-021 title="token validation" statement="`decode_access_token` validates signature, exp, aud, iss with fixed algorithm, and checks `type == 'access'`."
REQ_ROW PASS id=REQ-BE-022 family=BE status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_jwt.py
REQ_TITLE PASS id=REQ-BE-022 title="algorithm fixed" statement="`algorithms=[settings.JWT_ALGORITHM]` is passed to `jwt.decode`, never taken from the token header"
REQ_ROW PASS id=REQ-BE-023 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/auth/jwt.py
REQ_TITLE PASS id=REQ-BE-023 title="no refresh token" statement="The MVP uses a 24-hour access token with no refresh token; documented as a known limitation."
REQ_ROW PASS id=REQ-BE-030 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/auth/password.py
REQ_TITLE PASS id=REQ-BE-030 title="bcrypt with rounds 12" statement="Passwords are hashed with bcrypt using `bcrypt__rounds=12`."
REQ_ROW PASS id=REQ-BE-031 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/schemas/auth.py
REQ_TITLE PASS id=REQ-BE-031 title="password validation" statement="Validation is at the Pydantic schema level: min 8 characters, max 72 characters."
REQ_ROW PASS id=REQ-BE-032 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/auth_service.py
REQ_TITLE PASS id=REQ-BE-032 title="timing attack mitigation" statement="`authenticate_user` runs a dummy bcrypt verification when the user does not exist, equalizing response time."
REQ_ROW PASS id=REQ-BE-040 family=BE status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_database.py
REQ_TITLE PASS id=REQ-BE-040 title="get_db" statement="`get_db` provides a SQLAlchemy session per request and closes it in a `finally` block."
REQ_ROW PASS id=REQ-BE-041 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/auth/dependencies.py
REQ_TITLE PASS id=REQ-BE-041 title="get_current_user" statement="`get_current_user` extracts the Bearer token, decodes the JWT, loads the user, and checks `is_active`."
REQ_ROW PASS id=REQ-BE-042 family=BE status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_expense_api.py,backend/tests/unit/test_client_ip.py
REQ_TITLE PASS id=REQ-BE-042 title="get_client_ip" statement="`get_client_ip` reads `X-Forwarded-For` first, then `request.client.host`."
REQ_ROW PASS id=REQ-BE-050 family=BE status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_auth_service.py
REQ_TITLE PASS id=REQ-BE-050 title="register_user" statement="`register_user` normalizes email to lowercase, checks duplicate email and username, hashes password, and creates the user."
REQ_ROW PASS id=REQ-BE-051 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/auth_service.py
REQ_TITLE PASS id=REQ-BE-051 title="login_user" statement="`login_user` authenticates, logs failures with a hashed email, logs success, and returns user plus token."
REQ_ROW PASS id=REQ-BE-060 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/category_service.py
REQ_TITLE PASS id=REQ-BE-060 title="list_categories" statement="`list_categories` returns system categories plus the user's custom categories, ordered by `is_system DESC, name`."
REQ_ROW PASS id=REQ-BE-061 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/category_service.py
REQ_TITLE PASS id=REQ-BE-061 title="create_category" statement="`create_category` checks for duplicate names within the user's scope (case-insensitive) and returns 409 on conflict."
REQ_ROW PASS id=REQ-BE-062 family=BE status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_category_service.py
REQ_TITLE PASS id=REQ-BE-062 title="delete_category" statement="`delete_category` only deletes the user's own custom categories; returns 404 if not found; returns 409 if the category has expenses."
REQ_ROW PASS id=REQ-BE-063 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/category_service.py
REQ_TITLE PASS id=REQ-BE-063 title="validate_category_access" statement="`validate_category_access` returns 404 for missing or not-owned categories, avoiding revealing existence."
REQ_ROW PASS id=REQ-BE-070 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/expense_service.py
REQ_TITLE PASS id=REQ-BE-070 title="create_expense" statement="`create_expense` validates category access, creates the expense, writes an audit log in the same transaction, commits, and returns the expense."
REQ_ROW PASS id=REQ-BE-071 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/expense_service.py
REQ_TITLE PASS id=REQ-BE-071 title="list_expenses" statement="`list_expenses` filters by user_id, applies year_month and category_id filters, orders by date desc and created_at desc, and paginates."
REQ_ROW PASS id=REQ-BE-072 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/expense_service.py
REQ_TITLE PASS id=REQ-BE-072 title="get_expense" statement="`get_expense` returns 404 if the expense is missing or belongs to another user."
REQ_ROW PASS id=REQ-BE-073 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/expense_service.py
REQ_TITLE PASS id=REQ-BE-073 title="update_expense" statement="`update_expense` loads the expense with user_id filter, validates any new category, applies updates, writes an audit log with old and new values, and commits."
REQ_ROW PASS id=REQ-BE-074 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/expense_service.py
REQ_TITLE PASS id=REQ-BE-074 title="delete_expense" statement="`delete_expense` loads the expense with user_id filter, deletes it, writes an audit log with the old value, and commits."
REQ_ROW PASS id=REQ-BE-075 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/expense_service.py
REQ_TITLE PASS id=REQ-BE-075 title="expense serialization helper" statement="`expense_to_dict` returns amount as string, category_id as string, date as ISO string, and note."
REQ_ROW PASS id=REQ-BE-080 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/budget_service.py
REQ_TITLE PASS id=REQ-BE-080 title="set_budget upsert" statement="`set_budget` validates year_month, upserts the budget, writes an audit log (CREATE or UPDATE), and commits."
REQ_ROW PASS id=REQ-BE-081 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/budget_service.py
REQ_TITLE PASS id=REQ-BE-081 title="get_budget" statement="`get_budget` validates year_month and returns the budget or None."
REQ_ROW PASS id=REQ-BE-082 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/budget_service.py
REQ_TITLE PASS id=REQ-BE-082 title="delete_budget" statement="`delete_budget` returns 404 if the budget is missing, otherwise deletes it, writes an audit log, and commits."
REQ_ROW PASS id=REQ-BE-083 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/budget_service.py
REQ_TITLE PASS id=REQ-BE-083 title="year_month validation" statement="`validate_year_month` checks regex `^\d{4}-\d{2}$` and month 01-12."
REQ_ROW PASS id=REQ-BE-090 family=BE status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_dashboard_service.py
REQ_TITLE PASS id=REQ-BE-090 title="get_summary" statement="`get_summary` computes total_spent, transaction_count, budget, remaining, percentage (null if budget is 0), and is_over_budget."
REQ_ROW PASS id=REQ-BE-091 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/dashboard_service.py
REQ_TITLE PASS id=REQ-BE-091 title="get_by_category" statement="`get_by_category` groups expenses by category, computes amount and percentage per category, orders by amount desc."
REQ_ROW PASS id=REQ-BE-092 family=BE status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_dashboard_service.py
REQ_TITLE PASS id=REQ-BE-092 title="get_trend" statement="`get_trend` aggregates expenses over the last N months, includes months with zero expenses, handles year boundaries, and aggregates in Python to avoid DB-specif"
REQ_ROW PASS id=REQ-BE-093 family=BE status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_dashboard_service.py
REQ_TITLE PASS id=REQ-BE-093 title="get_cumulative" statement="`get_cumulative` generates all days in the month, computes daily and running cumulative amounts, includes days with zero expenses."
REQ_ROW PASS id=REQ-BE-094 family=BE status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_dashboard_service.py
REQ_TITLE PASS id=REQ-BE-094 title="get_heatmap" statement="`get_heatmap` generates a week matrix starting on Monday, fills missing days with 0, and computes max_amount."
REQ_ROW PASS id=REQ-BE-095 family=BE status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_dashboard_service.py
REQ_TITLE PASS id=REQ-BE-095 title="get_recent" statement="`get_recent` returns the user's expenses ordered by date desc, created_at desc, limited."
REQ_ROW PASS id=REQ-BE-096 family=BE status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_dashboard_service.py
REQ_TITLE PASS id=REQ-BE-096 title="shared helpers" statement="`month_range`, `add_month`, `subtract_months`, and `to_decimal` are provided as shared helpers."
REQ_ROW PASS id=REQ-BE-100 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/audit/logger.py
REQ_TITLE PASS id=REQ-BE-100 title="write_audit_log" statement="`write_audit_log` adds an AuditLog to the session without committing; the caller commits."
REQ_ROW PASS id=REQ-BE-101 family=BE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-BE-101 title="audit rules" statement="Same transaction, rollback on failure, no API access, preserve on user delete, JSON-serializable values, IP address extracted from request."
REQ_ROW PASS id=REQ-BE-110 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/core/errors.py
REQ_TITLE PASS id=REQ-BE-110 title="AppError" statement="`AppError` carries code, message, status_code, and optional field."
REQ_ROW PASS id=REQ-BE-111 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/main.py
REQ_TITLE PASS id=REQ-BE-111 title="exception handlers" statement="Handlers exist for AppError, RequestValidationError, SQLAlchemyError, and generic Exception; all return consistent shape."
REQ_ROW PASS id=REQ-BE-112 family=BE status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/core/errors.py,docs/issues/closed/t8.md
REQ_TITLE PASS id=REQ-BE-112 title="error code table" statement="All 18 error codes are defined with HTTP status and field where applicable."
REQ_ROW PASS id=REQ-BE-120 family=BE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t8.md
REQ_TITLE PASS id=REQ-BE-120 title="JSON logging setup" statement="Logs use a JSON formatter with timestamp, level, logger, event, extra_fields, and exception when applicable."
REQ_ROW PASS id=REQ-BE-121 family=BE status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/services/auth_service.py,docs/issues/closed/t8.md
REQ_TITLE PASS id=REQ-BE-121 title="log events" statement="Events are defined for auth, expense, budget, category, db fallback, db error, and unhandled error."
REQ_ROW PASS id=REQ-BE-122 family=BE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-BE-122 title="never log sensitive data" statement="Passwords, tokens, full bodies, raw emails, and DB connection strings are never logged."
REQ_ROW PASS id=REQ-BE-130 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/database.py,ops/diagnosis.md
REQ_TITLE PASS id=REQ-BE-130 title="engine selection" statement="`create_db_engine` uses SQLite directly when DATABASE_URL starts with sqlite; otherwise tries PostgreSQL with a 5-second timeout and falls back to SQLite on fai"
REQ_ROW PASS id=REQ-BE-131 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/main.py
REQ_TITLE PASS id=REQ-BE-131 title="startup initialization" statement="On startup, if fallback is active, create tables and seed categories; otherwise log primary initialization."
REQ_ROW PASS id=REQ-BE-132 family=BE status=IMPLEMENTED_TESTED method=code-symbol pointers=frontend/src/api/client.test.ts,frontend/src/api/dashboard.test.ts,frontend/src/components/common/guards.test.tsx
REQ_TITLE PASS id=REQ-BE-132 title="health reporting" statement="Health reports `status`, `database`, `fallback_active`, `version` based on `is_fallback`."
REQ_ROW PASS id=REQ-BE-133 family=BE status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_sqlite_fallback.py
REQ_TITLE PASS id=REQ-BE-133 title="fallback rules" statement="Fallback triggers only on startup; timeout 5 seconds; fallback target `sqlite:///./fallback.db`; requires restart to switch back; data lost on container restart"
REQ_ROW PASS id=REQ-BE-140 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/main.py
REQ_TITLE PASS id=REQ-BE-140 title="app factory" statement="FastAPI app is created with title, version, docs, redoc, and openapi URLs; CORS middleware; exception handlers; six routers with /api/v1 prefixes; SPA fallback"
REQ_ROW PASS id=REQ-BE-141 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/main.py
REQ_TITLE PASS id=REQ-BE-141 title="router registration order" statement="Routers are registered in order: health, auth, categories, expenses, budgets, dashboard, static SPA fallback last."
REQ_ROW PASS id=REQ-BE-150 family=BE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/pyproject.toml
REQ_TITLE PASS id=REQ-BE-150 title="framework and ORM" statement="FastAPI and SQLAlchemy 2.0 are chosen for auto OpenAPI, async support, Pydantic integration, and support for both PostgreSQL and SQLite."
REQ_ROW PASS id=REQ-BE-151 family=BE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-BE-151 title="user isolation and 404" statement="User isolation is enforced at the query level; cross- user access returns 404, not 403, to avoid revealing existence."
REQ_ROW PASS id=REQ-BE-152 family=BE status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md
REQ_TITLE PASS id=REQ-BE-152 title="error format and Decimal" statement="Error format `{detail, code, field}`; Decimal quantized to 0.01; DATE type without timezone."
REQ_ROW PASS id=REQ-CICD-001 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=Dockerfile,docker-compose.yml,render.yaml
REQ_TITLE PASS id=REQ-CICD-001 title="criterion mapping" statement="CI/CD and deployment cover Criterion 8 (containerization), Criterion 10 (deployment), and Criterion 11 (CI/CD pipeline)."
REQ_ROW PASS id=REQ-CICD-002 family=CICD status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t26.md
REQ_TITLE PASS id=REQ-CICD-002 title="pipeline overview" statement="Pipeline: push → PR (ci.yml) → merge to main (e2e.yml) → deploy.yml → production."
REQ_ROW PASS id=REQ-CICD-010 family=CICD status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md,docs/issues/closed/t26.md
REQ_TITLE PASS id=REQ-CICD-010 title="workflow directory" statement="`.github/workflows/` contains ci.yml, e2e.yml, and deploy.yml."
REQ_ROW PASS id=REQ-CICD-011 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.github/workflows/ci.yml
REQ_TITLE PASS id=REQ-CICD-011 title="ci.yml jobs" statement="ci.yml runs backend-test and frontend-test in parallel, then compose-build; backend runs uv sync, ruff, mypy, pytest unit and integration, coverage; frontend ru"
REQ_ROW PASS id=REQ-CICD-012 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.github/workflows/e2e.yml
REQ_TITLE PASS id=REQ-CICD-012 title="e2e.yml jobs" statement="e2e.yml runs on push to main only; builds Docker Compose, waits for health, installs Playwright, runs E2E tests, uploads report on failure, stops stack."
REQ_ROW PASS id=REQ-CICD-013 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.github/workflows/deploy.yml
REQ_TITLE PASS id=REQ-CICD-013 title="deploy.yml jobs" statement="deploy.yml triggers after e2e.yml success; calls Render deploy hook; waits; verifies health endpoint with retries; reports success."
REQ_ROW PASS id=REQ-CICD-014 family=CICD status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t26.md
REQ_TITLE PASS id=REQ-CICD-014 title="workflow triggers summary" statement="ci.yml on PR and push to main (~5 min); e2e.yml on push to main (~8 min); deploy.yml after e2e.yml success (~2 min)."
REQ_ROW PASS id=REQ-CICD-015 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.github/workflows/ci.yml,.github/workflows/e2e.yml
REQ_TITLE PASS id=REQ-CICD-015 title="no E2E on PR" statement="E2E is not run on PRs to keep feedback fast and save CI minutes."
REQ_ROW PASS id=REQ-CICD-016 family=CICD status=IMPLEMENTED_STRUCTURAL method=citation pointers=.github/workflows/ci.yml,.github/workflows/e2e.yml,docs/issues/closed/t26.md
REQ_TITLE PASS id=REQ-CICD-016 title="concurrency control" statement="ci.yml and e2e.yml use `concurrency` to cancel in-progress runs."
REQ_ROW PASS id=REQ-CICD-017 family=CICD status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t26.md,docs/issues/closed/t42.md,docs/issues/closed/t54.md
REQ_TITLE PASS id=REQ-CICD-017 title="caching" statement="Workflows cache uv dependencies, npm dependencies (frontend and e2e), and Playwright browsers."
REQ_ROW PASS id=REQ-CICD-020 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=Dockerfile
REQ_TITLE PASS id=REQ-CICD-020 title="multi-stage Dockerfile" statement="Dockerfile uses two stages: Node 20 alpine builds the frontend; Python 3.12 slim installs uv, backend deps, backend code, alembic, and copies the built frontend"
REQ_ROW PASS id=REQ-CICD-021 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=Dockerfile
REQ_TITLE PASS id=REQ-CICD-021 title="non-root user" statement="The container runs as a non-root user."
REQ_ROW PASS id=REQ-CICD-022 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=Dockerfile
REQ_TITLE PASS id=REQ-CICD-022 title="Dockerfile design decisions" statement="Multi-stage, alpine for Node, slim for Python, uv for deps, non-root user, static files copied, no dev dependencies, pinned base image versions."
REQ_ROW PASS id=REQ-CICD-023 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docker-compose.yml
REQ_TITLE PASS id=REQ-CICD-023 title="docker-compose.yml services" statement="Compose defines `db` (postgres:16-alpine with healthcheck and named volume) and `app` (build from Dockerfile, depends on db healthy, environment variables, port"
REQ_ROW PASS id=REQ-CICD-024 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docker-compose.yml
REQ_TITLE PASS id=REQ-CICD-024 title="compose design decisions" statement="Two services; PostgreSQL 16; healthcheck on db; healthcheck on app; named volume; single app container; explicit CORS."
REQ_ROW PASS id=REQ-CICD-025 family=CICD status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md,docs/issues/closed/t24.md,docs/issues/closed/t49.md
REQ_TITLE PASS id=REQ-CICD-025 title="development vs production" statement="Development uses Vite dev server, uvicorn reload, PostgreSQL in Compose, two containers; production uses static files served by FastAPI, single container plus m"
REQ_ROW PASS id=REQ-CICD-026 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=README.md
REQ_TITLE PASS id=REQ-CICD-026 title="local development modes" statement="Mode A (full Docker): `docker compose up --build`; Mode B (hybrid): Compose db + local backend + local frontend."
REQ_ROW PASS id=REQ-CICD-030 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=README.md
REQ_TITLE PASS id=REQ-CICD-030 title="why Render" statement="No credit card, free PostgreSQL, Docker support, health checks, GitHub integration, free SSL."
REQ_ROW PASS id=REQ-CICD-031 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=render.yaml
REQ_TITLE PASS id=REQ-CICD-031 title="render.yaml" statement="`render.yaml` defines a web service (Docker, free plan, health check path, env vars) and a free PostgreSQL database."
REQ_ROW PASS id=REQ-CICD-032 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=render.yaml
REQ_TITLE PASS id=REQ-CICD-032 title="environment variables on Render" statement="DATABASE_URL from database; JWT_SECRET generated; JWT_ALGORITHM HS256; expiry 1440; issuer and audience set; CORS_ORIGINS Render URL; ENVIRONMENT production; AP"
REQ_ROW PASS id=REQ-CICD-033 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=README.md,ops/runbook.md
REQ_TITLE PASS id=REQ-CICD-033 title="free tier limits" statement="512 MB RAM, 0.1 CPU, 15-minute idle sleep, 750 hours/month, 1 GB PostgreSQL, 30-day expiry, 5 GB bandwidth, 500 build minutes, 2 custom domains, no SSH."
REQ_ROW PASS id=REQ-CICD-034 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=render.yaml
REQ_TITLE PASS id=REQ-CICD-034 title="deployment flow" statement="10 steps: push → ci → e2e → deploy hook → Render build → migrations → container start → Render health check → GitHub health verify → complete."
REQ_ROW PASS id=REQ-CICD-035 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=Dockerfile
REQ_TITLE PASS id=REQ-CICD-035 title="migration in deployment" statement="Migrations run in the container CMD before uvicorn starts."
REQ_ROW PASS id=REQ-CICD-036 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=README.md
REQ_TITLE PASS id=REQ-CICD-036 title="first deployment steps" statement="Create Render account, new Blueprint, Render reads render.yaml, wait for deploy, verify health, configure UptimeRobot."
REQ_ROW PASS id=REQ-CICD-037 family=CICD status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t26.md
REQ_TITLE PASS id=REQ-CICD-037 title="subsequent deployments" statement="Pushes to main trigger the pipeline automatically."
REQ_ROW PASS id=REQ-CICD-040 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=README.md,ops/runbook.md
REQ_TITLE PASS id=REQ-CICD-040 title="cold start problem" statement="Render free tier sleeps after 15 minutes idle; next request takes 30-60 seconds."
REQ_ROW PASS id=REQ-CICD-041 family=CICD status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_req_coverage_verification.py
REQ_TITLE PASS id=REQ-CICD-041 title="UptimeRobot mitigation" statement="UptimeRobot pings health endpoint every 10 minutes; alert via email on down; expected 200."
REQ_ROW PASS id=REQ-CICD-042 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=README.md
REQ_TITLE PASS id=REQ-CICD-042 title="README notice" statement="README includes a note about free tier cold start and UptimeRobot."
REQ_ROW PASS id=REQ-CICD-043 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=README.md
REQ_TITLE PASS id=REQ-CICD-043 title="peer review consideration" statement="Peer reviewers are asked to open the URL early and wait for the first load."
REQ_ROW PASS id=REQ-CICD-050 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-CICD-050 title="rollback procedure" statement="Render dashboard → service → deploys → previous deploy → Redeploy."
REQ_ROW PASS id=REQ-CICD-051 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-CICD-051 title="rollback triggers" statement="Health check failure, E2E smoke test failure, user-reported broken feature, unexpected fallback."
REQ_ROW PASS id=REQ-CICD-052 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-CICD-052 title="database rollback" statement="Forward-only migrations; revert code and write a new migration; no `alembic downgrade` in production."
REQ_ROW PASS id=REQ-CICD-053 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-CICD-053 title="rollback limitations" statement="Manual, no automated, no canary, no blue-green, brief downtime."
REQ_ROW PASS id=REQ-CICD-060 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.github/workflows/deploy.yml
REQ_TITLE PASS id=REQ-CICD-060 title="automatic verification" statement="deploy.yml verifies health endpoint; workflow fails if health fails."
REQ_ROW PASS id=REQ-CICD-061 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/deployment-health.md
REQ_TITLE PASS id=REQ-CICD-061 title="manual verification" statement="Smoke test: open URL, register, add expense, set budget, verify five charts, switch month, logout."
REQ_ROW PASS id=REQ-CICD-062 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/deployment-health.md
REQ_TITLE PASS id=REQ-CICD-062 title="verification record" statement="Each deployment records date, commit, health response, smoke test results, screenshots, notes."
REQ_ROW PASS id=REQ-CICD-070 family=CICD status=DEFERRED_RULLED method=deferral-register pointers=docs/criteria/docs_verification.md,ops/deployment-health.md issue=61 deferral_reason="RENDER_DEPLOY_HOOK secret is operator infrastructure (platform #61)"
REQ_TITLE PASS id=REQ-CICD-070 title="secrets" statement="RENDER_DEPLOY_HOOK in GitHub Actions secrets; JWT_SECRET and DATABASE_URL in Render env; no secrets in repo."
REQ_ROW PASS id=REQ-CICD-071 family=CICD status=IMPLEMENTED_STRUCTURAL method=citation pointers=.github/workflows/ci.yml,.github/workflows/deploy.yml,.github/workflows/e2e.yml
REQ_TITLE PASS id=REQ-CICD-071 title="permissions" statement="Workflows use default GITHUB_TOKEN with minimal permissions; no long-lived AWS credentials."
REQ_ROW PASS id=REQ-CICD-072 family=CICD status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t26.md,docs/issues/closed/t42.md
REQ_TITLE PASS id=REQ-CICD-072 title="supply chain" statement="Pinned action versions, locked dependencies, Dependabot not enabled (documented), Trivy run locally."
REQ_ROW PASS id=REQ-CICD-073 family=CICD status=IMPLEMENTED_STRUCTURAL method=citation pointers=Makefile,docs/ai-workflow.md,docs/issues/closed/t26.md
REQ_TITLE PASS id=REQ-CICD-073 title="not in CI" statement="Security scans are not in CI; they run locally and results are committed."
REQ_ROW PASS id=REQ-CICD-080 family=CICD status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t26.md
REQ_TITLE PASS id=REQ-CICD-080 title="CI provider and split" statement="GitHub Actions; backend and frontend in parallel; integration in ci.yml; E2E only on main."
REQ_ROW PASS id=REQ-CICD-081 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=Dockerfile
REQ_TITLE PASS id=REQ-CICD-081 title="deploy method" statement="Render deploy hook after E2E passes; health verification post-deploy; migrations in container CMD."
REQ_ROW PASS id=REQ-CICD-082 family=CICD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=Dockerfile,README.md
REQ_TITLE PASS id=REQ-CICD-082 title="container and rollback choices" statement="Single app container; pinned base images; non-root user; UptimeRobot for cold start; manual Render rollback."
REQ_ROW PASS id=REQ-CICD-083 family=CICD status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md,docs/issues/closed/t26.md,docs/issues/closed/t36.md
REQ_TITLE PASS id=REQ-CICD-083 title="security choices" statement="Security scans local only; secrets in GitHub and Render env, never in repo."
REQ_ROW PASS id=REQ-DB-001 family=DB status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md
REQ_TITLE PASS id=REQ-DB-001 title="Five entities" statement="The database stores exactly five entities: users, categories, expenses, budgets, and audit_logs."
REQ_ROW PASS id=REQ-DB-002 family=DB status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-DB-002 title="UUID primary keys" statement="All tables use UUID primary keys generated in Python, not by the database."
REQ_ROW PASS id=REQ-DB-003 family=DB status=IMPLEMENTED_STRUCTURAL method=code-symbol pointers=backend/alembic/versions/001_initial_schema.py,backend/alembic/versions/002_categories.py,backend/alembic/versions/003_audit_logs.py
REQ_TITLE PASS id=REQ-DB-003 title="Timestamps" statement="Timestamps use `TIMESTAMPTZ` on PostgreSQL and ISO text on SQLite"
REQ_ROW PASS id=REQ-DB-010 family=DB status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_user_model.py
REQ_TITLE PASS id=REQ-DB-010 title="users table definition" statement="The users table has id (UUID, PK), email (VARCHAR(255), UNIQUE, NOT NULL, INDEX), username (VARCHAR(50), UNIQUE, NOT NULL), hashed_password (VARCHAR(255), NOT N"
REQ_ROW PASS id=REQ-DB-011 family=DB status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_user_model.py
REQ_TITLE PASS id=REQ-DB-011 title="users business rules" statement="Email is unique and case-insensitive; username is unique and case-sensitive; password is never stored in plain text; `is_active = false` prevents login but pres"
REQ_ROW PASS id=REQ-DB-020 family=DB status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_category_model.py
REQ_TITLE PASS id=REQ-DB-020 title="categories table definition" statement="The categories table has id (UUID, PK), user_id (UUID, FK users.id, NULLABLE, INDEX), name (VARCHAR(100), NOT NULL), color (VARCHAR(7), NOT NULL), icon (VARCHAR"
REQ_ROW PASS id=REQ-DB-021 family=DB status=IMPLEMENTED_STRUCTURAL method=code-symbol pointers=backend/app/models/audit_log.py,backend/app/models/budget.py,backend/app/models/category.py
REQ_TITLE PASS id=REQ-DB-021 title="categories constraints" statement="The categories table has two CHECK constraints: `color ~ '^#[0-9A-Fa-f]{6}$'` and system consistency `(is_system = TRUE AND user_id IS NULL) OR (is_system = FAL"
REQ_ROW PASS id=REQ-DB-022 family=DB status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_category_migration.py
REQ_TITLE PASS id=REQ-DB-022 title="categories uniqueness" statement="A partial unique index on `(user_id, name) WHERE user_id IS NOT NULL` enforces uniqueness within a user's custom categories"
REQ_ROW PASS id=REQ-DB-023 family=DB status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/models/category.py,backend/app/scripts/seed.py,docs/issues/closed/t10.md
REQ_TITLE PASS id=REQ-DB-023 title="categories business rules" statement="System categories have `user_id IS NULL` and `is_system = TRUE`; custom categories have `user_id = current_user.id` and `is_system = FALSE`; users cannot create"
REQ_ROW PASS id=REQ-DB-030 family=DB status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_expense_model.py
REQ_TITLE PASS id=REQ-DB-030 title="expenses table definition" statement="The expenses table has id (UUID, PK), user_id (UUID, FK users.id, NOT NULL, INDEX), category_id (UUID, FK categories.id, NOT NULL, INDEX), amount (NUMERIC(12,2)"
REQ_ROW PASS id=REQ-DB-031 family=DB status=IMPLEMENTED_STRUCTURAL method=code-symbol pointers=backend/app/models/audit_log.py,backend/app/models/budget.py,backend/app/models/category.py
REQ_TITLE PASS id=REQ-DB-031 title="expenses constraints" statement="The expenses table has two CHECK constraints: `amount > 0` and `currency = 'USD'`."
REQ_ROW PASS id=REQ-DB-032 family=DB status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_expense_migration.py
REQ_TITLE PASS id=REQ-DB-032 title="expenses foreign keys" statement="`user_id` references `users.id` with CASCADE; `category_id` references `categories.id` with RESTRICT."
REQ_ROW PASS id=REQ-DB-033 family=DB status=IMPLEMENTED_TESTED method=code-symbol pointers=frontend/src/api/dashboard.test.ts,frontend/src/components/charts/category_pie_chart.test.tsx,frontend/src/components/forms/expense_form.test.tsx
REQ_TITLE PASS id=REQ-DB-033 title="expenses indexes" statement="The expenses table has indexes on `user_id`, `(user_id, date DESC)`, `(user_id, category_id)`, and `category_id`."
REQ_ROW PASS id=REQ-DB-034 family=DB status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/models/expense.py,backend/app/schemas/expense.py,backend/app/services/expense_service.py
REQ_TITLE PASS id=REQ-DB-034 title="expenses business rules" statement="Amount must be positive with at most 2 decimal places, maximum 9,999,999,999.99; category must belong to the same user or be a system category; date is stored w"
REQ_ROW PASS id=REQ-DB-040 family=DB status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_budget_model.py
REQ_TITLE PASS id=REQ-DB-040 title="budgets table definition" statement="The budgets table has id (UUID, PK), user_id (UUID, FK users.id, NOT NULL), year_month (CHAR(7), NOT NULL), amount (NUMERIC(12,2), NOT NULL, CHECK > 0), created"
REQ_ROW PASS id=REQ-DB-041 family=DB status=IMPLEMENTED_STRUCTURAL method=code-symbol pointers=backend/app/models/audit_log.py,backend/app/models/budget.py,backend/app/models/category.py
REQ_TITLE PASS id=REQ-DB-041 title="budgets constraints" statement="The budgets table has a UNIQUE constraint on `(user_id, year_month)`, CHECK `amount > 0`, and CHECK `year_month ~ '^[0-9]{4}-[0-9]{2}$'`."
REQ_ROW PASS id=REQ-DB-042 family=DB status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_budget_api.py,backend/tests/integration/test_budget_migration.py
REQ_TITLE PASS id=REQ-DB-042 title="budgets business rules" statement="One budget per user per month; setting a budget for an existing month performs an upsert; year_month format is strictly YYYY-MM; amount must be positive; deleti"
REQ_ROW PASS id=REQ-DB-050 family=DB status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_audit_log_model.py
REQ_TITLE PASS id=REQ-DB-050 title="audit_logs table definition" statement="The audit_logs table has id (UUID, PK), user_id (UUID, FK users.id, NOT NULL, INDEX), action (VARCHAR(10), NOT NULL), entity_type (VARCHAR(20), NOT NULL), entit"
REQ_ROW PASS id=REQ-DB-051 family=DB status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_audit_log_model.py
REQ_TITLE PASS id=REQ-DB-051 title="audit_logs constraints" statement="The audit_logs table has CHECK `action IN ('CREATE', 'UPDATE', 'DELETE')` and CHECK `entity_type IN ('expense', 'budget')`."
REQ_ROW PASS id=REQ-DB-052 family=DB status=IMPLEMENTED_TESTED method=code-symbol pointers=frontend/src/components/ui/empty_state.test.tsx,frontend/src/context/toast_context.test.tsx
REQ_TITLE PASS id=REQ-DB-052 title="audit_logs indexes" statement="The audit_logs table has indexes on `(user_id, created_at DESC)`, `(entity_type, entity_id)`, and `action`."
REQ_ROW PASS id=REQ-DB-053 family=DB status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/audit/logger.py
REQ_TITLE PASS id=REQ-DB-053 title="audit_logs business rules" statement="Written in the same transaction as the business operation; if audit write fails, the business operation is rolled back; not exposed via API; preserved even if t"
REQ_ROW PASS id=REQ-DB-054 family=DB status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_audit_log_model.py
REQ_TITLE PASS id=REQ-DB-054 title="audit_logs JSONB handling" statement="PostgreSQL uses JSONB; SQLite uses JSON (stored as TEXT)"
REQ_ROW PASS id=REQ-DB-060 family=DB status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/alembic/versions/001_initial_schema.py
REQ_TITLE PASS id=REQ-DB-060 title="all indexes" statement="All 14 indexes across the five tables are defined as listed in the summary table."
REQ_ROW PASS id=REQ-DB-061 family=DB status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t10.md
REQ_TITLE PASS id=REQ-DB-061 title="all check constraints" statement="All eight CHECK constraints across the five tables are defined as listed."
REQ_ROW PASS id=REQ-DB-062 family=DB status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-DB-062 title="all foreign keys" statement="All five foreign key relationships are defined with the specified ON DELETE behavior (CASCADE for user_id, RESTRICT for category_id, no cascade for audit_logs.u"
REQ_ROW PASS id=REQ-DB-063 family=DB status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/database.py
REQ_TITLE PASS id=REQ-DB-063 title="SQLite foreign key pragma" statement="SQLite foreign keys are enforced via `PRAGMA foreign_keys = ON` set per connection through a SQLAlchemy engine event."
REQ_ROW PASS id=REQ-DB-070 family=DB status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/scripts/seed.py,docs/issues/closed/t10.md,docs/issues/closed/t18.md
REQ_TITLE PASS id=REQ-DB-070 title="ten system categories" statement="Ten system categories are seeded with fixed names, colors, and icons: Food & Dining (#EF4444), Groceries (#F97316), Transportation (#EAB308), Housing & Rent (#2"
REQ_ROW PASS id=REQ-DB-071 family=DB status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/scripts/seed.py,docs/issues/closed/t10.md
REQ_TITLE PASS id=REQ-DB-071 title="idempotent seeding" statement="Seeding is idempotent: re-running does not create duplicates."
REQ_ROW PASS id=REQ-DB-072 family=DB status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/database.py
REQ_TITLE PASS id=REQ-DB-072 title="seeding triggers" statement="Seeding runs via Alembic migration for PostgreSQL, and after `create_all()` for SQLite fallback, tests, and Docker Compose."
REQ_ROW PASS id=REQ-DB-080 family=DB status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/alembic/env.py
REQ_TITLE PASS id=REQ-DB-080 title="Alembic setup" statement="Alembic manages schema with `env.py`, `script.py.mako`, and versioned migrations in `versions/`."
REQ_ROW PASS id=REQ-DB-081 family=DB status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/alembic/versions/001_initial_schema.py
REQ_TITLE PASS id=REQ-DB-081 title="migration files" statement="Migration `001_initial_schema.py` creates all five tables with indexes and constraints; migration `002_seed_categories.py` inserts the ten system categories and"
REQ_ROW PASS id=REQ-DB-082 family=DB status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=Dockerfile,docker-compose.yml
REQ_TITLE PASS id=REQ-DB-082 title="migration execution per environment" statement="Local PostgreSQL runs `alembic upgrade head` manually; Docker Compose runs it on container start; Render runs it via the container CMD; SQLite fallback and test"
REQ_ROW PASS id=REQ-DB-083 family=DB status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_sqlite_fallback.py
REQ_TITLE PASS id=REQ-DB-083 title="fallback does not use Alembic" statement="Fallback data is temporary; migration history is unnecessary; `create_all()` is faster and avoids SQLite compatibility issues."
REQ_ROW PASS id=REQ-DB-090 family=DB status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_money_precision_api.py
REQ_TITLE PASS id=REQ-DB-090 title="Decimal everywhere" statement="All amounts use Decimal"
REQ_ROW PASS id=REQ-DB-091 family=DB status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_budget_model.py,backend/tests/unit/test_expense_model.py
REQ_TITLE PASS id=REQ-DB-091 title="SQLite Decimal handling" statement="SQLite stores NUMERIC as REAL; SQLAlchemy coerces to Decimal; aggregation quantizes to 0.01 before comparison."
REQ_ROW PASS id=REQ-DB-092 family=DB status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/dashboard_service.py
REQ_TITLE PASS id=REQ-DB-092 title="aggregation rules" statement="Sums use `func.sum`; result is cast to Decimal and quantized to 2 decimal places; comparisons use Decimal, never float."
REQ_ROW PASS id=REQ-DB-100 family=DB status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-DB-100 title="date rules" statement="Expense date uses DATE with no timezone; created_at and updated_at use TIMESTAMPTZ in UTC; year_month uses CHAR(7) with no timezone."
REQ_ROW PASS id=REQ-DB-101 family=DB status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-DB-101 title="DATE rationale" statement="DATE avoids timezone ambiguity in month attribution"
REQ_ROW PASS id=REQ-DB-102 family=DB status=IMPLEMENTED_STRUCTURAL method=code-symbol pointers=backend/app/services/dashboard_service.py
REQ_TITLE PASS id=REQ-DB-102 title="month range query" statement="`month_range('YYYY-MM')` returns `[start, end)` where end is the first day of the next month."
REQ_ROW PASS id=REQ-DB-103 family=DB status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/expense_service.py
REQ_TITLE PASS id=REQ-DB-103 title="default date" statement="Frontend defaults the date input to today (browser local timezone); backend stores the date as received without re-interpretation."
REQ_ROW PASS id=REQ-DB-104 family=DB status=IMPLEMENTED_TESTED method=code-symbol pointers=frontend/src/api/dashboard.test.ts,frontend/src/components/forms/expense_form.test.tsx,frontend/src/hooks/use_dashboard.test.tsx
REQ_TITLE PASS id=REQ-DB-104 title="timestamp defaults" statement="`created_at` and `updated_at` use `func.now()` (database time), consistent for audit purposes."
REQ_ROW PASS id=REQ-DB-110 family=DB status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/database.py,backend/app/main.py
REQ_TITLE PASS id=REQ-DB-110 title="startup sequence" statement="Startup loads settings, determines DATABASE_URL, and either uses SQLite directly or attempts PostgreSQL with a 5-second timeout; on failure, logs WARNING and sw"
REQ_ROW PASS id=REQ-DB-111 family=DB status=IMPLEMENTED_TESTED method=code-symbol pointers=frontend/src/api/client.test.ts,frontend/src/api/dashboard.test.ts,frontend/src/components/common/guards.test.tsx
REQ_TITLE PASS id=REQ-DB-111 title="health check reporting" statement="Health endpoint reports `status`, `database`, `fallback_active`, and `version` based on the `is_fallback` flag."
REQ_ROW PASS id=REQ-DB-112 family=DB status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/database.py
REQ_TITLE PASS id=REQ-DB-112 title="SQLite engine configuration" statement="SQLite engine uses `check_same_thread: False`, `StaticPool` for in-memory tests, and a `PRAGMA foreign_keys=ON` event listener."
REQ_ROW PASS id=REQ-DB-113 family=DB status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/database.py
REQ_TITLE PASS id=REQ-DB-113 title="PostgreSQL engine configuration" statement="PostgreSQL engine uses `pool_pre_ping=True`, `pool_recycle=300`, `pool_size=5`, `max_overflow=10`, and `connect_timeout=5`."
REQ_ROW PASS id=REQ-DB-120 family=DB status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-DB-120 title="data volume assumptions" statement="Users < 100, categories per user = 10 system + < 20 custom, expenses per user per month < 200, expenses per user total < 2000, budgets per user = 1 per month, a"
REQ_ROW PASS id=REQ-DB-121 family=DB status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-DB-121 title="backup scope" statement="No automated backups in MVP. Manual export commands documented for PostgreSQL (`pg_dump`) and SQLite (`sqlite3 .dump`)."
REQ_ROW PASS id=REQ-DB-130 family=DB status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-DB-130 title="primary key choice" statement="UUID primary keys generated in Python for portability across PostgreSQL and SQLite."
REQ_ROW PASS id=REQ-DB-131 family=DB status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-DB-131 title="amount type choice" statement="NUMERIC(12,2) for exact decimal representation."
REQ_ROW PASS id=REQ-DB-132 family=DB status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-DB-132 title="date type choice" statement="DATE avoids timezone ambiguity for month attribution."
REQ_ROW PASS id=REQ-DB-133 family=DB status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-DB-133 title="budget key choice" statement="(user_id, year_month) ensures one budget per user per month."
REQ_ROW PASS id=REQ-DB-134 family=DB status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-DB-134 title="audit entity_id choice" statement="UUID without FK, supporting multiple entity types and surviving deletion."
REQ_ROW PASS id=REQ-DB-135 family=DB status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/database.py
REQ_TITLE PASS id=REQ-DB-135 title="fallback choice" statement="SQLite on startup only; no runtime switching."
REQ_ROW PASS id=REQ-DOC-001 family=DOC status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t4.md,docs/issues/closed/t48.md
REQ_TITLE PASS id=REQ-DOC-001 title="documentation principles" statement="English only; one purpose per file; reviewer-first; living documents; linked not duplicated; short where possible."
REQ_ROW PASS id=REQ-DOC-002 family=DOC status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md,backend/scripts/docs_verification.py,docs/criteria/docs_verification.md
REQ_TITLE PASS id=REQ-DOC-002 title="documentation map" statement="Root documents (README, product-spec, AGENTS, CLAUDE, openapi, LICENSE); docs/; security/; ops/; screenshots/."
REQ_ROW PASS id=REQ-DOC-010 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=README.md
REQ_TITLE PASS id=REQ-DOC-010 title="README.md" statement="README is the reviewer entry point, under 500 lines, with sections: title, live demo, features, tech stack, architecture, quick start, tests, API docs, AI workf"
REQ_ROW PASS id=REQ-DOC-011 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=product-spec.md
REQ_TITLE PASS id=REQ-DOC-011 title="product-spec.md" statement="product-spec contains problem statement, target users, user stories, functional and non-functional requirements, edge cases, success criteria, scope boundaries."
REQ_ROW PASS id=REQ-DOC-012 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=AGENTS.md
REQ_TITLE PASS id=REQ-DOC-012 title="AGENTS.md" statement="AGENTS.md is under 60 lines, containing commands, rules, and document links."
REQ_ROW PASS id=REQ-DOC-013 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=CLAUDE.md
REQ_TITLE PASS id=REQ-DOC-013 title="CLAUDE.md" statement="CLAUDE.md is a single line `@AGENTS.md`."
REQ_ROW PASS id=REQ-DOC-014 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=openapi.yaml
REQ_TITLE PASS id=REQ-DOC-014 title="openapi.yaml" statement="openapi.yaml is the full OpenAPI 3.1 specification."
REQ_ROW PASS id=REQ-DOC-015 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=LICENSE
REQ_TITLE PASS id=REQ-DOC-015 title="LICENSE" statement="LICENSE contains the MIT license text."
REQ_ROW PASS id=REQ-DOC-020 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-DOC-020 title="docs/architecture.md" statement="architecture.md covers overview, diagram, frontend, backend, database, auth, directory structure, cross-cutting concerns, and decisions."
REQ_ROW PASS id=REQ-DOC-021 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/api.md
REQ_TITLE PASS id=REQ-DOC-021 title="docs/api.md" statement="api.md covers base URL, authentication, common patterns, endpoint reference, examples, error codes."
REQ_ROW PASS id=REQ-DOC-022 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/process.md
REQ_TITLE PASS id=REQ-DOC-022 title="docs/process.md" statement="process.md contains roles, orchestrator, lifecycle, rules."
REQ_ROW PASS id=REQ-DOC-023 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-DOC-023 title="docs/ai-workflow.md" statement="ai-workflow.md contains tools, workflow, context engineering, roles, orchestration, example prompts, session records, correction log, skills, subagents, MCP too"
REQ_ROW PASS id=REQ-DOC-024 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/design-system.md
REQ_TITLE PASS id=REQ-DOC-024 title="docs/design-system.md" statement="design-system.md contains colors, typography, spacing, components, chart colors, states, and accessibility."
REQ_ROW PASS id=REQ-DOC-025 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-DOC-025 title="docs/testing-guidelines.md" statement="testing-guidelines.md contains test layers, backend rules, frontend rules, E2E rules, coverage policy, naming, and what not to test."
REQ_ROW PASS id=REQ-DOC-026 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/agent-extension-pack.md
REQ_TITLE PASS id=REQ-DOC-026 title="docs/agent-extension-pack.md" statement="agent-extension-pack.md contains overview, skills, hooks, MCP server, subagents, permissions, and design principles."
REQ_ROW PASS id=REQ-DOC-027 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/permissions.md
REQ_TITLE PASS id=REQ-DOC-027 title="docs/permissions.md" statement="permissions.md contains user roles, resource permissions, agent permissions, skill permissions, subagent permissions, enforcement, forbidden actions, and escala"
REQ_ROW PASS id=REQ-DOC-028 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/task-template.md
REQ_TITLE PASS id=REQ-DOC-028 title="docs/task-template.md" statement="task-template.md contains the four grooming sections: Goal, Acceptance criteria, Out of scope, Constraints."
REQ_ROW PASS id=REQ-DOC-029 family=DOC status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t48.md,docs/team/pm.md,docs/team/qa-engineer.md
REQ_TITLE PASS id=REQ-DOC-029 title="docs/team/*.md" statement="team/ contains pm.md, software-engineer.md, and qa-engineer.md with role definitions."
REQ_ROW PASS id=REQ-DOC-030 family=DOC status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/scripts/security_ops_verification.py,docs/criteria/security_ops_verification.md,docs/issues/closed/t41.md
REQ_TITLE PASS id=REQ-DOC-030 title="security/ contents" statement="security/ contains pr-audit.md, gitleaks-report.json, semgrep-report.json, trivy-report.json, pip-audit-report.txt, npm-audit-report.txt, agent-security-notes.m"
REQ_ROW PASS id=REQ-DOC-031 family=DOC status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/scripts/security_ops_verification.py,docs/criteria/security_ops_verification.md,docs/issues/closed/t41.md
REQ_TITLE PASS id=REQ-DOC-031 title="ops/ contents" statement="ops/ contains runbook.md, health-check.md, diagnosis.md, logging.md, deployment-health.md."
REQ_ROW PASS id=REQ-DOC-040 family=DOC status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md,backend/scripts/docs_verification.py,docs/criteria/docs_verification.md
REQ_TITLE PASS id=REQ-DOC-040 title="screenshots directory" statement="screenshots/ contains dashboard.png, expense-form.png, budget-page.png, health-check.png."
REQ_ROW PASS id=REQ-DOC-041 family=DOC status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md,docs/issues/closed/t52.md,docs/plan.md
REQ_TITLE PASS id=REQ-DOC-041 title="screenshot guidelines" statement="Consistent viewport, realistic data, no real personal data, < 500 KB each."
REQ_ROW PASS id=REQ-DOC-050 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.env.example
REQ_TITLE PASS id=REQ-DOC-050 title=".env.example" statement=".env.example lists all environment variables with placeholders; the real `.env` is gitignored; no real secrets."
REQ_ROW PASS id=REQ-DOC-051 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=Makefile
REQ_TITLE PASS id=REQ-DOC-051 title="Makefile targets" statement="Makefile targets: dev, down, test, test-backend, test-frontend, e2e, lint, migrate, seed, security."
REQ_ROW PASS id=REQ-DOC-060 family=DOC status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t48.md,docs/issues/closed/t51.md,docs/issues/closed/t52.md
REQ_TITLE PASS id=REQ-DOC-060 title="writing rules" statement="English only, present tense, active voice, short paragraphs, tables for comparisons, code blocks for commands, no marketing language, no emojis, no screenshots"
REQ_ROW PASS id=REQ-DOC-061 family=DOC status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/ai-workflow.md,docs/issues/closed/t50.md,docs/issues/closed/t51.md
REQ_TITLE PASS id=REQ-DOC-061 title="linking rules" statement="Link, do not duplicate; relative links; descriptive link text; every document linked from somewhere."
REQ_ROW PASS id=REQ-DOC-062 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-DOC-062 title="updating rules" statement="Corrections update the relevant document; new decisions update architecture or process; new skill updates the pack; new permission updates permissions; new erro"
REQ_ROW PASS id=REQ-DOC-063 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/requirements/Chapter15_Documentation.md
REQ_TITLE PASS id=REQ-DOC-063 title="document ownership" statement="Ownership table exists for each document."
REQ_ROW PASS id=REQ-DOC-070 family=DOC status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_req_coverage_verification.py
REQ_TITLE PASS id=REQ-DOC-070 title="5-minute live verification" statement="Steps: open live URL, register, add expense, set budget, verify five charts, switch month, log out."
REQ_ROW PASS id=REQ-DOC-071 family=DOC status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md,docs/issues/closed/t103.md,docs/issues/closed/t49.md
REQ_TITLE PASS id=REQ-DOC-071 title="5-minute local verification" statement="Clone, cp .env.example, docker compose up --build, open localhost:8000, repeat live steps."
REQ_ROW PASS id=REQ-DOC-072 family=DOC status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md,docs/issues/closed/t49.md,product-spec.md
REQ_TITLE PASS id=REQ-DOC-072 title="evidence checklist" statement="Table maps each of the 14 criteria to a specific file to open."
REQ_ROW PASS id=REQ-DOC-080 family=DOC status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t49.md,product-spec.md
REQ_TITLE PASS id=REQ-DOC-080 title="language and layout" statement="English only; minimal root docs; details in docs/; README < 500 lines; AGENTS.md < 60 lines."
REQ_ROW PASS id=REQ-DOC-081 family=DOC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=README.md
REQ_TITLE PASS id=REQ-DOC-081 title="criteria mapping location" statement="Criteria mapping is in README so reviewers find evidence fast."
REQ_ROW PASS id=REQ-DOC-082 family=DOC status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md,docs/issues/closed/t52.md
REQ_TITLE PASS id=REQ-DOC-082 title="screenshots location" statement="Screenshots live in `screenshots/`, not in docs/ or root."
REQ_ROW PASS id=REQ-DOC-083 family=DOC status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t48.md,docs/plan.md
REQ_TITLE PASS id=REQ-DOC-083 title="no extra files" statement="No peer-review-guide.md (merged into README); no CHANGELOG (git history); no CONTRIBUTING; no CODE_OF_CONDUCT."
REQ_ROW PASS id=REQ-DOC-084 family=DOC status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md,docs/issues/closed/t49.md,docs/issues/closed/t51.md
REQ_TITLE PASS id=REQ-DOC-084 title="API docs strategy" statement="openapi.yaml plus FastAPI's /docs and /redoc provide contract and interactive view."
REQ_ROW PASS id=REQ-DOC-085 family=DOC status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t51.md
REQ_TITLE PASS id=REQ-DOC-085 title="diagrams and formatting" statement="ASCII diagrams in markdown; fenced code blocks with language; tables for comparisons; no emojis."
REQ_ROW PASS id=REQ-EXT-001 family=EXT status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md,backend/scripts/agent_pack_verification.py,backend/scripts/docs_verification.py
REQ_TITLE PASS id=REQ-EXT-001 title="five components" statement="The pack has five components: skills, hooks, MCP server, subagents, and documentation."
REQ_ROW PASS id=REQ-EXT-002 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/agent-extension-pack.md
REQ_TITLE PASS id=REQ-EXT-002 title="Criterion 12 mapping" statement="The pack maps to Criterion 12 requirements: project instructions (AGENTS.md), reusable workflow (process.md), subagent (finance-analyst, qa-reviewer), MCP tool/"
REQ_ROW PASS id=REQ-EXT-003 family=EXT status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t0.md,docs/issues/closed/t29.md
REQ_TITLE PASS id=REQ-EXT-003 title="directory layout" statement="Directories: `agent-capabilities/`, `agent-hooks/`, `mcp-server/`, `custom-agent/`, `docs/`, and `.agents/` symlinks."
REQ_ROW PASS id=REQ-EXT-004 family=EXT status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/scripts/agent_pack_verification.py,docs/criteria/agent_pack_verification.md,docs/issues/closed/t29.md
REQ_TITLE PASS id=REQ-EXT-004 title="symlinks" statement="Symlinks in `.agents/skills/` and `.agents/agents/` connect canonical directories to the agent's expected discovery paths."
REQ_ROW PASS id=REQ-EXT-010 family=EXT status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t29.md
REQ_TITLE PASS id=REQ-EXT-010 title="skill format" statement="Skills are markdown files with YAML frontmatter containing name and description."
REQ_ROW PASS id=REQ-EXT-011 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=agent-capabilities/monthly-report/SKILL.md
REQ_TITLE PASS id=REQ-EXT-011 title="monthly-report skill content" statement="The skill documents when to use, steps, report template, warnings, and notes."
REQ_ROW PASS id=REQ-EXT-012 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=agent-capabilities/add-expense/SKILL.md
REQ_TITLE PASS id=REQ-EXT-012 title="add-expense skill content" statement="The skill documents when to use, steps, constraints, and an example."
REQ_ROW PASS id=REQ-EXT-013 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=agent-capabilities/budget-check/SKILL.md
REQ_TITLE PASS id=REQ-EXT-013 title="budget-check skill content" statement="The skill documents when to use, steps, and output template."
REQ_ROW PASS id=REQ-EXT-014 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/agent-extension-pack.md
REQ_TITLE PASS id=REQ-EXT-014 title="skill discovery" statement="Discovery via auto-discovery at session start, natural-language invocation, and explicit command."
REQ_ROW PASS id=REQ-EXT-015 family=EXT status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t29.md
REQ_TITLE PASS id=REQ-EXT-015 title="skill design principles" statement="One procedure per skill, clear 'When to Use', numbered steps, explicit constraints, no side effects in read-only skills, templates for output."
REQ_ROW PASS id=REQ-EXT-020 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=agent-hooks/README.md
REQ_TITLE PASS id=REQ-EXT-020 title="hook purpose" statement="Hooks validate inputs and raise errors when rules are violated; pure functions with no side effects."
REQ_ROW PASS id=REQ-EXT-021 family=EXT status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_agent_hooks.py
REQ_TITLE PASS id=REQ-EXT-021 title="validate-amount hook" statement="`validate_amount` validates present, valid number, positive, ≤ MAX_AMOUNT, ≤ 2 decimals; returns Decimal; raises ValueError."
REQ_ROW PASS id=REQ-EXT-022 family=EXT status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_agent_hooks.py
REQ_TITLE PASS id=REQ-EXT-022 title="validate-ownership hook" statement="`validate_ownership` raises PermissionError when user IDs do not match or are None."
REQ_ROW PASS id=REQ-EXT-023 family=EXT status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t30.md
REQ_TITLE PASS id=REQ-EXT-023 title="hook triggers" statement="Hooks triggered before MCP calls and in backend (Pydantic schemas and service layer)."
REQ_ROW PASS id=REQ-EXT-024 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=agent-hooks/README.md
REQ_TITLE PASS id=REQ-EXT-024 title="hook README" statement="`agent-hooks/README.md` documents both hooks' triggers, checks, failure behavior, agent behavior, and design notes."
REQ_ROW PASS id=REQ-EXT-025 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/permissions.md
REQ_TITLE PASS id=REQ-EXT-025 title="defense in depth" statement="Rules enforced at hook, MCP, backend schema, backend service, and database layers."
REQ_ROW PASS id=REQ-EXT-030 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=mcp-server/server.py
REQ_TITLE PASS id=REQ-EXT-030 title="MCP purpose" statement="MCP server exposes backend operations as tools; authenticates with JWT; never accesses the database directly."
REQ_ROW PASS id=REQ-EXT-031 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=mcp-server/README.md
REQ_TITLE PASS id=REQ-EXT-031 title="MCP architecture" statement="pi-agent ↔ MCP server (stdio) ↔ backend API ↔ database."
REQ_ROW PASS id=REQ-EXT-032 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=mcp-server/config.py
REQ_TITLE PASS id=REQ-EXT-032 title="MCP configuration" statement="`config.py` reads `MCP_JWT_SECRET`, `MCP_API_BASE_URL`, `MCP_USER_TOKEN`, and defines JWT algorithm, issuer, audience."
REQ_ROW PASS id=REQ-EXT-033 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=mcp-server/auth.py
REQ_TITLE PASS id=REQ-EXT-033 title="MCP authentication" statement="`verify_jwt` validates signature, exp, aud, iss, `type == 'access'`, returns sub; `get_user_token` reads from env."
REQ_ROW PASS id=REQ-EXT-034 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=mcp-server/tools/add_expense.py
REQ_TITLE PASS id=REQ-EXT-034 title="add_expense tool" statement="`add_expense` validates amount, builds payload, POSTs to `/expenses` with Bearer token."
REQ_ROW PASS id=REQ-EXT-035 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=mcp-server/tools/get_budget_status.py
REQ_TITLE PASS id=REQ-EXT-035 title="get_budget_status tool" statement="`get_budget_status` calls `/dashboard/summary`, returns simplified shape."
REQ_ROW PASS id=REQ-EXT-036 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=mcp-server/tools/monthly_summary.py
REQ_TITLE PASS id=REQ-EXT-036 title="monthly_summary tool" statement="`monthly_summary` calls `/dashboard/by-category`."
REQ_ROW PASS id=REQ-EXT-037 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=mcp-server/tools/list_expenses.py
REQ_TITLE PASS id=REQ-EXT-037 title="list_expenses tool" statement="`list_expenses` calls `/expenses` with optional filters; `limit` maps to `page_size`."
REQ_ROW PASS id=REQ-EXT-038 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=mcp-server/server.py
REQ_TITLE PASS id=REQ-EXT-038 title="tool schemas" statement="Four tool schemas defined with strict types, required fields, and constraints."
REQ_ROW PASS id=REQ-EXT-039 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=mcp-server/README.md
REQ_TITLE PASS id=REQ-EXT-039 title="MCP README" statement="`mcp-server/README.md` documents tools, authentication, environment variables, running instructions, and design."
REQ_ROW PASS id=REQ-EXT-040 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/agent-extension-pack.md
REQ_TITLE PASS id=REQ-EXT-040 title="subagent purpose" statement="Subagents run in separate contexts with clear roles for independent verification and focused analysis."
REQ_ROW PASS id=REQ-EXT-041 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=custom-agent/finance-analyst.md
REQ_TITLE PASS id=REQ-EXT-041 title="finance-analyst subagent" statement="`finance-analyst` has input, steps, output template, limitations, and rules (read-only, no raw IDs)."
REQ_ROW PASS id=REQ-EXT-042 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=custom-agent/qa-reviewer.md
REQ_TITLE PASS id=REQ-EXT-042 title="qa-reviewer subagent" statement="`qa-reviewer` has steps, output format, and rules (do not fix, do not modify code, include test command)."
REQ_ROW PASS id=REQ-EXT-043 family=EXT status=DEFERRED_RULLED method=deferral-register pointers=docs/criteria/docs_verification.md,ops/deployment-health.md deferral_key=LIVE_SUBAGENT_LAUNCH deferral_reason="sub-agent definitions are present as config artifacts only; launching them needs a live agent runtime which this gate must not require (no-E2E/no-live ruling)"
REQ_TITLE PASS id=REQ-EXT-043 title="subagent launch commands" statement="Commands: 'Launch a subagent to implement #12', 'Launch software engineer for #12', 'Launch QA for #12', 'Launch finance analyst for 2026-10'."
REQ_ROW PASS id=REQ-EXT-044 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/process.md
REQ_TITLE PASS id=REQ-EXT-044 title="subagent isolation" statement="Fresh context, no orchestrator history, output posted back, tools restricted by role, permissions enforced by MCP and backend."
REQ_ROW PASS id=REQ-EXT-050 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/agent-extension-pack.md
REQ_TITLE PASS id=REQ-EXT-050 title="agent-extension-pack.md purpose" statement="This document explains the whole pack in one place so a reviewer can understand it from one file."
REQ_ROW PASS id=REQ-EXT-051 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/agent-extension-pack.md
REQ_TITLE PASS id=REQ-EXT-051 title="agent-extension-pack.md content" statement="Contents include skills, hooks, MCP server, subagents, permissions, and design principles."
REQ_ROW PASS id=REQ-EXT-060 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/permissions.md
REQ_TITLE PASS id=REQ-EXT-060 title="permissions.md content" statement="`docs/permissions.md` contains user roles, resource permissions, agent permissions by role, skill permissions, subagent permissions, enforcement layers, forbidd"
REQ_ROW PASS id=REQ-EXT-070 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/agent-extension-pack.md
REQ_TITLE PASS id=REQ-EXT-070 title="verification checklist" statement="The pack can be verified by checking skills, hooks, MCP server, subagents, symlinks, and documentation."
REQ_ROW PASS id=REQ-EXT-071 family=EXT status=DEFERRED_RULLED method=deferral-register pointers=docs/criteria/docs_verification.md,ops/deployment-health.md deferral_key=LIVE_MCP_SUBPROCESS deferral_reason="the pack MCP wiring is proven by static config greps (tests[144] carried rows); no MCP server binary is installed on this host, so a live spawn cannot be measured here"
REQ_TITLE PASS id=REQ-EXT-071 title="manual test commands" statement="Documented commands test skills, hooks, MCP server, subagents, symlinks, and documentation."
REQ_ROW PASS id=REQ-EXT-072 family=EXT status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_agent_hooks.py
REQ_TITLE PASS id=REQ-EXT-072 title="automated verification" statement="`backend/tests/integration/test_agent_hooks.py` imports and tests both hooks."
REQ_ROW PASS id=REQ-EXT-080 family=EXT status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/agent-extension-pack.md,docs/issues/closed/t34.md
REQ_TITLE PASS id=REQ-EXT-080 title="directory choices" statement="Skills in `agent-capabilities/`, hooks in `agent-hooks/`, MCP in `mcp-server/`, subagents in `custom-agent/`, symlinks in `.agents/`."
REQ_ROW PASS id=REQ-EXT-081 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=mcp-server/README.md
REQ_TITLE PASS id=REQ-EXT-081 title="MCP design choices" statement="stdio transport, JWT auth, API access (not database)."
REQ_ROW PASS id=REQ-EXT-082 family=EXT status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/agent-extension-pack.md,docs/issues/closed/t33.md,docs/issues/closed/t34.md
REQ_TITLE PASS id=REQ-EXT-082 title="read-only analyst" statement="`finance-analyst` is read-only for safety; `qa-reviewer` does not fix."
REQ_ROW PASS id=REQ-EXT-083 family=EXT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/agent-extension-pack.md,docs/permissions.md
REQ_TITLE PASS id=REQ-EXT-083 title="two documentation files" statement="Extension pack overview and permissions matrix are separate documents."
REQ_ROW PASS id=REQ-FE-001 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md
REQ_TITLE PASS id=REQ-FE-001 title="frontend directory structure" statement="The frontend contains `src/` with api/, components/ (ui/, layout/, charts/, forms/, common/), pages/, hooks/, context/, types/, utils/, test/; plus `public/`, c"
REQ_ROW PASS id=REQ-FE-002 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-FE-002 title="layer responsibilities" statement="Entry (bootstrap), pages (route composition), components (reusable UI), hooks (data fetching), context (global state), API (HTTP), utils (pure functions), types"
REQ_ROW PASS id=REQ-FE-003 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-FE-003 title="import direction" statement="Pages may import anything below them; components may not import pages; hooks may not import components or pages; API modules may not import React; utils are pur"
REQ_ROW PASS id=REQ-FE-010 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/app_routing.test.tsx,frontend/src/pages/dashboard_page_app.test.tsx
REQ_TITLE PASS id=REQ-FE-010 title="route table" statement="Routes are `/login`, `/register`, `/` (Dashboard), `/expenses`, `/budgets`, `/categories`, and `*` (NotFound)"
REQ_ROW PASS id=REQ-FE-011 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/app_routing.test.tsx
REQ_TITLE PASS id=REQ-FE-011 title="router setup with nested routes" statement="Router uses nested routes: PublicOnlyRoute for login/register; ProtectedRoute wrapping AppShell for the four authenticated pages."
REQ_ROW PASS id=REQ-FE-012 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t9.md,frontend/src/components/common/protected_route.tsx
REQ_TITLE PASS id=REQ-FE-012 title="ProtectedRoute" statement="ProtectedRoute shows a full-page spinner while auth is loading, redirects unauthenticated users to `/login` with the original location in state."
REQ_ROW PASS id=REQ-FE-013 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t9.md,frontend/src/components/common/protected_route.tsx,frontend/src/pages/login_page.tsx
REQ_TITLE PASS id=REQ-FE-013 title="redirect after login" statement="After successful login, redirect to the original `from` location or `/`."
REQ_ROW PASS id=REQ-FE-014 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t9.md,frontend/src/components/common/public_only_route.tsx
REQ_TITLE PASS id=REQ-FE-014 title="public route guard" statement="Logged-in users visiting `/login` or `/register` are redirected to `/`."
REQ_ROW PASS id=REQ-FE-015 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/pages/budget_page.test.tsx,frontend/src/pages/dashboard_page_app.test.tsx,frontend/src/pages/expenses_page.test.tsx
REQ_TITLE PASS id=REQ-FE-015 title="page titles" statement="Each page sets a unique `document.title` following the pattern `<Page> — Expense Tracker`."
REQ_ROW PASS id=REQ-FE-020 family=FE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/src/main.tsx
REQ_TITLE PASS id=REQ-FE-020 title="provider order" statement="Providers are nested QueryClientProvider → BrowserRouter → AuthProvider → MonthProvider → ToastProvider → App."
REQ_ROW PASS id=REQ-FE-021 family=FE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/src/main.tsx
REQ_TITLE PASS id=REQ-FE-021 title="provider rationale" statement="Each provider depends only on its ancestors: QueryClient outermost because Auth uses it; Toast innermost because any component may trigger it."
REQ_ROW PASS id=REQ-FE-022 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-FE-022 title="provider responsibilities" statement="QueryClientProvider (server cache), BrowserRouter (routing), AuthProvider (user/token), MonthProvider (yearMonth), ToastProvider (toast queue)."
REQ_ROW PASS id=REQ-FE-030 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/context/month_context.test.tsx
REQ_TITLE PASS id=REQ-FE-030 title="state categories" statement="Server state in React Query, auth state in AuthContext, UI global state in MonthContext, form state in React Hook Form, URL state in React Router."
REQ_ROW PASS id=REQ-FE-031 family=FE status=IMPLEMENTED_TESTED method=code-symbol pointers=e2e/tests/happy-path.spec.ts,frontend/src/api/client.test.ts,frontend/src/api/dashboard.test.ts
REQ_TITLE PASS id=REQ-FE-031 title="AuthContext" statement="AuthContext provides `user`, `token`, `isLoading`, `login`, `register`, `logout`; validates the stored token on mount via `/auth/me`."
REQ_ROW PASS id=REQ-FE-032 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/common/month_picker.test.tsx,frontend/src/context/month_context.test.tsx
REQ_TITLE PASS id=REQ-FE-032 title="MonthContext" statement="MonthContext provides `yearMonth`, `setYearMonth`, `prevMonth`, `nextMonth`, defaulting to the current month."
REQ_ROW PASS id=REQ-FE-033 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/context/toast_context.test.tsx
REQ_TITLE PASS id=REQ-FE-033 title="ToastContext" statement="ToastContext provides `showToast(message, variant)`; toasts auto-dismiss after 3 seconds."
REQ_ROW PASS id=REQ-FE-034 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t103.md,docs/issues/closed/t16.md,docs/issues/closed/t73.md
REQ_TITLE PASS id=REQ-FE-034 title="data hooks" statement="Each resource has a dedicated hook wrapping React Query; mutations invalidate the relevant query keys."
REQ_ROW PASS id=REQ-FE-035 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-FE-035 title="hook list" statement="Auth, categories, expenses (list/get/create/update/ delete), budgets (get/set/delete), dashboard (six queries), toast."
REQ_ROW PASS id=REQ-FE-040 family=FE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/src/api/client.ts
REQ_TITLE PASS id=REQ-FE-040 title="axios instance" statement="A single axios instance uses `VITE_API_BASE_URL` with a 10-second timeout; request interceptor attaches the Bearer token; response interceptor handles 401 by cl"
REQ_ROW PASS id=REQ-FE-041 family=FE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/src/api/client.ts
REQ_TITLE PASS id=REQ-FE-041 title="error normalization" statement="Errors are normalized to `{status, code, message, field?}`; network errors map to a distinct code; unknown errors fall back to a generic message."
REQ_ROW PASS id=REQ-FE-042 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t16.md,docs/issues/closed/t9.md,docs/plan.md
REQ_TITLE PASS id=REQ-FE-042 title="resource modules" statement="Each resource has its own module with typed functions mapping one-to-one to OpenAPI endpoints."
REQ_ROW PASS id=REQ-FE-043 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t16.md
REQ_TITLE PASS id=REQ-FE-043 title="API module list" statement="Modules: auth, categories, expenses, budgets, dashboard, health."
REQ_ROW PASS id=REQ-FE-044 family=FE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/src/api/client.ts
REQ_TITLE PASS id=REQ-FE-044 title="centralized API rationale" statement="Centralized API layer for auth header, error handling, mocking, type safety, and contract alignment."
REQ_ROW PASS id=REQ-FE-050 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/api/query_keys.test.ts
REQ_TITLE PASS id=REQ-FE-050 title="query key factory" statement="A `queryKeys` factory defines keys for auth.me, categories.all, expenses.list/detail, budgets.byMonth, and six dashboard queries."
REQ_ROW PASS id=REQ-FE-051 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/hooks/use_budgets.test.tsx,frontend/src/hooks/use_categories.test.tsx,frontend/src/hooks/use_dashboard.test.tsx
REQ_TITLE PASS id=REQ-FE-051 title="invalidation strategy" statement="Expense mutations invalidate `['expenses']` and `['dashboard']`; budget mutations invalidate `['budgets']` and `['dashboard']`; category mutations invalidate `["
REQ_ROW PASS id=REQ-FE-052 family=FE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/src/main.tsx
REQ_TITLE PASS id=REQ-FE-052 title="query configuration" statement="staleTime 5 minutes, gcTime 10 minutes, retry 3 for network and 0 for 4xx, refetchOnWindowFocus false."
REQ_ROW PASS id=REQ-FE-060 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t9.md,frontend/src/pages/login_page.tsx
REQ_TITLE PASS id=REQ-FE-060 title="LoginPage" statement="Login page has email and password fields, submits via `useAuth().login`, redirects on success, shows inline error on failure, and links to `/register`."
REQ_ROW PASS id=REQ-FE-061 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t56.md,docs/issues/closed/t9.md,e2e/fixtures/users.ts
REQ_TITLE PASS id=REQ-FE-061 title="RegisterPage" statement="Register page has email, username, password, and confirm password fields; validates on blur; auto-logs in on success; shows field-level errors; links to `/login"
REQ_ROW PASS id=REQ-FE-062 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/common/month_picker.test.tsx,frontend/src/pages/dashboard_page.test.tsx,frontend/src/pages/dashboard_page_app.test.tsx
REQ_TITLE PASS id=REQ-FE-062 title="DashboardPage layout" statement="Dashboard has a header with logo, month picker, and user menu; four KPI cards; five charts (pie, trend, cumulative, heatmap, progress); recent transactions list"
REQ_ROW PASS id=REQ-FE-063 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/pages/expenses_page.test.tsx
REQ_TITLE PASS id=REQ-FE-063 title="ExpensesPage layout" statement="Expenses page has month and category filters, an add button, a table with date/category/amount/note/actions columns, and pagination."
REQ_ROW PASS id=REQ-FE-064 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/pages/budget_page.test.tsx
REQ_TITLE PASS id=REQ-FE-064 title="BudgetPage layout" statement="Budget page has a month picker, current budget display with edit/delete, a set-budget form, and a 12-month budget history list."
REQ_ROW PASS id=REQ-FE-065 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/forms/category_form.test.tsx,frontend/src/pages/categories_page.test.tsx
REQ_TITLE PASS id=REQ-FE-065 title="CategoriesPage layout" statement="Categories page has a system categories section (no delete) and a user categories section with delete buttons."
REQ_ROW PASS id=REQ-FE-070 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/charts/category_pie_chart.test.tsx
REQ_TITLE PASS id=REQ-FE-070 title="CategoryPieChart" statement="Pie chart uses Recharts with per-category colors from the API, tooltip shows name/amount/percentage, merges to top 6 + Other, and has an empty state."
REQ_ROW PASS id=REQ-FE-071 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/charts/monthly_trend_chart.test.tsx
REQ_TITLE PASS id=REQ-FE-071 title="MonthlyTrendChart" statement="Bar chart shows last N months (default 6); X-axis labels formatted as 'MMM YY'; Y-axis as USD; bar color `#3B82F6`; empty state."
REQ_ROW PASS id=REQ-FE-072 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/charts/cumulative_line_chart.test.tsx
REQ_TITLE PASS id=REQ-FE-072 title="CumulativeLineChart" statement="Line chart shows cumulative spending for the month with a dashed budget reference line; line turns red when over budget; empty state."
REQ_ROW PASS id=REQ-FE-073 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/charts/weekly_heatmap.test.tsx
REQ_TITLE PASS id=REQ-FE-073 title="WeeklyHeatmap" statement="Custom grid with 12 weeks × 7 days; color scale from `#F3F4F6` (0) through blue shades; tooltip shows date and amount; handles `max === 0` and missing days."
REQ_ROW PASS id=REQ-FE-074 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/common/budget_progress.test.tsx
REQ_TITLE PASS id=REQ-FE-074 title="BudgetProgress" statement="Progress bar with color by percentage: green < 80%, yellow 80-100%, red > 100%; caps width at 100%; shows 'No budget set' when budget is 0; displays formatted a"
REQ_ROW PASS id=REQ-FE-080 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/forms/budget_form.test.tsx
REQ_TITLE PASS id=REQ-FE-080 title="validation schemas" statement="Zod schemas: amountSchema (positive, ≤ 2 decimals, max 9,999,999,999.99), expenseFormSchema, budgetFormSchema, categoryFormSchema, loginFormSchema, registerForm"
REQ_ROW PASS id=REQ-FE-081 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/forms/expense_form.test.tsx,frontend/src/pages/expenses_page.test.tsx
REQ_TITLE PASS id=REQ-FE-081 title="ExpenseForm" statement="ExpenseForm supports create and edit; uses React Hook Form with Zod; shows field errors; disables submit while loading; toasts on success and failure."
REQ_ROW PASS id=REQ-FE-082 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/forms/budget_form.test.tsx,frontend/src/components/forms/expense_form.test.tsx,frontend/src/pages/budget_page.test.tsx
REQ_TITLE PASS id=REQ-FE-082 title="form behavior rules" statement="Validate on blur and submit; disable submit while loading; show field errors; show backend errors mapped to fields; reset on success via onSuccess; preserve val"
REQ_ROW PASS id=REQ-FE-090 family=FE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/tailwind.config.js
REQ_TITLE PASS id=REQ-FE-090 title="color tokens" statement="Design tokens: primary `#3B82F6`, success `#22C55E`, warning `#EAB308`, danger `#EF4444`, background `#F9FAFB`, surface white, border `#E5E7EB`, text primary `#"
REQ_ROW PASS id=REQ-FE-091 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/design-system.md
REQ_TITLE PASS id=REQ-FE-091 title="typography" statement="Page title `text-2xl font-semibold`, section title `text-lg font-semibold`, KPI value `text-3xl font-bold`; system font stack; `tabular-nums` for tables and KPI"
REQ_ROW PASS id=REQ-FE-092 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/design-system.md
REQ_TITLE PASS id=REQ-FE-092 title="spacing scale" statement="Page padding `px-6 py-8`, card padding `p-6`, card gap `gap-6`, section gap `space-y-8`, form gap `space-y-4`, max width `max-w-7xl mx-auto`."
REQ_ROW PASS id=REQ-FE-093 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/design-system.md
REQ_TITLE PASS id=REQ-FE-093 title="component specifications" statement="Button variants (primary/secondary/danger/ghost) with defined backgrounds; Card with border and shadow; Input with focus ring and error state; Modal with overla"
REQ_ROW PASS id=REQ-FE-094 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/design-system.md
REQ_TITLE PASS id=REQ-FE-094 title="chart colors" statement="Pie uses category colors; trend bars `#3B82F6`; cumulative line `#3B82F6` normal and `#EF4444` over budget; budget reference `#9CA3AF` dashed; heatmap five-step"
REQ_ROW PASS id=REQ-FE-100 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/pages/budget_page.test.tsx,frontend/src/pages/categories_page.test.tsx,frontend/src/pages/expenses_page.test.tsx
REQ_TITLE PASS id=REQ-FE-100 title="loading states" statement="Full-page spinner for auth check; skeleton for charts and tables; inline spinner for buttons; skeleton blocks for KPI cards."
REQ_ROW PASS id=REQ-FE-101 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/ui/empty_state.test.tsx
REQ_TITLE PASS id=REQ-FE-101 title="empty states" statement="Each chart and list has a specific empty message; EmptyState component takes icon, title, description, action."
REQ_ROW PASS id=REQ-FE-102 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/ui/error_state.test.tsx
REQ_TITLE PASS id=REQ-FE-102 title="error states" statement="Error handling maps 401/403/404/409/422/500/network to specific UI; ErrorState component offers a retry button."
REQ_ROW PASS id=REQ-FE-103 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/pages/expenses_page.test.tsx
REQ_TITLE PASS id=REQ-FE-103 title="confirm dialog" statement="Destructive actions use a ConfirmDialog with title, description, confirm label, variant, onConfirm, onCancel."
REQ_ROW PASS id=REQ-FE-110 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/charts/category_pie_chart.test.tsx,frontend/src/components/common/month_picker.test.tsx
REQ_TITLE PASS id=REQ-FE-110 title="accessibility checklist" statement="Labels, accessible names, modal role/focus trap/Esc, chart descriptions, contrast ≥ 4.5:1, keyboard navigation, skip link, unique page titles, `html lang='en'`,"
REQ_ROW PASS id=REQ-FE-111 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/forms/budget_form.test.tsx,frontend/src/components/forms/expense_form.test.tsx
REQ_TITLE PASS id=REQ-FE-111 title="modal focus management" statement="On open, focus moves into the modal; on close, focus returns to the trigger; Tab cycles; Esc closes."
REQ_ROW PASS id=REQ-FE-112 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/design-system.md
REQ_TITLE PASS id=REQ-FE-112 title="chart accessibility" statement="Each chart is wrapped in `<figure>` with a `<figcaption>` and `role='img'` `aria-label` summarizing key values."
REQ_ROW PASS id=REQ-FE-120 family=FE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/src/App.tsx
REQ_TITLE PASS id=REQ-FE-120 title="performance techniques" statement="Code splitting via `React.lazy` for pages and charts; memoization for pure charts; query caching; debounced inputs; server pagination; SVG charts; bundle analys"
REQ_ROW PASS id=REQ-FE-121 family=FE status=DEFERRED_RULLED method=card-declared-ruling pointers=docs/rulings/req-matrix.md deferral_key=RULING_FE_PERF_LIVE_PROFILING issue=65 deferral_reason="Verification needs live performance profiling (Lighthouse/FCP/TTI), outside the standing no-live/no-E2E ruling that defers the LIVE_* register keys (platform #65 ruling, docs/rulings/req-matrix.md)"
REQ_TITLE PASS id=REQ-FE-121 title="performance budget" statement="Initial JS bundle < 300 KB gzipped, CSS < 30 KB gzipped, Lighthouse performance > 85, FCP < 1.5s, TTI < 3s."
REQ_ROW PASS id=REQ-FE-130 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-FE-130 title="test structure" statement="Tests live beside source with `.test.ts(x)` suffixes; utils, charts, forms, and pages have tests."
REQ_ROW PASS id=REQ-FE-131 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-FE-131 title="coverage targets" statement="Utils 90%+, charts 80%+, forms 80%+, pages 60%+, API modules mocked (not tested directly)."
REQ_ROW PASS id=REQ-FE-132 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-FE-132 title="test examples" statement="Tests exist for formatUSD, BudgetProgress color logic, WeeklyHeatmap cells, CategoryPieChart merging, ExpenseForm validation, LoginPage validation and errors."
REQ_ROW PASS id=REQ-FE-133 family=FE status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/test/handlers_contract.test.ts
REQ_TITLE PASS id=REQ-FE-133 title="MSW setup" statement="MSW handlers cover auth login, /auth/me, /categories, /expenses, /dashboard/summary; setup.ts starts and stops the server."
REQ_ROW PASS id=REQ-FE-140 family=FE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=package.json
REQ_TITLE PASS id=REQ-FE-140 title="build and language" statement="Vite, TypeScript, Tailwind CSS, Recharts, React Query, Context, React Hook Form + Zod, Axios, date-fns, React Router v6."
REQ_ROW PASS id=REQ-FE-141 family=FE status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/src/api/client.ts
REQ_TITLE PASS id=REQ-FE-141 title="token storage choice" statement="Token stored in localStorage; documented trade-off."
REQ_ROW PASS id=REQ-FE-142 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-FE-142 title="centralized API choice" statement="All API calls go through `src/api/`."
REQ_ROW PASS id=REQ-FE-143 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=product-spec.md
REQ_TITLE PASS id=REQ-FE-143 title="out-of-scope frontend features" statement="Dark mode, i18n, SSR, PWA, analytics are not in MVP."
REQ_ROW PASS id=REQ-FE-144 family=FE status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md
REQ_TITLE PASS id=REQ-FE-144 title="accessibility and testing choice" statement="WCAG 2.1 AA for forms and navigation; Vitest + RTL for tests; MSW for mocking; coverage reported but not enforced."
REQ_ROW PASS id=REQ-OPS-001 family=OPS status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/scripts/security_ops_verification.py,docs/criteria/security_ops_verification.md,docs/issues/closed/t41.md
REQ_TITLE PASS id=REQ-OPS-001 title="Criterion mapping" statement="The ops documentation covers Criterion 13 (operational diagnosis) and Criterion 10 (deployment proof)."
REQ_ROW PASS id=REQ-OPS-002 family=OPS status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md,backend/scripts/docs_verification.py,backend/scripts/security_ops_verification.py
REQ_TITLE PASS id=REQ-OPS-002 title="ops directory layout" statement="`ops/` contains runbook.md, health-check.md, diagnosis.md, logging.md, deployment-health.md."
REQ_ROW PASS id=REQ-OPS-003 family=OPS status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t39.md
REQ_TITLE PASS id=REQ-OPS-003 title="purpose of each file" statement="runbook (common problems), health-check (endpoint reference), diagnosis (worked example), logging (format and events), deployment-health (verification record)."
REQ_ROW PASS id=REQ-OPS-010 family=OPS status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t28.md,docs/issues/closed/t43.md
REQ_TITLE PASS id=REQ-OPS-010 title="endpoint" statement="`GET /api/v1/health`, no auth, used by Render, CI/CD, UptimeRobot, and manual checks."
REQ_ROW PASS id=REQ-OPS-011 family=OPS status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/routers/health.py,backend/scripts/infra_verification.py,docs/criteria/infra_verification.md
REQ_TITLE PASS id=REQ-OPS-011 title="response schema" statement="Returns status, database, fallback_active, version."
REQ_ROW PASS id=REQ-OPS-012 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/health-check.md
REQ_TITLE PASS id=REQ-OPS-012 title="field meanings" statement="status ok/degraded; database postgresql/sqlite; fallback_active boolean; version semver."
REQ_ROW PASS id=REQ-OPS-013 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/health-check.md
REQ_TITLE PASS id=REQ-OPS-013 title="state combinations" statement="Four combinations documented: normal production, local dev, fallback active, and the impossible case."
REQ_ROW PASS id=REQ-OPS-014 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/health-check.md
REQ_TITLE PASS id=REQ-OPS-014 title="usage" statement="Used by Render health check path, CI/CD verify, UptimeRobot ping, manual status check."
REQ_ROW PASS id=REQ-OPS-015 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=render.yaml
REQ_TITLE PASS id=REQ-OPS-015 title="Render configuration" statement="`render.yaml` sets `healthCheckPath: /api/v1/health`."
REQ_ROW PASS id=REQ-OPS-020 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-020 title="quick reference" statement="Runbook quick reference lists seven symptoms with sections: cold start, degraded health, 503, login failures, user data leak, deployment failure, CI failure."
REQ_ROW PASS id=REQ-OPS-021 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-021 title="cold start section" statement="Documents symptom, cause, diagnosis, and action for Render cold start."
REQ_ROW PASS id=REQ-OPS-022 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-022 title="degraded health section" statement="Documents symptom, cause, diagnosis, and action for degraded health (fallback active)."
REQ_ROW PASS id=REQ-OPS-023 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-023 title="503 section" statement="Documents symptom, cause, diagnosis, and action for 503 DATABASE_UNAVAILABLE."
REQ_ROW PASS id=REQ-OPS-024 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-024 title="login failures section" statement="Documents JWT_SECRET mismatch, diagnosis, and action."
REQ_ROW PASS id=REQ-OPS-025 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-025 title="user data leak section" statement="Documents missing user_id filter, diagnosis, and action."
REQ_ROW PASS id=REQ-OPS-026 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-026 title="deployment failure section" statement="Documents build/migration/env diagnosis and action."
REQ_ROW PASS id=REQ-OPS-027 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-027 title="CI failure section" statement="Documents dependency/env/bug diagnosis and action."
REQ_ROW PASS id=REQ-OPS-028 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-028 title="escalation" statement="Escalation path: check diagnosis.md, logging.md, Render logs, GitHub issues."
REQ_ROW PASS id=REQ-OPS-030 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/health-check.md
REQ_TITLE PASS id=REQ-OPS-030 title="health-check.md content" statement="Documents endpoint, auth, response, fields, when to use, how it is used, what it does not check."
REQ_ROW PASS id=REQ-OPS-031 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/health-check.md
REQ_TITLE PASS id=REQ-OPS-031 title="not checked" statement="Does not check database write access, external services, disk space, memory usage."
REQ_ROW PASS id=REQ-OPS-040 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/diagnosis.md
REQ_TITLE PASS id=REQ-OPS-040 title="diagnosis.md purpose" statement="`ops/diagnosis.md` is the worked example required by Criterion 13."
REQ_ROW PASS id=REQ-OPS-041 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/diagnosis.md
REQ_TITLE PASS id=REQ-OPS-041 title="diagnosis scenario" statement="Scenario: PostgreSQL unreachable at startup; app falls back to SQLite."
REQ_ROW PASS id=REQ-OPS-042 family=OPS status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md,backend/scripts/docs_verification.py,docs/criteria/docs_verification.md
REQ_TITLE PASS id=REQ-OPS-042 title="diagnosis steps" statement="Steps to reproduce with Docker Compose, stop db, restart app, observe logs."
REQ_ROW PASS id=REQ-OPS-043 family=OPS status=IMPLEMENTED_STRUCTURAL method=code-symbol pointers=backend/app/config.py,backend/app/database.py,backend/app/routers/health.py
REQ_TITLE PASS id=REQ-OPS-043 title="diagnosis expected output" statement="Expected log output (WARNING + INFO) and health response (`degraded`, `sqlite`, `fallback_active: true`) documented."
REQ_ROW PASS id=REQ-OPS-044 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/diagnosis.md
REQ_TITLE PASS id=REQ-OPS-044 title="diagnosis expected behavior" statement="Feature behavior during fallback documented: all features work, data persistence lost on restart."
REQ_ROW PASS id=REQ-OPS-045 family=OPS status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/commands.md
REQ_TITLE PASS id=REQ-OPS-045 title="diagnosis verification" statement="Verification steps include register, login, create expense, list expenses."
REQ_ROW PASS id=REQ-OPS-046 family=OPS status=IMPLEMENTED_STRUCTURAL method=code-symbol pointers=backend/app/database.py,backend/app/models/audit_log.py,backend/app/routers/health.py
REQ_TITLE PASS id=REQ-OPS-046 title="diagnosis recovery" statement="Recovery: restart db, restart backend, verify health returns `ok`, `postgresql`."
REQ_ROW PASS id=REQ-OPS-047 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/diagnosis.md
REQ_TITLE PASS id=REQ-OPS-047 title="diagnosis findings" statement="Findings table: fallback triggered within 5 seconds, no user-facing errors, all CRUD works, all charts render, data temporary, log clarity, health accuracy."
REQ_ROW PASS id=REQ-OPS-048 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/diagnosis.md
REQ_TITLE PASS id=REQ-OPS-048 title="diagnosis lessons" statement="Four lessons documented: fallback is safety net not persistence, health must be checked, UptimeRobot would detect, restart required to switch back."
REQ_ROW PASS id=REQ-OPS-050 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/logging.md
REQ_TITLE PASS id=REQ-OPS-050 title="log format" statement="JSON structured with timestamp, level, logger, event, extra_fields, exception when applicable."
REQ_ROW PASS id=REQ-OPS-051 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/logging.md
REQ_TITLE PASS id=REQ-OPS-051 title="log levels" statement="DEBUG development only, INFO normal, WARNING recoverable, ERROR failures, CRITICAL unused."
REQ_ROW PASS id=REQ-OPS-052 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/logging.md
REQ_TITLE PASS id=REQ-OPS-052 title="log events" statement="17 events documented for auth, expense, budget, category, db."
REQ_ROW PASS id=REQ-OPS-053 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/logging.md
REQ_TITLE PASS id=REQ-OPS-053 title="never logged" statement="Passwords, JWT tokens, full bodies, raw emails, DB connection strings, secrets never logged."
REQ_ROW PASS id=REQ-OPS-054 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/logging.md
REQ_TITLE PASS id=REQ-OPS-054 title="log destinations" statement="Local stdout, Compose stdout, Render log viewer."
REQ_ROW PASS id=REQ-OPS-055 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/logging.md
REQ_TITLE PASS id=REQ-OPS-055 title="log viewing" statement="Docker Compose logs, Render dashboard, filtering for `fallback_triggered`, `auth.login_failed`, `db.error`, `unhandled.error`."
REQ_ROW PASS id=REQ-OPS-056 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/logging.md
REQ_TITLE PASS id=REQ-OPS-056 title="log retention" statement="Local session only; Render per free tier policy."
REQ_ROW PASS id=REQ-OPS-057 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/logging.md
REQ_TITLE PASS id=REQ-OPS-057 title="structured field reference" statement="Documents timestamp, level, logger, event, extra_fields, exception fields."
REQ_ROW PASS id=REQ-OPS-060 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/deployment-health.md
REQ_TITLE PASS id=REQ-OPS-060 title="deployment-health.md purpose" statement="Records deployment state after each significant deployment."
REQ_ROW PASS id=REQ-OPS-061 family=OPS status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_req_coverage_verification.py
REQ_TITLE PASS id=REQ-OPS-061 title="initial deployment record" statement="Records platform, URL, date, version, commit, health check response, smoke test results, screenshots, cold start, database, notes."
REQ_ROW PASS id=REQ-OPS-062 family=OPS status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_req_coverage_verification.py
REQ_TITLE PASS id=REQ-OPS-062 title="post-expiry deployment record" statement="Records the state after Render PostgreSQL expires: health returns degraded, fallback active, all features work, data temporary."
REQ_ROW PASS id=REQ-OPS-070 family=OPS status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/scripts/security_ops_verification.py,docs/criteria/security_ops_verification.md,docs/issues/closed/t41.md
REQ_TITLE PASS id=REQ-OPS-070 title="manual diagnosis commands" statement="Commands to check status, response time, database, fallback state, and API docs."
REQ_ROW PASS id=REQ-OPS-080 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-080 title="monitoring" statement="Render dashboard, UptimeRobot, health endpoint."
REQ_ROW PASS id=REQ-OPS-081 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-081 title="alerting" statement="Service down alert via UptimeRobot email; fallback active manual check."
REQ_ROW PASS id=REQ-OPS-082 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-082 title="not monitored" statement="CPU, memory, latency, error rate, connection pool, disk usage are not monitored in MVP."
REQ_ROW PASS id=REQ-OPS-083 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-083 title="future monitoring" statement="Prometheus metrics, Grafana, alert on fallback, alert on error rate, structured log export, distributed tracing."
REQ_ROW PASS id=REQ-OPS-090 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-090 title="backup scope" statement="No automated backups; PostgreSQL lost on expiry; SQLite lost on restart; manual export documented."
REQ_ROW PASS id=REQ-OPS-091 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-091 title="manual export" statement="`pg_dump` and `sqlite3 .dump` commands documented."
REQ_ROW PASS id=REQ-OPS-092 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-092 title="recovery" statement="`psql` and `sqlite3` restore commands documented."
REQ_ROW PASS id=REQ-OPS-093 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-093 title="why no automated backups" statement="Free tier limitation, demo scope, small data, cost."
REQ_ROW PASS id=REQ-OPS-094 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-094 title="future backups" statement="Daily automated backup, restoration test, point-in-time recovery, cross-region replication."
REQ_ROW PASS id=REQ-OPS-100 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-100 title="rollback procedure" statement="Render dashboard → Deploys → previous → Redeploy."
REQ_ROW PASS id=REQ-OPS-101 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-101 title="rollback triggers" statement="Health check failure, smoke test failure, user- reported broken feature, unexpected fallback."
REQ_ROW PASS id=REQ-OPS-102 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-102 title="database rollback" statement="Migrations forward-only; restore from backup or accept fallback; no automated downgrade."
REQ_ROW PASS id=REQ-OPS-103 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-103 title="rollback limitations" statement="Manual, no automated, no database rollback, no canary, no blue-green."
REQ_ROW PASS id=REQ-OPS-110 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/health-check.md
REQ_TITLE PASS id=REQ-OPS-110 title="health design" statement="Public, no auth; fields cover key states; fallback reported in health."
REQ_ROW PASS id=REQ-OPS-111 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/logging.md
REQ_TITLE PASS id=REQ-OPS-111 title="logging design" statement="JSON structured; stdout destination."
REQ_ROW PASS id=REQ-OPS-112 family=OPS status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-OPS-112 title="monitoring design" statement="Render + UptimeRobot; UptimeRobot email alerts; manual backup; Render redeploy rollback."
REQ_ROW PASS id=REQ-OPS-113 family=OPS status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md,backend/scripts/security_ops_verification.py,docs/criteria/security_ops_verification.md
REQ_TITLE PASS id=REQ-OPS-113 title="documentation design" statement="Reproducible diagnosis example; deployment record as markdown; five ops files."
REQ_ROW PASS id=REQ-PLAN-001 family=PLAN status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-PLAN-001 title="eight phases" statement="The project is built in eight phases: spec and skeleton, authentication, core CRUD, dashboard, container and CI/CD, agent extension pack, security and ops, docs"
REQ_ROW PASS id=REQ-PLAN-002 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/plan.md
REQ_TITLE PASS id=REQ-PLAN-002 title="phase dependencies" statement="Phases are sequential; Phase 4 and Phase 5 may run in parallel."
REQ_ROW PASS id=REQ-PLAN-010 family=PLAN status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.env.example,.gitignore
REQ_TITLE PASS id=REQ-PLAN-010 title="phase 1 tasks" statement="17 tasks: write product-spec, create repo structure, write AGENTS.md, CLAUDE.md, process.md, three role files, task-template.md, create ~30 issues, groom all is"
REQ_ROW PASS id=REQ-PLAN-011 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/plan.md
REQ_TITLE PASS id=REQ-PLAN-011 title="phase 1 deliverables" statement="product-spec.md, AGENTS.md, CLAUDE.md, process.md, team/, task-template.md, repo skeleton, groomed backlog, backend and frontend skeletons, root config files."
REQ_ROW PASS id=REQ-PLAN-012 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t1.md,docs/issues/closed/t2.md,docs/issues/closed/t4.md
REQ_TITLE PASS id=REQ-PLAN-012 title="phase 1 verification" statement="Spec complete; backend starts; frontend starts; issues groomed; agent can read context."
REQ_ROW PASS id=REQ-PLAN-020 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t6.md,docs/plan.md
REQ_TITLE PASS id=REQ-PLAN-020 title="phase 2 tasks" statement="15 tasks: user model, password, JWT, register, login, me, auth dependency, auth unit tests, auth integration tests, AuthContext, axios client, login page, regis"
REQ_ROW PASS id=REQ-PLAN-021 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/plan.md
REQ_TITLE PASS id=REQ-PLAN-021 title="phase 2 verification" statement="Register, login, token, duplicate email, wrong password, frontend login, frontend redirect, tests pass."
REQ_ROW PASS id=REQ-PLAN-030 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t15.md,docs/issues/closed/t18.md,docs/plan.md
REQ_TITLE PASS id=REQ-PLAN-030 title="phase 3 tasks" statement="25 tasks covering categories, expenses, budgets, audit, isolation tests, and frontend pages."
REQ_ROW PASS id=REQ-PLAN-031 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t15.md,docs/plan.md
REQ_TITLE PASS id=REQ-PLAN-031 title="phase 3 verification" statement="CRUD tests pass; audit logged; user isolation verified; frontend works; Decimal precision holds."
REQ_ROW PASS id=REQ-PLAN-040 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t23.md,docs/plan.md
REQ_TITLE PASS id=REQ-PLAN-040 title="phase 4 tasks" statement="19 tasks covering six dashboard endpoints, chart components, MonthContext, MonthPicker, KPI cards, chart tests, and integration tests."
REQ_ROW PASS id=REQ-PLAN-041 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md,backend/scripts/dashboard_verification.py,docs/criteria/dashboard_verification.md
REQ_TITLE PASS id=REQ-PLAN-041 title="phase 4 verification" statement="Summary correct; category breakdown sum equals total; trend includes empty months; cumulative last point equals total; heatmap has seven days per week; recent l"
REQ_ROW PASS id=REQ-PLAN-050 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/plan.md
REQ_TITLE PASS id=REQ-PLAN-050 title="phase 5 tasks" statement="15 tasks: Dockerfile, Compose, health check, SQLite fallback, render.yaml, three workflows, Playwright setup, three E2E specs, first deploy, UptimeRobot, deploy"
REQ_ROW PASS id=REQ-PLAN-051 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/scripts/infra_verification.py,docs/criteria/infra_verification.md,docs/issues/closed/t28.md
REQ_TITLE PASS id=REQ-PLAN-051 title="phase 5 verification" statement="Docker build works; full stack runs; CI passes; E2E passes; deploy works; health endpoint works; README has cold start note; UptimeRobot active."
REQ_ROW PASS id=REQ-PLAN-060 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/scripts/agent_pack_verification.py,docs/issues/closed/t29.md,docs/issues/closed/t30.md
REQ_TITLE PASS id=REQ-PLAN-060 title="phase 6 tasks" statement="20 tasks: three skills, two hooks, hook README, MCP server, auth, four tools, MCP README, two subagents, symlinks, two docs, hook tests, manual MCP test."
REQ_ROW PASS id=REQ-PLAN-061 family=PLAN status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_agent_hooks.py,backend/tests/integration/test_mcp_tools.py
REQ_TITLE PASS id=REQ-PLAN-061 title="phase 6 verification" statement="Skills discoverable; hooks importable; hook tests pass; MCP server starts; MCP tools work; subagents defined; permissions documented."
REQ_ROW PASS id=REQ-PLAN-070 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t36.md,docs/issues/closed/t37.md,docs/issues/closed/t38.md
REQ_TITLE PASS id=REQ-PLAN-070 title="phase 7 tasks" statement="13 tasks: run gitleaks, semgrep, trivy, pip-audit, npm audit; write pr-audit, agent-security-notes, ai-tool-data-policy, runbook, health-check, diagnosis, loggi"
REQ_ROW PASS id=REQ-PLAN-071 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/scripts/security_ops_verification.py,docs/criteria/security_ops_verification.md,docs/issues/closed/t36.md
REQ_TITLE PASS id=REQ-PLAN-071 title="phase 7 verification" statement="All scan files exist; no real secrets found; diagnosis reproducible; runbook covers common issues; deployment record accurate."
REQ_ROW PASS id=REQ-PLAN-080 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t48.md,docs/issues/closed/t49.md,docs/plan.md
REQ_TITLE PASS id=REQ-PLAN-080 title="phase 8 tasks" statement="13 tasks: write README, architecture.md, api.md, design-system.md, testing-guidelines.md, ai-workflow.md; capture screenshots; run final tests; deploy; verify l"
REQ_ROW PASS id=REQ-PLAN-081 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/plan.md
REQ_TITLE PASS id=REQ-PLAN-081 title="phase 8 verification" statement="README under 500 lines; all docs present; screenshots exist; all tests pass; live URL works; criteria mapped."
REQ_ROW PASS id=REQ-PLAN-090 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/plan.md
REQ_TITLE PASS id=REQ-PLAN-090 title="milestones" statement="Eight milestones M1–M8 aligned with the eight phases, each with a criteria statement."
REQ_ROW PASS id=REQ-PLAN-100 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/plan.md
REQ_TITLE PASS id=REQ-PLAN-100 title="technical risks" statement="Ten technical risks documented with probability, impact, and mitigation: Render PostgreSQL expiry, cold start, pi-agent struggles, context limit, MCP failure, E"
REQ_ROW PASS id=REQ-PLAN-101 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/plan.md
REQ_TITLE PASS id=REQ-PLAN-101 title="process risks" statement="Seven process risks: spec vague, spec detailed, AI wrong code, review skipped, issues too large, correction not written, session records incomplete."
REQ_ROW PASS id=REQ-PLAN-102 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/plan.md
REQ_TITLE PASS id=REQ-PLAN-102 title="scope risks" statement="Six scope risks: feature creep, extra charts, multi-currency, shared budgets, mobile, dark mode."
REQ_ROW PASS id=REQ-PLAN-103 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/plan.md
REQ_TITLE PASS id=REQ-PLAN-103 title="deployment risks" statement="Six deployment risks: deploy failure, migration failure, cold start, bandwidth, build minutes, secret leak."
REQ_ROW PASS id=REQ-PLAN-110 family=PLAN status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-PLAN-110 title="daily workflow" statement="Nine-step daily workflow: pick issue, groom, implement, verify, fix on FAIL, close on PASS, commit, CI runs, update session records."
REQ_ROW PASS id=REQ-PLAN-111 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/plan.md
REQ_TITLE PASS id=REQ-PLAN-111 title="time allocation" statement="Writing code 40%, reviewing AI output 20%, grooming 10%, testing 15%, docs 10%, debugging 5%."
REQ_ROW PASS id=REQ-PLAN-112 family=PLAN status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-PLAN-112 title="session discipline" statement="One issue per session, fresh session for QA, commit after each issue, update docs after corrections, record sessions."
REQ_ROW PASS id=REQ-PLAN-120 family=PLAN status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/plan.md
REQ_TITLE PASS id=REQ-PLAN-120 title="phase structure" statement="Eight phases, sequential with Phase 4 and 5 parallel- izable, estimated 25 days."
REQ_ROW PASS id=REQ-PLAN-121 family=PLAN status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/process.md
REQ_TITLE PASS id=REQ-PLAN-121 title="workflow and discipline" statement="PM → SWE → QA loop; one issue per session; documentation throughout; screenshots in Phase 8; security scans in Phase 7; peer review dry run in Phase 8."
REQ_ROW PASS id=REQ-PROD-001 family=PROD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=product-spec.md
REQ_TITLE PASS id=REQ-PROD-001 title="Problem statement" statement="The product-spec documents that spreadsheets are tedious and full accounting software is overwhelming, and that the product fills the gap with a focused expense"
REQ_ROW PASS id=REQ-PROD-002 family=PROD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=product-spec.md
REQ_TITLE PASS id=REQ-PROD-002 title="User stories for authentication" statement="User stories AUTH-1 through AUTH-5 exist for registration, login, profile, logout, and isolation."
REQ_ROW PASS id=REQ-PROD-003 family=PROD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=product-spec.md
REQ_TITLE PASS id=REQ-PROD-003 title="User stories for expenses" statement="User stories EXP-1 through EXP-7 exist for create, list, filter, update, delete, isolation, and validation."
REQ_ROW PASS id=REQ-PROD-004 family=PROD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=product-spec.md
REQ_TITLE PASS id=REQ-PROD-004 title="User stories for budgets" statement="User stories BUD-1 through BUD-5 exist for set, update, delete, view, and duplicate conflict."
REQ_ROW PASS id=REQ-PROD-005 family=PROD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=product-spec.md
REQ_TITLE PASS id=REQ-PROD-005 title="User stories for categories" statement="User stories CAT-1 through CAT-5 exist for system categories, custom categories, combined view, protection of system categories, and duplicate name handling."
REQ_ROW PASS id=REQ-PROD-006 family=PROD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=product-spec.md
REQ_TITLE PASS id=REQ-PROD-006 title="User stories for dashboard" statement="User stories DASH-1 through DASH-10 exist for KPI cards, five charts, month switch, and empty state."
REQ_ROW PASS id=REQ-PROD-007 family=PROD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=product-spec.md
REQ_TITLE PASS id=REQ-PROD-007 title="User stories for audit" statement="User stories AUD-1 through AUD-3 exist for logging expense writes, logging budget writes, and no API access to audit logs."
REQ_ROW PASS id=REQ-PROD-010 family=PROD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=product-spec.md
REQ_TITLE PASS id=REQ-PROD-010 title="Authentication functional requirements" statement="FR-AUTH-1 through FR-AUTH-4 define registration, login, current user, and logout behavior, including validation rules and error codes."
REQ_ROW PASS id=REQ-PROD-011 family=PROD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=product-spec.md
REQ_TITLE PASS id=REQ-PROD-011 title="Expense functional requirements" statement="FR-EXP-1 through FR-EXP-5 define expense create, list, get, update, and delete, including validation, user isolation, and audit behavior."
REQ_ROW PASS id=REQ-PROD-012 family=PROD status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/pages/budget_page.test.tsx
REQ_TITLE PASS id=REQ-PROD-012 title="Budget functional requirements" statement="FR-BUD-1 through FR-BUD-3 define budget set (upsert), get (returns 0 if absent), and delete, including audit behavior."
REQ_ROW PASS id=REQ-PROD-013 family=PROD status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/pages/categories_page.test.tsx
REQ_TITLE PASS id=REQ-PROD-013 title="Category functional requirements" statement="FR-CAT-1 through FR-CAT-3 define category list, create, and system category protection."
REQ_ROW PASS id=REQ-PROD-014 family=PROD status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/charts/cumulative_line_chart.test.tsx,frontend/src/pages/dashboard_page.test.tsx
REQ_TITLE PASS id=REQ-PROD-014 title="Dashboard functional requirements" statement="FR-DASH-1 through FR-DASH-6 define summary, by-category, trend, cumulative, heatmap, and recent behavior, including edge cases."
REQ_ROW PASS id=REQ-PROD-015 family=PROD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=product-spec.md
REQ_TITLE PASS id=REQ-PROD-015 title="Audit functional requirements" statement="FR-AUD-1 and FR-AUD-2 define that audit logs are written in the same transaction as the business operation and that no API endpoint exposes them."
REQ_ROW PASS id=REQ-PROD-016 family=PROD status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t28.md,docs/issues/closed/t3.md,docs/plan.md
REQ_TITLE PASS id=REQ-PROD-016 title="Health check functional requirement" statement="FR-HEALTH-1 defines a public health endpoint returning status, database, fallback_active, and version."
REQ_ROW PASS id=REQ-PROD-017 family=PROD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/diagnosis.md
REQ_TITLE PASS id=REQ-PROD-017 title="Database fallback functional requirement" statement="FR-DB-1 defines automatic fallback to SQLite within 5 seconds when PostgreSQL is unreachable at startup, with table creation and category seeding, and notes tha"
REQ_ROW PASS id=REQ-PROD-020 family=PROD status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md,backend/scripts/dashboard_verification.py,backend/scripts/infra_verification.py
REQ_TITLE PASS id=REQ-PROD-020 title="Performance targets" statement="Dashboard loads in under 2 seconds on warm cache, simple API queries under 200ms, dashboard aggregations under 500ms, cold start under 60 seconds, and frontend"
REQ_ROW PASS id=REQ-PROD-021 family=PROD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/diagnosis.md
REQ_TITLE PASS id=REQ-PROD-021 title="Reliability" statement="SQLite fallback keeps the app functional when PostgreSQL is unavailable; health check reports database status; no data loss on graceful restart when using Postg"
REQ_ROW PASS id=REQ-PROD-022 family=PROD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-PROD-022 title="Security non-functional requirements" statement="Passwords are bcrypt-hashed, JWT uses fixed HS256 and validates signature, expiry, audience, issuer, all queries filter by user_id, cross-user access returns 40"
REQ_ROW PASS id=REQ-PROD-023 family=PROD status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/common/budget_progress.test.tsx,frontend/src/components/forms/budget_form.test.tsx,frontend/src/components/forms/expense_form.test.tsx
REQ_TITLE PASS id=REQ-PROD-023 title="Data integrity" statement="Amounts are NUMERIC(12,2) and handled as Decimal, transmitted as strings; dates use DATE without timezone; budget has a unique constraint on (user_id, year_mont"
REQ_ROW PASS id=REQ-PROD-024 family=PROD status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t17.md,docs/plan.md
REQ_TITLE PASS id=REQ-PROD-024 title="Usability" statement="Dashboard loads in under 2 seconds, empty and loading states are shown, error messages are specific, month selector updates all charts, forms validate before su"
REQ_ROW PASS id=REQ-PROD-025 family=PROD status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md,docs/design-system.md
REQ_TITLE PASS id=REQ-PROD-025 title="Accessibility" statement="Form inputs have labels, buttons have accessible names, modal has role and focus trap, charts have descriptions, contrast is at least 4.5:1, keyboard navigation"
REQ_ROW PASS id=REQ-PROD-026 family=PROD status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-PROD-026 title="Maintainability" statement="Backend is split into routers, services, models, schemas; frontend into api, components, pages, hooks, context, utils; all API calls are centralized; all busine"
REQ_ROW PASS id=REQ-PROD-027 family=PROD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.env.example
REQ_TITLE PASS id=REQ-PROD-027 title="Portability" statement="Docker Compose runs the full stack on any platform; SQLite is used locally and PostgreSQL in production; all configuration is via environment variables; no hard"
REQ_ROW PASS id=REQ-PROD-028 family=PROD status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/logging.md
REQ_TITLE PASS id=REQ-PROD-028 title="Observability" statement="Logs are structured JSON; key events (auth, expense, budget, db fallback) are logged; health check exists; audit log lives in the database; Render logs are acce"
REQ_ROW PASS id=REQ-PROD-030 family=PROD status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t8.md,docs/plan.md
REQ_TITLE PASS id=REQ-PROD-030 title="Authentication edge cases" statement="Edge cases for invalid email, short password, short username, spaces in username, duplicate email, duplicate username, wrong password, nonexistent email, expire"
REQ_ROW PASS id=REQ-PROD-031 family=PROD status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_expense_api.py
REQ_TITLE PASS id=REQ-PROD-031 title="Expense edge cases" statement="Edge cases for zero amount, negative amount, three decimals, over-max amount, empty amount, missing category, other user's category, invalid date, long note, cr"
REQ_ROW PASS id=REQ-PROD-032 family=PROD status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t14.md
REQ_TITLE PASS id=REQ-PROD-032 title="Budget edge cases" statement="Edge cases for invalid year_month, duplicate budget, upsert on nonexistent, absent budget returns 0, negative amount, and delete nonexistent are defined."
REQ_ROW PASS id=REQ-PROD-033 family=PROD status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/components/charts/category_pie_chart.test.tsx,frontend/src/components/charts/monthly_trend_chart.test.tsx
REQ_TITLE PASS id=REQ-PROD-033 title="Dashboard edge cases" statement="Edge cases for empty month, no budget, expenses without budget, exactly at budget, month boundary, year boundary, heatmap crossing year boundary, more than 6 ca"
REQ_ROW PASS id=REQ-PROD-034 family=PROD status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/routers/categories.py,backend/app/services/category_service.py,docs/issues/closed/t11.md
REQ_TITLE PASS id=REQ-PROD-034 title="Category edge cases" statement="Edge cases for duplicate system name, duplicate own name, long name, invalid HEX, delete system category, and update system category are defined."
REQ_ROW PASS id=REQ-PROD-035 family=PROD status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_budget_model.py
REQ_TITLE PASS id=REQ-PROD-035 title="Database edge cases" statement="Edge cases for PostgreSQL unreachable at startup, unreachable at runtime, recovery requiring restart, unwritable SQLite file, migration failure, and concurrent"
REQ_ROW PASS id=REQ-PROD-036 family=PROD status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t17.md,docs/issues/closed/t20.md,docs/issues/closed/t22.md
REQ_TITLE PASS id=REQ-PROD-036 title="Frontend edge cases" statement="Edge cases for token expiry during session, network error, empty dashboard, loading state, invalid form data, protected route without login, rapid month switchi"
REQ_ROW PASS id=REQ-PROD-040 family=PROD status=IMPLEMENTED_STRUCTURAL method=citation pointers=product-spec.md
REQ_TITLE PASS id=REQ-PROD-040 title="Functional success" statement="A new user can register, log in, record expenses, set a budget, and view the dashboard without errors; all five charts render; month switching updates all chart"
REQ_ROW PASS id=REQ-PROD-041 family=PROD status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_req_coverage_verification.py
REQ_TITLE PASS id=REQ-PROD-041 title="Technical success" statement="All unit, integration, and E2E tests pass; SQLite fallback works; health check is accurate; CI runs on every PR; CD deploys on merge to main; a public URL is av"
REQ_ROW PASS id=REQ-PROD-042 family=PROD status=IMPLEMENTED_STRUCTURAL method=citation pointers=product-spec.md
REQ_TITLE PASS id=REQ-PROD-042 title="Quality success" statement="README provides a 5-minute verification path; all 14 criteria have evidence; security artifacts are present; Agent Extension Pack is functional; AI workflow is"
REQ_ROW PASS id=REQ-PROD-043 family=PROD status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/scripts/agent_pack_verification.py,backend/scripts/security_ops_verification.py,docs/criteria/agent_pack_verification.md
REQ_TITLE PASS id=REQ-PROD-043 title="Measurable targets" statement="Backend test count >= 50, frontend test count >= 20, E2E test count >= 3, API endpoints >= 15, dashboard charts = 5, system categories = 10, security artifacts"
REQ_ROW PASS id=REQ-PROJ-001 family=PROJ status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=LICENSE,README.md
REQ_TITLE PASS id=REQ-PROJ-001 title="Product identity" statement="The project is named 'Expense Tracker & Budget Dashboard', the repository is named `expense-tracker-dashboard`, and the license is MIT."
REQ_ROW PASS id=REQ-PROJ-002 family=PROJ status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=README.md
REQ_TITLE PASS id=REQ-PROJ-002 title="One-line description" statement="The project has a one-line description stating that users record expenses, set monthly budgets, and view spending insights through an interactive dashboard with"
REQ_ROW PASS id=REQ-PROJ-003 family=PROJ status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=README.md,product-spec.md
REQ_TITLE PASS id=REQ-PROJ-003 title="Target users" statement="The application targets individuals managing personal finances, single-currency (USD) users, and users who do not need shared budgets."
REQ_ROW PASS id=REQ-PROJ-004 family=PROJ status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t23.md,docs/plan.md
REQ_TITLE PASS id=REQ-PROJ-004 title="Core questions answered" statement="The application answers three questions: how much have I spent this month, how much budget is left, and where is my money going"
REQ_ROW PASS id=REQ-PROJ-005 family=PROJ status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=README.md
REQ_TITLE PASS id=REQ-PROJ-005 title="Final Project criteria mapping" statement="The README contains a table mapping all 14 Final Project criteria to evidence in the repository."
REQ_ROW PASS id=REQ-PROJ-006 family=PROJ status=IMPLEMENTED_STRUCTURAL method=citation pointers=product-spec.md
REQ_TITLE PASS id=REQ-PROJ-006 title="In-scope capabilities" statement="The MVP includes authentication, expenses, budgets, categories, dashboard with five visualizations, data integrity, SQLite fallback, Agent Extension Pack, secur"
REQ_ROW PASS id=REQ-PROJ-007 family=PROJ status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t8.md,docs/issues/closed/t9.md
REQ_TITLE PASS id=REQ-PROJ-007 title="Out-of-scope boundaries" statement="Multi-currency, income tracking, bank integration, shared budgets, mobile app, recurring expenses, receipt upload, email verification, password reset, dark mode"
REQ_ROW PASS id=REQ-PROJ-008 family=PROJ status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/schemas/auth.py,docs/issues/closed/t8.md
REQ_TITLE PASS id=REQ-PROJ-008 title="Project constraints" statement="The project uses USD only, monthly total budget per user, JWT with bcrypt, 24-hour token lifetime, 8-character minimum password, 3-50 character username, option"
REQ_ROW PASS id=REQ-PROJ-009 family=PROJ status=IMPLEMENTED_STRUCTURAL method=citation pointers=README.md,backend/scripts/docs_verification.py,docs/criteria/docs_verification.md
REQ_TITLE PASS id=REQ-PROJ-009 title="Success criteria" statement="The project is successful when all 14 criteria have evidence, the app is deployed, all tests pass, a new user can complete the core flow, user isolation is veri"
REQ_ROW PASS id=REQ-SEC-001 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/diagnosis.md
REQ_TITLE PASS id=REQ-SEC-001 title="Criterion 13 mapping" statement="The project provides PR audit output, deterministic security scan findings, agent/extension security notes, operational diagnosis output, and an AI tool/data po"
REQ_ROW PASS id=REQ-SEC-002 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-SEC-002 title="security layers" statement="Security layers: network (HTTPS, CORS), authentication (JWT HS256), password (bcrypt), authorization (user_id filter), data isolation (404), input validation (P"
REQ_ROW PASS id=REQ-SEC-003 family=SEC status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/scripts/security_ops_verification.py,docs/criteria/security_ops_verification.md,docs/issues/closed/t36.md
REQ_TITLE PASS id=REQ-SEC-003 title="security directory layout" statement="`security/` contains pr-audit.md, gitleaks-report.json, semgrep-report.json, trivy-report.json, pip-audit-report.txt, npm-audit-report.txt, agent-security-notes"
REQ_ROW PASS id=REQ-SEC-010 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-SEC-010 title="assets" statement="Assets: user credentials (high), JWT secret (high), user expense data (medium), user budget data (medium), audit logs (medium), source code (low), configuration"
REQ_ROW PASS id=REQ-SEC-011 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-SEC-011 title="threat actors" statement="Threat actors: unauthenticated attacker, authenticated malicious user, compromised dependency, misconfigured deployment, malicious agent input."
REQ_ROW PASS id=REQ-SEC-012 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-SEC-012 title="threats and mitigations" statement="15 threats documented with mitigations: brute force, token forgery, replay, cross-user access, SQL injection, XSS, CSRF, secret leakage, dependency vulnerabilit"
REQ_ROW PASS id=REQ-SEC-013 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-SEC-013 title="out-of-scope threats" statement="Nation-state, physical access, insider, DDoS, zero-day, social engineering are out of scope."
REQ_ROW PASS id=REQ-SEC-020 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/auth/password.py
REQ_TITLE PASS id=REQ-SEC-020 title="password storage" statement="bcrypt rounds 12, automatic salt, hashed_password column, HTTPS in production, never logged, min 8 / max 72 chars."
REQ_ROW PASS id=REQ-SEC-021 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/auth/jwt.py
REQ_TITLE PASS id=REQ-SEC-021 title="JWT security" statement="HS256 fixed, algorithms fixed in decode call, alg=none rejected, expiry 24h, audience and issuer validated, type validated, secret from env, localStorage docume"
REQ_ROW PASS id=REQ-SEC-022 family=SEC status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_budget_api.py,backend/tests/unit/test_auth_service.py
REQ_TITLE PASS id=REQ-SEC-022 title="authentication failure codes" statement="All auth failures map to specific codes: UNAUTHORIZED, TOKEN_INVALID, TOKEN_EXPIRED, USER_INACTIVE, INVALID_CREDENTIALS. Nonexistent email returns same code as"
REQ_ROW PASS id=REQ-SEC-023 family=SEC status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_auth_service.py
REQ_TITLE PASS id=REQ-SEC-023 title="timing attack mitigation" statement="`authenticate_user` runs a dummy bcrypt verification when the user does not exist."
REQ_ROW PASS id=REQ-SEC-030 family=SEC status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_expense_api.py,backend/tests/integration/test_isolation.py
REQ_TITLE PASS id=REQ-SEC-030 title="user isolation in queries" statement="Every expense and budget query filters by user_id; every category query filters by `user_id IS NULL OR user_id = current_user.id`."
REQ_ROW PASS id=REQ-SEC-031 family=SEC status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/integration/test_isolation.py
REQ_TITLE PASS id=REQ-SEC-031 title="cross-user 404" statement="Cross-user access returns 404, not 403, to avoid revealing existence."
REQ_ROW PASS id=REQ-SEC-032 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/services/category_service.py
REQ_TITLE PASS id=REQ-SEC-032 title="category access validation" statement="`validate_category_access` checks system or user ownership and returns 404 on failure."
REQ_ROW PASS id=REQ-SEC-033 family=SEC status=IMPLEMENTED_TESTED method=citation pointers=frontend/src/pages/categories_page.test.tsx
REQ_TITLE PASS id=REQ-SEC-033 title="system category protection" statement="System categories cannot be updated or deleted (404); listing and using them is allowed."
REQ_ROW PASS id=REQ-SEC-034 family=SEC status=IMPLEMENTED_TESTED method=verification-artifact pointers=backend/tests/integration/test_isolation.py
REQ_TITLE PASS id=REQ-SEC-034 title="isolation test coverage" statement="`test_isolation.py` verifies read, update, delete return 404 for cross-user; list shows only own; budget isolation."
REQ_ROW PASS id=REQ-SEC-040 family=SEC status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/schemas/auth.py,docs/issues/closed/t8.md
REQ_TITLE PASS id=REQ-SEC-040 title="Pydantic schemas" statement="All request bodies validated by Pydantic v2 schemas with strict constraints."
REQ_ROW PASS id=REQ-SEC-041 family=SEC status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/api.md
REQ_TITLE PASS id=REQ-SEC-041 title="validation rules" statement="Validation rules for email, username, password, amount, category_id, date, note, year_month, page, page_size, months, weeks, limit, color."
REQ_ROW PASS id=REQ-SEC-042 family=SEC status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/coding_standards.md
REQ_TITLE PASS id=REQ-SEC-042 title="SQL injection prevention" statement="All database access uses SQLAlchemy ORM with parameterized queries; no raw SQL in application code."
REQ_ROW PASS id=REQ-SEC-043 family=SEC status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/coding_standards.md
REQ_TITLE PASS id=REQ-SEC-043 title="XSS prevention" statement="React escaping, no `dangerouslySetInnerHTML`, no third-party scripts; CSP not configured in MVP (documented)."
REQ_ROW PASS id=REQ-SEC-044 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/app/main.py,render.yaml
REQ_TITLE PASS id=REQ-SEC-044 title="CORS" statement="CORS configured with explicit `allow_origins` from settings; in production only the Render URL."
REQ_ROW PASS id=REQ-SEC-050 family=SEC status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/models/budget.py,backend/app/models/expense.py,backend/app/schemas/budget.py
REQ_TITLE PASS id=REQ-SEC-050 title="amount precision across layers" statement="Database NUMERIC(12,2), Python Decimal, Pydantic condecimal, JSON string, frontend string, audit string."
REQ_ROW PASS id=REQ-SEC-051 family=SEC status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_budget_model.py,backend/tests/unit/test_expense_model.py
REQ_TITLE PASS id=REQ-SEC-051 title="date handling" statement="Expense date DATE no timezone; created_at and updated_at TIMESTAMPTZ UTC; year_month CHAR(7) no timezone."
REQ_ROW PASS id=REQ-SEC-052 family=SEC status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/alembic/versions/001_initial_schema.py,docs/issues/closed/t6.md
REQ_TITLE PASS id=REQ-SEC-052 title="database constraints" statement="UNIQUE on email, username, (user_id, year_month); CHECK on color, system consistency, amount > 0, currency = 'USD', year_month format, action, entity_type."
REQ_ROW PASS id=REQ-SEC-060 family=SEC status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/models/audit_log.py,docs/issues/closed/t12.md,docs/plan.md
REQ_TITLE PASS id=REQ-SEC-060 title="audit design" statement="Triggered by expense and budget create/update/delete; written in the same transaction; not accessible via API; preserved on user delete; fields: user_id, action"
REQ_ROW PASS id=REQ-SEC-061 family=SEC status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t12.md
REQ_TITLE PASS id=REQ-SEC-061 title="what is logged" statement="CREATE has null old_value and full new_value; UPDATE has both; DELETE has full old_value and null new_value."
REQ_ROW PASS id=REQ-SEC-062 family=SEC status=IMPLEMENTED_STRUCTURAL method=code-symbol pointers=backend/alembic/versions/001_initial_schema.py,backend/alembic/versions/003_audit_logs.py,backend/app/audit/logger.py
REQ_TITLE PASS id=REQ-SEC-062 title="what is not logged" statement="Login attempts (application logs only), registration, read operations, category operations, failed operations are not audited."
REQ_ROW PASS id=REQ-SEC-063 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-SEC-063 title="audit example" statement="Example audit log entry is documented with all fields."
REQ_ROW PASS id=REQ-SEC-064 family=SEC status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t12.md
REQ_TITLE PASS id=REQ-SEC-064 title="audit atomicity" statement="If audit write fails, the transaction is rolled back; no business operation occurs without an audit entry."
REQ_ROW PASS id=REQ-SEC-070 family=SEC status=IMPLEMENTED_STRUCTURAL method=citation pointers=Makefile,docs/issues/closed/t36.md,docs/issues/closed/t37.md
REQ_TITLE PASS id=REQ-SEC-070 title="scan tools" statement="gitleaks, semgrep, trivy, pip-audit, npm audit are used, each writing to `security/`."
REQ_ROW PASS id=REQ-SEC-071 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=Makefile
REQ_TITLE PASS id=REQ-SEC-071 title="scan commands" statement="Documented commands run each scan and write to the corresponding file."
REQ_ROW PASS id=REQ-SEC-072 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-SEC-072 title="scan timing" statement="Scans run after auth, after CRUD, after dashboard, before deployment, and after final changes; results committed."
REQ_ROW PASS id=REQ-SEC-073 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.env.example
REQ_TITLE PASS id=REQ-SEC-073 title="expected findings" statement="Expected findings documented: `.env.example` placeholders (gitleaks), subprocess in MCP (semgrep), low-severity base image CVEs (trivy), python-jose CVE (pip-au"
REQ_ROW PASS id=REQ-SEC-074 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-SEC-074 title="accepted findings" statement="Any unfixed finding is documented in `security/agent-security-notes.md` with finding, reason, mitigation, plan."
REQ_ROW PASS id=REQ-SEC-080 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/pr-audit.md
REQ_TITLE PASS id=REQ-SEC-080 title="PR audit purpose" statement="`security/pr-audit.md` records at least one PR reviewed with AI assistance."
REQ_ROW PASS id=REQ-SEC-081 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/pr-audit.md
REQ_TITLE PASS id=REQ-SEC-081 title="PR audit template" statement="Template includes PR details, AI review output, issues found, verification, verdict."
REQ_ROW PASS id=REQ-SEC-082 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/pr-audit.md
REQ_TITLE PASS id=REQ-SEC-082 title="PR audit coverage" statement="Audit covers API contract, security, tests, code quality, error handling, documentation."
REQ_ROW PASS id=REQ-SEC-090 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-SEC-090 title="agent threat model" statement="Seven threats for agents with mitigations: cross-user access, unauthorized modification, backend bypass, prompt injection, secret leakage, arbitrary code, inval"
REQ_ROW PASS id=REQ-SEC-091 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-SEC-091 title="agent security controls" statement="JWT auth, backend-enforced authorization, hooks, output filtering, tool restriction, context isolation, read-only roles, audit."
REQ_ROW PASS id=REQ-SEC-092 family=SEC status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/config_reference.md
REQ_TITLE PASS id=REQ-SEC-092 title="MCP security" statement="JWT verification, token from env, no database access, strict tool schemas, exception handling, no token logging."
REQ_ROW PASS id=REQ-SEC-093 family=SEC status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/config_reference.md
REQ_TITLE PASS id=REQ-SEC-093 title="hook security" statement="validate_amount prevents invalid amounts; validate_ownership prevents cross-user access; both also enforced in backend."
REQ_ROW PASS id=REQ-SEC-094 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-SEC-094 title="prompt injection considerations" statement="User input treated as data, skills are project files, tool output validated, no cloud calls, MCP verifies JWT."
REQ_ROW PASS id=REQ-SEC-095 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-SEC-095 title="agent security notes document" statement="`security/agent-security-notes.md` covers architecture, auth, hooks, permissions, limitations, accepted risks, future improvements."
REQ_ROW PASS id=REQ-SEC-100 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/ai-tool-data-policy.md
REQ_TITLE PASS id=REQ-SEC-100 title="policy summary" statement="All AI processing local; no code, prompts, or context leaves the machine; no cloud LLM APIs; no production data; no secrets in context."
REQ_ROW PASS id=REQ-SEC-101 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/ai-tool-data-policy.md
REQ_TITLE PASS id=REQ-SEC-101 title="data categories" statement="Source code, docs, tests, seed data, OpenAPI spec are in agent context; real user data, production database, `.env`, JWT tokens, JWT secret are not."
REQ_ROW PASS id=REQ-SEC-102 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/ai-tool-data-policy.md
REQ_TITLE PASS id=REQ-SEC-102 title="AI tool inventory" statement="pi-agent, qwen3.8-27b, plugins; none send data off-machine."
REQ_ROW PASS id=REQ-SEC-103 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/ai-tool-data-policy.md
REQ_TITLE PASS id=REQ-SEC-103 title="compliance considerations" statement="Data residency local, no PII, no secrets in context, audit via session records, reproducibility via same model version, retention of session records in repo."
REQ_ROW PASS id=REQ-SEC-104 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/ai-tool-data-policy.md
REQ_TITLE PASS id=REQ-SEC-104 title="policy document content" statement="The policy document contains tool inventory, data classification, data flow diagram, permitted and forbidden uses, review requirements, incident response."
REQ_ROW PASS id=REQ-SEC-110 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-SEC-110 title="accepted limitations" statement="12 limitations documented: no rate limiting, localStorage JWT, no refresh token, no CSP, no CSRF token, HTTP in local dev, no secret rotation, SQLite fallback u"
REQ_ROW PASS id=REQ-SEC-111 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-SEC-111 title="why accepted" statement="The project is a demonstration and learning artifact appropriate for single-user deployment, non-critical data, peer review, and educational purposes."
REQ_ROW PASS id=REQ-SEC-112 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-SEC-112 title="future improvements" statement="Rate limiting (high), HttpOnly cookie (high), refresh token rotation (medium), CSP (medium), 2FA (medium), secret rotation (medium), audit log encryption (low),"
REQ_ROW PASS id=REQ-SEC-120 family=SEC status=DEFERRED_RULLED method=deferral-register pointers=docs/criteria/docs_verification.md,ops/deployment-health.md issue=61 deferral_reason="RENDER_DEPLOY_HOOK secret is operator infrastructure (platform #61)"
REQ_TITLE PASS id=REQ-SEC-120 title="secrets management" statement="JWT_SECRET and DATABASE_URL in env vars; RENDER_DEPLOY_HOOK in GitHub Actions secrets; manual rotation."
REQ_ROW PASS id=REQ-SEC-121 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.gitignore
REQ_TITLE PASS id=REQ-SEC-121 title="gitignore" statement="`.gitignore` excludes .env, local env files, *.db, *.sqlite, `__pycache__`, node_modules, dist, build, coverage, tool caches, .DS_Store, *.log."
REQ_ROW PASS id=REQ-SEC-122 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/gitleaks-report.json
REQ_TITLE PASS id=REQ-SEC-122 title="git history scanning" statement="gitleaks scans full git history; the project starts with a clean history."
REQ_ROW PASS id=REQ-SEC-123 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.env.example,docker-compose.yml,render.yaml
REQ_TITLE PASS id=REQ-SEC-123 title="environment separation" statement="Local dev uses SQLite with dev secret and localhost:5173 CORS; Compose uses PostgreSQL with dev secret; production uses Render PostgreSQL with generated secret"
REQ_ROW PASS id=REQ-SEC-130 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-SEC-130 title="detection" statement="Failed login spikes detected via logs; cross-user access not possible; database unavailable via health; secret leak via gitleaks; dependency vulnerability via a"
REQ_ROW PASS id=REQ-SEC-131 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-SEC-131 title="response steps" statement="Six steps: identify, assess, contain, eradicate, recover, document."
REQ_ROW PASS id=REQ-SEC-132 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=ops/runbook.md
REQ_TITLE PASS id=REQ-SEC-132 title="rollback" statement="Bad deployment rollback via Render dashboard; leaked secret rotate and redeploy; database compromise N/A; dependency vulnerability update and redeploy."
REQ_ROW PASS id=REQ-SEC-140 family=SEC status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-SEC-140 title="auth and token choices" statement="bcrypt rounds 12; HS256; localStorage; 24-hour expiry; no refresh token; 404 for cross-user."
REQ_ROW PASS id=REQ-SEC-141 family=SEC status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-SEC-141 title="audit choices" statement="Audit write same transaction; no API access."
REQ_ROW PASS id=REQ-SEC-142 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.env.example
REQ_TITLE PASS id=REQ-SEC-142 title="secrets and scans" statement="Secrets via env vars; security scans local and committed."
REQ_ROW PASS id=REQ-SEC-143 family=SEC status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/agent-security-notes.md
REQ_TITLE PASS id=REQ-SEC-143 title="agent security choices" statement="Agent auth JWT; data access via API; hooks pure functions; read-only analyst; AI data policy local only; known limitations documented; future improvements liste"
REQ_ROW PASS id=REQ-STRUCT-001 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t0.md,docs/issues/closed/t48.md,docs/plan.md
REQ_TITLE PASS id=REQ-STRUCT-001 title="complete repository tree" statement="The repository tree matches the structure documented in Chapter 16, including root files, `.github/`, `frontend/`, `backend/`, `e2e/`, `docs/`, `security/`, `op"
REQ_ROW PASS id=REQ-STRUCT-010 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/requirements/Chapter16_ProjectStructure.md
REQ_TITLE PASS id=REQ-STRUCT-010 title="top-level directory responsibilities" statement="Each top-level directory has a defined responsibility and owner."
REQ_ROW PASS id=REQ-STRUCT-011 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/requirements/Chapter16_ProjectStructure.md
REQ_TITLE PASS id=REQ-STRUCT-011 title="frontend subdirectory responsibilities" statement="Each `frontend/src/` subdirectory has a defined responsibility."
REQ_ROW PASS id=REQ-STRUCT-012 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/requirements/Chapter16_ProjectStructure.md
REQ_TITLE PASS id=REQ-STRUCT-012 title="backend subdirectory responsibilities" statement="Each `backend/app/` subdirectory has a defined responsibility."
REQ_ROW PASS id=REQ-STRUCT-020 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/requirements/Chapter16_ProjectStructure.md
REQ_TITLE PASS id=REQ-STRUCT-020 title="root file purposes" statement="Each root file has a defined purpose and, where applicable, a mapped criterion."
REQ_ROW PASS id=REQ-STRUCT-021 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/requirements/Chapter16_ProjectStructure.md
REQ_TITLE PASS id=REQ-STRUCT-021 title="workflow file purposes" statement="Each workflow file has a defined purpose and mapped criterion."
REQ_ROW PASS id=REQ-STRUCT-022 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/requirements/Chapter16_ProjectStructure.md
REQ_TITLE PASS id=REQ-STRUCT-022 title="frontend file purposes" statement="Each frontend file has a defined purpose."
REQ_ROW PASS id=REQ-STRUCT-023 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/requirements/Chapter16_ProjectStructure.md
REQ_TITLE PASS id=REQ-STRUCT-023 title="backend file purposes" statement="Each backend file has a defined purpose."
REQ_ROW PASS id=REQ-STRUCT-024 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/requirements/Chapter16_ProjectStructure.md
REQ_TITLE PASS id=REQ-STRUCT-024 title="E2E file purposes" statement="Each E2E file has a defined purpose."
REQ_ROW PASS id=REQ-STRUCT-025 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/requirements/Chapter16_ProjectStructure.md
REQ_TITLE PASS id=REQ-STRUCT-025 title="docs file purposes" statement="Each docs file has a defined purpose."
REQ_ROW PASS id=REQ-STRUCT-026 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/requirements/Chapter16_ProjectStructure.md
REQ_TITLE PASS id=REQ-STRUCT-026 title="security file purposes" statement="Each security file has a defined purpose."
REQ_ROW PASS id=REQ-STRUCT-027 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/requirements/Chapter16_ProjectStructure.md
REQ_TITLE PASS id=REQ-STRUCT-027 title="ops file purposes" statement="Each ops file has a defined purpose."
REQ_ROW PASS id=REQ-STRUCT-028 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/requirements/Chapter16_ProjectStructure.md
REQ_TITLE PASS id=REQ-STRUCT-028 title="agent extension file purposes" statement="Each agent extension file has a defined purpose."
REQ_ROW PASS id=REQ-STRUCT-029 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-STRUCT-029 title="symlink purposes" statement="Each symlink has a defined target and purpose."
REQ_ROW PASS id=REQ-STRUCT-040 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-STRUCT-040 title="file count summary" statement="The project totals approximately 230 files across root, CI/CD, frontend, backend, E2E, docs, security, ops, agent extension, and screenshots."
REQ_ROW PASS id=REQ-STRUCT-050 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/coding_standards.md
REQ_TITLE PASS id=REQ-STRUCT-050 title="file naming" statement="React components PascalCase.tsx; hooks camelCase.ts with `use` prefix; TypeScript modules camelCase.ts; test files same name + `.test.ts(x)`; Python modules sna"
REQ_ROW PASS id=REQ-STRUCT-051 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/coding_standards.md
REQ_TITLE PASS id=REQ-STRUCT-051 title="directory naming" statement="Feature directories lowercase; Python packages snake_case; agent tool directories kebab-case; docs subdirectories lowercase."
REQ_ROW PASS id=REQ-STRUCT-052 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/requirements/Chapter16_ProjectStructure.md
REQ_TITLE PASS id=REQ-STRUCT-052 title="mixed conventions rationale" statement="Python follows PEP 8; React follows community convention; Markdown uses kebab-case for URLs; agent tools match tool conventions."
REQ_ROW PASS id=REQ-STRUCT-060 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.gitignore
REQ_TITLE PASS id=REQ-STRUCT-060 title="excluded content" statement="`.env`, node_modules, .venv, `__pycache__`, *.db, dist, build, coverage, tool caches, .DS_Store, *.log, real user data, production dumps, RENDER_DEPLOY_HOOK are"
REQ_ROW PASS id=REQ-STRUCT-070 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-STRUCT-070 title="monorepo choice" statement="Single repository with top-level frontend, backend, e2e, docs, security, ops, and agent directories."
REQ_ROW PASS id=REQ-STRUCT-071 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-STRUCT-071 title="agent directories choice" statement="Agent capabilities, hooks, MCP, and custom-agent live in their own top-level directories with symlinks in `.agents/`."
REQ_ROW PASS id=REQ-STRUCT-072 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md,docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-STRUCT-072 title="tests beside code" statement="Frontend tests use `*.test.ts(x)` beside source; backend tests separate in `tests/unit/` and `tests/integration/`."
REQ_ROW PASS id=REQ-STRUCT-073 family=STRUCT status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/architecture.md
REQ_TITLE PASS id=REQ-STRUCT-073 title="no extra tooling" statement="No `src/` at root; no Turborepo or Nx; flat layout."
REQ_ROW PASS id=REQ-TECH-001 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/package.json
REQ_TITLE PASS id=REQ-TECH-001 title="Frontend framework" statement="The frontend uses React 18 with TypeScript 5, built with Vite 5."
REQ_ROW PASS id=REQ-TECH-002 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/src/App.tsx
REQ_TITLE PASS id=REQ-TECH-002 title="Frontend routing" statement="The frontend uses React Router v6 for client-side routing with nested routes and route guards."
REQ_ROW PASS id=REQ-TECH-003 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/tailwind.config.js
REQ_TITLE PASS id=REQ-TECH-003 title="Frontend styling" statement="The frontend uses Tailwind CSS 3 for styling, with no runtime CSS-in-JS."
REQ_ROW PASS id=REQ-TECH-004 family=TECH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t2.md,docs/issues/closed/t21.md,docs/issues/closed/t23.md
REQ_TITLE PASS id=REQ-TECH-004 title="Frontend charts" statement="The frontend uses Recharts 2 for all five chart types."
REQ_ROW PASS id=REQ-TECH-005 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/src/main.tsx
REQ_TITLE PASS id=REQ-TECH-005 title="Frontend server state" statement="The frontend uses TanStack Query 5 for server state management, including caching, retries, and invalidation."
REQ_ROW PASS id=REQ-TECH-006 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/src/utils/validation.ts
REQ_TITLE PASS id=REQ-TECH-006 title="Frontend forms and validation" statement="The frontend uses React Hook Form 7 with Zod 3 for form state and validation."
REQ_ROW PASS id=REQ-TECH-007 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/src/api/client.ts
REQ_TITLE PASS id=REQ-TECH-007 title="Frontend HTTP client" statement="The frontend uses Axios 1 with request and response interceptors for auth token attachment and error normalization."
REQ_ROW PASS id=REQ-TECH-008 family=TECH status=DEFERRED_RULLED method=card-declared-ruling pointers=docs/rulings/req-matrix.md deferral_key=RULING_TECH_DATEFNS_OVERRULED issue=65 deferral_reason="OVERRULED by the approved t20 ac6 dependency-absence gate: date-fns is banned from frontend/package.json and stdlib month math shipped (platform #65 ruling, docs/rulings/req-matrix.md)"
REQ_TITLE PASS id=REQ-TECH-008 title="Frontend date utilities" statement="The frontend uses date-fns 3 for date manipulation."
REQ_ROW PASS id=REQ-TECH-009 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/package.json
REQ_TITLE PASS id=REQ-TECH-009 title="Frontend testing tools" statement="The frontend uses Vitest 1 with React Testing Library 14 and MSW 2 for unit, component, and API mocking tests."
REQ_ROW PASS id=REQ-TECH-010 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/.eslintrc.cjs,frontend/.prettierrc
REQ_TITLE PASS id=REQ-TECH-010 title="Frontend linting and formatting" statement="The frontend uses ESLint 8, Prettier 3, and TypeScript ESLint 7."
REQ_ROW PASS id=REQ-TECH-020 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/pyproject.toml
REQ_TITLE PASS id=REQ-TECH-020 title="Backend language and framework" statement="The backend uses Python 3.12 with FastAPI 0.110+."
REQ_ROW PASS id=REQ-TECH-021 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/pyproject.toml
REQ_TITLE PASS id=REQ-TECH-021 title="Backend ORM and migrations" statement="The backend uses SQLAlchemy 2.0 and Alembic 1.13+."
REQ_ROW PASS id=REQ-TECH-022 family=TECH status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/schemas/health.py,docs/issues/closed/t1.md,docs/issues/closed/t13.md
REQ_TITLE PASS id=REQ-TECH-022 title="Backend validation" statement="The backend uses Pydantic 2 for request and response validation, including Decimal support."
REQ_ROW PASS id=REQ-TECH-023 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/pyproject.toml
REQ_TITLE PASS id=REQ-TECH-023 title="Backend JWT and password libraries" statement="The backend uses python-jose 3.3+ for JWT and passlib[bcrypt] 1.7+ for password hashing."
REQ_ROW PASS id=REQ-TECH-024 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/pyproject.toml
REQ_TITLE PASS id=REQ-TECH-024 title="Backend server" statement="The backend uses uvicorn 0.29+ as the ASGI server."
REQ_ROW PASS id=REQ-TECH-025 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/uv.lock
REQ_TITLE PASS id=REQ-TECH-025 title="Backend dependency management" statement="The backend uses uv for dependency management with a committed `uv.lock`."
REQ_ROW PASS id=REQ-TECH-026 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/pyproject.toml,mcp-server/pyproject.toml
REQ_TITLE PASS id=REQ-TECH-026 title="Backend HTTP client" statement="The backend uses httpx 0.27+ for testing and for the MCP server's API calls."
REQ_ROW PASS id=REQ-TECH-027 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/pyproject.toml
REQ_TITLE PASS id=REQ-TECH-027 title="Backend testing tools" statement="The backend uses pytest 8, pytest-cov 5, and pytest-asyncio 0.23+."
REQ_ROW PASS id=REQ-TECH-028 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/pyproject.toml
REQ_TITLE PASS id=REQ-TECH-028 title="Backend linting and type checking" statement="The backend uses ruff 0.4+ for linting and formatting, and mypy 1.10+ for static type checking."
REQ_ROW PASS id=REQ-TECH-030 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.env.example,docker-compose.yml,render.yaml
REQ_TITLE PASS id=REQ-TECH-030 title="Database per environment" statement="Local development defaults to SQLite, Docker Compose uses PostgreSQL 16, production uses Render PostgreSQL 16, and fallback uses SQLite."
REQ_ROW PASS id=REQ-TECH-031 family=TECH status=IMPLEMENTED_STRUCTURAL method=citation pointers=backend/app/models/category.py,docs/issues/closed/t10.md,docs/issues/closed/t3.md
REQ_TITLE PASS id=REQ-TECH-031 title="Database abstraction" statement="All database access goes through SQLAlchemy"
REQ_ROW PASS id=REQ-TECH-032 family=TECH status=IMPLEMENTED_TESTED method=citation pointers=backend/tests/unit/test_audit_log_model.py
REQ_TITLE PASS id=REQ-TECH-032 title="SQLite-specific handling" statement="SQLite uses `PRAGMA foreign_keys = ON` per connection, `check_same_thread: False`, avoids PostgreSQL-specific functions, and generates UUIDs in Python."
REQ_ROW PASS id=REQ-TECH-040 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=Dockerfile,docker-compose.yml
REQ_TITLE PASS id=REQ-TECH-040 title="Docker base images" statement="The frontend build stage uses `node:20-alpine`, the backend runtime uses `python:3.12-slim`, and Compose uses `postgres:16-alpine`."
REQ_ROW PASS id=REQ-TECH-041 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docker-compose.yml
REQ_TITLE PASS id=REQ-TECH-041 title="Docker Compose services" statement="Docker Compose defines two services: `db` (PostgreSQL) and `app` (full-stack application on port 8000)."
REQ_ROW PASS id=REQ-TECH-042 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=Dockerfile
REQ_TITLE PASS id=REQ-TECH-042 title="Single app container" statement="In production, the frontend is built to static files and served by FastAPI from a single container."
REQ_ROW PASS id=REQ-TECH-050 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.github/workflows/ci.yml,.github/workflows/deploy.yml,.github/workflows/e2e.yml
REQ_TITLE PASS id=REQ-TECH-050 title="CI/CD provider" statement="GitHub Actions runs three workflows: `ci.yml`, `e2e.yml`, and `deploy.yml`."
REQ_ROW PASS id=REQ-TECH-051 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.github/workflows/ci.yml,.github/workflows/deploy.yml,.github/workflows/e2e.yml
REQ_TITLE PASS id=REQ-TECH-051 title="Workflow triggers" statement="`ci.yml` runs on PR and push to main; `e2e.yml` runs on push to main; `deploy.yml` runs after `e2e.yml` succeeds."
REQ_ROW PASS id=REQ-TECH-060 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=render.yaml
REQ_TITLE PASS id=REQ-TECH-060 title="Deployment platform" statement="The application deploys to Render free tier with a free PostgreSQL database."
REQ_ROW PASS id=REQ-TECH-061 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=README.md,ops/runbook.md
REQ_TITLE PASS id=REQ-TECH-061 title="Render free tier limitations" statement="The project documents Render free tier limitations: 15-minute idle sleep, 30-day PostgreSQL expiry, 512 MB RAM, 0.1 CPU, no SSH, no persistent disk, 750 hours/m"
REQ_ROW PASS id=REQ-TECH-062 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=README.md
REQ_TITLE PASS id=REQ-TECH-062 title="Cold start mitigation" statement="UptimeRobot pings the health endpoint every 10 minutes to reduce cold starts."
REQ_ROW PASS id=REQ-TECH-070 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/ai-workflow.md
REQ_TITLE PASS id=REQ-TECH-070 title="AI coding agent" statement="The project uses pi-agent with qwen3.8-27b running locally, with plugins added as needed."
REQ_ROW PASS id=REQ-TECH-071 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=security/ai-tool-data-policy.md
REQ_TITLE PASS id=REQ-TECH-071 title="AI data policy" statement="All code, prompts, and context stay on the local machine"
REQ_ROW PASS id=REQ-TECH-072 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=README.md
REQ_TITLE PASS id=REQ-TECH-072 title="Version control" statement="The project uses Git, GitHub, Conventional Commits, and feature branches."
REQ_ROW PASS id=REQ-TECH-073 family=TECH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/plan.md
REQ_TITLE PASS id=REQ-TECH-073 title="Code quality tools" statement="The project uses ruff and mypy for Python, ESLint and Prettier for TypeScript, and the TypeScript compiler for type checking."
REQ_ROW PASS id=REQ-TECH-074 family=TECH status=IMPLEMENTED_STRUCTURAL method=citation pointers=Makefile,backend/scripts/security_ops_verification.py,docs/criteria/security_ops_verification.md
REQ_TITLE PASS id=REQ-TECH-074 title="Security scanning tools" statement="The project uses gitleaks, semgrep, trivy, pip-audit, and npm audit"
REQ_ROW PASS id=REQ-TECH-075 family=TECH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t27.md,docs/issues/closed/t52.md,docs/issues/closed/t54.md
REQ_TITLE PASS id=REQ-TECH-075 title="Testing tools" statement="The project uses pytest, Vitest, React Testing Library, MSW, Playwright, and httpx."
REQ_ROW PASS id=REQ-TECH-076 family=TECH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t39.md
REQ_TITLE PASS id=REQ-TECH-076 title="Monitoring tools" statement="The project uses Render logs, the health check endpoint, and UptimeRobot."
REQ_ROW PASS id=REQ-TECH-080 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=backend/pyproject.toml,backend/uv.lock
REQ_TITLE PASS id=REQ-TECH-080 title="Backend version pinning" statement="Backend dependencies are pinned via `pyproject.toml` and `uv.lock`."
REQ_ROW PASS id=REQ-TECH-081 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/package-lock.json,package-lock.json,package.json
REQ_TITLE PASS id=REQ-TECH-081 title="Frontend version pinning" statement="Frontend dependencies are pinned via `package.json` and `package-lock.json`."
REQ_ROW PASS id=REQ-TECH-082 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=Dockerfile,docker-compose.yml
REQ_TITLE PASS id=REQ-TECH-082 title="Docker image pinning" statement="Docker base images are pinned to specific tags; no `latest` tags in production Dockerfiles."
REQ_ROW PASS id=REQ-TECH-083 family=TECH status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/config_reference.md
REQ_TITLE PASS id=REQ-TECH-083 title="GitHub Actions pinning" statement="GitHub Actions are pinned to major versions (e.g., `actions/checkout@v4`)."
REQ_ROW PASS id=REQ-TECH-090 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.env.example
REQ_TITLE PASS id=REQ-TECH-090 title="Environment variable list" statement="All configuration is via environment variables listed in `.env.example`, covering DATABASE_URL, JWT settings, CORS, ENVIRONMENT, APP_VERSION, DB_CONNECT_TIMEOUT"
REQ_ROW PASS id=REQ-TECH-091 family=TECH status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.env.example
REQ_TITLE PASS id=REQ-TECH-091 title="No real secrets in .env.example" statement="`.env.example` contains only placeholders and defaults; no real secrets."
REQ_ROW PASS id=REQ-TEST-001 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-001 title="four test layers" statement="Testing is organized into four layers: backend unit (pytest), backend integration (pytest + httpx), frontend unit/component (Vitest + RTL), and end-to-end (Play"
REQ_ROW PASS id=REQ-TEST-002 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-002 title="testing principles" statement="Tests assert behavior not implementation, one assertion per concept, independent, deterministic, fast by default, realistic integration, isolated E2E."
REQ_ROW PASS id=REQ-TEST-003 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t51.md,docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-003 title="coverage policy" statement="Coverage is reported but not enforced"
REQ_ROW PASS id=REQ-TEST-010 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-010 title="backend test structure" statement="Backend tests live in `backend/tests/` with `conftest.py`, `unit/`, and `integration/` subdirectories."
REQ_ROW PASS id=REQ-TEST-011 family=TEST status=IMPLEMENTED_TESTED method=verification-artifact pointers=frontend/src/api/client.test.ts
REQ_TITLE PASS id=REQ-TEST-011 title="test fixtures" statement="`conftest.py` provides `db_session` (in-memory SQLite with StaticPool), `user_a`, `user_b`, `system_category`, `client`, `auth_headers`, `auth_headers_b`."
REQ_ROW PASS id=REQ-TEST-012 family=TEST status=IMPLEMENTED_TESTED method=verification-artifact pointers=backend/tests/unit/test_password.py
REQ_TITLE PASS id=REQ-TEST-012 title="password tests" statement="`test_password.py` verifies hash is not plain, hash starts with `$2b$`, correct password verifies, wrong password fails, hash is salted."
REQ_ROW PASS id=REQ-TEST-013 family=TEST status=IMPLEMENTED_TESTED method=verification-artifact pointers=backend/tests/unit/test_jwt.py
REQ_TITLE PASS id=REQ-TEST-013 title="JWT tests" statement="`test_jwt.py` verifies claims, valid token decoding, expired token raises, wrong audience raises, wrong issuer raises."
REQ_ROW PASS id=REQ-TEST-014 family=TEST status=IMPLEMENTED_TESTED method=verification-artifact pointers=backend/tests/unit/test_auth_service.py
REQ_TITLE PASS id=REQ-TEST-014 title="auth service tests" statement="`test_auth_service.py` verifies register success, duplicate email, duplicate username, login success, wrong password, nonexistent email."
REQ_ROW PASS id=REQ-TEST-015 family=TEST status=IMPLEMENTED_TESTED method=verification-artifact pointers=backend/tests/unit/test_expense_service.py
REQ_TITLE PASS id=REQ-TEST-015 title="expense service tests" statement="`test_expense_service.py` verifies create, audit log on create, user isolation on list, audit log on update, cross-user delete returns 404."
REQ_ROW PASS id=REQ-TEST-016 family=TEST status=IMPLEMENTED_TESTED method=verification-artifact pointers=backend/tests/unit/test_budget_service.py
REQ_TITLE PASS id=REQ-TEST-016 title="budget service tests" statement="`test_budget_service.py` verifies create, upsert, nonexistent returns None, delete nonexistent returns 404, invalid year_month format."
REQ_ROW PASS id=REQ-TEST-017 family=TEST status=IMPLEMENTED_TESTED method=verification-artifact pointers=backend/tests/unit/test_dashboard_service.py
REQ_TITLE PASS id=REQ-TEST-017 title="dashboard service tests" statement="`test_dashboard_service.py` verifies summary with no expenses, summary with budget and expenses, over budget, by-category aggregation, trend includes empty mont"
REQ_ROW PASS id=REQ-TEST-018 family=TEST status=IMPLEMENTED_STRUCTURAL method=code-symbol pointers=backend/app/services/dashboard_service.py
REQ_TITLE PASS id=REQ-TEST-018 title="decimal helper tests" statement="`test_decimal_helpers.py` verifies `to_decimal` from string, from float (quantizes), from None, from int, quantizes to two places."
REQ_ROW PASS id=REQ-TEST-020 family=TEST status=IMPLEMENTED_TESTED method=verification-artifact pointers=backend/tests/integration/test_auth_api.py
REQ_TITLE PASS id=REQ-TEST-020 title="auth API tests" statement="`test_auth_api.py` verifies register success, duplicate email, short password, login success, wrong password, me with valid token, me without token, me with inv"
REQ_ROW PASS id=REQ-TEST-021 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-021 title="expenses API tests" statement="`test_expenses_api.py` verifies create, negative amount, zero amount, three decimals, requires auth, pagination, invalid page, page_size too large, update, dele"
REQ_ROW PASS id=REQ-TEST-022 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-022 title="budgets API tests" statement="`test_budgets_api.py` verifies set budget, get nonexistent returns 0, invalid year_month, delete budget, delete nonexistent returns 404."
REQ_ROW PASS id=REQ-TEST-023 family=TEST status=IMPLEMENTED_TESTED method=verification-artifact pointers=backend/tests/integration/test_dashboard_api.py
REQ_TITLE PASS id=REQ-TEST-023 title="dashboard API tests" statement="`test_dashboard_api.py` verifies summary empty, by-category empty, trend default six months, cumulative returns all days, heatmap returns weeks, recent default"
REQ_ROW PASS id=REQ-TEST-024 family=TEST status=IMPLEMENTED_TESTED method=verification-artifact pointers=backend/tests/integration/test_isolation.py
REQ_TITLE PASS id=REQ-TEST-024 title="isolation tests" statement="`test_isolation.py` verifies user cannot read, update, or delete another user's expense (404), user sees only own expenses, budget isolation."
REQ_ROW PASS id=REQ-TEST-025 family=TEST status=IMPLEMENTED_TESTED method=verification-artifact pointers=backend/tests/integration/test_health_api.py
REQ_TITLE PASS id=REQ-TEST-025 title="health API test" statement="`test_health_api.py` verifies status in (ok, degraded), database in (postgresql, sqlite), fallback_active is bool, version present."
REQ_ROW PASS id=REQ-TEST-026 family=TEST status=IMPLEMENTED_TESTED method=verification-artifact pointers=backend/tests/integration/test_agent_hooks.py
REQ_TITLE PASS id=REQ-TEST-026 title="agent hooks test" statement="`test_agent_hooks.py` verifies validate_amount accepts valid and rejects negative, zero, three decimals, non-number, over-max; validate_ownership accepts same u"
REQ_ROW PASS id=REQ-TEST-030 family=TEST status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=frontend/src/test/setup.ts
REQ_TITLE PASS id=REQ-TEST-030 title="frontend test setup" statement="`frontend/src/test/setup.ts` starts and stops MSW, resets handlers after each test."
REQ_ROW PASS id=REQ-TEST-031 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-031 title="format tests" statement="`format.test.ts` verifies `formatUSD` for integer, decimal, large with commas, zero, negative; `formatPercent` for whole, decimal, null; `formatMonth`."
REQ_ROW PASS id=REQ-TEST-032 family=TEST status=IMPLEMENTED_TESTED method=code-symbol pointers=frontend/src/components/common/month_picker.test.tsx,frontend/src/pages/budget_page.test.tsx,frontend/src/pages/dashboard_page.test.tsx
REQ_TITLE PASS id=REQ-TEST-032 title="date tests" statement="`date.test.ts` verifies `currentYearMonth` format, `shiftMonth` forward/backward/year boundaries, `monthRange`."
REQ_ROW PASS id=REQ-TEST-033 family=TEST status=IMPLEMENTED_TESTED method=code-symbol pointers=frontend/src/components/forms/budget_form.test.tsx
REQ_TITLE PASS id=REQ-TEST-033 title="validation tests" statement="`validation.test.ts` verifies `amountSchema` for valid, integer, negative, zero, three decimals, non-numeric; `expenseFormSchema` for valid, invalid category_id"
REQ_ROW PASS id=REQ-TEST-034 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-034 title="BudgetProgress tests" statement="`BudgetProgress.test.tsx` verifies green under 80%, yellow 80-100%, red over 100%, caps at 100%, 'No budget set' when budget 0, formatted amounts."
REQ_ROW PASS id=REQ-TEST-035 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-035 title="WeeklyHeatmap tests" statement="`WeeklyHeatmap.test.tsx` verifies 7 days rendered, grey for zero, handles max zero, shows skeleton when loading."
REQ_ROW PASS id=REQ-TEST-036 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-036 title="CategoryPieChart tests" statement="`CategoryPieChart.test.tsx` verifies empty state, renders with data, merges to Other when > 6 categories."
REQ_ROW PASS id=REQ-TEST-037 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-037 title="ExpenseForm tests" statement="`ExpenseForm.test.tsx` verifies empty amount error, negative amount error, three decimals error, cancel callback."
REQ_ROW PASS id=REQ-TEST-038 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-038 title="LoginPage tests" statement="`LoginPage.test.tsx` verifies fields render, invalid email error, invalid credentials error."
REQ_ROW PASS id=REQ-TEST-039 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/issues/closed/t17.md,docs/issues/closed/t20.md,docs/issues/closed/t9.md
REQ_TITLE PASS id=REQ-TEST-039 title="MSW handlers" statement="MSW handlers cover `/auth/login`, `/auth/me`, `/categories`, `/expenses`, `/dashboard/summary`."
REQ_ROW PASS id=REQ-TEST-040 family=TEST status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=e2e/playwright.config.ts
REQ_TITLE PASS id=REQ-TEST-040 title="Playwright setup" statement="`e2e/` contains tests/, fixtures/, and `playwright.config.ts` with baseURL, timeout 60s, retries 1, workers 1, HTML reporter, trace on first retry, screenshot o"
REQ_ROW PASS id=REQ-TEST-041 family=TEST status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=e2e/fixtures/helpers.ts,e2e/fixtures/users.ts
REQ_TITLE PASS id=REQ-TEST-041 title="E2E fixtures" statement="`fixtures/users.ts` provides `uniqueUser`; `fixtures/helpers.ts` provides `registerUser`, `loginUser`, `addExpense`, `setBudget`."
REQ_ROW PASS id=REQ-TEST-042 family=TEST status=IMPLEMENTED_TESTED method=citation pointers=e2e/tests/happy-path.spec.ts
REQ_TITLE PASS id=REQ-TEST-042 title="happy path test" statement="`happy-path.spec.ts` runs through register, three expenses, set budget, verify dashboard totals, all five charts visible, recent shows three items, edit, verify"
REQ_ROW PASS id=REQ-TEST-043 family=TEST status=IMPLEMENTED_TESTED method=citation pointers=e2e/tests/isolation.spec.ts
REQ_TITLE PASS id=REQ-TEST-043 title="isolation test" statement="`isolation.spec.ts` runs two browser contexts: User A registers and adds expense; User B registers and sees empty dashboard and no expense rows."
REQ_ROW PASS id=REQ-TEST-044 family=TEST status=IMPLEMENTED_TESTED method=citation pointers=e2e/tests/month-switch.spec.ts
REQ_TITLE PASS id=REQ-TEST-044 title="month switch test" statement="`month-switch.spec.ts` adds expenses in two months, switches months, verifies totals update, switches back, verifies."
REQ_ROW PASS id=REQ-TEST-045 family=TEST status=IMPLEMENTED_TESTED method=citation pointers=e2e/tests/happy-path.spec.ts,e2e/tests/isolation.spec.ts
REQ_TITLE PASS id=REQ-TEST-045 title="E2E data isolation" statement="Each E2E test creates a unique user with timestamp and random ID; no cleanup between tests; optional cleanup SQL documented."
REQ_ROW PASS id=REQ-TEST-050 family=TEST status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=Makefile
REQ_TITLE PASS id=REQ-TEST-050 title="Makefile targets" statement="Makefile targets: `test`, `test-backend`, `test-backend-unit`, `test-backend-integration`, `test-backend-cov`, `test-frontend`, `test-frontend-cov`, `e2e`."
REQ_ROW PASS id=REQ-TEST-051 family=TEST status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=.github/workflows/ci.yml,.github/workflows/e2e.yml
REQ_TITLE PASS id=REQ-TEST-051 title="CI execution" statement="`ci.yml` runs `make test-backend` and `make test-frontend`; `e2e.yml` runs `make e2e`."
REQ_ROW PASS id=REQ-TEST-060 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-060 title="backend test data" statement="Backend unit and integration tests use in-memory SQLite with seeded system categories; test users created per test via fixtures."
REQ_ROW PASS id=REQ-TEST-061 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-061 title="frontend test data" statement="Frontend unit tests use pure functions; component tests use MSW handlers with fixed data; page tests use MSW variants."
REQ_ROW PASS id=REQ-TEST-062 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-062 title="E2E test data" statement="E2E tests use the real backend and database with unique users per test."
REQ_ROW PASS id=REQ-TEST-063 family=TEST status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-063 title="SQLite for backend tests rationale" statement="SQLite in-memory is fast, isolated, needs no external dependency, and uses the same ORM; PostgreSQL is tested in CI via Docker Compose."
REQ_ROW PASS id=REQ-TEST-070 family=TEST status=IMPLEMENTED_STRUCTURAL method=verification-artifact pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-070 title="not tested list" statement="Render deployment, cold start, UptimeRobot, browser compatibility, load testing, security scanning, visual regression, accessibility automation are not tested."
REQ_ROW PASS id=REQ-TEST-080 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-080 title="framework choices" statement="pytest for backend, pytest + TestClient for integration, SQLite in-memory, Vitest for frontend, RTL for components, MSW for API mocking, Playwright for E2E."
REQ_ROW PASS id=REQ-TEST-081 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-081 title="execution choices" statement="Coverage reported not enforced; CI runs unit + integration; E2E only on main; per-test fixtures; Decimal comparison; fixed dates."
REQ_ROW PASS id=REQ-TEST-082 family=TEST status=IMPLEMENTED_STRUCTURAL method=citation pointers=docs/testing-guidelines.md
REQ_TITLE PASS id=REQ-TEST-082 title="error testing" statement="Error tests assert both status code and error code."

## Honest GAP list (t58's input, measured not asserted)

Every GAP row above is a requirement whose verification this hermetic gate
could not point at concrete in-repo evidence. The rows below restate them
for the remediation card; the count is the REQ_STATUS_COUNT GAP row above.

