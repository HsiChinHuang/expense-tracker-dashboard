# Scoring-map verification record - process dimensions

Milestone: phase_20_readme_scoring_map. Card: t112 (platform issue 118).
This file is t112's entire deliverable and the evidence record the README Part 2
table cites. Every claim was re-measured by the builder against the shipped tree
at build time (main 6e36d4f, 2026-10-23); the card's fences re-measure each one,
so a path or count that moves without this record moving turns a fence RED
rather than leaving a stale claim standing.

Honesty rule (binding on every line): a claim is allowed only if a reader can
check it within 30 seconds at the named First entry point. Counts of growing
artifacts are stated as date-stamped floors, never as present-tense numbers.

## Problem Description

- Claim: 2/2
- Reason: README.md describes the problem on its first screen, names the functionality in its Features table and demonstrates expected behaviour in its Online demo section, so all three clauses of the rubric are checkable in one file.
- First entry point: `README.md`
- Evidence: `README.md`, `product-spec.md`, `docs/requirements/Chapter1_ProjectOverview.md`, `docs/requirements/Chapter2_ProductSpecification.md`
- Deep dive: `docs/requirements/Chapter1_ProjectOverview.md`

## Product Specification

- Claim: 2/2
- Reason: the spec lives at product-spec.md, the task tracker is the public GitHub Issues list on this repository where every card carries acceptance criteria, and the process evidence is re-countable in-repo - measured 2026-10-23: at least 110 closed cards under docs/issues/closed, 110 merge-history entries under the entries key, and a WAL whose highest seq is 1269.
- First entry point: `product-spec.md`
- Evidence: `product-spec.md`, `docs/issues/closed`, `docs/log/orchestrator_wal.jsonl`, `docs/state/merge_history.json`
- Deep dive: `docs/criteria/req_coverage_verification.md`

## Agent Team Specification

- Claim: 2/2
- Reason: the team is written down as four role contracts (AGENTS.md plus the builder, definer, orchestrator and verifier SKILL.md files under skills/) and the process of working together is documented in docs/process.md with the human-facing role descriptions in docs/team.
- First entry point: `AGENTS.md`
- Evidence: `AGENTS.md`, `skills/builder/SKILL.md`, `skills/definer/SKILL.md`, `skills/orchestrator/SKILL.md`, `skills/verifier/SKILL.md`, `docs/process.md`, `docs/team/pm.md`, `docs/team/software-engineer.md`, `docs/team/qa-engineer.md`
- Deep dive: `docs/process.md`

## Context Management

- Claim: 2/2
- Reason: AGENTS.md carries a Pointers section that routes each role to its own skill file, docs/process.md documents agent context loading by name, and the modular docs tree holds 17 requirements chapters under docs/requirements plus the ownership map at docs/ownership.md (measured 2026-10-23).
- First entry point: `AGENTS.md`
- Evidence: `AGENTS.md`, `docs/process.md`, `docs/ownership.md`, `docs/requirements/Chapter1_ProjectOverview.md`, `docs/requirements/Chapter16_ProjectStructure.md`
- Deep dive: `docs/process.md`
