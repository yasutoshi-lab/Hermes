# hermes log

## Overview

Views structured execution logs with optional task filtering and real-time streaming.

## Synopsis

```bash
hermes log
hermes log -n COUNT
hermes log --follow
hermes log --task-id TASK_ID
```

## Description

The `log` command provides access to Hermes execution logs stored in `~/.hermes/log/`. Logs are:

- **Structured**: Each line has timestamp, level, category, and message
- **Daily rotated**: New file per day (`hermes-YYYYMMDD.log`)
- **User-facing**: Focuses on task progress, not internal debugging

Use `hermes debug` for detailed developer logs.

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-n, --lines INT` | Integer | `50` | Number of log lines to display |
| `-f, --follow` | Flag | `false` | Stream logs in real-time (like `tail -f`) |
| `--task-id TEXT` | String | Latest running | Filter logs for specific task ID |

## Log Format

Each log line follows this structure:

```
YYYY-MM-DDTHH:MM:SS.mmmmmm+TZ [LEVEL] [CATEGORY] Message key=value ...
```

### Example

```
2025-11-14T14:28:30.123456+09:00 [INFO] [RUN] Starting task execution task_id=2025-0005 prompt=Quantum computing
2025-11-14T14:28:30.234567+09:00 [INFO] [RUN] Initializing LangGraph workflow
2025-11-14T14:28:45.345678+09:00 [INFO] [WEB] Collected 8 sources for query="quantum error correction"
2025-11-14T14:30:52.456789+09:00 [INFO] [RUN] Task execution completed task_id=2025-0005 sources=24
```

## Log Levels

| Level | Description |
|-------|-------------|
| **INFO** | Normal operation events (task start, completion, source collection) |
| **WARNING** | Potential issues (fallback used, retry attempted) |
| **ERROR** | Execution failures (timeout, connection refused, validation failed) |

## Log Categories

| Category | Description |
|----------|-------------|
| **RUN** | Task execution lifecycle |
| **WEB** | Web research operations |
| **OLLAMA** | LLM API interactions |
| **DOCKER** | Container operations |
| **CONFIG** | Configuration changes |

## Examples

### View last 50 lines (default)

```bash
hermes log
```

**Output:**
```
2025-11-14T14:28:30+09:00 [INFO] [RUN] Starting task execution task_id=2025-0005
2025-11-14T14:28:30+09:00 [INFO] [RUN] Initializing LangGraph workflow
2025-11-14T14:28:45+09:00 [INFO] [WEB] Collected 8 sources
2025-11-14T14:30:52+09:00 [INFO] [RUN] Task execution completed sources=24
...
```

### View last 100 lines

```bash
hermes log -n 100
```

### Follow logs in real-time

```bash
hermes log --follow
```

**Output:**
```
Following log (Ctrl+C to exit)...

