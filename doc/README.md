# Hermes Documentation

This directory contains detailed documentation for the Hermes CLI research agent.

## Documentation Structure

```
doc/
├── command/           # Command-line interface documentation
│   ├── README.md     # Command overview and quick reference
│   ├── init.md       # hermes init command
│   ├── run.md        # hermes run command
│   ├── task.md       # hermes task command
│   ├── queue.md      # hermes queue command
│   ├── history.md    # hermes history command
│   ├── log.md        # hermes log command
│   └── debug.md      # hermes debug command
│
├── dependencies/      # External dependencies documentation
│   ├── README.md     # Dependencies overview and setup guide
│   ├── ollama.md     # Ollama LLM server setup
│   ├── browser-use.md # Browser automation setup
│   └── container-use.md # Docker integration setup
│
└── test/             # Test suite documentation
    └── README.md     # Test overview, requirements, and guides
```

## Quick Navigation

### For Users

- **Getting Started**: See [README.md](../README.md) in project root
- **Installation**: [README.md](../README.md#installation)
- **Quick Start**: [README.md](../README.md#quick-start)
- **Commands**: [command/README.md](./command/README.md)
- **Dependencies Setup**: [dependencies/README.md](./dependencies/README.md)
- **Usage Examples**: [USAGE_GUIDE.md](../USAGE_GUIDE.md)
- **Integration Setup**: [README.md](../README.md#integration-setup)

### For Developers

- **Architecture**: [ARCHITECTURE.md](../ARCHITECTURE.md)
- **Development Guide**: [DEVELOPMENT.md](../DEVELOPMENT.md)
- **Test Documentation**: [test/README.md](./test/README.md)
- **Claude Code Guide**: [CLAUDE.md](../CLAUDE.md)

## Documentation by Task

### First-time Setup

1. [Installation](../README.md#installation) - Install Hermes and dependencies
2. [Dependencies Setup](./dependencies/README.md) - Configure Ollama, Docker, and browser-use
   - [Ollama Setup](./dependencies/ollama.md) - Required LLM server
   - [Docker Setup](./dependencies/container-use.md) - Optional container isolation
   - [browser-use Setup](./dependencies/browser-use.md) - Optional enhanced web search
3. [hermes init](./command/init.md) - Initialize workspace
4. [Quick Start](../README.md#quick-start) - Run your first task

### Running Research Tasks

- [hermes run](./command/run.md) - Execute single task
- [hermes task](./command/task.md) - Schedule tasks for later
- [hermes queue](./command/queue.md) - Process scheduled tasks in batch
- [hermes history](./command/history.md) - View and export results

### Monitoring and Debugging

- [hermes log](./command/log.md) - Monitor execution progress
- [hermes debug](./command/debug.md) - Troubleshoot failures
- [Troubleshooting](../README.md#troubleshooting-highlights) - Common issues

### Development and Testing

- [Development Guide](../DEVELOPMENT.md) - Set up dev environment
- [Test Documentation](./test/README.md) - Run and write tests
- [Architecture Overview](../ARCHITECTURE.md) - Understand system design

## Command Reference

All commands support `--help` for inline documentation:

```bash
hermes --help
hermes run --help
hermes task --help
```

| Command | Purpose | Documentation |
|---------|---------|---------------|
| `hermes init` | Initialize workspace | [init.md](./command/init.md) |
| `hermes run` | Execute research task | [run.md](./command/run.md) |
| `hermes task` | Manage scheduled tasks | [task.md](./command/task.md) |
| `hermes queue` | Process task queue | [queue.md](./command/queue.md) |
| `hermes history` | View execution history | [history.md](./command/history.md) |
| `hermes log` | View execution logs | [log.md](./command/log.md) |
| `hermes debug` | View debug logs | [debug.md](./command/debug.md) |

## Key Concepts

### Task Lifecycle

```
Create → Schedule → Execute → Validate → Complete
  ↓                    ↓          ↓          ↓
task.yaml         running     looping    history/
```

1. **Create**: `hermes task --prompt "..."`
2. **Schedule**: Task stored as `task-YYYY-NNNN.yaml`
3. **Execute**: `hermes queue` or `hermes run --task-id`
4. **Validate**: Configurable validation loops (1-N)
5. **Complete**: Report saved to `history/`

### Data Flow

```
Prompt → Query Generation → Web Research → Processing → Draft → Validation → Report
         (Ollama)            (DuckDuckGo)   (Docker)    (Ollama)  (Loop)    (Output)
```

See [ARCHITECTURE.md](../ARCHITECTURE.md) for detailed flow.

### File Organization

```
~/.hermes/
├── config.yaml          # Configuration
├── history/             # Generated reports
│   ├── report-*.md
│   └── report-*.meta.yaml
├── task/                # Scheduled tasks
│   └── task-*.yaml
├── log/                 # Execution logs
│   └── hermes-YYYYMMDD.log
└── debug_log/           # Debug logs
    └── hermes-YYYYMMDD.log
```

## Configuration

### Main Config File

Location: `~/.hermes/config.yaml`

Key settings:

```yaml
ollama:
  api_base: http://localhost:11434/api/chat
  model: gpt-oss:20b
  retry: 3
  timeout_sec: 180

language: ja  # or "en"

validation:
  min_loops: 1
  max_loops: 3

search:
  min_sources: 3
  max_sources: 8
```

### Runtime Overrides

All config values can be overridden via CLI flags:

```bash
hermes run --prompt "..." \
  --model llama2:70b \
  --language en \
  --max-validation 5 \
  --max-search 12
```

See [hermes run](./command/run.md#options) for all options.

## Common Workflows

### Single Task Research

```bash
hermes run --prompt "Your research question"
hermes history --limit 1
hermes history --export 2025-0001:./report.md
```

### Batch Processing

```bash
# Schedule tasks
hermes task --prompt "Topic A"
hermes task --prompt "Topic B"
hermes task --prompt "Topic C"

# Process queue
hermes queue --all

# Review results
hermes history --limit 10
```

### Monitoring Long Tasks

```bash
# Terminal 1: Execute task
hermes run --prompt "Complex research" --max-validation 5

# Terminal 2: Follow logs
hermes log --follow

# Terminal 3: Watch for errors
hermes debug --follow --error
```

### Troubleshooting Failed Task

```bash
# Find failed task
hermes history | grep failed

# Check error logs
hermes debug --error -n 200 | grep task_id=2025-0003

# View full logs
hermes log --task-id 2025-0003 -n 500
```

## External Dependencies

### Required

- **Python 3.10+**: Runtime environment
- **Ollama**: LLM inference (`ollama serve`)
- **Model**: `gpt-oss:20b` or similar (`ollama pull gpt-oss:20b`)

### Optional

- **Docker 20.10+**: Container isolation for text processing
- **browser-use**: Advanced web automation (install from source)

See [README.md](../README.md#integration-setup) for setup instructions.

## Support and Resources

### Documentation Files

- **README.md**: Project overview and installation
- **USAGE_GUIDE.md**: Task-oriented walkthroughs
- **DEVELOPMENT.md**: Development environment setup
- **ARCHITECTURE.md**: System design and data flow
- **CLAUDE.md**: Guide for Claude Code (AI assistant)
- **doc/command/**: Detailed command documentation
- **doc/test/**: Test suite documentation

### Getting Help

1. **Command help**: `hermes COMMAND --help`
2. **Troubleshooting**: [README.md](../README.md#troubleshooting-highlights)
3. **Issues**: [GitHub Issues](https://github.com/your-org/Hermes/issues)
4. **Logs**: `hermes log` and `hermes debug`

### Contributing

See [DEVELOPMENT.md](../DEVELOPMENT.md) for:

- Setting up development environment
- Running tests
- Code style guidelines
- Submitting pull requests

## Version History

Documentation corresponds to Hermes CLI version 1.0.0.

For changelog and version history, see project root.

## License

MIT License - See project root for details.

---

**Navigation**: [↑ Documentation Root](#hermes-documentation) | [→ Commands](./command/README.md) | [→ Tests](./test/README.md)
