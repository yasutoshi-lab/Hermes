# Task: System Documentation Creation

**Task ID**: phase4_documentation
**Priority**: medium
**Assigned to**: worker-2
**Dependencies**: All Phase 3 tasks completed

## Objective
Create comprehensive documentation for the Hermes system including README, usage guide, architecture documentation, and development guide.

## Context
Documentation helps users understand how to install, configure, and use Hermes, and helps future developers understand the system architecture and contribute to the project.

Reference design document: `/home/ubuntu/python_project/Hermes/詳細設計書.md` (all sections)

## Requirements

### 1. Create `README.md`

Main project README with:

```markdown
# Hermes CLI

Hermes is a powerful CLI-based information gathering agent that leverages local LLMs, browser automation, and containerized processing to conduct comprehensive research and generate detailed reports.

## Features

- 🤖 **LLM-Powered Research**: Uses local Ollama models for intelligent query generation and report creation
- 🌐 **Automated Web Research**: Browser automation for gathering information from multiple sources
- 🔄 **Validation Loops**: Iterative refinement of reports through configurable validation cycles
- 📦 **Containerized Processing**: Secure and reproducible text processing in isolated environments
- 📊 **History Management**: Track and export all research executions
- 🎨 **Beautiful CLI**: Rich terminal UI with progress indicators and formatted output

## Prerequisites

- Python 3.10 or higher
- Ollama with `gpt-oss:20b` model installed
- Docker (for container-use features)

## Installation

### Using pip

```bash
pip install -e .
```

### Using uv (recommended)

```bash
uv pip install -e .
```

## Quick Start

### 1. Initialize Hermes

```bash
hermes init
```

This creates `~/.hermes/` with configuration and data directories.

### 2. Run Your First Research Task

```bash
hermes run --prompt "Explain quantum computing error correction methods"
```

### 3. View Results

```bash
hermes history
```

Reports are saved in `~/.hermes/history/`.

## Usage

### Basic Research

```bash
# Single-shot research
hermes run --prompt "Your research question"

# With options
hermes run --prompt "AI trends 2024" --language en --max-validation 5
```

### Task Scheduling

```bash
# Create scheduled task
hermes task --prompt "Research topic"

# List tasks
hermes task --list

# Delete task
hermes task --delete 2025-0001
```

### History Management

```bash
# List execution history
hermes history

# Export specific report
hermes history --export 2025-0001:/path/to/report.md
```

### Logs and Debugging

```bash
# View recent logs
hermes log

# Follow logs in real-time
hermes log --follow

# Debug mode with error filtering
hermes debug --error
```

## Configuration

Edit `~/.hermes/config.yaml`:

```yaml
ollama:
  api_base: "http://localhost:11434/api/chat"
  model: "gpt-oss:20b"
  retry: 3
  timeout_sec: 60

language: "ja"  # or "en"

validation:
  min_loops: 1
  max_loops: 3

search:
  min_sources: 3
  max_sources: 8
```

## Architecture

```
hermes_cli/
├── commands/      # CLI command implementations
├── services/      # Business logic layer
├── agents/        # LangGraph workflow and nodes
├── tools/         # External tool integrations
└── persistence/   # Data storage layer
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design.

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for contribution guidelines.

## License

[Your License]