2025-11-14T14:35:00+09:00 [INFO] [RUN] Starting task execution task_id=2025-0006
2025-11-14T14:35:00+09:00 [INFO] [RUN] Initializing LangGraph workflow
... (continues until Ctrl+C)
```

### Filter by task ID

```bash
hermes log --task-id 2025-0005 -n 200
```

**Output:**
```
2025-11-14T14:28:30+09:00 [INFO] [RUN] Starting task execution task_id=2025-0005
2025-11-14T14:28:30+09:00 [INFO] [RUN] Initializing LangGraph workflow
2025-11-14T14:30:52+09:00 [INFO] [RUN] Task execution completed task_id=2025-0005
```

All lines not containing `task_id=2025-0005` are filtered out.

### Monitor active task

```bash
# Automatically selects latest running task
hermes log --follow
```

**Output:**
```
Defaulting to latest running task 2025-0006
Following log (Ctrl+C to exit)...
```

## Log File Locations

Logs are stored in `~/.hermes/log/` with daily rotation:

```
~/.hermes/log/
├── hermes-20251114.log  # Today
├── hermes-20251113.log  # Yesterday
├── hermes-20251112.log
└── ...
```

## Daily Rotation

- New log file created at midnight (local time)
- Previous day's logs preserved indefinitely
- No automatic cleanup (manage manually if needed)

## Filtering Behavior

### Task ID filtering

When `--task-id` is specified:
1. Command reads specified number of lines
2. Filters to lines containing `task_id=TASK_ID`
3. Displays filtered results

If no matching lines found:
```
No log lines found for task 2025-9999
```

### Without task ID

Defaults to latest running task:
```bash
# Equivalent to:
hermes log  # Auto-selects latest running task
```

If no running tasks, shows all logs (unfiltered).

## Real-time Streaming

### Follow mode

```bash
hermes log --follow
```

- Streams new log lines as they're written
- Press `Ctrl+C` to exit
- Works with task filtering:
  ```bash
  hermes log --follow --task-id 2025-0005
  ```

### Use cases

Monitor long-running task:
```bash
hermes run --prompt "complex query" --max-validation 10 &
hermes log --follow
```

Multiple terminal windows:
```
Terminal 1: hermes queue --all
Terminal 2: hermes log --follow
```

## Combining with Standard Tools

### Grep for errors

```bash
hermes log -n 500 | grep ERROR
```

### Count web sources

```bash
hermes log -n 200 | grep "Collected.*sources" | wc -l
```

### Extract task IDs

```bash
hermes log -n 100 | grep -oE 'task_id=[0-9]{4}-[0-9]{4}' | sort -u
```

### Save to file

```bash
hermes log -n 1000 > analysis.log
```

## Performance Notes

- Reading logs is fast (<100ms for 1000 lines)
- Follow mode has minimal overhead
- Task ID filtering scans all specified lines
- Large line counts (>10000) may be slow

## Exit Codes

- **0**: Success
- **1**: Log service error

## Multi-day Tasks

Tasks running across midnight span multiple log files:

```bash
# Task started Nov 13 at 23:50, finished Nov 14 at 00:10

# Check both days
hermes log --task-id 2025-0005 -n 1000  # Might only show Nov 14 portion

# Manual approach
cat ~/.hermes/log/hermes-20251113.log | grep task_id=2025-0005
cat ~/.hermes/log/hermes-20251114.log | grep task_id=2025-0005
```

## Log Cleanup

Logs are never automatically deleted. To manage disk space:

### Delete old logs

```bash
# Remove logs older than 30 days
find ~/.hermes/log -name "hermes-*.log" -mtime +30 -delete
```

### Archive old logs

```bash
# Compress logs older than 7 days
find ~/.hermes/log -name "hermes-*.log" -mtime +7 -exec gzip {} \;
```

### Check disk usage

```bash
du -sh ~/.hermes/log
ls -lh ~/.hermes/log/*.log
```

## Troubleshooting

### No logs displayed

Check log directory:
```bash
ls -la ~/.hermes/log/
hermes init  # Recreate if missing
```

### Follow mode not updating

Ensure task is actually running:
```bash
ps aux | grep hermes
hermes task --list
```

### Task ID filter returns nothing

Verify task ID format:
```bash
hermes history  # Check correct task ID
hermes log --task-id 2025-0005  # Use correct format
```

### Log file too large

Rotate manually:
```bash
mv ~/.hermes/log/hermes-$(date +%Y%m%d).log{,.bak}
```

## Comparison with Debug Logs

| Feature | `hermes log` | `hermes debug` |
|---------|--------------|----------------|
| **Purpose** | User-facing task progress | Developer debugging |
| **Verbosity** | Low (INFO+) | High (DEBUG+) |
| **Location** | `~/.hermes/log/` | `~/.hermes/debug_log/` |
| **Filtering** | By task ID | By log level |
| **Typical use** | Monitor execution | Troubleshoot failures |

Use `hermes log` for normal monitoring, `hermes debug` for investigation.

## Related Commands

- [`hermes debug`](./debug.md) - View detailed debug logs
- [`hermes history`](./history.md) - View execution results
- [`hermes run`](./run.md) - Execute tasks

## Notes

- Log entries are written immediately (no buffering)
- Structured format enables easy parsing
- Timestamps include timezone offset
- Task ID format is always `YYYY-NNNN`
- Follow mode works with pipes: `hermes log -f | grep ERROR`
