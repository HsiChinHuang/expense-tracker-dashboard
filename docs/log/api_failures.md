# API Failures

Runtime-maintained. Write rules are in `api_failures_rules.md`.

**Writer**: Orchestrator only.

## Format

    [SEQ] [TS] [ENDPOINT] [STATUS] [RETRY_COUNT] [NOTE]

## Entries

(none yet)
[18] 2026-10-07T15:11:04Z POST /repos/HsiChinHuang/expense-tracker-dashboard/issues 500 3 POST/DELETE broken on issue endpoints; GET/PATCH OK; GraphQL createIssue also fails
[19] 2026-10-07T17:05:00Z POST /repos/HsiChinHuang/expense-tracker-dashboard/issues/6/comments 500 6 MERGE VERDICT post-merge comment for t3 failed; 6 attempts with backoff ~16:53-17:05Z all HTTP 500 null; GET/PATCH OK; logged by verifier per Orchestrator authorization (t3 verify_post_merge)
