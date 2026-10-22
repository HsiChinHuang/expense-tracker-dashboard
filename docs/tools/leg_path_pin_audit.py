#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""leg_path_pin_audit.py - literal card-path pin audit for the merge-test index.

t104 deliverable; UPGRADED IN t106 to see the base64 class of pins; UPGRADED IN
t107 to REPLAY a findings record honestly (--against-record, see below).

The merge-test index (docs/state/merge_test_index.json) is ORCHESTRATOR-OWNED:
this tool READS it and REPORTS; it never writes it and it never patches a leg.
Stored legs that LITERALLY name docs/issues/t<digits>.md break when cards are
archived (leg 230's t62 pin is measurably RED today; leg 279's t78 pin is GREEN
only because docs/issues/t78.md was restored as a named exemption, WAL
1229/1230).

THE CLASS THIS UPGRADE MAKES VISIBLE (WAL 1236): some legs run their real test
through a quoted base64 payload (the leg echoes a long base64 chunk, pipes it
through a decoder and feeds the result to python3), and the DECODED payload
names a card path. The shipped t104 auditor grepped the
PLAINTEXT command only, so eleven legs carrying live card pins (0-based array
indices 282, 306-309, 310-312, 315-317) were invisible to it while three of them
were measurably RED. The upgrade ADDS a decoded view; it does not replace the
plaintext view: every (leg, path, status) observation t104 made is still made,
and each pin line now DISCLOSES how the pin was found via the via= field
(plaintext / decoded_base64 / plaintext+decoded_base64). Leg numbers are 0-based
array indices into the tests array and never travel bare: issue_id and ac print
with them (WAL 1240 W2 - the sweep runner prints 1-based, this checker does not).

Contract (unchanged from t104):
  * stdlib-only, offline, read-only. No network client, no writes, no shell.
  * Scans EVERY leg command in the index for a literal card path, in the
    command text AND inside decodable base64 payloads.
  * CLASSIFIES each pin: present (resolves where the leg looks), moved (the
    card exists under docs/issues/closed/ or docs/issues/groom/ but not at the
    pinned path), or missing_everywhere (the card exists in no location).
    Broken pins are COUNTED in broken_pins whether found in plaintext or in a
    decoded payload, so a consumer's broken-pin gate is no longer blind to the
    hidden class.
  * A base64 chunk that decodes but does not re-encode to its own bytes is
    NON-CANONICAL (dirty padding bits - the shape a hand-mangled payload
    takes). It gets a VISIBLE note naming the leg, is NOT mined for pins, and
    does not change the exit code: a note, never a traceback, never a silence.
  * An audit reports by PRINTING: it exits 0 even when it finds breaks, so a
    gate can consume its record without the auditor itself going red. The
    optional --expect-pins=<n> gate exists for callers that DO want a nonzero
    exit when the derived pin count moves; it is off by default and is the ONLY
    nonzero path this tool has (besides 2 for an unreadable index).
  * It runs NO stored leg, and no stored leg runs it, so this upgrade changes
    no leg's rc.

WHAT --against-record ADDS (t107 - the W1 replay made honest): a findings
record that carries a top-level index_stamp declaring WHICH index blob it was
generated against can be replayed against any index, and every observation
difference then becomes a COMPUTED statement rather than a reading-comprehension
test. The four classes are the whole contract:

  * record carries no index_stamp             -> print an UNSTAMPED note, exit 0
    (a legacy record cannot be classified; saying so beats guessing);
  * stamp == scanned blob, observations agree -> print EXPECTED lines, exit 0;
  * stamp == scanned blob, observations differ -> print DRIFT lines naming
    leg/issue/ac/path/record-vs-fresh plus the AGAINST-RECORD GATE line, exit 1
    (same-blob disagreement is REAL drift - the ONLY nonzero this cross-check
    adds, besides the pre-existing 1 for --expect-pins and 2 for an unreadable
    index);
  * stamp != scanned blob (cross-blob replay) -> differences are EXPECTED by
    definition, printed as such with a count, exit 0: the record was never a
    claim about THIS index.

