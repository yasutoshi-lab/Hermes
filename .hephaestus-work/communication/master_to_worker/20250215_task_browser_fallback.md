# Task: Stabilize Browser Client Dependencies

**Task ID**: task_browser_fallback
**Priority**: high
**Assigned to**: worker-1
**Dependencies**: None (coordinate with worker-2 once LLM wiring lands)

## Objective
Resolve the installation blocker called out in `INTEGRATION_TEST_REPORT.md` and deliver a working browser research path that does not depend on a non-existent PyPI package, while still keeping the door open for the official `browser-use` integration later.

## Context
- `pip install -e .` currently fails because both `requirements.txt` and `pyproject.toml` hard-require `browser-use`, which is not published on PyPI.
- `hermes_cli/tools/browser_use_client.py` and `agents/nodes/web_researcher.py` are placeholders that always return empty result sets, so the workflow produces no real research data.
- We need a pragmatic fallback (e.g., DuckDuckGo or Brave Search API via `duckduckgo-search`) plus optional dependency handling so local installs succeed immediately.

## Requirements
- Remove the hard dependency on `browser-use` from the default `dependencies` list (pyproject + requirements). Expose it as an optional extra (e.g., `[project.optional-dependencies.browser]`) with a comment explaining that it requires manual installation from source once available.
- Introduce a readily available fallback search dependency (suggested: `duckduckgo-search>=6.2.0`) and wire it into `BrowserUseClient`.
- Update `BrowserUseClient` to:
  - Attempt to import and use `browser_use` when installed, otherwise automatically fall back to the DuckDuckGo client.
  - Return structured `BrowserSearchResult` objects populated with URL, title, snippet, and timestamp.
  - Offer at least basic content extraction by fetching each result URL via `httpx` (respect robots.txt politely) and trimming the body to a few paragraphs so downstream nodes have text to process.
- Update `web_researcher` to surface the new data (log how many sources were gathered per query, skip gracefully on HTTP failures, keep existing error aggregation).
- Refresh documentation to explain the new dependency story:
  - `README.md` installation section
  - `DEVELOPMENT.md` environment setup
  - `INTEGRATION_TEST_REPORT.md` issue log (mark the missing dependency issue as mitigated and describe the fallback behaviour)
- Add/extend smoke coverage so `python3 tests/test_persistence.py && python3 tests/test_config.py && python3 tests/test_logging.py` is joined by a new CLI/web research sanity script (place under `tests/`), proving that `BrowserUseClient.search()` returns at least one result for a sample query when the fallback path is active.

## Expected Output
- Updated dependency files + browser client implementation + doc/test changes committed in the workspace.
- Test script output or notes in the worker report summarizing the executed commands and their results.

## Resources
- Dependency specs: `pyproject.toml`, `requirements.txt`
- Browser client: `hermes_cli/tools/browser_use_client.py`
- Workflow hook: `hermes_cli/agents/nodes/web_researcher.py`
- Docs/tests: `README.md`, `DEVELOPMENT.md`, `INTEGRATION_TEST_REPORT.md`, `tests/`
