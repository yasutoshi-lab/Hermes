# Hermes Architecture

Hermes follows a layered design so that CLI commands, services, the LangGraph
workflow, tool integrations, and file-based persistence can evolve
independently while sharing the same data contracts.

```
┌─────────────────────────────────────┐
│         CLI Layer (Typer)           │  User Interface
├─────────────────────────────────────┤
│       Services Layer (Business)     │  Task orchestration
├─────────────────────────────────────┤
│    Agents Layer (LangGraph)         │  Research workflow
├─────────────────────────────────────┤
│     Tools Layer (Integrations)      │  External systems
├─────────────────────────────────────┤
│   Persistence Layer (Data Store)    │  ~/.hermes/* files
└─────────────────────────────────────┘
```

## Layer Overview

| Layer | Key Modules | Responsibilities |
| --- | --- | --- |
| CLI | `hermes_cli/main.py`, `hermes_cli/commands/*.py` | Typer command definitions, argument parsing, console UX via Rich |
| Services | `hermes_cli/services/*.py` | Business logic, config overrides, workflow orchestration, log/history/task helpers |
| Agents | `hermes_cli/agents/graph.py`, `state.py`, `nodes/` | LangGraph workflow that produces reports from prompts |
| Tools | `hermes_cli/tools/*.py` | Wrappers for Ollama, browser-use, and container-use clients |
| Persistence | `hermes_cli/persistence/*.py` | File-based storage under `~/.hermes/` |

## CLI Layer (`hermes_cli/commands/`)

- **Entry point** – `hermes_cli/main.py` instantiates a Typer app named
  `hermes` and registers the six command handlers exported from
  `hermes_cli/commands/__init__.py`.
- **Commands** – Each `*_cmd.py` module handles validation, user messaging, and
  delegates real work to services:
  - `init_cmd.py` – builds `~/.hermes/`, writes the default config, idempotent.
  - `task_cmd.py` – creates/list/deletes YAML task definitions (provides a
    `--deleate` alias to match the CLI spec).
  - `run_cmd.py` – executes single prompts, handles config overrides, exports
    the most recent report, or resets config with `--clear`.
  - `history_cmd.py` – lists reports, exports `TASK_ID:path`, deletes entries.
  - `log_cmd.py` – tails structured logs or streams them live. Task filtering is
    acknowledged but not yet implemented.
  - `debug_cmd.py` – surfaces combined log streams with simple level filtering.
- **Console UX** – The CLI uses Rich for tables, panels, and progress spinners,
  keeping error handling friendly while returning deterministic exit codes.

## Services Layer (`hermes_cli/services/`)

Each service receives optional `FilePaths`/dependencies so that tests or future
entrypoints can inject fakes.

- `ConfigService` – Reads/writes `config.yaml` via `ConfigRepository`, creates
  defaults, and applies CLI overrides (API/model/retry/validation/search knobs).
- `TaskService` – CRUD wrapper for `TaskRepository`, enforces ID generation and
  status updates.
- `RunService` – Loads config, builds a `HermesState`, invokes the LangGraph
  workflow (`create_hermes_workflow()`), writes structured logs, and persists
  `HistoryMeta` + report files.
- `HistoryService` – Lists metadata, fetches/exports reports, deletes entries.
- `LogService` – Wraps `LogRepository` tail/stream helpers.
- `DebugService` – Merges regular and debug logs, offers level filtering, and
  reuses `LogService` for streaming.

> Logging discipline: every service logs successes/failures using Python's
> `logging` module while `LogRepository` writes human-readable lines for users.

## Agents Layer (`hermes_cli/agents/`)

### State (`state.py`)

- `HermesState` is a Pydantic model shared by all nodes. It tracks the prompt,
  generated queries, research results, normalized notes, draft/validated report,
  validation loop counters, search bounds, and accumulated errors.

### Graph (`graph.py`)

- Builds a LangGraph `Graph`, registers each node, adds conditional routing for
  validation loops, and compiles the workflow. The helper `should_continue_validation`
  checks `state.validation_complete` to decide between `validator` and
  `final_reporter`.

### Nodes (`nodes/*.py`)

1. `prompt_normalizer` – trims/normalizes prompt text based on language.
2. `query_generator` – (TODO) calls Ollama to derive diverse search queries.
3. `web_researcher` – (TODO) uses `BrowserUseClient` to collect per-query sources.
4. `container_processor` – (TODO) normalizes gathered content (currently local).
5. `draft_aggregator` – (TODO) synthesizes a markdown draft with Ollama.
6. `validation_controller` – enforces min/max loop counts, toggles completion.
7. `validator` – (TODO) critiques/improves drafts, increments `loop_count`.
8. `final_reporter` – adds metadata headers and finalizes `validated_report`.

