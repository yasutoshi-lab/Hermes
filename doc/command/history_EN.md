# hermes history

## Overview

Lists, exports, and manages execution history and generated reports.

## Synopsis

```bash
hermes history
hermes history --limit COUNT
hermes history --export TASK_ID:PATH
hermes history --delete TASK_ID
```

## Description

The `history` command provides access to completed research task results. Each execution generates:

- **Report file**: Markdown document with research findings (`report-YYYY-NNNN.md`)
- **Metadata file**: YAML with execution details (`report-YYYY-NNNN.meta.yaml`)

History entries persist indefinitely until explicitly deleted.

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--limit INT` | Integer | `100` | Maximum number of history entries to display |
| `--export TEXT` | String | None | Export report in format `TASK_ID:PATH` |
| `--delete TEXT` | String | None | Delete history entry by task ID |
| `--deleate TEXT` | String | None | Delete history by ID (typo alias) |

## Examples

### List recent history (default 100 entries)

```bash
hermes history
```

**Output:**
```
Execution History (last 5)
┏━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━┓
┃ Task ID ┃ Status  ┃ Created        ┃ Finished     ┃ Model    ┃ Loops ┃ Sources ┃ Error ┃
┡━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━┩
│ 2025-05 │ success │ 2025-11-14 ... │ 14:30 (142s) │ gpt-o... │     2 │      24 │       │
│ 2025-04 │ success │ 2025-11-14 ... │ 14:15 (98s)  │ gpt-o... │     1 │      18 │       │
│ 2025-03 │ failed  │ 2025-11-14 ... │ 13:50 (5s)   │ gpt-o... │     0 │       0 │ Time… │
│ 2025-02 │ success │ 2025-11-14 ... │ 13:30 (215s) │ gpt-o... │     3 │      36 │       │
│ 2025-01 │ success │ 2025-11-14 ... │ 10:15 (87s)  │ gpt-o... │     1 │      12 │       │
└─────────┴─────────┴────────────────┴──────────────┴──────────┴───────┴─────────┴───────┘
```

### List last 10 entries

```bash
hermes history --limit 10
```

### Export specific report

```bash
hermes history --export 2025-0005:./quantum-report.md
```

**Output:**
```
✓ Report exported to ./quantum-report.md
```

### Export with relative path

```bash
hermes history --export 2025-0003:../reports/ai-safety.md
```

### Delete history entry

```bash
hermes history --delete 2025-0001
```

**Output:**
```
✓ History 2025-0001 deleted
```

This removes both the report and metadata files.

## History Table Columns

| Column | Description |
|--------|-------------|
| **Task ID** | Unique identifier (YYYY-NNNN format) |
| **Status** | `success` (green) or `failed` (red) |
| **Created** | Execution start timestamp |
| **Finished** | Completion time and duration |
| **Model** | Ollama model used (truncated) |
| **Loops** | Number of validation loops executed |
| **Sources** | Total web sources collected |
| **Error** | Error message (truncated, only for failed) |

## Metadata File Format

Each history entry has a metadata file:

```yaml
# ~/.hermes/history/report-2025-0005.meta.yaml
id: 2025-0005
prompt: "Explain quantum computing error correction"
created_at: "2025-11-14T14:28:30+09:00"
finished_at: "2025-11-14T14:30:52+09:00"
model: gpt-oss:20b
language: ja
validation_loops: 2
source_count: 24
report_file: report-2025-0005.md
status: success
error_message: null
```

## Report File Format

Reports are structured Markdown:

```markdown
---
query: <original prompt>
language: ja
queries_generated: 3
queries_executed: 6
sources_collected: 24
validation_loops: 2
quality_score: 0.85
---

# <Report Title>

## Executive Summary
...

## Key Findings
...

## Supporting Details
...

## Recommended Next Steps
...
```

## Export Behavior

### Success case

```bash
hermes history --export 2025-0001:./report.md
```

- Report file is copied to specified path
- Existing file at destination is overwritten
- Parent directories are created if needed

### Failure cases

```bash
# Task not found
hermes history --export 2025-9999:./report.md
# Output: ✗ History 2025-9999 not found

# Task failed (no report generated)
hermes history --export 2025-0003:./report.md
# Output: ✗ History 2025-0003 failed; no report to export
# Reason: Ollama timeout
```

### Invalid format

```bash
# Missing colon separator
hermes history --export 2025-0001 ./report.md
# Output: ✗ Export format must be TASK_ID:PATH (e.g., 2025-0001:./report.md)
```

## File Locations

History files are stored in `~/.hermes/history/`:

```
~/.hermes/history/
├── report-2025-0001.md         # Report markdown
├── report-2025-0001.meta.yaml  # Metadata
├── report-2025-0002.md
├── report-2025-0002.meta.yaml
└── ...
```

## Filtering and Sorting

### By status

Failed tasks show in red with error messages:

```bash
hermes history | grep -E "failed|✗"
```

### By date

History is sorted by creation time (newest first):

```bash
# Oldest entries
hermes history --limit 1000 | tail -20
```

### By model

```bash
hermes history | grep "llama"
```

## Exit Codes

- **0**: Success
- **1**: Operation failed (export/delete)
- **2**: Invalid arguments

## Use Cases

### Generate summary report

```bash
# Export all recent reports
for id in $(hermes history --limit 10 | grep -oE '2025-[0-9]{4}'); do
  hermes history --export "$id:reports/$id.md"
done
```

### Cleanup old history

```bash
# Delete all failed tasks
for id in $(hermes history | grep failed | grep -oE '2025-[0-9]{4}'); do
  hermes history --delete "$id"
done
```

### Archive successful reports

```bash
# Copy reports to archive directory
mkdir -p archive/$(date +%Y-%m)
for id in $(hermes history --limit 30 | grep success | grep -oE '2025-[0-9]{4}'); do
  cp ~/.hermes/history/report-$id.md archive/$(date +%Y-%m)/
done
```

## Performance Notes

- Listing history scans all metadata files in `~/.hermes/history/`
- With thousands of entries, consider using `--limit` to reduce load time
- Export is a simple file copy operation (fast)
- Delete removes both `.md` and `.meta.yaml` files atomically

## Troubleshooting

### No history found

Ensure tasks have been executed:
```bash
hermes run --prompt "test query"
hermes history
```

### Export path error

Check parent directory exists:
```bash
mkdir -p reports/
hermes history --export 2025-0001:reports/test.md
```

### Corrupted metadata

If metadata is corrupted, manually inspect:
```bash
cat ~/.hermes/history/report-2025-0001.meta.yaml
```

Re-run the task if recovery is not possible.

### Permission denied on export

Ensure write permission:
```bash
touch ./test.md
hermes history --export 2025-0001:./test.md
```

## Related Commands

- [`hermes run`](./run.md) - Generate new reports
- [`hermes task`](./task.md) - Schedule tasks for execution
- [`hermes queue`](./queue.md) - Process multiple tasks
- [`hermes log`](./log.md) - View execution logs

## Notes

- History persists across Hermes reinstalls (stored in `~/.hermes/`)
- Deleting history does not affect task definitions
- Failed tasks still create metadata files (for auditing)
- The `--deleate` typo alias is provided for backwards compatibility
- Export does not modify the original report file