## Credits

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - Workflow orchestration
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [Ollama](https://ollama.ai/) - Local LLM runtime
```

### 2. Create `ARCHITECTURE.md`

Detailed architecture documentation:

```markdown
# Hermes Architecture

## Overview

Hermes follows a layered architecture with clear separation of concerns.

## Layer Architecture

```
┌─────────────────────────────────────┐
│         CLI Layer (Typer)           │  User Interface
├─────────────────────────────────────┤
│       Services Layer (Business)     │  Business Logic
├─────────────────────────────────────┤
│    Agents Layer (LangGraph)         │  Workflow Engine
├─────────────────────────────────────┤
│     Tools Layer (Integrations)      │  External Services
├─────────────────────────────────────┤
│   Persistence Layer (Data Storage)  │  Data Management
└─────────────────────────────────────┘
```

## Component Details

### CLI Layer (`commands/`)

Entry point for user interaction. Each command module handles:
- Argument parsing with Typer
- Input validation
- Service invocation
- Output formatting with Rich

**Commands**:
- `init_cmd.py` - Initialize Hermes environment
- `task_cmd.py` - Task management (create, list, delete)
- `run_cmd.py` - Execute research tasks
- `log_cmd.py` - View execution logs
- `history_cmd.py` - Manage research history
- `debug_cmd.py` - Debug log viewing

### Services Layer (`services/`)

Business logic orchestration:

- **ConfigService**: Configuration management, override application
- **TaskService**: Task lifecycle (CRUD operations)
- **RunService**: Workflow execution orchestration
- **HistoryService**: Report and metadata management
- **LogService**: Log viewing and streaming
- **DebugService**: Filtered log viewing

### Agents Layer (`agents/`)

LangGraph-based workflow implementation:

**State Management** (`state.py`):
- Pydantic-based state model
- Type-safe field definitions
- Progress tracking

**Workflow Graph** (`graph.py`):
- Node orchestration
- Conditional routing
- Validation loop control

**Nodes** (`nodes/`):
1. **PromptNormalizer**: Input preprocessing
2. **QueryGenerator**: LLM-based query generation
3. **WebResearcher**: Browser automation for research
4. **ContainerProcessor**: Containerized text processing
5. **DraftAggregator**: Report generation from research
6. **ValidationController**: Loop control logic
7. **Validator**: Report validation and improvement
8. **FinalReporter**: Report finalization with metadata

### Tools Layer (`tools/`)

External service integrations:

- **OllamaClient**: LLM API with retry logic
- **BrowserUseClient**: Web automation wrapper
- **ContainerUseClient**: Container execution wrapper

### Persistence Layer (`persistence/`)

Data storage and retrieval:

- **FilePaths**: Cross-platform path management
- **ConfigRepository**: YAML configuration I/O
- **TaskRepository**: Task CRUD operations
- **HistoryRepository**: Report and metadata storage
- **LogRepository**: Structured logging

## Data Flow

```
User Command
    ↓
CLI Command
    ↓
Service Layer
    ↓
Agent Workflow (LangGraph)
    ↓
Tools (LLM, Browser, Container)
    ↓
Persistence Layer
    ↓
Storage (~/.hermes/)
```

## Workflow Execution Flow

```
1. User: hermes run --prompt "query"
2. RunCommand: Parse arguments
3. RunService: Load config, create state
4. LangGraph: Execute workflow nodes
   a. Normalize prompt
   b. Generate queries (LLM)
   c. Research queries (Browser)
   d. Process results (Container)
   e. Create draft (LLM)
   f. Validate (loop if needed)
   g. Finalize report
5. HistoryRepository: Save report + metadata
6. CLI: Display results to user
```

## Error Handling Strategy

- **CLI Layer**: User-friendly error messages, exit codes
- **Services Layer**: Graceful degradation, logging
- **Agents Layer**: Per-node error handling, partial results
- **Tools Layer**: Retry logic, fallbacks
- **Persistence Layer**: File operation safety

## Configuration Management

Configuration flows through layers:
1. Load from `~/.hermes/config.yaml`
2. Apply CLI option overrides
3. Pass to services and agents
4. Use in tool clients

## Extensibility Points

- **New Commands**: Add to `commands/`, register in `main.py`
- **New Services**: Add to `services/`, use existing repositories
- **New Nodes**: Add to `agents/nodes/`, update graph
- **New Tools**: Add to `tools/`, integrate in nodes
- **New Storage**: Add to `persistence/`

## Design Principles

1. **Separation of Concerns**: Each layer has clear responsibilities
2. **Dependency Injection**: Services receive dependencies
3. **Type Safety**: Comprehensive type hints throughout
4. **Error Resilience**: Graceful handling at all layers
5. **Testability**: Modular design for unit testing
```

### 3. Create `DEVELOPMENT.md`

Developer guide:

```markdown
# Hermes Development Guide

## Setup Development Environment

### 1. Clone Repository

```bash
git clone <repository-url>
cd Hermes
```

### 2. Install Dependencies

```bash
# Using pip
pip install -e .

# Using uv (recommended)
uv pip install -e .
```

### 3. Install Development Dependencies

```bash
pip install pytest black ruff mypy
```

## Project Structure

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture.

```
Hermes/
├── hermes_cli/           # Main package
│   ├── commands/         # CLI commands
│   ├── services/         # Business logic
│   ├── agents/           # LangGraph workflow
│   ├── tools/            # External integrations
│   └── persistence/      # Data layer
├── tests/                # Test suite
├── pyproject.toml        # Project metadata
└── requirements.txt      # Dependencies
```

## Development Workflow

### 1. Code Style

Use Black for formatting:
```bash
black hermes_cli/
```

Use Ruff for linting:
```bash
ruff check hermes_cli/
```

### 2. Type Checking

Run mypy:
```bash
mypy hermes_cli/
```

### 3. Testing

Run pytest:
```bash
pytest tests/
```

## Adding New Features

### Adding a New CLI Command

1. Create `hermes_cli/commands/newcmd_cmd.py`:
```python
import typer
from rich.console import Console

console = Console()

def newcmd_command(
    option: str = typer.Option(..., "--option", help="Description"),
):
    \"\"\"Command description.\"\"\"
    # Implementation
    pass
```

2. Export in `hermes_cli/commands/__init__.py`:
```python
from .newcmd_cmd import newcmd_command

__all__ = [..., "newcmd_command"]
```

3. Register in `hermes_cli/main.py`:
```python
from hermes_cli.commands import newcmd_command

app.command("newcmd")(newcmd_command)
```

### Adding a New Service

1. Create `hermes_cli/services/new_service.py`:
```python
from typing import Optional
import logging
from hermes_cli.persistence.file_paths import FilePaths

class NewService:
    def __init__(self, file_paths: Optional[FilePaths] = None):
        self.file_paths = file_paths or FilePaths()
        self.logger = logging.getLogger(__name__)

    def operation(self):
        # Implementation
        pass
```

2. Export in `hermes_cli/services/__init__.py`

### Adding a New Agent Node

1. Create `hermes_cli/agents/nodes/new_node.py`:
```python
from hermes_cli.agents.state import HermesState
import logging

logger = logging.getLogger(__name__)

def new_node(state: HermesState) -> HermesState:
    \"\"\"Node description.\"\"\"
    logger.info("Node started")
    # Implementation
    return state
```

2. Export in `hermes_cli/agents/nodes/__init__.py`

3. Add to workflow in `hermes_cli/agents/graph.py`

## Testing Guidelines

### Unit Tests

Test individual components:
```python
# tests/test_config_service.py
from hermes_cli.services import ConfigService

def test_config_load():
    service = ConfigService()
    config = service.load()
    assert config.ollama.model == "gpt-oss:20b"
```

### Integration Tests

Test component interactions:
```python
# tests/test_workflow.py
from hermes_cli.agents import create_hermes_workflow, HermesState

def test_workflow_creation():
    workflow = create_hermes_workflow()
    assert workflow is not None
```

## Code Guidelines

1. **Type Hints**: Always use type hints
2. **Docstrings**: Google-style docstrings for all public functions
3. **Error Handling**: Use try-except with specific exceptions
4. **Logging**: Use logging module, not print
5. **Testing**: Write tests for new features

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### View Debug Logs

```bash
hermes debug --all
```

### Test Individual Components

```python
# Test script
from hermes_cli.services import ConfigService

service = ConfigService()
config = service.load()
print(config)
```

## Release Process

1. Update version in `hermes_cli/__init__.py`
2. Update `pyproject.toml`
3. Run tests: `pytest`
4. Run linters: `black .` and `ruff check`
5. Build: `python -m build`
6. Tag release: `git tag v1.0.0`
```

### 4. Create `USAGE_GUIDE.md`

Comprehensive usage examples:

```markdown
# Hermes Usage Guide

## Installation

See [README.md](README.md#installation) for installation instructions.

## Configuration

### Initial Setup

```bash
hermes init
```

This creates:
- `~/.hermes/config.yaml` - Configuration file
- `~/.hermes/cache/` - Temporary cache
- `~/.hermes/task/` - Scheduled tasks
- `~/.hermes/log/` - Execution logs
- `~/.hermes/debug_log/` - Debug logs
- `~/.hermes/history/` - Research reports

### Configuring Ollama

Edit `~/.hermes/config.yaml`:

```yaml
ollama:
  api_base: "http://localhost:11434/api/chat"
  model: "gpt-oss:20b"
  retry: 3
  timeout_sec: 60
```

## Basic Usage

### Simple Research

```bash
hermes run --prompt "What are the latest developments in quantum computing?"
```

### Research with Options

```bash
# English output
hermes run --prompt "AI trends" --language en

# More validation loops
hermes run --prompt "Complex topic" --max-validation 5

# More sources
hermes run --prompt "Research topic" --max-search 10
```

### Viewing Results

```bash
# List all research history
hermes history

# Export specific report
hermes history --export 2025-0001:./my-report.md

# Export latest report
hermes run --export ./report.md
```

## Advanced Usage

### Task Scheduling

```bash
# Create task for later execution
hermes task --prompt "Regular monitoring topic"

# List scheduled tasks
hermes task --list

# Execute scheduled task (future feature)
hermes run --task-id 2025-0001
```

### Custom Configuration

```bash
# Use different Ollama endpoint
hermes run --prompt "query" --api http://remote:11434/api/chat

# Use different model
hermes run --prompt "query" --model llama2:70b

# Override validation settings
hermes run --prompt "query" --min-validation 2 --max-validation 4
```

### Log Monitoring

```bash
# View recent logs
hermes log

# View more lines
hermes log -n 100

# Follow logs in real-time
hermes log --follow

# Debug mode
hermes debug --error
```

## Common Workflows

### Research Workflow

1. Initialize Hermes: `hermes init`
2. Run research: `hermes run --prompt "your topic"`
3. View progress: `hermes log --follow` (in another terminal)
4. Check results: `hermes history`
5. Export report: `hermes history --export TASK_ID:./report.md`

### Batch Research

```bash
# Create multiple tasks
hermes task --prompt "Topic 1"
hermes task --prompt "Topic 2"
hermes task --prompt "Topic 3"

# List tasks
hermes task --list

# Execute each (manual for now)
hermes run --prompt "Topic 1"
# ... repeat
```

## Troubleshooting

### Ollama Not Running

```bash
Error: Connection refused to Ollama

Solution: Start Ollama
ollama serve
```

### Model Not Found

```bash
Error: Model gpt-oss:20b not found

Solution: Pull model
ollama pull gpt-oss:20b
```

### Logs

View detailed logs:
```bash
hermes debug --all
```

Check log files:
```bash
tail -f ~/.hermes/log/hermes-$(date +%Y%m%d).log
```

## Tips and Best Practices

1. **Start Simple**: Begin with basic queries to understand output
2. **Iterate**: Use validation loops for complex topics
3. **Monitor**: Use `hermes log --follow` to watch progress
4. **Export**: Always export important reports for safekeeping
5. **Configure**: Adjust `config.yaml` for your needs
```

## Expected Output

All documentation files created in `/home/ubuntu/python_project/Hermes/`:
1. `README.md` - Main project README
2. `ARCHITECTURE.md` - Architecture documentation
3. `DEVELOPMENT.md` - Developer guide
4. `USAGE_GUIDE.md` - Comprehensive usage guide

## Success Criteria

- All documentation files created
- README covers installation, quick start, basic usage
- ARCHITECTURE explains system design clearly
- DEVELOPMENT provides clear contribution guidelines
- USAGE_GUIDE covers common scenarios
- All markdown properly formatted
- Cross-references work correctly