The placeholders log their gaps so integrators know where to finish web and
container automation work.

## Tools Layer (`hermes_cli/tools/`)

- `OllamaClient` – HTTPX-based client with retry/timeout logic and context
  manager support. Accepts an `OllamaConfig` dataclass produced by persistence.
- `BrowserUseClient` – Placeholder wrapper that will encapsulate browser-use.
  Currently warns and returns empty result lists so downstream code remains safe.
- `ContainerUseClient` – Placeholder for dagger-io/container-use execution.
  Provides a simple local normalization fallback so reports can still be saved.

Each client exposes context-manager friendly APIs so nodes can use `with` blocks
to ensure cleanup once real integrations land.

## Persistence Layer (`hermes_cli/persistence/`)

- `FilePaths` – Resolves `~/.hermes/` directories (Linux/macOS and Windows) and
  creates them on demand.
- `ConfigRepository` – Reads/writes YAML configs and defines default values used
  by `ConfigService`.
- `TaskRepository` – Manages `task-<ID>.yaml` files, generates IDs, and ensures
  datetimes are serialized/deserialized via ISO 8601.
- `HistoryRepository` – Stores report markdown (`report-<ID>.md`) and metadata
  (`report-<ID>.meta.yaml`), lists entries, exports reports, and handles deletes.
- `LogRepository` – Writes structured log lines, tails files, and implements a
  basic `tail -f` stream generator for both regular and debug log directories.

All user data is stored outside the repository in `~/.hermes/`, keeping the repo
clean and making it easy to reset the runtime environment.

## Runtime Data Flow

```
hermes run --prompt "... "
    ↓
RunCommand (Typer) validates args and builds overrides
    ↓
RunService loads ~/.hermes/config.yaml, applies overrides, generates run ID
    ↓
LangGraph workflow executes nodes in order, writing log lines along the way
    ↓
HistoryRepository saves report markdown + metadata
    ↓
CLI prints success panel with IDs and storage paths
```

Parallel flows:
- `LogRepository` writes entries such as `2025-11-14T10:31:02+09:00 [INFO] [RUN] ...`.
- `HistoryService` exposes reports for export and listing.
- `TaskService` uses the same ID generator/format so scheduled items look like
  runtime histories (`YYYY-NNNN`).

## Configuration Propagation & Validation

1. `hermes init` or `ConfigService.reset_to_default()` creates the baseline YAML.
2. Commands that accept overrides (`run`, `task`, etc.) build a dict of CLI flags.
3. `ConfigService.apply_overrides()` clones nested dataclasses so the base config
   on disk remains unchanged.
4. `RunService` injects search/validation bounds into `HermesState`. Nodes read
   from the state, not directly from the config file.
5. `validation_controller` ensures `loop_count` respects both `min_loops` and
   `max_loops`. Since the current validator is a placeholder, loop counts only
   advance when the node increments `state.loop_count`.

## Error Handling & Logging

- CLI commands catch exceptions, print Rich-formatted error messages, and exit
  with non-zero codes so shell scripts can detect failures.
- Services log errors via Python logging and also write entries through
  `LogRepository`, ensuring both developer logs and user-facing logs capture
  the same events.
- The placeholder integrations (browser/container) append friendly messages to
  `state.error_log`, so future report templates can include diagnostics.

## Extensibility Roadmap

- **Add a command** – Create `hermes_cli/commands/<name>_cmd.py`, export it in
  `commands/__init__.py`, and register it in `main.py`.
- **Add a service** – Place new business logic in `hermes_cli/services/`,
  accept optional `FilePaths`, and expose the class in `services/__init__.py`.
- **Add a node** – Implement the node in `agents/nodes/`, export it, and wire it
  into `graph.py` with the desired edges/conditions.
- **Add a tool** – Implement the client in `hermes_cli/tools/` and import it
  from nodes or services as needed.
- **Alter persistence** – Extend repositories or create new ones (e.g., metrics)
  and store additional files under `~/.hermes/`.

Because each layer uses dependency injection, new tests can pass fake
repositories or in-memory file paths without rewriting large chunks of code.

## External Interfaces

- **Ollama** – HTTP API at `http://localhost:11434/api/chat` by default.
- **LangGraph** – Provided by the `langgraph` package; `test_workflow.py`
  verifies that `create_hermes_workflow()` and `HermesState` import correctly.
- **browser-use** – Placeholder for headless browsing; integrate once the
  dependency is available in the runtime environment.
- **container-use / dagger-io** – Placeholder for isolated text processing. The
  current fallback runs lightweight normalization locally.

See [DEVELOPMENT.md](DEVELOPMENT.md) for setup/testing tips and
[USAGE_GUIDE.md](USAGE_GUIDE.md) for command walkthroughs.
