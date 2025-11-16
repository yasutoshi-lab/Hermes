# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hermes is a locally-executable CLI information gathering agent powered by local LLMs (Large Language Models). It automates web searches, content analysis, and report generation while maintaining complete privacy. Built with LangGraph for multi-stage workflows, it integrates SearxNG for web search, Ollama for LLM inference, Redis for caching, and optional Langfuse for tracing.

## Development Commands

### Installation & Setup
```bash
# Install dependencies using uv (required package manager)
uv sync

# Install CLI in editable mode
uv pip install -e .

# Initialize Hermes (creates ~/.hermes directory with config and Docker setup)
hermes init
```

### Running the Application
```bash
# Execute with immediate prompt
hermes run --prompt "Your research topic"

# Execute a specific task by ID
hermes run --task-id 2025-0001

# Execute all scheduled tasks
hermes run --task-all

# Manage tasks
hermes task --add "Research topic"
hermes task --list
hermes task --show <task-id>
```

### Testing
```bash
# Run all tests
pytest

# Run only unit tests (fast, no external dependencies)
pytest tests/unit -v -m unit

# Run specific test markers
pytest -m integration        # Integration tests (requires external services)
pytest -m "not slow"        # Exclude slow tests
pytest -m dependency        # Dependency health checks

# Run with coverage
pytest --cov=hermes_cli --cov-report=html --cov-report=term

# Run dependency health check (verifies Redis, Ollama, SearxNG, Langfuse)
python tests/test_dependencies.py

# Run single test file
pytest tests/unit/test_task_service.py -v
```

### Code Quality
```bash
# Format code
black hermes_cli/

# Lint code
ruff check hermes_cli/

# Type checking
mypy hermes_cli/
```

## Architecture

### LangGraph Workflow

Hermes uses a multi-stage LangGraph workflow defined in `hermes_cli/agents/graph.py`:

1. **normalize** (`prompt_normalizer.py`) - Normalizes and preprocesses user prompts
2. **generate_queries** (`query_generator.py`) - LLM generates search queries based on prompt
3. **search** (`web_researcher.py`) - Parallel web search via SearxNG with Redis caching
4. **process** (`container_processor.py`) - LLM analyzes and summarizes scraped content
5. **draft** (`draft_aggregator.py`) - Creates draft report with citations
6. **validate** (`validator.py`) - Validates report quality and identifies gaps
7. **finalize** (`final_reporter.py`) - Generates final Markdown report

The workflow includes a validation loop: if the validator finds issues, it can loop back to the search step for additional information gathering (controlled by `validation.min_validation` and `validation.max_validation` in config).

### Service-Oriented Architecture

The codebase follows a layered architecture:

- **`hermes_cli/commands/`** - Click CLI command definitions (init, task, run, log, history)
- **`hermes_cli/services/`** - Business logic layer (TaskService, RunService, HistoryService, ConfigService, LogService)
- **`hermes_cli/persistence/`** - Data access layer (repositories for tasks, config, history, logs)
- **`hermes_cli/agents/`** - LangGraph workflow and nodes
- **`hermes_cli/tools/`** - External integrations (OllamaClient, Langfuse, container scraping)
- **`hermes_cli/models/`** - Pydantic models for state, config, tasks, reports, search results
- **`hermes_cli/utils/`** - Shared utilities

### Key Design Patterns

- **Pydantic validation** - All configuration and data models use Pydantic for validation
- **Dependency injection** - Services receive `HermesConfig` in constructors
- **Repository pattern** - Persistence layer abstracts file I/O
- **Async/await** - Async patterns throughout for I/O operations
- **Loguru logging** - Structured logging with category-based filtering

## Configuration

Configuration is stored in `~/.hermes/config.yaml` (created by `hermes init`). The config structure is defined in `hermes_cli/models/config.py`:

- **ollama** - LLM API endpoint, model name, timeout, temperature, max_tokens
- **search** - SearxNG URL, Redis URL, query_count, min/max search results, cache TTL
- **validation** - min/max validation loops for quality assurance
- **logging** - Log level, format, rotation, retention
- **langfuse** - Optional tracing (enabled, host, keys)

CLI options in `hermes run` can temporarily override config values.

## Important Implementation Details

### State Management
- `WorkflowState` (in `hermes_cli/models/state.py`) tracks workflow progress through LangGraph
- State includes: original/normalized prompts, queries, search results, scraped content, draft/final reports, validation status, errors

### Search & Caching
- SearxNG performs parallel searches across multiple engines
- Redis caches search results with configurable TTL (`search.cache_ttl`)
- Search respects `min_search` and `max_search` bounds for source count

### LLM Integration
- `OllamaClient` in `hermes_cli/tools/ollama_client.py` handles all LLM interactions
- Supports retry logic and timeout configuration
- Uses streaming=false for deterministic responses

### Task Management
- Tasks stored as YAML files in `~/.hermes/task/`
- Task IDs follow format: `YYYY-NNNN` (e.g., 2025-0001)
- Task status: scheduled, running, completed, failed

### Report Generation
- Final reports saved to `~/.hermes/history/<task-id>/report.md`
- Reports include metadata, sections, and citations with source URLs
- Report model defined in `hermes_cli/models/report.py`

## Testing Strategy

The project has three test levels (see `doc/test/tests_en.md`):

1. **Unit tests** (`tests/unit/`) - Fast, mocked dependencies, test individual components
2. **Integration tests** (`tests/integration/`) - Test component interactions, require running services
3. **E2E tests** (`tests/e2e/`) - Full system tests from CLI to report generation

When writing tests:
- Use `@pytest.mark.unit` for unit tests
- Use `@pytest.mark.integration` for integration tests
- Use `@pytest.mark.slow` for long-running tests
- Use fixtures from `tests/conftest.py` for common setup

## Docker Services

The project requires these Docker services (managed via `~/.hermes/docker-compose.yaml`):
- **SearxNG** (port 8080) - Meta-search engine
- **Redis** (port 6379) - Search result caching
- **Langfuse** (port 3000, optional) - Execution tracing

## File Paths & Structure

User data is stored in `~/.hermes/`:
```
~/.hermes/
├── config.yaml              # Main configuration
├── docker-compose.yaml      # Docker service definitions
├── task/                    # Task YAML files
├── history/                 # Execution history and reports
│   └── <task-id>/
│       └── report.md
├── log/                     # Normal logs
├── debug_log/               # Debug logs
├── cache/                   # Application cache
└── searxng/                 # SearxNG configuration
```

Template files are in `.hermes_template/` in the repository root.

## Common Patterns

### Adding a New LangGraph Node
1. Create node function in `hermes_cli/agents/nodes/`
2. Import and register in `hermes_cli/agents/graph.py`
3. Add node to workflow with `workflow.add_node()`
4. Define edges or conditional edges
5. Update `WorkflowState` if new state fields needed

### Adding a New CLI Command
1. Create command file in `hermes_cli/commands/`
2. Define Click command with `@click.command()` decorator
3. Import and register in `hermes_cli/main.py` with `cli.add_command()`

### Modifying Configuration
1. Update Pydantic models in `hermes_cli/models/config.py`
2. Update template in `.hermes_template/config.yaml.template`
3. Update documentation in `doc/config/config_en.md`
