# Multi-Agent Research Coordinator

A Claude Code multi-agent system that orchestrates parallel research subagents to produce structured markdown reports. Built as part of the Claude Architect Course — Domain 1: Agentic Orchestration.

## What it does

Given a research query, the coordinator:

1. Launches a **web search subagent** and a **document analysis subagent** in parallel
2. Validates both outputs against a shared JSON schema
3. Passes the combined results to a **synthesis subagent** that writes a report to `reports/`

## Project structure

```
project/
├── coordinator.md              # Main coordinator prompt — orchestrates the full flow
├── subagents/
│   ├── web-search-subagent.md  # Searches the web via Brave, fetches page content
│   ├── doc-analysis-subagent.md # Scans local course documents for relevant content
│   └── synthesis-subagent.md   # Merges results and writes the final report
├── schemas/
│   └── research-metadata.schema.json  # Shared JSON schema validated before synthesis
├── hooks/
│   └── validate_schema.py      # Schema validation script called after each subagent
├── reports/                    # Output directory for generated research reports
├── tests/                      # Test suite
├── TODOS.md                    # Tracked improvements and open questions
└── CLAUDE.md                   # Project-level Claude Code instructions
```

## How to run

Open `coordinator.md` as a Claude Code prompt, then send a research query:

```
What are the key patterns for multi-agent orchestration in LLM systems?
```

The coordinator handles the rest — parallel subagent calls, schema validation, and report synthesis.

## Key design patterns demonstrated

- **Parallel fan-out**: Both subagents are spawned in a single response turn, running simultaneously rather than serially
- **Schema-gated synthesis**: Subagent outputs are validated against `research-metadata.schema.json` before reaching the synthesis step — invalid output halts the pipeline
- **PostToolUse hooks**: A hook fires on every `brave_web_search` call to normalize raw MCP output into a consistent `additionalContext` block the subagent reads
- **Tool-level vs agent-level parallelism**: The coordinator uses agent-level parallelism; a tracked improvement (see `TODOS.md`) would add tool-level parallelism inside the web search subagent

## Architecture

```
User query
    │
    ▼
Coordinator
    ├──► Web Search Subagent  ──► schema validation ──┐
    │         (brave-search + fetch)                   ├──► Synthesis Subagent ──► reports/
    └──► Doc Analysis Subagent ──► schema validation ──┘
              (local file scan)
```

Both subagents output raw JSON conforming to `schemas/research-metadata.schema.json`. The coordinator writes each result to `/tmp/`, validates, then passes a combined array to synthesis.