The stamp is MEASURED from bytes with hashlib: sha1 over the git blob header
plus the CR-normalized index bytes, which reproduces git's own blob id
in-process precisely so the auditor keeps its offline read-only contract and
shells out to NOTHING (hashlib is t107's single import admission).

Usage:
  python3 docs/tools/leg_path_pin_audit.py [--index PATH] [--expect-pins N]
                                           [--against-record PATH]
"""
import argparse
import base64
import hashlib
import json
import os
import re
import sys

# Same pattern the findings record cross-check uses (ac4 re-derives
# independently, so a divergence between the two is itself a finding).
PIN_PAT = re.compile(r"docs/issues/[A-Za-z0-9_./-]*?t\d+[A-Za-z0-9_./-]*?\.md")

# A candidate base64 payload: a run of at least 80 alphabet characters with at
# most two padding characters at its end, bounded so it cannot start or end in
# the middle of a longer token. 80 is the floor measured at t106 groom: every
# real payload in the index is longer, and no shorter run can carry a card path
# by accident.
CHUNK_PAT = re.compile(r"(?<![A-Za-z0-9+/=])([A-Za-z0-9+/]{80,}={0,2})(?![A-Za-z0-9+/=])")


def index_stamp(index_path):
    """The stamp of an index file, MEASURED from its bytes (stdlib, offline).

    git_blob_id is sha1 over b'blob <N>' + NUL + the CR-normalized bytes -
    exactly git's own blob id, computed in-process so the auditor shells out to
    nothing. The normalization is stated inside the stamp itself because under
    core.autocrlf=true the worktree bytes and the stored blob disagree by bytes
    only, and a reader who hashes the wrong shape gets a false mismatch.
    """
    with open(index_path, "rb") as fh:
        raw = fh.read()
    norm = raw.replace(b"\r\n", b"\n")
    sh = hashlib.sha1()
    sh.update(b"blob %d\0" % len(norm))
    sh.update(norm)
    return {"git_blob_id": sh.hexdigest(),
            "sha256_cr_normalized": hashlib.sha256(norm).hexdigest(),
            "bytes_cr_normalized": len(norm)}


def record_observations(rec):
    """A findings record's per-path observations as a leg-keyed tuple set."""
    obs = {}
    for e in rec.get("path_pin_findings", []):
        leg = int(e["leg_index"])
        members = set()
        for pth, sub in (e.get("per_path_status") or {}).items():
            members.add((e.get("issue_id"), e.get("ac"), pth,
                         sub.get("status"), sub.get("via")))
        obs.setdefault(leg, set()).update(members)
    return obs


def classify(pinned, repo_root):
    """present / moved / missing_everywhere for one pinned card path."""
    if os.path.isfile(os.path.join(repo_root, pinned.replace("/", os.sep))):
        return "present"
    base = os.path.basename(pinned)
    for mirror in ("docs/issues/closed", "docs/issues/groom"):
        if os.path.isfile(os.path.join(repo_root, mirror.replace("/", os.sep), base)):
            return "moved"
    return "missing_everywhere"


def b64_canonical(chunk):
    """True when re-encoding the decoded bytes reproduces the chunk exactly.

    A chunk whose padding bits are dirty decodes to the same bytes but
    re-encodes differently; that is the measurable definition of
    non-canonical, and it is what a hand-edited payload looks like. Strict
    re-encode equality also rejects malformed lengths, so it is the ONLY test
    here - a hand-rolled padding-shape test would disagree with it (a one-pad
    group is legal, and that mistake was measured while writing this).
    """
    try:
        raw = base64.b64decode(chunk)
    except Exception:
        return False
    return base64.b64encode(raw).decode("ascii") == chunk


def decoded_paths(chunk):
    """Card paths named inside a canonical base64 payload ([] if undecodable)."""
    try:
        text = base64.b64decode(chunk).decode("utf-8")
    except Exception:
        return []
    return PIN_PAT.findall(text)


def scan_leg(command):
    """(paths in the command text, paths found only in decoded payloads, dirty legs)."""
    plain = set(PIN_PAT.findall(command))
    hidden = set()
    dirty = 0
    for m in CHUNK_PAT.finditer(command):
        chunk = m.group(1)
        if not b64_canonical(chunk):
            dirty += 1
            continue
        hidden.update(decoded_paths(chunk))
    return plain, hidden - plain, dirty


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--index", default="docs/state/merge_test_index.json",
                    help="path to the merge-test index (read-only)")
    ap.add_argument("--expect-pins", type=int, default=None,
                    help="optional gate: exit 1 if the derived pinned-leg "
                         "count differs from N. Off by default, because the "
                         "audit's job is to report, not to gate.")
    ap.add_argument("--against-record", default=None, metavar="PATH",
                    help="optional cross-check: replay this scan against a "
                         "stamped findings record and classify every "
                         "observation EXPECTED or DRIFT against the blob the "
                         "record declares. Read-only; its only nonzero is the "
                         "AGAINST-RECORD GATE on same-blob drift.")
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
    notes = []
    dirty_legs = 0
    for i, leg in enumerate(legs):
        command = leg.get("command") or ""
        plain, hidden, dirty = scan_leg(command)
        if dirty:
            dirty_legs += 1
            notes.append("leg_path_pin_audit: NOTE leg %s issue=%s ac=%s carries %d non-canonical "
                         "base64 chunk(s) (decodes, but re-encode differs - dirty padding bits); "
                         "not mined for pins, exit code unaffected"
                         % (i, leg.get("issue_id"), leg.get("ac"), dirty))
        paths = plain | hidden
        if paths:
            via = {}
            for p in paths:
                if p in plain and p in hidden:
                    via[p] = "plaintext+decoded_base64"
                elif p in plain:
                    via[p] = "plaintext"
                else:
                    via[p] = "decoded_base64"
            pinned_legs[i] = (leg.get("issue_id"), leg.get("ac"), sorted(paths), via)

    broken = 0
    print("leg_path_pin_audit: index=%s" % args.index)
    print("leg_path_pin_audit: legs_scanned=%d" % len(legs))
    print("leg_path_pin_audit: pinned_legs=%d" % len(pinned_legs))
    for note in notes:
        print(note)
    for i in sorted(pinned_legs):
        issue_id, ac, paths, via = pinned_legs[i]
        for p in paths:
            status = classify(p, repo_root)
            if status == "missing_everywhere":
                broken += 1
            print("leg_path_pin_audit: pin leg %s issue=%s ac=%s path=%s status=%s via=%s"
                  % (i, issue_id, ac, p, status, via[p]))
    print("leg_path_pin_audit: broken_pins=%d" % broken)
    print("leg_path_pin_audit: dirty_b64_legs=%d" % dirty_legs)
    print("leg_path_pin_audit: the index is orchestrator-owned; this audit is read-only and patched nothing")

    if args.expect_pins is not None and len(pinned_legs) != args.expect_pins:
        print("leg_path_pin_audit: EXPECT-PINS GATE: derived pinned_legs=%d but --expect-pins=%s"
              % (len(pinned_legs), args.expect_pins))
        return 1
    # Reporting is the deliverable: breaks are PRINTED, not exited on, so the
    # audit never becomes the thing that goes red.
    if args.against_record is not None:
        return against_record(args.against_record, args.index, pinned_legs, repo_root)
    return 0


