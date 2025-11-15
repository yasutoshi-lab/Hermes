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
- 🌐 **Web research capabilities** – DuckDuckGo integration provides immediate web
  search functionality; optional browser-use upgrade available for advanced automation.
- 🐳 **Container isolation** – Docker-based processing via dagger-io with automatic
  fallback to local processing when containers are unavailable.

## Prerequisites

- Python 3.10+ (tested with CPython 3.10-3.12; use a virtual environment)
- `uv` or `pip` for dependency management
- [Ollama](https://ollama.ai/) with the `gpt-oss:20b` model pulled locally
  ```bash
  # Install Ollama from https://ollama.ai/download
  # Pull the required model
  ollama pull gpt-oss:20b

  # Start the Ollama server (keep running in a separate terminal)
  ollama serve
  ```
- **Docker** (required for container-use integration)
  - Docker 20.10+ recommended
  - See [Integration Setup](#integration-setup) section for detailed instructions
- **Optional: browser-use** for advanced web automation
  - DuckDuckGo fallback works without it
  - See [Integration Setup](#integration-setup) section for installation

> ℹ️ Hermes requires `ollama serve` to be running for LLM operations. Web research
> works out-of-the-box with DuckDuckGo; browser-use provides enhanced capabilities
> when installed. Container-use provides isolated processing when Docker is available,
> falling back to local processing otherwise.

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

# Note: DuckDuckGo web search works immediately.
# For advanced browser automation, see the Integration Setup section below.
```

To include developer tooling (pytest, ruff, mypy, black):

```bash
pip install -e .[dev]
# or
uv pip install -e '.[dev]'
```

## Integration Setup

### Container-use (dagger-io)

Hermes uses container-use (via dagger-io) for isolated text normalization and processing. The `dagger-io` package is installed automatically, but Docker must be running for full functionality.

**Setup Steps:**

1. **Install Docker** (if not already installed):
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install docker.io
   sudo systemctl start docker
   sudo systemctl enable docker

   # macOS (use Docker Desktop)
   # Download from https://www.docker.com/products/docker-desktop

   # Verify installation
   docker --version
   ```

2. **Add your user to docker group** (Linux only, to avoid sudo):
   ```bash
   sudo usermod -aG docker $USER
   # Log out and back in for changes to take effect
   ```

3. **Test container access**:
   ```bash
   docker ps
   # Should show running containers (or empty list if none running)
   ```

**Fallback Behavior:**
If Docker is unavailable, Hermes automatically falls back to local text normalization with a warning logged. The workflow continues without container isolation.

### Browser-use

Hermes supports two modes for web research:

1. **DuckDuckGo Fallback (Default)** - Works out-of-the-box with `duckduckgo-search`
2. **browser-use (Optional)** - Provides advanced browser automation capabilities

**Option A: Use DuckDuckGo Fallback (Recommended for Getting Started)**

No additional setup required. The `duckduckgo-search` package is installed automatically and provides reliable web search functionality.

**Option B: Install browser-use for Advanced Features**

Currently, `browser-use` must be installed from source as it's not yet available on PyPI.

1. **Clone and install browser-use**:
   ```bash
   # In a separate directory
   cd /tmp
   git clone https://github.com/browser-use/browser-use.git
   cd browser-use
   pip install -e .
   ```

2. **Install Hermes with browser extra**:
   ```bash
   cd /path/to/Hermes
   pip install -e .[browser]
   ```

3. **Install browser dependencies**:
   ```bash
   # Install Playwright browsers
   playwright install chromium

   # On Linux, you may need additional system dependencies
   playwright install-deps chromium
   ```

4. **Verify browser-use is detected**:
   ```bash
   # Run a test query - check logs for "browser-use detected"
   hermes run --prompt "test query" --max-validation 1
   hermes log -n 10 | grep browser
   ```

**Switching Between Modes:**

Hermes automatically detects if `browser-use` is installed and uses it. To force DuckDuckGo fallback even when browser-use is available, uninstall it:

```bash
pip uninstall browser-use
```

**Troubleshooting:**

- **DuckDuckGo rate limiting**: If you see errors about rate limits, add delays between runs or use smaller `--max-sources` values.
- **browser-use initialization fails**: Check Playwright installation with `playwright --version` and ensure chromium is installed.
- **Robots.txt blocking**: Some sites block automated access. Hermes respects robots.txt and will skip those URLs.

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

- **Browser research**: DuckDuckGo integration works out-of-the-box for immediate web
  search capabilities. For advanced automation features, install `browser-use` from
  source following the [Integration Setup](#integration-setup) instructions. Hermes
  automatically detects and uses browser-use when available.
- **Container processing**: Requires Docker 20.10+ for isolated text normalization.
  When Docker is unavailable, Hermes automatically falls back to local processing
  with a warning logged. See [Integration Setup](#integration-setup) for Docker
  installation steps.
- **Validation loops**: Quality scoring and follow-up query generation use evolving
  heuristic thresholds. Expect some variation in loop counts as the evaluation
  metrics improve with more usage data.
- **Task scheduling**: Tasks are stored as YAML files but require manual execution
  via `hermes queue` or `hermes run --task-id`. There is no background daemon;
  schedule your queue runs with system cron/systemd if needed.
- **Log filtering**: `hermes log --task-id` filters entries, but log files are
  segmented by day (`hermes-YYYYMMDD.log`). For long-running tasks that span
  midnight, you may need to check multiple log files.
- **Model timeout**: Default Ollama timeout is 180 seconds (configurable via
  `~/.hermes/config.yaml: ollama.timeout_sec`). Large models or complex queries
  may require higher values.

For implementation details and extension points, see integration notes in
`hermes_cli/tools/` and `hermes_cli/agents/nodes/`.

## Troubleshooting Highlights

- **Ollama connection errors** – Ensure `ollama serve` is running locally and
  that `~/.hermes/config.yaml` points `ollama.api_base` to the correct host.
  Check connectivity with `curl http://localhost:11434/api/version`.
- **Model not found** – Run `ollama pull gpt-oss:20b` (or the model you set via
  CLI). Hermes surfaces the HTTP 404/500 errors in `hermes log`.
- **Timeout errors** – Increase `ollama.timeout_sec` in `~/.hermes/config.yaml`
  from the default 180 seconds. Large models may need 300+ seconds for complex queries.
- **Docker connection refused** – Container-use requires Docker running. Check with
  `docker ps`. If unavailable, Hermes falls back to local processing with a warning.
- **DuckDuckGo rate limiting** – Space out requests or reduce `--max-sources`. The
  service may temporarily block rapid queries; wait 1-2 minutes and retry.
- **browser-use not detected** – After installing from source, verify with
  `python -c "import browser_use; print('OK')"`. Reinstall playwright browsers if needed.
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
