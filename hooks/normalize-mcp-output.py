#!/usr/bin/env python3
"""
PostToolUse hook: normalize brave-search output.

Fires after every mcp__brave-search__brave_web_search call.
Reads raw {tool_name, tool_input, tool_response} JSON from stdin.
Prints normalized JSON to stdout — Claude sees this as additionalContext.

The subagent is instructed to use this normalized data instead of the raw
tool result when building the schema-conforming response.
"""

import json
import sys
import datetime
import re


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def normalize(data: dict) -> dict:
    tool_response = data.get("tool_response", {})
    results = tool_response.get("results", [])
    retrieved_at = datetime.datetime.utcnow().isoformat() + "Z"

    normalized_results = []
    for r in results:
        if not isinstance(r, dict):
            continue
        normalized_results.append(
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": strip_html(r.get("description", "")),
            }
        )

    return {
        "source_type": "web_search",
        "retrieved_at": retrieved_at,
        "results": normalized_results,
    }


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        # Write error to stderr so it shows in hook logs without polluting stdout
        print(f"normalize-mcp-output: failed to parse stdin: {e}", file=sys.stderr)
        sys.exit(1)

    normalized = normalize(data)
    print(json.dumps(normalized))


if __name__ == "__main__":
    main()
