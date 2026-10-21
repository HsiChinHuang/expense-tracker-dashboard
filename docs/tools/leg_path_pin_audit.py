#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""leg_path_pin_audit.py - literal card-path pin audit for the merge-test index.

t104 deliverable. The merge-test index (docs/state/merge_test_index.json) is
ORCHESTRATOR-OWNED: this tool READS it and REPORTS; it never writes it and it
never patches a leg. Stored legs that LITERALLY name docs/issues/t<digits>.md
break when cards are archived (leg 230's t62 pin is measurably RED today; leg
279's t78 pin is GREEN only because docs/issues/t78.md was restored as a named
exemption, WAL 1229/1230).

Contract:
  * stdlib-only, offline, read-only. No network client, no writes.
  * Scans EVERY leg command in the index for a literal card path.
  * CLASSIFIES each pin: present (resolves where the leg looks), moved (the
    card exists under docs/issues/closed/ or docs/issues/groom/ but not at the
    pinned path), or missing_everywhere (the card exists in no location).
  * An audit reports by PRINTING: it exits 0 even when it finds breaks, so a
    gate can consume its record without the auditor itself going red. The
    optional --expect-pins=<n> gate exists for callers that DO want a nonzero
    exit when the derived pin count moves; it is off by default.

Usage:
  python3 docs/tools/leg_path_pin_audit.py [--index PATH] [--expect-pins N]
"""
import argparse
import json
import os
import re
import sys

# Same pattern the findings record cross-check uses (ac4 re-derives
# independently, so a divergence between the two is itself a finding).
PIN_PAT = re.compile(r"docs/issues/[A-Za-z0-9_./-]*?t\d+[A-Za-z0-9_./-]*?\.md")


def classify(pinned, repo_root):
    """present / moved / missing_everywhere for one pinned card path."""
    if os.path.isfile(os.path.join(repo_root, pinned.replace("/", os.sep))):
        return "present"
    base = os.path.basename(pinned)
    for mirror in ("docs/issues/closed", "docs/issues/groom"):
        if os.path.isfile(os.path.join(repo_root, mirror.replace("/", os.sep), base)):
            return "moved"
    return "missing_everywhere"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--index", default="docs/state/merge_test_index.json",
                    help="path to the merge-test index (read-only)")
    ap.add_argument("--expect-pins", type=int, default=None,
                    help="optional gate: exit 1 if the derived pinned-leg "
                         "count differs from N. Off by default, because the "
                         "audit's job is to report, not to gate.")
    args = ap.parse_args(argv)

    try:
        with open(args.index, encoding="utf-8") as fh:
            idx = json.load(fh)
    except (OSError, ValueError) as exc:
        sys.stderr.write("leg_path_pin_audit: cannot read index %s: %s\n" % (args.index, exc))
        return 2
    legs = idx.get("tests", [])
    # Pinned paths are repo-root-relative and the audit is run from the
    # repository root (the --index override may point at a copy in a throwaway
    # dir, so the root is the CWD, not a path derived from the index).
    repo_root = os.getcwd()

    pinned_legs = {}
    for i, leg in enumerate(legs):
        paths = sorted(set(PIN_PAT.findall(leg.get("command") or "")))
        if paths:
            pinned_legs[i] = (leg.get("issue_id"), paths)

    broken = 0
    print("leg_path_pin_audit: index=%s" % args.index)
    print("leg_path_pin_audit: legs_scanned=%d" % len(legs))
    print("leg_path_pin_audit: pinned_legs=%d" % len(pinned_legs))
    for i in sorted(pinned_legs):
        issue_id, paths = pinned_legs[i]
        for p in paths:
            status = classify(p, repo_root)
            if status == "missing_everywhere":
                broken += 1
            print("leg_path_pin_audit: pin leg %s issue=%s path=%s status=%s"
                  % (i, issue_id, p, status))
    print("leg_path_pin_audit: broken_pins=%d" % broken)
    print("leg_path_pin_audit: the index is orchestrator-owned; this audit is read-only and patched nothing")

    if args.expect_pins is not None and len(pinned_legs) != args.expect_pins:
        print("leg_path_pin_audit: EXPECT-PINS GATE: derived pinned_legs=%d but --expect-pins=%s"
              % (len(pinned_legs), args.expect_pins))
        return 1
    # Reporting is the deliverable: breaks are PRINTED, not exited on, so the
    # audit never becomes the thing that goes red.
    return 0


if __name__ == "__main__":
    sys.exit(main())
