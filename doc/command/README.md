# Hermes Command Documentation

This directory contains detailed documentation for all Hermes CLI commands.

## Available Commands

| Command | Description | Documentation |
|---------|-------------|---------------|
| `hermes init` | Initialize Hermes workspace and configuration | [init.md](./init.md) |
| `hermes run` | Execute research tasks with LangGraph workflow | [run.md](./run.md) |
| `hermes task` | Manage scheduled tasks | [task.md](./task.md) |
| `hermes queue` | Process scheduled tasks sequentially | [queue.md](./queue.md) |
| `hermes history` | View and export execution history | [history.md](./history.md) |
| `hermes log` | View structured execution logs | [log.md](./log.md) |
| `hermes debug` | View detailed debug logs | [debug.md](./debug.md) |

## Quick Reference

### First-time Setup

```bash
# 1. Initialize workspace
hermes init

# 2. Start Ollama server (separate terminal)
ollama serve

# 3. Run your first task
hermes run --prompt "Your research question"
```

### Common Workflows

#### Single Task Execution

```bash
hermes run --prompt "Research topic" --language ja
hermes history --limit 1
hermes history --export 2025-0001:./report.md
```

#### Batch Processing

```bash
# Schedule multiple tasks
hermes task --prompt "Topic A"
hermes task --prompt "Topic B"
hermes task --prompt "Topic C"

# Review queue
hermes task --list

# Process all
hermes queue --all

# Check results
hermes history --limit 10
```

#### Monitoring and Troubleshooting

```bash
# Monitor active task
hermes log --follow

# Check for errors
hermes debug --error -n 100

# View specific task logs
hermes log --task-id 2025-0005 -n 200
```

## Command Relationships

```
init → run → history
       ↓      ↓
      task → queue
       ↓
      log / debug
```

1. **init**: Creates workspace (one-time setup)
2. **run**: Executes single task immediately
3. **task**: Schedules task for later
4. **queue**: Processes scheduled tasks
5. **history**: Views completed reports
6. **log**: Monitors execution progress
7. **debug**: Troubleshoots failures

## Global Options

All commands support:

- Standard output to terminal
- Piping to other commands
- Exit codes for scripting
- Rich formatting (colors, tables)

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Validation failed |

## Environment Variables

None currently supported. Configuration is via `~/.hermes/config.yaml`.

## File Locations

| Directory | Purpose | Files |
|-----------|---------|-------|
| `~/.hermes/` | Base directory | `config.yaml` |
| `~/.hermes/history/` | Reports | `report-*.md`, `report-*.meta.yaml` |
| `~/.hermes/task/` | Scheduled tasks | `task-*.yaml` |
| `~/.hermes/log/` | Execution logs | `hermes-YYYYMMDD.log` |
| `~/.hermes/debug_log/` | Debug logs | `hermes-YYYYMMDD.log` |
| `~/.hermes/cache/` | Temporary files | (various) |

## Getting Help

For command-specific help:

```bash
hermes COMMAND --help
```

For detailed documentation:

- See individual command `.md` files in this directory
- Refer to [USAGE_GUIDE.md](../../USAGE_GUIDE.md) for task-oriented workflows
- Check [ARCHITECTURE.md](../../ARCHITECTURE.md) for system internals

## Common Issues

See each command's documentation for command-specific troubleshooting.

### General Issues

1. **Ollama not running**: `ollama serve` must be active
2. **Model not found**: `ollama pull gpt-oss:20b`
3. **Permission denied**: Check `~/.hermes/` permissions
4. **Timeout errors**: Increase `ollama.timeout_sec` in config

## Shell Completion

Hermes uses Typer which supports shell completion:

```bash
# Bash
hermes --install-completion bash

# Zsh
hermes --install-completion zsh

# Fish
hermes --install-completion fish
```

## API/Programmatic Access

Commands are thin wrappers around service classes. For programmatic use:

```python
from hermes_cli.services import RunService, TaskService

# Execute task programmatically
run_service = RunService()
history_meta = run_service.run_prompt("Your prompt", options={})
```

See [DEVELOPMENT.md](../../DEVELOPMENT.md) for details.

## Changelog

Command interfaces are stable. Breaking changes will be noted in release notes.

## Contributing

To add a new command:

1. Create `hermes_cli/commands/new_cmd.py`
2. Implement command function with Typer decorators
3. Export in `hermes_cli/commands/__init__.py`
4. Register in `hermes_cli/main.py`
5. Add documentation to `doc/command/new.md`
6. Add tests to `tests/test_new_cmd.py`

See [DEVELOPMENT.md](../../DEVELOPMENT.md) for contribution guidelines.
