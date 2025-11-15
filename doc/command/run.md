# hermes run

## Overview

Executes research tasks using the LangGraph workflow with Ollama LLM and web search capabilities.

## Synopsis

```bash
hermes run --prompt "research question" [OPTIONS]
hermes run --task-id TASK_ID [OPTIONS]
hermes run --export PATH
hermes run --clear
```

## Description

The `run` command is the primary interface for executing research tasks. It:

1. Normalizes the input prompt
2. Generates search queries using Ollama
3. Collects sources via DuckDuckGo (or browser-use if available)
4. Processes and normalizes content
5. Generates a draft report
6. Validates and refines through configured loop iterations
7. Saves the final report to `~/.hermes/history/`

## Options

### Core Options

| Option | Type | Description |
|--------|------|-------------|
| `--prompt TEXT` | String | Research question or prompt to investigate |
| `--task-id TEXT` | String | Execute a pre-scheduled task by ID |
| `--export PATH` | Path | Export the most recent report to specified path |
| `--clear` | Flag | Reset configuration to defaults and exit |

### LLM Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--api TEXT` | String | `http://localhost:11434/api/chat` | Ollama API endpoint |
| `--model TEXT` | String | `gpt-oss:20b` | Model name to use |
| `--retry INT` | Integer | `3` | Number of retry attempts for failed requests |

### Validation Control

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--min-validation INT` | Integer | `1` | Minimum validation loops (always enforced) |
| `--max-validation INT` | Integer | `3` | Maximum validation loops (hard limit) |

### Search Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--min-search INT` | Integer | `3` | Minimum sources to collect per query |
| `--max-search INT` | Integer | `8` | Maximum sources to collect per query |
| `--query INT` | Integer | `3` | Number of search queries to generate |

### Output Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--language TEXT` | String | `ja` | Output language code (`ja` or `en`) |

## Examples

### Basic research task

```bash
hermes run --prompt "Explain quantum computing error correction"
```

**Output:**
```
⠙ Executing research task...
╭───────── Execution Complete ─────────╮
│ ✓ Task completed successfully!      │
│                                      │
│ Task ID: 2025-0001                   │
│ Model: gpt-oss:20b                   │
│ Sources: 24                          │
│ Validation loops: 2                  │
│ Duration: 142s                       │
│                                      │
│ Report: ~/.hermes/history/...        │
╰──────────────────────────────────────╯
```

### English output with custom validation

```bash
hermes run \
  --prompt "Latest developments in AI safety research" \
  --language en \
  --min-validation 2 \
  --max-validation 5
```

### Use different model

```bash
hermes run \
  --prompt "量子コンピュータの現状" \
  --model llama2:70b \
  --language ja
```

### Execute scheduled task

```bash
# First, create a task
hermes task --prompt "Weekly AI news summary"

# Then execute it
hermes run --task-id 2025-0042
```

### Export recent report

```bash
hermes run --export ./my-report.md
```

### Reset configuration

```bash
hermes run --clear
```

## Workflow Stages

The research workflow progresses through these stages:

1. **Prompt Normalization** - Cleans and validates input
2. **Query Generation** - Creates diverse search queries (Ollama)
3. **Web Research** - Collects sources (DuckDuckGo/browser-use)
4. **Container Processing** - Normalizes text (Docker/local fallback)
5. **Draft Aggregation** - Synthesizes initial report (Ollama)
6. **Validation Controller** - Checks quality and loop limits
7. **Validator** - Critiques and generates follow-up queries (Ollama)
8. **Final Reporter** - Adds metadata and finalizes report

The workflow loops between stages 3-7 based on validation settings.

## Output Files

Each execution creates:

- **Report file**: `~/.hermes/history/report-YYYY-NNNN.md`
- **Metadata file**: `~/.hermes/history/report-YYYY-NNNN.meta.yaml`
- **Log entries**: `~/.hermes/log/hermes-YYYYMMDD.log`

## Exit Codes

- **0**: Success - report generated
- **1**: Execution failed (see logs)
- **2**: Invalid arguments
- **3**: Validation failed (no report produced)

## Environment Requirements

### Required Services

- **Ollama server**: Must be running (`ollama serve`)
  ```bash
  # Check status
  curl http://localhost:11434/api/version
  ```

- **Model**: Must be pulled locally
  ```bash
  ollama pull gpt-oss:20b
  ```

### Optional Services

- **Docker**: For container-based processing (falls back to local if unavailable)
- **browser-use**: For advanced web automation (uses DuckDuckGo fallback by default)

## Configuration Override Precedence

Settings are applied in this order (last wins):

1. Hardcoded defaults
2. `~/.hermes/config.yaml`
3. Command-line flags

Example:
```yaml
# config.yaml sets timeout to 180s
ollama:
  timeout_sec: 180
```

```bash
# This run uses 180s timeout
hermes run --prompt "test"

# This run uses 300s timeout (override)
hermes run --prompt "test" --timeout 300
```

## Performance Tuning

### Fast execution (fewer sources, no validation)

```bash
hermes run \
  --prompt "Quick summary of topic" \
  --min-validation 1 \
  --max-validation 1 \
  --max-search 3 \
  --query 2
```

### Comprehensive research (many sources, thorough validation)

```bash
hermes run \
  --prompt "In-depth analysis of topic" \
  --min-validation 3 \
  --max-validation 5 \
  --max-search 12 \
  --query 5
```

## Troubleshooting

### Timeout errors

Increase timeout in `~/.hermes/config.yaml`:

```yaml
ollama:
  timeout_sec: 300  # Default: 180
```

### No sources returned

- Check internet connectivity
- Verify DuckDuckGo is not rate-limiting
- Try reducing `--max-sources`
- Wait 1-2 minutes between runs

### Model not found

```bash
# List available models
ollama list

# Pull required model
ollama pull gpt-oss:20b
```

### Workflow did not produce report

Check logs for errors:
```bash
hermes log -n 50
hermes debug --error -n 100
```

Common causes:
- Ollama server not running
- Model timeout on complex queries
- All web searches failed (rate limiting)

## Related Commands

- [`hermes init`](./init.md) - Initialize workspace
- [`hermes task`](./task.md) - Schedule tasks for later execution
- [`hermes queue`](./queue.md) - Execute multiple scheduled tasks
- [`hermes history`](./history.md) - View and export reports
- [`hermes log`](./log.md) - View execution logs

## Notes

- The `--clear` flag resets configuration but preserves history and logs
- Validation loops can increase execution time significantly
- DuckDuckGo may rate-limit aggressive querying
- Reports are saved even if validation fails
- Task IDs follow the format `YYYY-NNNN` (e.g., `2025-0001`)
