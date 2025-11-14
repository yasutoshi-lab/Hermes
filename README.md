# Hermes CLI

Hermes is a CLI-first research agent that orchestrates LangGraph workflows,
Ollama-hosted LLMs, and (future) browser/container integrations to gather
information, iterate through validation loops, and save reports locally.

## Features

- 🤖 **LLM-driven workflow** – Typer CLI feeds prompts into a LangGraph graph
  (`hermes_cli/agents/graph.py`) that normalizes input, generates queries, and
  produces structured markdown reports.
- 🔁 **Configurable validation loops** – `~/.hermes/config.yaml` controls the
  minimum/maximum validation cycles enforced by `validation_controller`. Each
  loop re-enters the draft stage until limits are met.
- 🗂️ **File-based persistence** – Tasks, logs, and history are persisted as YAML
  and Markdown under `~/.hermes/` via repositories in `hermes_cli/persistence/`.
- 🛠️ **Service layer abstraction** – Commands defer to services (config, run,
  task, history, log, debug) that can be reused in other entry points.
- 📜 **Full audit trail** – `hermes history`, `hermes log`, and `hermes debug`
  provide report exports, structured logs, and filtered debug streams.
- ⚠️ **Clear limitations** – Browser-use and container-use clients are wired in
  but still return placeholder data; external integration work is required
  before Hermes can browse the web or execute isolated scripts.

## Prerequisites

