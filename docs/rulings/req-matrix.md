# Requirement-matrix hard-case rulings (platform #65)

This artifact is the in-repo pointer target for the two card-declared
rulings that close the t57 coverage matrix's honest-hard cases. It is a
pointer-only document: `backend/scripts/req_coverage_verification.py`
never reads it at runtime. The two rulings are STATIC code constants in
the generator (`RULING_TECH_DATEFNS_OVERRULED` and
`RULING_FE_PERF_LIVE_PROFILING`), so the hermetic out-of-repo self-test
copy of the generator (which sees only `docs/requirements.md`, the
deferral register, and the generator itself) still enumerates both rows
without any new file read. Platform issue #65 carries the operator
ruling; the matrix rows for both ids point here and at issue 65.

The keys deliberately do not start with `LIVE_`. The carried deferral
register in `docs/criteria/docs_verification.md` parses only `^LIVE_`
rows and stays at exactly 4 DEFERRED entries; these two keys are
generator constants, never register rows, and adding them to the
register is out of scope for this card.

## Ruling 1: REQ-TECH-008 is OVERRULED (date-fns)

REQ-TECH-008 states that the frontend uses date-fns 3 for date
manipulation. The requirement was never dropped silently; it was
overruled by an approved dependency-absence gate that landed earlier in
the same milestone, and the t57 matrix correctly refused to grade an
overruled requirement as implemented. The gate is t20 acceptance
criterion ac6, quoted verbatim from `docs/issues/closed/t20.md`:

> **neither `recharts` nor `date-fns` is present in
> `frontend/package.json` at the end of this issue** (the phase's
> one-door test-enforcement: recharts enters ONLY in t21, date-fns
> never - plan rulings 1/2)

The same card records the constraint twice more, in the same words the
builder was held to: "Month math: stdlib string arithmetic only
(survey ruling 2 - date-fns rejected, and ac6 keeps it banned)" and
"recharts + date-fns ABSENT from frontend/package.json". The gate is
executed, not asserted: ac6's dependency leg loads
`frontend/package.json` and exits nonzero if either `recharts` or
`date-fns` appears in the merged dependency maps, so a later import of
date-fns fails a stored gate rather than passing quietly.

Consequently the date-fns pin in REQ-TECH-008 cannot be satisfied by
any honest evidence in this repository, and authoring documentation
about it would be fabrication. The post-t20 frontend imports no date
library at all (the dependency-absence leg greps the merged
`frontend/package.json` for both `recharts` and `date-fns`). Status: DEFERRED_RULLED, key `RULING_TECH_DATEFNS_OVERRULED`,
issue 65. The requirement text in `docs/requirements.md` is left
untouched; the id universe is frozen at 749 and a ruling is not an
edit. The shipped alternative is stdlib string arithmetic on the
`YYYY-MM` key: `frontend/src/utils/chart_data.ts` does its month math
with plain string operations and no date library, and ac6's
dependency-leg grep is what keeps it that way.

## Ruling 2: REQ-FE-121 is DEFERRED (live performance profiling)

REQ-FE-121 states the performance budget: initial JS bundle under
300 KB gzipped, CSS under 30 KB gzipped, Lighthouse performance above
85, First Contentful Paint under 1.5 s, and Time To Interactive under
3 s. Every clause of that budget is a measurement taken against a
running browser and a deployed page. This repository's verification
surface is hermetic by standing operator ruling: no live stack, no
browser profiling, no E2E execution inside a stored gate. The ruling is
the same one the carried deferral register already records for the
`LIVE_*` family; the register's own wording for the closest analogue is
"launching them needs a live agent runtime which this gate must not
require (no-E2E/no-live ruling)".

The static half of the budget is not deferred and is not claimed here:
bundle composition is constrained by the same ac6 dependency-absence
gate above (no charting or date library enters the bundle), and the
production image build is pinned by the carried infrastructure gates.
What cannot be closed hermetically is the numeric profiling claim
(Lighthouse score, FCP, TTI), so the row is deferred rather than
laundered through a citation. Status: DEFERRED_RULLED, key
`RULING_FE_PERF_LIVE_PROFILING`, issue 65. The live check is the
operator path, exactly as it is for the four register keys: run
Lighthouse against the deployed URL and record the numbers in
`ops/deployment-health.md`.

## Scope of these rulings

Issue 65 covers exactly these two ids. It is not a general licence to
defer: the other 97 rows of the t57 GAP set close on authored evidence
in their assigned artifacts, and the fail-closed fence in the generator
still exits nonzero if any row is GAP or any non-GAP row loses its
pointer. Issue 65 closes when the remediation branch merges.
