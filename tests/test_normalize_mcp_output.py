"""
Unit tests for hooks/normalize-mcp-output.py

5 code paths:
1. Happy path: valid brave-search results normalize correctly
2. HTML stripped from description
3. Missing description field → empty snippet (no KeyError)
4. Empty results list → empty normalized results
5. Invalid JSON on stdin → exit 1
"""

import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).parent.parent / "hooks" / "normalize-mcp-output.py"


def run_hook(stdin_data: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(stdin_data),
        capture_output=True,
        text=True,
    )


def test_happy_path():
    data = {
        "tool_name": "mcp__brave-search__brave_web_search",
        "tool_input": {"query": "Claude Code Agent tool"},
        "tool_response": {
            "results": [
                {
                    "title": "Claude Code Docs",
                    "url": "https://example.com/claude",
                    "description": "Claude Code is an AI coding tool.",
                }
            ]
        },
    }
    result = run_hook(data)
    assert result.returncode == 0, result.stderr
    normalized = json.loads(result.stdout)
    assert normalized["source_type"] == "web_search"
    assert "retrieved_at" in normalized
    assert len(normalized["results"]) == 1
    assert normalized["results"][0]["title"] == "Claude Code Docs"
    assert normalized["results"][0]["url"] == "https://example.com/claude"
    assert normalized["results"][0]["snippet"] == "Claude Code is an AI coding tool."


def test_html_stripped():
    data = {
        "tool_response": {
            "results": [
                {
                    "title": "Test",
                    "url": "https://example.com",
                    "description": "<b>Bold</b> and <a href='x'>link</a> text",
                }
            ]
        }
    }
    result = run_hook(data)
    assert result.returncode == 0
    normalized = json.loads(result.stdout)
    assert normalized["results"][0]["snippet"] == "Bold and link text"


def test_missing_description():
    data = {
        "tool_response": {
            "results": [
                {
                    "title": "No Description",
                    "url": "https://example.com",
                    # description key absent
                }
            ]
        }
    }
    result = run_hook(data)
    assert result.returncode == 0
    normalized = json.loads(result.stdout)
    assert normalized["results"][0]["snippet"] == ""


def test_empty_results():
    data = {"tool_response": {"results": []}}
    result = run_hook(data)
    assert result.returncode == 0
    normalized = json.loads(result.stdout)
    assert normalized["results"] == []


def test_invalid_json_stdin():
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input="this is not json",
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "failed to parse stdin" in proc.stderr
