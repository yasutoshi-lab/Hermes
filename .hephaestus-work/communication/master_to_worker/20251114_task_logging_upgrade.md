# Task: Structured Logging & CLI Filtering

**Task ID**: task_logging_upgrade
**Priority**: high
**Assigned to**: worker-1
**Dependencies**: All Phase 3 services are completed; coordinate with worker-2 if their LangGraph changes touch shared state.

## Objective
Bring the logging pipeline up to the 詳細設計書 specs (§7.5, §11) by emitting structured task-scoped events (regular + debug logs) and letting `hermes log` actually filter by task ID.

## Context
- `LogRepository.write_log()` currently writes only to the regular log file and nothing ever reaches `~/.hermes/debug_log` (`hermes_cli/persistence/log_repository.py:53-120`).
- Workflow nodes only use the standard `logging` module, so the structured log files never record browser/container/LLM phases (`hermes_cli/agents/nodes/*.py`).
- `hermes log` ignores its `--task-id` option and simply tails the entire file (`hermes_cli/commands/log_cmd.py:16-55`).
- RunService already injects `task_id` into start/stop log lines, so you can reuse that pattern to wire a richer callback (`hermes_cli/services/run_service.py:60-190`).

## Requirements
- Extend `LogRepository.write_log()` with a `debug: bool = False` flag so we can write to both log streams; add a convenience helper (or second method) if that keeps the call sites clean.
- Teach `LogService.tail/stream` to accept an optional `task_id` filter that returns only matching lines (scan enough of the file to satisfy `lines`).
- Add a lightweight logging hook to `HermesState` (e.g., `log_event(level, component, message, **kwargs)`) and have `RunService` pass a partial that injects `task_id` + writes to debug when `level == "DEBUG"`.
- Update the following nodes to call the hook so structured logs capture each phase:
  - `query_generator`, `web_researcher`, `container_processor`, `draft_aggregator`, `validator`, `final_reporter`, `validation_controller`.
  - Use the component labels from 詳細設計書 examples (RUN/BROWSER/CONTAINER/LLM/VALIDATION/etc.).
- Improve `hermes log` behaviour:
  - If `--task-id` is provided, tail/stream only matching lines (still allow `--follow`).
  - If `--task-id` is omitted, default to `TaskService.get_latest_running_task()`; if none, fall back to the most recent history entry or print a friendly note.
  - Add a `--debug/--no-debug` flag to opt into the debug log file.
- Update README/USAGE docs so the Logging section explains the new filtering behaviour and how debug logs work (`README.md`, `USAGE_GUIDE.md`).
- Tests:
  - Add pytest coverage for the new filtering logic (e.g., write temp log files via `LogRepository` and assert `LogService.tail(..., task_id="2025-0001")` only returns expected lines).
  - Extend `tests/test_run_service.py` or create a new test to assert the state’s `log_event` callback is invoked when the workflow runs (can inject a stub factory to capture calls).

## Expected Output
- Updated logging infrastructure + CLI command + documentation in the repo.
- New/updated tests under `tests/` and green `python -m pytest tests/test_logging.py tests/test_run_service.py` (expand list if you add new files).
- Worker report summarizing scenarios executed (at minimum the pytest command above).

## Resources
- Logging persistence: `hermes_cli/persistence/log_repository.py`
- Services: `hermes_cli/services/log_service.py`, `hermes_cli/services/run_service.py`
- State/nodes: `hermes_cli/agents/state.py`, `hermes_cli/agents/nodes/*.py`
- CLI: `hermes_cli/commands/log_cmd.py`
- Docs: `README.md`, `USAGE_GUIDE.md`
- Tests baseline: `tests/test_logging.py`, `tests/test_run_service.py`
