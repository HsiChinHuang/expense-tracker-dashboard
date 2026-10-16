#!/usr/bin/env python3
"""Pinned validator for the t81 incident-response answer contract.

The AI on-call pass reads an evidence bundle and answers with one JSON
document. A claim nobody can reject is not a gate, so this file is the
single checkable authority over that answer: it validates the answer
against incident-response/response.schema.json and exits 0 only when the
answer is fully schema-valid.

Modes (the CLI surface is pinned by card t81, ac3):

  --check-schema  audit the schema document itself against the keyword
                  subset implemented here; a schema carrying a keyword
                  this validator does not implement is REFUSED loudly,
                  so schema and validator cannot drift apart unnoticed.
  --answer PATH   validate PATH against the schema; reject anything the
                  schema rejects and say which rule rejected it.

Exit codes: 0 accepted, 1 rejected, 2 bad usage or unreadable input.

Dependencies: the stdlib trio json/re/sys and nothing else. No third-party
schema library, no network client, no install step; the same python3 the
merged verification gates already use is enough, offline.
"""

import json
import re
import sys

PINNED_DRAFT = "https://json-schema.org/draft/2020-12/schema"

# The keyword subset this validator implements. A schema keyword outside
# this set is a REFUSAL, never a silent skip: a gate that quietly ignores
# a rule is worse than no gate at all. The last three entries are JSON
# Schema annotation keywords: they carry no validation semantics, so this
# validator declares them and reads them as prose. Everything else must be
# a rule this file actually enforces.
ALLOWED_SCHEMA_KEYWORDS = frozenset(
    [
        "$schema",
        "$id",
        "title",
        "description",
        "type",
        "required",
        "properties",
        "items",
        "additionalProperties",
        "enum",
        "pattern",
        "minLength",
        "maxLength",
        "minimum",
        "maximum",
        "minItems",
        "maxItems",
    ]
)