- Python 3.10+ (tested with CPython; use a virtual environment)
- `uv` or `pip` for dependency management
- [Ollama](https://ollama.ai/) with the `gpt-oss:20b` model pulled locally
- Docker (or another OCI runtime) for future container-use integration
- Optional: `watchdog` for live log monitoring (already listed in deps)
- Start the Ollama server before running Hermes:
  ```bash
  ollama serve
  ```

> ℹ️ Hermes currently stubs browser/container actions. Hermes now talks to a real
> Ollama server for query generation, drafting, and validation, so keep
> `ollama serve` running when using `hermes run`.

## Installation

```bash
git clone https://example.com/Hermes.git
cd Hermes

# Create & activate a virtual environment (adjust path/shell as needed)
python -m venv .venv
source .venv/bin/activate

# Editable install via pip
pip install -e .

# or install with uv (faster resolver)
uv pip install -e .

# Optional browser automation extra (requires browser-use installed from source)
# pip install -e .[browser]
# See the Browser Client section below for details.
```

To include developer tooling (pytest, ruff, mypy, black):

```bash
pip install -e .[dev]
# or
uv pip install -e '.[dev]'
```

## Quick Start

1. **Start the Ollama daemon**
   ```bash
   ollama serve
   ```
   Leave this running in another terminal so Hermes can reach the API.

2. **Initialize workspace**
   ```bash
   hermes init
   ```
   Creates `~/.hermes/` with `config.yaml`, `history/`, `log/`, and related
   directories. Rerunning prints a reminder if everything already exists.

3. **Run your first research task**
   ```bash
   hermes run --prompt "Explain quantum computing error correction methods"
   ```
   `RunService` loads config, builds LangGraph state, writes structured logs,
   and saves `report-<ID>.md` plus metadata in `~/.hermes/history/`.

4. **Inspect the results**
   ```bash
   hermes history --limit 5
   hermes run --export ./latest-report.md    # exports most recent report
   hermes history --export 2025-0001 ./report.md
   ```

5. **Follow the logs**
   ```bash
   hermes log --follow       # tail ~/.hermes/log/hermes-YYYYMMDD.log
   hermes debug --error -n 100
   ```

6. **Drain scheduled tasks when ready**
   ```bash
   hermes task --prompt "Weekly AI recap"
   hermes queue --all        # execute every scheduled task in order
   ```
   `QueueService` picks the oldest `scheduled` entries and runs them sequentially
   so you do not have to trigger each task manually.

7. **Reset configuration if needed**
   ```bash
   hermes run --clear
   ```
   `ConfigService` recreates the default YAML with Ollama + validation settings.

See [USAGE_GUIDE.md](USAGE_GUIDE.md) for task-oriented walkthroughs.

## Core Commands

| Command | Description |
| --- | --- |
| `hermes init` | Creates `~/.hermes/` directories and the default `config.yaml`. |
| `hermes run --prompt ...` | Executes a one-off research task. Options include `--language`, `--api`, `--model`, `--min-validation`, `--max-validation`, `--min-search`, `--max-search`, `--retry`, `--query`, `--export` (latest run), and `--task-id` to run a scheduled task. |
| `hermes task --prompt ...` | Saves prompts for later via `task-<ID>.yaml`. List with `--list`, delete with `--delete TASK_ID`. |
| `hermes queue` | Executes scheduled tasks sequentially. Use `-n/--limit` to cap the run or `--all` to drain the queue. |
| `hermes history` | Lists stored runs, exports reports with `--export TASK_ID PATH`, and deletes entries via `--delete`. |
| `hermes log` | Shows or follows structured logs in `~/.hermes/log/`; `--task-id` filters to a specific run (defaults to the newest running task), `--follow` streams, and `-n` controls line count. |
| `hermes debug` | Reads from both standard and debug log files with level filters (`--error`, `--warning`, `--info`, `--all`). |

Command implementations live in `hermes_cli/commands/` and delegate to services
in `hermes_cli/services/` for testability.

## Configuration Overview

`hermes init` (or the `ConfigService`) ensures the following layout:

```
~/.hermes/
├── cache/
├── config.yaml
├── history/
│   ├── report-<ID>.md
│   └── report-<ID>.meta.yaml
├── task/
│   └── task-<ID>.yaml
├── log/
│   └── hermes-YYYYMMDD.log
└── debug_log/
    └── hermes-YYYYMMDD.log
```

Key config fields (`~/.hermes/config.yaml`):

- `ollama.api_base`, `ollama.model`, `ollama.retry`, `ollama.timeout_sec`
- `language`: default output locale (`ja` by default)
- `validation.min_loops`, `validation.max_loops`: determine when Hermès stops
  looping through the validator; min loops are always enforced even if quality
  checks pass.
- `search.min_sources`, `search.max_sources`: hints passed to nodes/tools when
  collecting sources; current placeholders still respect provided bounds.
- `logging.log_dir`, `logging.debug_log_dir`
- `cli.history_limit`: default cap for `hermes history`

All run-time overrides map directly to CLI flags (e.g., `--model llama2:70b`
updates the Ollama config only for that invocation).

## Current Limitations & Notes

- Browser research now defaults to DuckDuckGo + httpx fetching and automatically
  upgrades to `browser-use` when that optional dependency is installed. Until
  an official PyPI release ships, install `browser-use` from source and then
  use `pip install -e .[browser]` to enable richer automation.
- Container processing prefers a disposable Docker/Python container for text
  normalization. If Docker is unavailable, Hermes falls back to deterministic
  local normalization and logs a warning.
- Validation loops perform lightweight quality scoring plus follow-up query
  generation, but the heuristic thresholds are still evolving. Expect some
  over- or under-shooting as more evaluation data arrives.
- Task scheduling stores prompts and metadata, but there is no background
  scheduler. Use `hermes queue` (or `hermes run --task-id ...`) to process
  entries when you're ready.
- `hermes log --task-id` filters log lines, but historical log files are still
  segmented by day. You may need to raise `--lines` to capture earlier phases.

See the open integration notes inside `hermes_cli/tools/` and
`hermes_cli/agents/nodes/` for TODO markers.

## Troubleshooting Highlights

- **Ollama connection errors** – Ensure `ollama serve` is running locally and
  that `~/.hermes/config.yaml` points `ollama.api_base` to the correct host.
- **Model not found** – Run `ollama pull gpt-oss:20b` (or the model you set via
  CLI). Hermes surfaces the HTTP 404/500 errors in `hermes log`.
- **Stale configuration** – `hermes run --clear` regenerates the default config.
- **Missing history/log files** – `hermes init` can be rerun safely; logs are
  rotated per day (`hermes-YYYYMMDD.log`).
- **LangGraph import issues** – Use `python test_workflow.py` to confirm that
  `create_hermes_workflow()` compiles; reinstall dependencies if this fails.

## Documentation Set

- [ARCHITECTURE.md](ARCHITECTURE.md) – layer breakdown, data flow, and node map
- [DEVELOPMENT.md](DEVELOPMENT.md) – environment setup, tooling, testing tips
- [USAGE_GUIDE.md](USAGE_GUIDE.md) – task-based walkthroughs and CLI flags

These documents live alongside this README at the repository root. Keep them
updated as new services or integrations land.
