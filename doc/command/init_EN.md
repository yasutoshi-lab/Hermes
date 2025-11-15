# hermes init

## Overview

Initializes the Hermes workspace by creating the data directory structure and default configuration file.

## Synopsis

```bash
hermes init
```

## Description

The `init` command sets up Hermes for first-time use by:

1. Creating the `~/.hermes/` directory structure
2. Generating a default `config.yaml` with Ollama and validation settings
3. Setting up subdirectories for history, logs, tasks, and cache

This command is **idempotent** - running it multiple times is safe and will not overwrite existing configurations.

## Directory Structure Created

```
~/.hermes/
├── cache/              # Temporary cache files
├── config.yaml         # Main configuration file
├── history/            # Report markdown files and metadata
├── task/               # Scheduled task definitions
├── log/                # Structured log files (daily rotation)
└── debug_log/          # Debug-level logs (daily rotation)
```

## Default Configuration

The generated `config.yaml` includes:

- **Ollama settings**: API endpoint (`http://localhost:11434/api/chat`), model (`gpt-oss:20b`), timeout (180s)
- **Validation loops**: min=1, max=3
- **Search sources**: min=3, max=8
- **Language**: Japanese (`ja`) by default
- **Logging**: INFO level, log directories

## Examples

### First-time initialization

```bash
hermes init
```

**Output:**
```
╭─────── Initialization Complete ───────╮
│ ✓ Hermes initialized successfully!   │
│                                       │
│ Data directory: /home/user/.hermes   │
│ Config file: /home/user/.hermes/...  │
│                                       │
│ You can now use:                      │
│ hermes run --prompt "your query"      │
╰───────────────────────────────────────╯
```

### Already initialized

```bash
hermes init
```

**Output:**
```
Hermes is already initialized.
Location: /home/user/.hermes
```

## Exit Codes

- **0**: Success
- **1**: Initialization failed (permissions, disk space, etc.)

## Notes

- The command checks for existing configuration before creating files
- If `config.yaml` exists, it will not be overwritten
- Directory creation uses `mkdir -p` semantics (no error if exists)
- All files are created with user-only permissions on Unix systems

## Related Commands

- [`hermes run --clear`](./run.md#reset-configuration) - Reset configuration to defaults
- [`hermes history`](./history.md) - View execution history
- [`hermes log`](./log.md) - View logs

## Configuration File Location

- **Linux/macOS**: `~/.hermes/config.yaml`
- **Windows**: `%USERPROFILE%\.hermes\config.yaml`

## Troubleshooting

### Permission denied

Ensure you have write access to your home directory:

```bash
ls -ld ~
mkdir -p ~/.hermes
```

### Disk space issues

Check available space:

```bash
df -h ~
```

The initialization requires minimal space (<1 MB).
