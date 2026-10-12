# Task template

Every issue card in `docs/issues/` follows this template. The definer
authors the card during the defined and groomed states; the pinned
verification commands inside it are the contract the builder and
verifier must both reproduce verbatim. See [process.md](process.md) for
the lifecycle that produces and consumes these cards.

## Frontmatter convention

Each card opens with YAML frontmatter carrying exactly the fields this
repository uses in practice:

```yaml
---
id: tNN
title: short imperative title of the change
depends: [tXX, tYY]
platform_issue: NNN
---
```

- `id: tNN` - the local issue id, matching the file name.
- `title:` - one-line statement of intent.
- `depends: [tXX, tYY]` - local ids of cards that must be closed first
  (empty list `[]` when the card is isolated).
- `platform_issue:` - the tracker issue number the card maps to via
  `docs/state/issue_map.json`.

## Goal

One to three sentences written by the definer stating the outcome the
card must deliver, in terms a reviewer can check. The goal restates the
requirement ids the card satisfies - it never introduces new scope.

## Acceptance criteria

The checkbox list (`- [ ] ac1 ...`) that defines done. Each criterion
is a single observable behavior, phrased so that one verification
command can decide it. Criteria are frozen at groom time; changing one
is the definer's job via re-groom, not the builder's.

## Out of scope

An explicit list of files, features, and adjacent requirements this
card must not touch, with the name of the card that owns each excluded
item. The composite purity gate reads the delta against this list.

## Constraints

The hard rules the implementation must respect: the file allow-list,
byte-frozen manifests and pins, environment preconditions (for example
the Docker daemon state for frontend legs), and toolchain notes. A
builder that needs a constraint relaxed writes a BLOCKER handoff rather
than silently widening the delta.