def fresh_observations(pinned_legs, repo_root):
    """The fresh scan's observations in the SAME shape a record stores."""
    obs = {}
    for i, (issue_id, ac, paths, via) in pinned_legs.items():
        obs[i] = set((issue_id, ac, p, classify(p, repo_root), via[p]) for p in paths)
    return obs


def against_record(record_path, index_path, pinned_legs, repo_root):
    """The t107 cross-check: classify observations EXPECTED vs DRIFT.

    Read-only, stdlib-only, offline. The four classes are the whole contract,
    and the GATE line always prints when this returns 1, so a nonzero exit is
    never unattributable in a CI log.
    """
    print("leg_path_pin_audit: against-record=%s" % record_path)
    try:
        with open(record_path, encoding="utf-8") as fh:
            rec = json.load(fh)
    except (OSError, ValueError) as exc:
        # An unreadable record is REPORTED, not gated on - the same honesty rule
        # as the UNSTAMPED class: a gate needs something to read.
        print("leg_path_pin_audit: UNREADABLE-RECORD note: cannot read %s (%s); "
              "nothing can be classified, reporting only" % (record_path, exc))
        return 0
    stamp = rec.get("index_stamp")
    if not isinstance(stamp, dict) or not stamp.get("git_blob_id"):
        print("leg_path_pin_audit: UNSTAMPED note: record %s carries no index_stamp "
              "(no declared git_blob_id) - its observations cannot be classified "
              "against this index; a legacy record is REPORTED, not gated on"
              % record_path)
        return 0
    try:
        measured = index_stamp(index_path)
    except OSError as exc:
        print("leg_path_pin_audit: UNREADABLE-INDEX note: cannot measure %s (%s)"
              % (index_path, exc))
        return 0
    scanned = measured["git_blob_id"]
    declared = str(stamp["git_blob_id"])
    want = record_observations(rec)
    have = fresh_observations(pinned_legs, repo_root)
    legs = sorted(set(want) | set(have))

    diffs = []
    agrees = 0
    for leg in legs:
        w = want.get(leg, set())
        h = have.get(leg, set())
        for member in sorted(w | h, key=repr):
            if member in w and member in h:
                agrees += 1
                continue
            diffs.append((leg, member, member in w))
    if declared != scanned:
        # Cross-blob replay: the record was never a claim about THIS index.
        for leg, (issue_id, ac, pth, status, via), in_record in diffs:
            print("leg_path_pin_audit: EXPECTED leg %s issue=%s ac=%s path=%s "
                  "record=%s fresh=%s - stamp mismatch, classified EXPECTED"
                  % (leg, issue_id, ac, pth,
                     "(%s,%s)" % (status, via) if in_record else "absent",
                     "(%s,%s)" % (status, via) if not in_record else "absent"))
        print("leg_path_pin_audit: AGAINST-RECORD cross-blob: record %s is stamped for "
              "blob %s but the scanned index %s hashes to %s - %d observation(s) "
              "classified EXPECTED (stamp mismatch), %d in agreement; the record was "
              "never a claim about this index, so a mismatch here is EXPECTED, not drift"
              % (record_path, declared[:12], index_path, scanned[:12], len(diffs), agrees))
        return 0
    if not diffs:
        for leg in legs:
            for (issue_id, ac, pth, status, via) in sorted(have.get(leg, set()), key=repr):
                print("leg_path_pin_audit: EXPECTED leg %s issue=%s ac=%s path=%s status=%s "
                      "via=%s (record agrees on the stamped blob)"
                      % (leg, issue_id, ac, pth, status, via))
        print("leg_path_pin_audit: AGAINST-RECORD same-blob: record %s is stamped for blob "
              "%s == the scanned index blob; %d observation(s) EXPECTED, 0 disagreement(s)"
              % (record_path, scanned[:12], agrees))
        return 0
    for leg, (issue_id, ac, pth, status, via), in_record in diffs:
        print("leg_path_pin_audit: DRIFT leg %s issue=%s ac=%s path=%s record=%s fresh=%s "
              "- the record's stamp names the scanned blob, so this is real drift"
              % (leg, issue_id, ac, pth,
                 "(%s,%s)" % (status, via) if in_record else "absent",
                 "absent" if in_record else "(%s,%s)" % (status, via)))
    print("leg_path_pin_audit: AGAINST-RECORD GATE: record %s is stamped for blob %s which IS "
          "the scanned index blob, yet %d observation(s) disagree (%d EXPECTED) - same-blob "
          "disagreement is real drift, not a stale snapshot"
          % (record_path, scanned[:12], len(diffs), agrees))
    return 1


if __name__ == "__main__":
    sys.exit(main())
