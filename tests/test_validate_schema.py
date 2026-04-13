"""
Unit tests for hooks/validate_schema.py

6 code paths:
1. Valid web_search document → exit 0, prints "VALID"
2. Valid document document → exit 0, prints "VALID"
3. Missing required field → exit 1, prints validation error
4. Wrong source_type value → exit 1, prints validation error
5. File not found → exit 1, prints error
6. Invalid JSON file → exit 1, prints error
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

VALIDATOR = Path(__file__).parent.parent / "hooks" / "validate_schema.py"


def run_validator(data: dict) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        tmp_path = f.name
    return subprocess.run(
        [sys.executable, str(VALIDATOR), tmp_path],
        capture_output=True,
        text=True,
    )


VALID_WEB = {
    "source_type": "web_search",
    "query": "Claude Code Agent tool",
    "retrieved_at": "2026-04-13T19:00:00Z",
    "results": [
        {
            "title": "Claude Docs",
            "content": "Claude Code is an agentic coding tool.",
            "source_attribution": {
                "url": "https://example.com",
                "retrieved_at": "2026-04-13T19:00:00Z",
            },
        }
    ],
}

VALID_DOC = {
    "source_type": "document",
    "query": "agentic orchestration",
    "retrieved_at": "2026-04-13T19:00:00Z",
    "results": [
        {
            "title": "domain-1 notes",
            "content": "The Agent tool is synchronous from coordinator perspective.",
            "source_attribution": {
                "url": "/Users/user/docs/notes.md",
                "retrieved_at": "2026-04-13T19:00:00Z",
                "relevance_note": "Matched keyword: agent",
            },
        }
    ],
}


def test_valid_web_search():
    result = run_validator(VALID_WEB)
    assert result.returncode == 0, result.stdout
    assert "VALID" in result.stdout


def test_valid_document():
    result = run_validator(VALID_DOC)
    assert result.returncode == 0, result.stdout
    assert "VALID" in result.stdout


def test_missing_required_field():
    data = dict(VALID_WEB)
    del data["query"]
    result = run_validator(data)
    assert result.returncode == 1
    assert "INVALID" in result.stdout


def test_wrong_source_type():
    data = dict(VALID_WEB)
    data["source_type"] = "twitter"
    result = run_validator(data)
    assert result.returncode == 1
    assert "INVALID" in result.stdout


def test_file_not_found():
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "/tmp/does-not-exist-xyz.json"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "not found" in result.stdout


def test_invalid_json_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("{ this is not json }")
        tmp_path = f.name
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), tmp_path],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "invalid JSON" in result.stdout
