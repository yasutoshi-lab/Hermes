# Repository Guidelines

## Project Structure & Module Organization
Source lives under `hermes_cli/` with clear layers: `commands/` hosts the Typer entry points, `services/` contains business rules, `agents/` wires the LangGraph workflow, `tools/` provides client adapters, and `persistence/` manages `~/.hermes/` I/O. Tests sit in `tests/` plus the standalone `test_workflow.py` LangGraph smoke test. Docs (`README.md`, `DEVELOPMENT.md`, `ARCHITECTURE.md`, `USAGE_GUIDE.md`) stay at the repo root for quick onboarding.

## Build, Test, and Development Commands
Activate a Python 3.10+ virtualenv, then install locally with `pip install -e .` (or `uv pip install -e .`); include tooling via `pip install -e .[dev]`. Run `black hermes_cli` to format, `ruff check hermes_cli` for linting, and `mypy hermes_cli` for typing. Execute `pytest` for unit/integration suites, `python test_workflow.py` to ensure the graph compiles, and `python tests/test_browser_client.py` to verify the DuckDuckGo fallback. Launch the CLI with `hermes init` followed by `hermes run --prompt "example"`; package builds use `python -m build`.

## Coding Style & Naming Conventions
Use 4-space indentation, type hints everywhere, and prefer dataclasses for structured state. `black` enforces 100-character lines per `pyproject.toml`. Keep module and file names `snake_case`, Typer command functions in `<feature>_cmd.py`, and LangGraph nodes/classes in `PascalCase`. Run `ruff check --fix` when touching shared modules so imports, ordering, and docstrings stay consistent.

## Testing Guidelines
Add new tests beside the code they exercise: `tests/services/test_run_service.py`, `tests/agents/test_nodes.py`, etc., following the `test_<feature>.py` pattern. Each feature PR should cover the happy path and at least one failure branch. Re-run `pytest`, `python test_workflow.py`, and any browser/client smoke tests before opening a PR. When altering persistence logic, manually inspect `~/.hermes/history/` outputs to confirm serialization changes.

## Commit & Pull Request Guidelines
Recent history (`git log`) shows short, imperative commits ("add README.md", "finish draft"); follow that style and keep subjects under 72 chars. Reference GitHub issues in the body when applicable. PRs must describe the workflow impact, list verification commands (`pytest`, `python test_workflow.py`, etc.), and attach screenshots or log excerpts for CLI-facing changes. Mention validation loop or Ollama impacts explicitly so reviewers can reproduce the environment.

## Security & Configuration Tips
Never commit contents from `~/.hermes/`; treat it as user data. Store Ollama endpoints and tokens in local config files only, and ensure placeholder browser/container clients continue to warn instead of executing real commands unless guarded behind feature flags. When editing `FilePaths` or repository classes, validate directory permissions to avoid overwriting existing user artifacts.
