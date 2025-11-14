# Task: Validation Loop & Research Refresh

**Task ID**: task_validation_loop_upgrade
**Priority**: high
**Assigned to**: worker-2
**Dependencies**: task_logging_upgrade (you will be touching HermesState/run_service while worker-1 adds log hooks—coordinate on any merge points).

## Objective
Align the LangGraph validation loop with 詳細設計書 §9.2 by re-entering the research pipeline when quality checks fail, and add measurable heuristics so `validation_controller` decides whether another loop is needed.

## Context
- The current graph only routes `validator → draft_aggregator` and never revisits `web_researcher`/`container_processor`, so additional loops cannot pull new evidence (`hermes_cli/agents/graph.py:52-95`).
- `validation_controller` stops immediately after `min_validation` with a TODO for quality checks (`hermes_cli/agents/nodes/validation_controller.py:25-50`).
- README still claims validation loops are placeholders even though the validator now calls Ollama (`README.md:170`).

## Requirements
1. **Graph routing**
   - Update `create_hermes_workflow()` so the “continue” path becomes `validator → web_researcher → container_processor → draft_aggregator`. Keep the `final_reporter` path unchanged when `validation_complete` is True.
   - Ensure repeated passes reuse existing queries rather than regenerating them; it’s fine to overwrite `state.query_results[...]` with the latest crawl.
2. **Quality gating**
   - Enhance `validation_controller` so, after `min_validation` is satisfied and before `max_validation`, it inspects:
     - Whether each query gathered at least `min_sources` results.
     - Whether `state.draft_report` meets simple completeness heuristics (e.g., minimum length or the presence of all sections).
     - Whether any errors were captured in `state.error_log`.
   - If any heuristic fails, set `validation_complete = False` and attach a short reason to the log (use the logging hook worker-1 is adding; include a TODO to call it once their work lands).
3. **State resets**
   - Add helper(s) so each new loop starts with a clean slate where appropriate (e.g., clear `processed_notes` before the next `container_processor` run while preserving `queries`). Document the behavior in `HermesState` docstrings.
4. **Tests**
   - Create a new pytest module (e.g., `tests/test_validation_loop.py`) that monkeypatches the node functions to counters and proves the graph calls `web_researcher` twice when the controller keeps `validation_complete=False`.
   - Add unit tests for the heuristic logic (directly instantiate `HermesState` with sparse sources and assert the controller requests another loop).
5. **Docs**
   - Update the README “Current Limitations” section to reflect the new validation behavior (remove the outdated sentence at `README.md:170` and describe the refreshed loop + heuristics).
   - If you add new helper options or heuristics that users should know about, mirror them in `USAGE_GUIDE.md`.
6. **Regression safety**
   - Re-run existing workflow/unit tests (`python -m pytest tests/test_nodes_ollama.py tests/test_run_service.py tests/test_validation_loop.py`). Document the command + results in your worker report.

## Expected Output
- Updated `hermes_cli/agents/graph.py`, `validation_controller.py`, and any supporting state helpers.
- New/updated tests under `tests/` verifying the routing + heuristics.
- Documentation updates committed at the repo root.

## Resources
- Workflow definition: `hermes_cli/agents/graph.py`
- Nodes: `hermes_cli/agents/nodes/validation_controller.py`, `validator.py`, `web_researcher.py`, `container_processor.py`, `draft_aggregator.py`
- State helpers: `hermes_cli/agents/state.py`
- Docs: `README.md`, `USAGE_GUIDE.md`
- Tests entry points: `test_workflow.py`, `tests/test_nodes_ollama.py`
