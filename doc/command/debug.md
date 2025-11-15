# hermes debug

## Overview

Views detailed debug logs with filtering by log level for troubleshooting and development.

## Synopsis

```bash
hermes debug
hermes debug --error
hermes debug --warning
hermes debug --info
hermes debug --all
hermes debug -n COUNT
hermes debug --follow
```

## Description

The `debug` command provides access to verbose debug logs stored in `~/.hermes/debug_log/`. These logs include:

- Internal state transitions
- Detailed error traces with stack traces
- API request/response details
- Performance metrics
- Node-level workflow events

Debug logs are more verbose than regular logs and are intended for:
- Troubleshooting execution failures
- Performance analysis
- Development and debugging
- Understanding workflow internals

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-n, --lines INT` | Integer | `50` | Number of log lines to display |
| `--error` | Flag | `false` | Show only ERROR level logs |
| `--warning` | Flag | `false` | Show only WARNING level logs |
| `--info` | Flag | `false` | Show only INFO level logs |
| `--all` | Flag | `false` | Show all log levels (explicit) |
| `-f, --follow` | Flag | `false` | Stream logs in real-time |

## Log Level Precedence

If multiple level flags are specified, the most specific wins:

1. `--error` (most specific)
2. `--warning`
3. `--info`
4. `--all` or none (default, shows all levels)

## Log Format

Debug logs follow the same format as regular logs but with additional details:

```
YYYY-MM-DDTHH:MM:SS.mmmmmm+TZ [LEVEL] [MODULE] Detailed message
```

### Example

```
2025-11-14T14:28:30.123456+09:00 [DEBUG] [nodes.query_generator] Generating queries for prompt="quantum computing"
2025-11-14T14:28:31.234567+09:00 [DEBUG] [tools.ollama_client] Sending request to http://localhost:11434/api/chat
2025-11-14T14:28:35.345678+09:00 [DEBUG] [tools.ollama_client] Received response: 347 tokens in 3.2s
2025-11-14T14:28:36.456789+09:00 [ERROR] [tools.browser_use_client] DuckDuckGo rate limit exceeded, retrying after 2s
```

## Log Levels in Debug Logs

| Level | Description |
|-------|-------------|
| **DEBUG** | Detailed internal operations, state changes, API calls |
| **INFO** | Key milestones and workflow progression |
| **WARNING** | Potential issues, fallbacks, retries, degraded performance |
| **ERROR** | Failures with stack traces, timeouts, connection errors |

## Examples

### View all debug logs (default 50 lines)

```bash
hermes debug
```

### View last 100 lines

```bash
hermes debug -n 100
```

### Show only errors

```bash
hermes debug --error -n 200
```

**Output:**
```
2025-11-14T14:28:36+09:00 [ERROR] [tools.browser_use_client] DuckDuckGo rate limit
2025-11-14T14:32:15+09:00 [ERROR] [tools.ollama_client] Request timeout after 180s
2025-11-14T14:35:22+09:00 [ERROR] [services.run_service] Execution failed: 'dict' object has no attribute 'validated_report'
Traceback (most recent call last):
  File "hermes_cli/services/run_service.py", line 121
  ...
```

### Show warnings and errors

```bash
hermes debug --warning -n 150
```

### Show info level only

```bash
hermes debug --info -n 75
```

### Follow debug logs in real-time

```bash
hermes debug --follow
```

**Output:**
```
Following debug logs [level=all] (Ctrl+C to exit)...

2025-11-14T14:40:00+09:00 [DEBUG] [nodes.prompt_normalizer] Normalizing prompt
2025-11-14T14:40:01+09:00 [DEBUG] [nodes.query_generator] Calling Ollama for queries
... (continues until Ctrl+C)
```

### Follow errors only

```bash
hermes debug --follow --error
```

**Output:**
```
Following debug logs [level=error] (Ctrl+C to exit)...

