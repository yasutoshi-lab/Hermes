# hermes queue

## Overview

Processes scheduled tasks sequentially from the task queue until empty or limit reached.

## Synopsis

```bash
hermes queue
hermes queue --all
hermes queue -n COUNT
hermes queue --limit COUNT
```

## Description

The `queue` command executes scheduled tasks in FIFO (first-in, first-out) order. It:

1. Retrieves all tasks with `status: scheduled`
2. Sorts by creation timestamp (oldest first)
3. Executes each task using `RunService`
4. Updates task status (`running` → `completed`)
5. Generates execution summary table

This command is ideal for batch processing multiple research tasks without manual intervention.

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-n, --limit INT` | Integer | `1` | Maximum number of tasks to execute |
| `--all` | Flag | `false` | Process entire queue (overrides `--limit`) |

### Limit Behavior

- **Default** (`hermes queue`): Processes 1 task
- **Specific count** (`-n 5`): Processes up to 5 tasks
- **Unlimited** (`--all` or `-n 0`): Processes all scheduled tasks

## Examples

### Process one task (default)

```bash
hermes queue
```

**Output:**
```
Queue Execution Summary
┏━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Task ID  ┃ Status  ┃ Report               ┃ Error  ┃
┡━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ 2025-001 │ success │ report-2025-001.md   │        │
└──────────┴─────────┴──────────────────────┴────────┘

✓ Completed queue run: 1 succeeded, 0 failed.
```

### Process first 3 tasks

```bash
hermes queue -n 3
```

### Drain entire queue

```bash
hermes queue --all
```

**Output:**
```
Queue Execution Summary
┏━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Task ID  ┃ Status  ┃ Report               ┃ Error            ┃
┡━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ 2025-001 │ success │ report-2025-001.md   │                  │
│ 2025-002 │ success │ report-2025-002.md   │                  │
│ 2025-003 │ failed  │                      │ Ollama timeout   │
│ 2025-004 │ success │ report-2025-004.md   │                  │
└──────────┴─────────┴──────────────────────┴──────────────────┘

✓ Completed queue run: 3 succeeded, 1 failed.
```

### Process all with short syntax

```bash
hermes queue -n 0
```

## Execution Flow

For each task in the queue:

1. **Load task**: Read YAML from `~/.hermes/task/task-YYYY-NNNN.yaml`
2. **Update status**: Set `status: running`
3. **Execute workflow**: Call `RunService.run_task(task_id)`
4. **Save report**: Write to `~/.hermes/history/`
5. **Update metadata**: Create `HistoryMeta` with results
6. **Handle completion**: Task remains in task directory but marked completed

If execution fails, the task is marked as failed and the queue continues to the next task.

## Output Summary

The execution summary table shows:

- **Task ID**: Unique identifier (YYYY-NNNN format)
- **Status**: `success` (green) or `failed` (red)
- **Report**: Report filename (only for successful tasks)
- **Error**: Error message (only for failed tasks)

Final summary line shows total succeeded and failed counts.

## Sequential Processing

Tasks are processed **sequentially** (not in parallel):

- Each task completes before the next starts
- Total execution time = sum of individual task times
- Failed tasks do not stop queue processing
- Ollama server handles one request at a time

## Exit Codes

- **0**: Success (all processed tasks completed, even if some failed)
- **1**: Queue service error (infrastructure failure)

Note: Individual task failures result in exit code 0; check summary table for per-task status.

## Empty Queue Handling

```bash
hermes queue --all
```

**Output:**
```
No scheduled tasks to process
```

This is not an error; exit code is 0.

## Use Cases

### Overnight batch processing

```bash
# Schedule tasks during the day
hermes task --prompt "Topic 1 analysis"
hermes task --prompt "Topic 2 research"
hermes task --prompt "Topic 3 summary"
# ... (add more tasks)

# Run at night via cron
0 2 * * * cd /path/to/project && hermes queue --all >> queue.log 2>&1
```

### Rate-limited processing

```bash
# Process 3 tasks every hour to avoid rate limits
hermes queue -n 3
```

### Manual review between batches

```bash
# Process one at a time, review results
hermes queue
hermes history --limit 1
# ... review the report ...
hermes queue
# ... repeat ...
```

## Integration with Cron/Systemd

### Cron example

```cron
# Process queue daily at 2 AM
0 2 * * * /home/user/.venv/bin/hermes queue --all

# Process 5 tasks every 6 hours
0 */6 * * * /home/user/.venv/bin/hermes queue -n 5
```

### Systemd timer example

```ini
# /etc/systemd/system/hermes-queue.service
[Unit]
Description=Hermes Queue Processor
After=network.target

[Service]
Type=oneshot
User=hermes-user
WorkingDirectory=/home/hermes-user
ExecStart=/home/hermes-user/.venv/bin/hermes queue --all
```

```ini
# /etc/systemd/system/hermes-queue.timer
[Unit]
Description=Run Hermes queue daily

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

## Performance Considerations

### Execution time estimation

If each task takes ~3 minutes on average:

- 1 task: ~3 minutes
- 10 tasks: ~30 minutes
- 50 tasks: ~2.5 hours

Plan accordingly when using `--all` with large queues.

### Ollama resource usage

- Ollama processes one task at a time (no parallel execution)
- GPU/CPU usage will be high during queue processing
- Ensure sufficient system resources for unattended runs

## Troubleshooting

### No scheduled tasks found

Check task directory:
```bash
hermes task --list
ls ~/.hermes/task/
```

Create tasks first:
```bash
hermes task --prompt "Research topic"
```

### All tasks failing

Check Ollama server:
```bash
curl http://localhost:11434/api/version
ollama list
```

Review logs:
```bash
hermes log -n 100
hermes debug --error -n 50
```

### Queue processing interrupted

Resume by running queue command again:
```bash
hermes queue --all
```

Tasks marked as `running` when interrupted will be skipped; manually reset their status if needed by editing the YAML file.

### Task stuck in 'running' state

If a task was interrupted mid-execution:

```bash
# Find the task file
ls ~/.hermes/task/task-YYYY-NNNN.yaml

# Manually edit status back to 'scheduled'
# Then re-run
hermes queue
```

## Related Commands

- [`hermes task`](./task.md) - Create and manage scheduled tasks
- [`hermes run --task-id`](./run.md) - Execute single task by ID
- [`hermes history`](./history.md) - View completed task results
- [`hermes log`](./log.md) - Monitor execution logs

## Notes

- Task files remain in `~/.hermes/task/` even after completion
- Use `hermes task --delete` to remove completed tasks
- Failed tasks can be re-executed by setting status back to `scheduled`
- Queue processing respects all configuration overrides from task definitions
