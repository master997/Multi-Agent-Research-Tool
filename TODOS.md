# TODOS

## [ ] Parallel fetch calls in web-search subagent

**What:** Web-search subagent currently fetches top 2-3 URLs serially. Claude Code supports parallel tool calls — issuing all fetch calls in a single message would run them simultaneously.

**Why:** Latency. Serial fetch on 3 URLs at ~2s each = 6s. Parallel = ~2s. Same data, 3x faster.

**Pros:** Demonstrates that fan-out applies at the tool level, not just the agent level. Same pattern as the coordinator's parallel Agent calls.
**Cons:** More complex subagent instructions. Not the primary learning goal.
**Context:** After the system runs end-to-end, change `subagents/web-search-subagent.md` step 3 to say: "Issue all fetch calls in a single message — do not wait for one to complete before issuing the next."
**Depends on:** System running successfully first.

---

## [ ] Hook behavior integration test

**What:** Write a small integration test that verifies the PostToolUse hook stdout actually lands in the agent's context as `additionalContext` in a real Claude Code session.

**Why:** Open Question 1 was resolved by documentation search, but the exact behavior (does `additionalContext` appear before or after the raw tool result? Is it always injected?) is only confirmed by running it. A small test closes this permanently.

**Pros:** Turns "confirmed by docs" into "confirmed by observation." Good debugging skill. Will catch if hook behavior changes in a future Claude Code version.
**Cons:** Requires a real Claude Code session to run, not just pytest. Slightly more complex setup.
**Context:** Write `coordinator-hook-test.md` — a minimal prompt that calls brave-search with a known query, instructs the subagent to report exactly what it sees in the tool result vs. additionalContext, and outputs both verbatim. Compare to verify normalization is additive.
**Depends on:** Hook implementation (normalize-mcp-output.py) done and registered in settings.json.
