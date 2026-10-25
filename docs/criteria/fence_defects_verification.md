# Fence-defect verification carrier (t131)

Carrier for the five inventoried CARD-FENCE DEFECT classes from the phase_22 sweep
(t124/t126 verdicts). This file is the committed, greppable record of the corrected
fence blocks and their measured values. It is NOT taught to any generator (the t124
no-generator ruling) and it moves zero index bytes.

- Card: `docs/issues/t131.md` (platform issue 135, milestone `phase_23_backlog_hygiene`)
- Card ac_hash measured against: `sha256:d44883772732eeab844f84ac6830b99024424c8dfc9c65be49afeb8b95e8b53f`
- Base: main `c02f3027197d8cb30439377b0ab8b192ff36614a`
- Host class: WSL worktree (Windows `.git/worktrees` pointer), builder worktree
  `pi-worktree-ec8ff2eb-464b-415c-a04c-40c0d55d913d-s0-0`
- Every value below was MEASURED on the builder's tree by running the card's own
  fences (ac1-ac4 verbatim), not copied from the card's Context table.

## Pinned rows (the ac6 contract)

| FENCE_DEFECT | class1_readme_lines_pin | 421 |
| FENCE_DEFECT | class1_offby_one_value | 422 |
| FENCE_DEFECT | class2_corrected_guard_rc | 0 |
| FENCE_DEFECT | class2_bare_git_rc | 128 |
| FENCE_DEFECT | class3_live_matching_record | docs/state/outputs/t124_definer_gate_amendment_v2.json |
| FENCE_DEFECT | class4_ac_less_count | 193 |
| FENCE_DEFECT | class4_anchor_count | 8 |
| FENCE_DEFECT | class4_amendments_needed | 0 |
| FENCE_DEFECT | class5_disposition | out-of-scope-follow-up |
| FENCE_DEFECT | zero_amendment_record | docs/state/outputs/t131_definer_gate_amendment.json |
| FENCE_DEFECT | carrier_run | t131 builder implement at base c02f302 on the WSL worktree class, fences ac1-ac4 run verbatim, all GREEN rc=0 |

## Class 1 - split-newlines off-by-one (t124 ac5 class)

Defect: `len(raw.split("\n"))` on a newline-terminated file returns lines+1, so a
fence pinning `README_LINES` via `split("\n")` is structurally RED on every
newline-terminated tree.

Measured on this tree: pin `README_LINES = 421`; `len(raw.splitlines())` = 421
(CORRECTED, GREEN); `tr -d "\r" | wc -l` = 421 (CORRECTED shell spelling, GREEN);
`len(raw.split("\n"))` = 422 = pin+1 (OFF-BY-ONE negative control, measured).

Corrected convention:

```python
corrected = len(raw.splitlines())          # GREEN: equals the pin
shell_corrected = 'tr -d "\\r" < README.md | wc -l'   # GREEN: equals the pin
off_by_one = len(raw.split("\n"))          # RED specimen: pin + 1 on terminated files
```

## Class 2 - `--git-dir`/plain-git WSL guard (t124/t126 ac5 class)

Defect: inside the WSL worktree, the worktree gitdir pointer is a Windows path, so
bare `git rev-parse --git-dir` exits rc=128 (`fatal: not a git repository:
.../C:/Users/...`) - a fence whose guard is bare git is structurally RED in this
worktree class.

Measured on this tree: corrected cmd.exe-wrapped guard exits rc=0 (gitdir named:
`C:/Users/tw097/Desktop/261007_project01/expense-tracker-dashboard/.git/worktrees/pi-worktree-ec8ff2eb-464b-415c-a04c-40c0d55d913d-s0-0`);
bare `git rev-parse --git-dir` exits rc=128 (negative control, measured).

Corrected guard:

```bash
ROOT=$(pwd)
G=$(wslpath -w "$ROOT" 2>/dev/null || pwd -W 2>/dev/null || echo "$ROOT")
cmd.exe /d /c "git -C $G rev-parse --git-dir"   # rc=0 on the WSL worktree class
```

## Class 3 - hardcoded superseded amendment path (t124 ac2 class)

Defect: a fence that hardcodes `docs/state/outputs/t124_definer_gate_amendment.json`
(v1) is structurally RED once the orchestrator applies the superseding v2 record -
v1 still names the superseded guessed command and its pins no longer match the
live leg.

Measured on this tree: live `tests[284]` (owned by `t81`) command sha and entry sha
resolve against EXACTLY ONE amendment record:
`docs/state/outputs/t124_definer_gate_amendment_v2.json`; the path-pinned v1 record
matches NEITHER the live `new_command_sha256`/`entry_sha_after` (negative control,
measured non-matching).

Corrected fence pattern: glob the record family and pick the record whose
`new_command_sha256` + `entry_sha_after` MATCH the live leg - never a hardcoded path:

```python
for path in sorted(glob.glob("docs/state/outputs/t124_definer_gate_amendment*.json")):
    am = json.load(open(path, encoding="utf-8"))["amendments"][0]
    if csha(live_cmd) == am["new_command_sha256"] and live_entry == am["entry_sha_after"]:
        matches.append(path)   # exactly one match, or the supersession is ambiguous
```

## Class 4 - the 193 index legs missing the `ac` key (t126 verifier finding)

Measured on this tree: EXACTLY indices `0..192` (193 legs, the contiguous legacy
prefix, issues t0..t47 era) lack `ac`; every leg >= 193 carries `ac`; all 8
`INDEX_ANCHORS` positions recompute GREEN over the ac-less entries; 6 anchored legs
(`16, 54, 131, 132, 133, 135`) sit INSIDE the ac-less prefix and their pinned
digests are AC-LESS digests; the in-memory key-injection negative control CHANGED
entry 16's digest (armed, RED as expected).

Classification: **ZERO of the 193 need a fence amendment.** No consumer of those
legs reads an `ac` key, and adding one breaks six generator-pinned anchor digests.
The key fix is a GENERATOR + index coordination move (`INDEX_ANCHORS` re-pin in
`backend/scripts/docs_verification.py`) - product work, out of scope here; recorded
as a follow-up candidate.

## Class 5 - LINK_CHECK `.pytest_cache` pollution (t120 ac5 disclosure class)

Disposition: **out-of-scope-follow-up.** `SKIP_DIRS` in
`backend/scripts/docs_verification.py` does not contain `.pytest_cache`, so a
pytest run creates `backend/.pytest_cache/README.md` which LINK_CHECK counts; the
fix is a generator PRODUCT change (teach `SKIP_DIRS` the cache class), and the
stale-count half is regeneration hygiene (t132 class). This card commits the
classification, not the product fix.

## Gate-amendment posture

The gate-amendment record for this card is the ZERO-amendment record
`docs/state/outputs/t131_definer_gate_amendment.json` (t126 shape, `amendments: []`,
`add_count: 0`). Zero LIVE index legs change command text under this card; the
corrected class-1/2/3 blocks live in this card's fences and this carrier only.
