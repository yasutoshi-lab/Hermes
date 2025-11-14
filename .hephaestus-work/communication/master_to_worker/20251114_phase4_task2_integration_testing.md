# Task: Integration Testing & Validation Report

**Task ID**: phase4_task2_integration_testing
**Priority**: high
**Assigned to**: worker-3
**Dependencies**: phase3_task1_remaining_services, phase3_task2_cli_commands (complete)

## Objective
Execute the integration test plan from `20251114_phase4_integration_test.md`, validate the end-to-end Hermes CLI experience on this repo, and capture results plus follow-up issues in a formal report.

## Context
All feature work is merged, but we have not yet proven the stack works together. We need deterministic instructions/scripts so anyone can reproduce the validation (install, init, CLI flows, workflow sanity checks) and a Markdown report that records pass/fail status and any bugs.

## Requirements
- **Environment preparation**
  - Work inside `/home/ubuntu/python_project/Hermes/`.
  - Use editable install (`pip install -e .`) or uv equivalent; document exact command.
- **Test execution** (aligns with phase 4 spec)
  1. Dependency install + import sanity (`python -c "import hermes_cli; print(hermes_cli.__version__)"`).
  2. CLI help coverage (`python -m hermes_cli.main ... --help` and `--version`).
  3. `hermes init` run after wiping `~/.hermes` (safe rm -rf) and verification of directories + config.
  4. ConfigService override demo via small script (see spec sample) showing before/after values.
  5. Persistence smoke test (TaskService + HistoryService) proving CRUD paths—use temporary IDs/files under `~/.hermes` and clean up.
  6. Agent workflow instantiation using `test_workflow.py` (already present) or an improved script; note placeholders for browser/container/LLM.
  7. CLI task command exercise: create/list/delete a sample task.
  8. Any other sanity checks you deem necessary (e.g., `hermes log --lines 5` after writing sample log entries via LogRepository).
- Capture commands/scripts under `tests/` (e.g., `tests/test_config.py`, `tests/test_persistence.py`) where it improves repeatability. Lightweight scripts are fine; prefer Python over ad-hoc shell when logic is non-trivial.
- Document all results in `INTEGRATION_TEST_REPORT.md` using the table/template from the phase 4 spec. Include PASS/FAIL plus notes, issues encountered, and recommended fixes/workarounds.
- If you uncover bugs that block completion, document them with clear reproduction steps in the report and leave TODO comments or GitHub-style checklists for follow-up.

## Expected Output
- Any helper test scripts placed in `/home/ubuntu/python_project/Hermes/tests/` (create the directory if missing).
- Clean console logs or captured snippets that prove each step ran (may embed in the report or referenced files).
- `INTEGRATION_TEST_REPORT.md` at repo root summarizing execution outcomes, issues, and readiness verdict.
- Status update in `communication/worker_to_master/` describing results and linking to failing steps if any.

## Resources
- File paths: `/home/ubuntu/python_project/Hermes/test_workflow.py`, `hermes_cli/` modules, `~/.hermes/`
- Documentation: `/home/ubuntu/python_project/Hermes/詳細設計書.md`, `20251114_phase4_integration_test.md`
