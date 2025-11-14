# Hermes Usage Guide

This guide walks through the day-to-day commands for installing, initializing,
running research jobs, managing history, and troubleshooting Hermes.

> Installation instructions live in [README.md](README.md#installation). Make
> sure the `hermes` CLI is on your `PATH` before continuing.

## 1. Initialize Runtime Directories

```bash
hermes init
```

Creates `~/.hermes/` with:

- `config.yaml` – editable settings for Ollama, validation loops, search bounds
- `task/` – scheduled task definitions (`task-<ID>.yaml`)
- `history/` – reports (`report-<ID>.md`) and metadata (`*.meta.yaml`)
- `log/` – user-facing logs (`hermes-YYYYMMDD.log`)
- `debug_log/` – verbose logs for `hermes debug`
- `cache/` – scratch space for future features

Running `hermes init` again is safe; it simply points to the existing location.

## 2. Run Research Tasks

### Basic Run

```bash
hermes run --prompt "Summarize current LLM distillation techniques"
```

Steps performed:
1. Load `config.yaml` via `ConfigService`.
2. Create a `HermesState` with validation/search bounds.
3. Execute the LangGraph workflow.
4. Write logs to `~/.hermes/log/`.
5. Save `report-<ID>.md` and metadata under `~/.hermes/history/`.

### Customize the Run

```bash
# Force English output and extended validation loop
hermes run \
  --prompt "LLM safety milestones" \
  --language en \
  --min-validation 2 \
  --max-validation 5

# Point to a different Ollama endpoint & model for a single run
hermes run \
  --prompt "Edge AI trends" \
  --api http://remote-host:11434/api/chat \
  --model llama2:70b
```

### Export Latest Report

```bash
hermes run --export ./latest-report.md
```

Exports the most recent history entry without needing the task ID. Requires at
least one completed run.

## 3. Manage Scheduled Tasks

```bash
# Save prompt for later execution
hermes task --prompt "Weekly AI news sweep"

# List stored tasks
hermes task --list

# Delete a task (typo alias --deleate also works)
hermes task --delete 2025-0003
```

Tasks are stored as YAML files in `~/.hermes/task/`. Use `hermes queue` to drain
all scheduled work (oldest first) or `hermes run --task-id <ID>` when you only
need to execute a single entry.

## 4. Execute the Task Queue

```bash
# Run the oldest scheduled task
hermes queue

# Drain the entire queue
hermes queue --all

# Run up to N tasks
hermes queue -n 3
```

`QueueService` looks for tasks whose status is `scheduled`, orders them by
creation time, and invokes `RunService.run_task()` for each. Failures are logged
and the queue continues so the backlog does not stall.

## 5. Review History & Export Reports

```bash
# List most recent entries (default limit = 100)
hermes history

# Limit to 10 entries
hermes history --limit 10

# Export a specific report
hermes history --export 2025-0004 ./reports/weekly.md

# Delete an entry (metadata + markdown)
hermes history --delete 2025-0002
```

History metadata tables show creation/finish times, model name, validation loop
count, and number of sources recorded by the workflow.

## 6. Inspect Logs & Debug Output

```bash
# Tail recent user-facing logs (default 50 lines)
hermes log

# Follow new entries live
hermes log --follow

# Increase line count
hermes log -n 200

# Filter by severity in debug logs (info/warning/error/all)
hermes debug --error -n 100

# Stream combined logs
hermes debug --all --follow
```

If `--task-id` is omitted, `hermes log` looks for the most recent task whose
status is `running` and automatically filters log lines for that ID. Pass an
explicit `--task-id` to override the default, or drop the flag to view all logs.

## 7. Configuration & Validation Loops

- Edit `~/.hermes/config.yaml` directly to change defaults:

  ```yaml
  validation:
    min_loops: 1
    max_loops: 3
  search:
    min_sources: 3
    max_sources: 8
  ```

- CLI overrides (`--language`, `--min-validation`, `--max-validation`,
  `--min-search`, `--max-search`, `--model`, `--api`, `--retry`) only affect the
  current command.
- `validation_controller` always enforces the minimum loop count before allowing
  the workflow to exit; the placeholder `validator` currently increments the
  counter without yet performing LLM-based critiques.

Resetting the configuration:

```bash
hermes run --clear
```

This recreates the default YAML and reinitializes directories if needed.

## 8. CLI Flag Reference

| Command | Flag | Description | Default |
| --- | --- | --- | --- |
| `hermes run` | `--prompt TEXT` | Research question (required unless `--export`/`--clear`/`--task-id`) | `None` |
| `hermes run` | `--task-id ID` | Execute a scheduled task (disables other overrides) | `None` |
| `hermes run` | `--language {ja,en}` | Output language override | `config.language` |
| `hermes run` | `--api URL` | Temporary Ollama API endpoint | `config.ollama.api_base` |
| `hermes run` | `--model NAME` | Temporary model selection | `config.ollama.model` |
| `hermes run` | `--min-validation INT` / `--max-validation INT` | Validation loop bounds | Configured values |
| `hermes run` | `--min-search INT` / `--max-search INT` | Source collection hints | Configured values |
| `hermes run` | `--query INT` | Number of queries to generate | `None` (node default) |
| `hermes run` | `--retry INT` | Override Ollama retry count | `config.ollama.retry` |
| `hermes run` | `--export PATH` | Copy latest successful report to path | Uses most recent history |
| `hermes run` | `--clear` | Reset `config.yaml` to defaults | `False` |
| `hermes task` | `--prompt TEXT` | Create task with prompt | `None` |
| `hermes task` | `--list` | Display tasks table | `False` |
| `hermes task` | `--delete/--deleate ID` | Remove task file | `None` |
| `hermes queue` | `-n/--limit INT`, `--all` | Execute scheduled tasks sequentially | `-n 1` |
| `hermes history` | `--limit INT` | Control table size | `100` |
| `hermes history` | `--export ID PATH` | Export report markdown | `None` |
| `hermes history` | `--delete/--deleate ID` | Delete history entry | `None` |
| `hermes log` | `-n/--lines INT` | Tail the last N log lines | `50` |
| `hermes log` | `-f/--follow` | Stream logs | `False` |
| `hermes log` | `--task-id ID` | Filter logs for a specific task/run | Auto-selects latest `running` |
| `hermes debug` | `--info/--warning/--error/--all` | Level filter | `--all` |
| `hermes debug` | `-n/--lines INT` | Tail debug logs | `50` |
| `hermes debug` | `-f/--follow` | Stream debug logs | `False` |

## 9. Typical Workflows

### Research & Export

```bash
hermes init
hermes run --prompt "AI policy changes in 2025" --language en
hermes log --follow                    # watch progress in another terminal
hermes history                         # get the task ID
hermes history --export 2025-0005 ./reports/policy.md
```

### Weekly Monitoring Loop

```bash
hermes task --prompt "Weekly AI governance recap"
hermes task --list

# When ready to run, either drain the queue or execute a single task
hermes queue
# hermes run --task-id 2025-0006
hermes history --export 2025-0006 ./reports/week-42.md
```

### Reset & Recover

```bash
# Regenerate config and directories
hermes run --clear
hermes init     # optional, but prints current path if already set up

# If logs look stale, delete the day's file manually and rerun commands
rm ~/.hermes/log/hermes-$(date +%Y%m%d).log
hermes log
```

## 10. Troubleshooting

- **Ollama connection refused** – Run `ollama serve` and confirm the port in
  `~/.hermes/config.yaml`. Retry the command.
- **Model missing** – `ollama pull gpt-oss:20b` (or whichever model you set via
  `--model`).
- **No history entries** – Ensure at least one `hermes run --prompt ...` has
  completed; `hermes run --export` requires existing history.
- **Log streaming silent** – Logs are stored per day; if the file doesn't exist
  yet, the command creates an empty file and waits for new entries.
- **Placeholder behavior** – Browser/container integrations currently log
  warnings and return empty result sets. This is expected until real integrations
  are wired in.

For deeper architectural details, refer to [ARCHITECTURE.md](ARCHITECTURE.md).
For development workflows, read [DEVELOPMENT.md](DEVELOPMENT.md).
