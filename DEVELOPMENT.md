# Hermes Development Guide

This guide explains how to set up a development environment, run quality gates,
extend the CLI/services/workflow, and verify the LangGraph stack locally.

## 1. Repository Setup

```bash
git clone https://example.com/Hermes.git
cd Hermes

# Create + activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
```

### Install Dependencies

```bash
# Editable install with pip
pip install -e .

# or with uv (faster resolver + lock-free workflow)
uv pip install -e .

# Optional browser automation extra (requires browser-use installed from source)
# pip install -e .[browser]
```

### Install Dev Tooling

```bash
pip install -e .[dev]
# or
uv pip install -e '.[dev]'
```

The `dev` extra pulls in `pytest`, `black`, `ruff`, and `mypy` as declared in
`pyproject.toml`.

## 2. Project Layout

```
Hermes/
├── hermes_cli/
│   ├── commands/        # Typer commands
│   ├── services/        # Business logic
│   ├── agents/          # LangGraph workflow & nodes
│   ├── tools/           # External clients (Ollama, browser, container)
│   └── persistence/     # File-based repositories (~/.hermes)
├── README.md
├── ARCHITECTURE.md
├── DEVELOPMENT.md
├── USAGE_GUIDE.md
├── pyproject.toml
├── requirements.txt
└── test_workflow.py     # LangGraph smoke test
```

The layered responsibilities are detailed in [ARCHITECTURE.md](ARCHITECTURE.md).

## 3. Quality Checks

Run these commands from the repo root after activating your environment.

| Check | Command | Notes |
| --- | --- | --- |
| Formatting | `black hermes_cli` | Configured for 100-char lines via `pyproject.toml`. |
| Linting | `ruff check hermes_cli` | Use `ruff check --fix` to auto-fix violations. |
| Type checking | `mypy hermes_cli` | Uses `python_version = 3.10` config. |
| Unit/Integration tests | `pytest` | Add tests under `tests/` when available. |
| LangGraph smoke test | `python test_workflow.py` | Confirms `HermesState` and `create_hermes_workflow()` import/compile. |
| Browser fallback smoke | `python tests/test_browser_client.py` | Ensures `BrowserUseClient.search()` returns data via DuckDuckGo. |

If you use `uv`, prefix each command with `uv run ...` to avoid manually
activating the environment.

## 4. Running Hermes Locally

1. Install the package via `pip install -e .` (or `uv pip install -e .`).
2. Ensure `hermes` is on `$PATH` (reopen the shell if necessary).
3. Start the Ollama daemon before running LangGraph nodes:
   ```bash
   ollama serve
   ```
4. Run `hermes init`, then `hermes run --prompt "test prompt"`.
5. Inspect `~/.hermes/` to verify reports/logs are written.

Use `python test_workflow.py` whenever you touch the LangGraph code to ensure
the graph still compiles without executing the full CLI.

## 5. Extending the Codebase

### CLI Commands (`hermes_cli/commands/`)

1. Create `<feature>_cmd.py` with a Typer command function.
2. Export the function in `hermes_cli/commands/__init__.py`.
3. Register it in `hermes_cli/main.py` via `app.command("<name>")(feature_command)`.
4. Keep command modules thin—delegate heavy lifting to services.

### Services (`hermes_cli/services/`)

- Accept `FilePaths` or other dependencies via the constructor for testability.
- Log using `logging.getLogger(__name__)` and surface user-facing errors through
  the CLI layer.
- When adding a new service, expose it in `services/__init__.py`.

### LangGraph Workflow (`hermes_cli/agents/`)

- Update or add nodes under `agents/nodes/`, exporting them in
  `agents/nodes/__init__.py`.
- Wire new nodes inside `graph.py` by adding edges or conditions.
- Extend `HermesState` with new fields when required (remember to update
  serialization or persistence logic if the data leaves the workflow).

### Tool Clients (`hermes_cli/tools/`)

- Follow the context-manager pattern used by existing clients so nodes can use
  `with Client() as client`.
- Implement retries, timeouts, and helpful exceptions so services can provide
  actionable feedback (visible in `hermes log`/`hermes debug`).

### Persistence (`hermes_cli/persistence/`)

- Create repositories that operate on `Path` objects from `FilePaths`.
- Serialize dataclasses or Pydantic models consistently (ISO timestamps, UTF-8
  encoding).
- Keep runtime data under `~/.hermes/` to avoid polluting the repo.

## 6. Workflow & Validation Tips

- Run `hermes run --prompt ... --language en --max-validation 4` to exercise the
  validation loop logic while you work on nodes.
- Inspect `~/.hermes/log/hermes-YYYYMMDD.log` to verify services emit the
  expected events; tests should assert on repository outputs instead of parsing
  console output.
- `BrowserUseClient` now uses DuckDuckGo + httpx by default and will
  automatically switch to `browser-use` once that optional dependency is
  installed. Keep the method signatures stable so downstream nodes keep working.
- `ContainerUseClient` is still a placeholder—replace it carefully once the
  integration is ready.
- Unit tests stub the Ollama client factory, but manual CLI tests require
  `ollama serve` to be running.

## 7. Troubleshooting the Dev Environment

- **`hermes` command not found** – Ensure the virtual environment is activated or
  reinstall with `pip install -e .`.
- **LangGraph import errors** – Reinstall dependencies (`pip install -e .[dev]`)
  and run `python test_workflow.py` to isolate graph issues.
- **Missing `~/.hermes/` directories** – Run `hermes init` or call
  `FilePaths.ensure_directories()` in tests.
- **Ollama HTTP errors** – Verify `ollama serve` is running and that
  `~/.hermes/config.yaml` points to the right `api_base`.

## 8. Release Checklist

1. Update version strings in `hermes_cli/__init__.py` and `pyproject.toml`.
2. Run all quality gates (`black`, `ruff`, `mypy`, `pytest`, `python test_workflow.py`).
3. Regenerate or review `README.md`/docs if features changed.
4. Build artifacts (`python -m build`) if publishing.
5. Tag the release (`git tag vX.Y.Z`) and push tags.

For deeper architectural context, see [ARCHITECTURE.md](ARCHITECTURE.md). For
user-facing walkthroughs, refer to [USAGE_GUIDE.md](USAGE_GUIDE.md).
