# Hermes CLI Usage

The Hermes CLI wraps the LangGraph workflow and history/model tooling so you can run research tasks directly from the terminal. This document summarizes the available commands, options, and typical workflows.

## Installation

After installing the project (`pip install -e .`), the `hermes` entry point becomes available on your PATH:

```bash
hermes --help
```

## Commands

### `hermes query`

Run a single-shot research query and print the resulting report.

```
hermes query "LangGraph 最新動向をまとめて" \
  --language ja \
  --model gpt-oss:20b \
  --output reports/langgraph.md \
  --format markdown \
  --verbose
```

Options:
- `--language ja|en` – override default language
- `--model` – choose a different LLM model name
- `--output PATH` – save the Markdown report to a file
- `--format markdown|pdf|both` – declare desired report format (PDF links rely on the workflow’s report node)
- `--verbose` – stream node-by-node progress using the orchestrator’s event feed

### `hermes interactive`

Starts an interactive REPL loop. Type a query, hit Enter, and Hermes will run the full workflow. Type `exit`, `quit`, or press `Ctrl+C` to leave. Supports the same `--language` and `--model` overrides as `query`.

### `hermes history`

Manage saved session artifacts (search results, processed data, reports).

- `hermes history list --limit 5` – show the most recent session IDs.
- `hermes history show <session_id> --section report|search_results|processed_data|input|state` – display a specific artifact.
- `hermes history cleanup --session-id <session_id>` – delete a single session.
- `hermes history cleanup --keep-last 10` – prune everything except the N latest sessions.

### `hermes models`

Interact with Ollama models via the `ModelManager`.

- `hermes models list` – list locally available models.
- `hermes models info gpt-oss:20b` – check whether a model is installed.
- `hermes models pull mistral:7b` – download/pull a model (requires Ollama).

> **Note:** These commands require the `ollama` Python package and access to your running Ollama daemon. The CLI surfaces meaningful errors if the dependency is missing or the daemon is unreachable.

## Streaming & Events

Passing `--verbose` to `hermes query` (or enabling verbose mode in future integrations) sets `stream=True` on `run_workflow`. The orchestrator returns a `WorkflowRunResult` so the CLI can render a table of `WorkflowEvent`s, showing the order of node execution along with the keys each node updated.

## Troubleshooting

- **History warnings**: If the CLI reports “history path unavailable,” either disable history in config or ensure the sessions directory is writable.
- **Model errors**: Use `hermes models pull <name>` to download missing models. If `ollama` is not installed, install it and restart the CLI.
- **PDF output missing**: The report node only writes PDFs when `report_format` is `pdf` or `both` and the `reportlab` package (or placeholder fallback) is available.

Refer back to `docs/LANGGRAPH_IMPLEMENTATION.md` for deeper architectural context or open an issue if additional CLI workflows are needed.
