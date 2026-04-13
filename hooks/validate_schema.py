#!/usr/bin/env python3
"""
Validate a JSON file against the research-metadata schema.

Usage:
    python3 hooks/validate_schema.py <path-to-json-file>

Exit codes:
    0  — valid, prints "VALID"
    1  — invalid or error, prints the validation error message
"""

import json
import sys
import os

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(1)


SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "schemas",
    "research-metadata.schema.json",
)


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-json-file>")
        sys.exit(1)

    json_path = sys.argv[1]

    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: file not found: {json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON in {json_path}: {e}")
        sys.exit(1)

    try:
        with open(SCHEMA_PATH, "r") as f:
            schema = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: schema not found at {SCHEMA_PATH}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON in schema: {e}")
        sys.exit(1)

    try:
        jsonschema.validate(instance=data, schema=schema)
        print("VALID")
        sys.exit(0)
    except jsonschema.ValidationError as e:
        print(f"INVALID: {e.message}")
        sys.exit(1)
    except jsonschema.SchemaError as e:
        print(f"ERROR: schema is malformed: {e.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