def is_number(value):
    """True only for real numbers; in JSON a bool is not a number."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def type_matches(value, expected):
    """Report whether a JSON value carries the schema type name."""
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    if expected == "number":
        return is_number(value)
    if expected == "integer":
        return is_number(value) and float(value).is_integer()
    return False


def validate_value(value, schema, path):
    """Check one JSON value against one schema node; return problem lines."""
    problems = []
    expected = schema.get("type")
    if expected is not None and not type_matches(value, expected):
        return ["%s: expected type %s" % (path, expected)]
    if "enum" in schema and value not in schema["enum"]:
        problems.append("%s: value not in the pinned enum" % path)
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            problems.append(
                "%s: string shorter than minLength %d" % (path, schema["minLength"])
            )
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            problems.append(
                "%s: string longer than maxLength %d" % (path, schema["maxLength"])
            )
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            problems.append("%s: value does not match the pinned pattern" % path)
    elif is_number(value):
        if "minimum" in schema and value < schema["minimum"]:
            problems.append("%s: below the pinned minimum" % path)
        if "maximum" in schema and value > schema["maximum"]:
            problems.append("%s: above the pinned maximum" % path)
    elif isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            problems.append("%s: fewer items than minItems %d" % (path, schema["minItems"]))
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            problems.append("%s: more items than maxItems %d" % (path, schema["maxItems"]))
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                problems.extend(validate_value(item, item_schema, "%s[%d]" % (path, index)))
    elif isinstance(value, dict):
        for name in schema.get("required") or []:
            if name not in value:
                problems.append("%s: required field %s is missing" % (path, name))
        properties = schema.get("properties") or {}
        extra = schema.get("additionalProperties", True)
        for key, child in value.items():
            if key in properties:
                problems.extend(validate_value(child, properties[key], "%s.%s" % (path, key)))
            elif extra is False:
                problems.append("%s: unknown key %s is rejected" % (path, key))
            elif isinstance(extra, dict):
                problems.extend(validate_value(child, extra, "%s.%s" % (path, key)))
    return problems


def check_schema_node(schema, path, problems):
    """Audit one schema node: implemented keywords, sane shapes, recursion."""
    if isinstance(schema, bool):
        return
    if not isinstance(schema, dict):
        problems.append("%s: a schema node must be an object or a boolean" % path)
        return
    for keyword in sorted(schema):
        if keyword not in ALLOWED_SCHEMA_KEYWORDS:
            problems.append(
                "%s: keyword %s is outside the implemented subset; refusing to"
                " pretend a rule this validator does not implement was checked" % (path, keyword)
            )
    if "type" not in schema:
        problems.append("%s: no type; this validator pins typed nodes only" % path)
    if "enum" in schema:
        allowed = schema["enum"]
        if not isinstance(allowed, list) or not allowed:
            problems.append("%s: enum must be a non-empty list" % path)
    if "required" in schema:
        names = schema["required"]
        if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
            problems.append("%s: required must be a list of names" % path)
        declared = schema.get("properties") or {}
        for name in names if isinstance(names, list) else []:
            if isinstance(name, str) and name not in declared:
                problems.append("%s: required %s has no property declaration" % (path, name))
    if "pattern" in schema:
        try:
            re.compile(schema["pattern"])
        except re.error as exc:
            problems.append("%s: pattern does not compile (%s)" % (path, exc))
    extra = schema.get("additionalProperties", True)
    if not (extra is False or extra is True or isinstance(extra, dict)):
        problems.append("%s: additionalProperties must be false, true, or a schema" % path)
    properties = schema.get("properties")
    if isinstance(properties, dict):
        for name in sorted(properties):
            check_schema_node(properties[name], "%s.properties.%s" % (path, name), problems)
    if "items" in schema:
        check_schema_node(schema["items"], "%s.items" % path, problems)
    if isinstance(extra, dict):
        check_schema_node(extra, "%s.additionalProperties" % path, problems)


def check_schema(schema):
    """Audit the whole schema document; return the list of problems."""
    problems = []
    if schema.get("$schema") != PINNED_DRAFT:
        problems.append("root: $schema must pin the draft %s" % PINNED_DRAFT)
    check_schema_node(schema, "root", problems)
    return problems


def load_json(path, label):
    """Read one JSON document or fail loudly with a readable reason."""
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle), None
    except OSError as exc:
        return None, "%s file %s could not be read: %s" % (label, path, exc)
    except ValueError as exc:
        return None, "%s file %s is not valid JSON: %s" % (label, path, exc)


def usage(stream):
    """Print the pinned CLI surface; a typo must never validate nothing."""
    stream.write(
        "usage: validate_response.py --schema PATH (--answer PATH | --check-schema)\n"
    )
    stream.write(
        "       --schema PATH   the response schema (required in both modes)\n"
    )
    stream.write(
        "       --answer PATH   the incident answer document to validate\n"
    )
    stream.write(
        "       --check-schema  audit the schema against the keyword subset\n"
    )


def main(argv):
    """Entry point: parse the pinned CLI, run one mode, exit 0/1/2."""
    schema_path = None
    answer_path = None
    check_only = False
    index = 0
    while index < len(argv):
        token = argv[index]
        if token == "--schema":
            if index + 1 >= len(argv):
                sys.stderr.write("unknown or incomplete argument: --schema\n")
                usage(sys.stderr)
                return 2
            schema_path = argv[index + 1]
            index += 2
        elif token == "--answer":
            if index + 1 >= len(argv):
                sys.stderr.write("unknown or incomplete argument: --answer\n")
                usage(sys.stderr)
                return 2
            answer_path = argv[index + 1]
            index += 2
        elif token == "--check-schema":
            check_only = True
            index += 1
        else:
            sys.stderr.write("unknown argument: %s\n" % token)
            usage(sys.stderr)
            return 2
    if schema_path is None:
        sys.stderr.write("unknown mode: --schema PATH is required\n")
        usage(sys.stderr)
        return 2
    if not check_only and answer_path is None:
        sys.stderr.write("unknown mode: pass --answer PATH or --check-schema\n")
        usage(sys.stderr)
        return 2
    schema, failure = load_json(schema_path, "schema")
    if failure is not None:
        sys.stderr.write("REJECT %s\n" % failure)
        return 2
    problems = check_schema(schema)
    if problems:
        for line in problems:
            sys.stderr.write("REJECT schema %s\n" % line)
        return 1
    if check_only:
        print("ACCEPT schema %s passes the pinned keyword subset" % schema_path)
        return 0
    answer, failure = load_json(answer_path, "answer")
    if failure is not None:
        sys.stderr.write("REJECT %s\n" % failure)
        return 2
    problems = validate_value(answer, schema, "$")
    if problems:
        for line in problems:
            sys.stderr.write("REJECT answer %s\n" % line)
        return 1
    print("ACCEPT answer %s satisfies %s" % (answer_path, schema_path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