(waits for errors to occur)
```

## Debug Log File Locations

Debug logs are stored in `~/.hermes/debug_log/` with daily rotation:

```
~/.hermes/debug_log/
├── hermes-20251114.log  # Today
├── hermes-20251113.log  # Yesterday
├── hermes-20251112.log
└── ...
```

## Use Cases

### Investigate Ollama timeouts

```bash
hermes debug --error -n 500 | grep -i timeout
```

### Check web research failures

```bash
hermes debug --warning -n 200 | grep -i duckduckgo
```

### Analyze validation loop behavior

```bash
hermes debug -n 1000 | grep -i validator
```

### Monitor node execution order

```bash
hermes debug --follow | grep -E "nodes\.(prompt|query|web|container|draft|validator|final)"
```

### Debug configuration issues

```bash
hermes debug -n 100 | grep -i config
```

### Extract error stack traces

```bash
hermes debug --error -n 500 > errors.log
```

## Level Filtering Behavior

### --error flag

Shows only lines with `[ERROR]` level:

```bash
hermes debug --error -n 100
```

Includes stack traces that follow error lines.

### --warning flag

Shows only lines with `[WARNING]` level:

```bash
hermes debug --warning -n 100
```

### --info flag

Shows only lines with `[INFO]` level:

```bash
hermes debug --info -n 100
```

### --all or no flag

Shows all levels (DEBUG, INFO, WARNING, ERROR):

```bash
hermes debug -n 100
# Equivalent to:
hermes debug --all -n 100
```

## Combining with Standard Tools

### Count errors per module

```bash
hermes debug --error -n 1000 | grep -oE '\[.*?\]' | sort | uniq -c | sort -nr
```

### Extract Ollama response times

```bash
hermes debug -n 500 | grep "Received response" | grep -oE '[0-9.]+s'
```

### Find slowest operations

```bash
hermes debug -n 1000 | grep -i "took" | sort -t ' ' -k 10 -nr | head -20
```

### Save filtered errors

```bash
hermes debug --error -n 1000 > errors-$(date +%Y%m%d).log
```

## Performance Notes

- Debug logs are significantly larger than regular logs (10-50x)
- Level filtering happens after reading lines (not at file level)
- Large line counts (>5000) may be slow
- Follow mode has minimal overhead

## Debug Log Management

### Check disk usage

```bash
du -sh ~/.hermes/debug_log
```

Debug logs can grow large (100+ MB per day with heavy usage).

### Clean old debug logs

```bash
# Delete debug logs older than 7 days
find ~/.hermes/debug_log -name "hermes-*.log" -mtime +7 -delete
```

### Compress old logs

```bash
# Compress logs older than 3 days
find ~/.hermes/debug_log -name "hermes-*.log" -mtime +3 -exec gzip {} \;
```

### Disable debug logging

Edit `~/.hermes/config.yaml`:

```yaml
logging:
  level: INFO  # Change from DEBUG
  debug_log_dir: ~/.hermes/debug_log
```

This reduces debug log verbosity but still writes to debug_log directory.

## Common Debugging Workflows

### Investigate failed task

```bash
# 1. Find the task ID
hermes history --limit 10 | grep failed

# 2. Check errors
hermes debug --error -n 500 | grep task_id=2025-0003

# 3. Check warnings
hermes debug --warning -n 500 | grep task_id=2025-0003

# 4. Full context
hermes debug -n 2000 | grep task_id=2025-0003 > task-2025-0003-debug.log
```

### Monitor live execution

```bash
# Terminal 1: Run task
hermes run --prompt "complex query"

# Terminal 2: Watch for errors
hermes debug --follow --error

# Terminal 3: Watch all activity
hermes debug --follow
```

### Analyze performance

```bash
# Extract timing information
hermes debug -n 2000 | grep -E "(took|duration|elapsed|seconds)" | less
```

## Exit Codes

- **0**: Success
- **1**: Debug service error

## Comparison with Regular Logs

| Feature | `hermes log` | `hermes debug` |
|---------|--------------|----------------|
| **Verbosity** | Low | Very high |
| **Audience** | End users | Developers |
| **Location** | `~/.hermes/log/` | `~/.hermes/debug_log/` |
| **File size** | Small (1-10 MB/day) | Large (50-500 MB/day) |
| **Stack traces** | No | Yes |
| **Performance data** | No | Yes |
| **Filtering** | By task ID | By log level |

## Troubleshooting

### No debug logs

Ensure debug logging is enabled:
```bash
cat ~/.hermes/config.yaml | grep -A 3 logging
```

Check debug log directory exists:
```bash
ls -la ~/.hermes/debug_log/
hermes init  # Recreate if missing
```

### Too much output

Use level filtering:
```bash
hermes debug --error -n 50  # Only errors
hermes debug --warning -n 100  # Warnings and above
```

### Follow mode not working

Ensure task is running:
```bash
ps aux | grep hermes
```

### Log file missing

Debug logs are created on first write. Run a task:
```bash
hermes run --prompt "test query"
hermes debug -n 20
```

## Related Commands

- [`hermes log`](./log.md) - View user-facing logs
- [`hermes history`](./history.md) - View execution results
- [`hermes run`](./run.md) - Execute tasks

## Notes

- Debug logs persist indefinitely (manual cleanup required)
- Stack traces span multiple lines (not filtered by level)
- Timestamps include microseconds for performance analysis
- Follow mode works with level filtering
- Debug logs may contain sensitive data (prompt content, API responses)
- Disable debug logging in production for performance and disk space
