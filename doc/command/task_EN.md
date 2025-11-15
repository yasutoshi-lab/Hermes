# hermes task

## Overview

Manages scheduled tasks that can be executed later via `hermes run` or `hermes queue`.

## Synopsis

```bash
hermes task --prompt "research question"
hermes task --list
hermes task --delete TASK_ID
```

## Description

The `task` command provides task scheduling functionality by saving prompts and metadata to YAML files in `~/.hermes/task/`. Tasks are not executed immediately; use `hermes run --task-id` or `hermes queue` to process them.

This is useful for:
- Batch processing multiple research topics
- Scheduling tasks to run during off-peak hours
- Saving interesting prompts for later investigation
- Building a backlog of research questions

## Options

| Option | Type | Description |
|--------|------|-------------|
| `--prompt TEXT` | String | Create a new task with the specified prompt |
| `--list` | Flag | Display all scheduled tasks |
| `--delete TEXT` | String | Delete task by ID |
| `--deleate TEXT` | String | Delete task by ID (typo alias for backwards compatibility) |

## Task Lifecycle

Tasks have three states:

1. **scheduled** - Created but not executed
2. **running** - Currently being processed (set by `RunService`)
3. **completed** - Finished execution (archived in history)

The `task` command only manages tasks in the **scheduled** state.

## Examples

### Create a new task

```bash
hermes task --prompt "Analyze the impact of quantum computing on cryptography"
```

**Output:**
```
✓ Task created: 2025-0010
Prompt: Analyze the impact of quantum computing on cryptography
Status: scheduled

Execute with: hermes run --task-id 2025-0010
```

### List all scheduled tasks

```bash
hermes task --list
```

**Output:**
```
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Task ID  ┃ Created         ┃ Status    ┃ Prompt                      ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2025-001 │ 2025-11-14 1... │ scheduled │ Quantum computing analysis  │
│ 2025-002 │ 2025-11-14 1... │ scheduled │ AI safety research summary  │
│ 2025-003 │ 2025-11-14 1... │ running   │ Climate change solutions    │
└──────────┴─────────────────┴───────────┴─────────────────────────────┘
```

### Delete a task

```bash
hermes task --delete 2025-0001
```

**Output:**
```
✓ Task 2025-0001 deleted
```

### Delete using typo alias

```bash
hermes task --deleate 2025-0002
```

**Output:**
```
✓ Task 2025-0002 deleted
```

## Task File Format

Tasks are stored as YAML files in `~/.hermes/task/`:

```yaml
# task-2025-0001.yaml
id: 2025-0001
prompt: "Explain quantum error correction methods"
created_at: "2025-11-14T10:30:00+09:00"
status: scheduled
language: ja
config_overrides: {}
```

## Executing Scheduled Tasks

### Execute single task

```bash
hermes run --task-id 2025-0001
```

### Execute all scheduled tasks

```bash
hermes queue --all
```

### Execute first N tasks

```bash
hermes queue -n 5
```

## Exit Codes

- **0**: Success
- **1**: Task not found (for delete operations)
- **2**: Invalid arguments

## Notes

- Task IDs are auto-generated in format `YYYY-NNNN` (e.g., `2025-0042`)
- Tasks persist across Hermes restarts
- Deleting a task does not affect its execution history if already run
- The `--deleate` option exists to handle common typos (both spellings work)
- Running tasks show as "running" in the list but remain in the task directory until completed

## Workflow Integration

### Typical workflow

```bash
# 1. Create several tasks
hermes task --prompt "Topic A research"
hermes task --prompt "Topic B analysis"
hermes task --prompt "Topic C summary"

# 2. Review the queue
hermes task --list

# 3. Execute all at once
hermes queue --all

# 4. Check results
hermes history --limit 10
```

## Related Commands

- [`hermes run --task-id`](./run.md) - Execute a single scheduled task
- [`hermes queue`](./queue.md) - Process multiple tasks sequentially
- [`hermes history`](./history.md) - View completed task results

## File Locations

- **Task files**: `~/.hermes/task/task-YYYY-NNNN.yaml`
- **Config**: `~/.hermes/config.yaml` (default settings for new tasks)

## Troubleshooting

### Task not found when listing

Ensure Hermes is initialized:
```bash
hermes init
ls ~/.hermes/task/
```

### Cannot delete task

Check if task ID exists:
```bash
hermes task --list
# Use exact ID from the list
```

### Task creation fails

Verify disk space and permissions:
```bash
df -h ~/.hermes
ls -ld ~/.hermes/task
```
