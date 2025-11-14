# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Hermes is a CLI-first research agent that orchestrates LangGraph workflows with Ollama-hosted LLMs to gather information, iterate through validation loops, and save markdown reports locally. The codebase follows a strict layered architecture with clear separation of concerns.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies (prefer uv for faster resolution)
uv pip install -e .
# or: pip install -e .

# Install dev tools (pytest, black, ruff, mypy)
uv pip install -e '.[dev]'
```

### Quality Gates (run before commits)
```bash
black hermes_cli              # Format code (100-char line length)
ruff check hermes_cli --fix   # Lint and auto-fix
mypy hermes_cli               # Type check (Python 3.10+)
pytest                        # Run all tests
python test_workflow.py       # Verify LangGraph graph compiles
```

### Running the CLI
```bash
# Start Ollama daemon first (required for LLM operations)
ollama serve

# Initialize workspace
hermes init

# Run a research task
hermes run --prompt "Your research question"

# View results
hermes history --limit 5
hermes log --follow
```

### Testing Specific Components
```bash
# Test individual modules
pytest tests/test_persistence.py
pytest tests/test_run_service.py
pytest tests/test_nodes_ollama.py

# Test with coverage
pytest --cov=hermes_cli
```

## Architecture Overview

Hermes uses a 5-layer architecture where each layer has distinct responsibilities:

```
CLI Layer (Typer commands)
    ↓
Services Layer (Business logic)
    ↓
Agents Layer (LangGraph workflow)
    ↓
Tools Layer (External integrations: Ollama, browser, container)
    ↓
Persistence Layer (File-based storage in ~/.hermes/)
```

### Key Architectural Principles

1. **Dependency Injection**: All services accept `FilePaths` or other dependencies via constructor for testability
2. **File-based Persistence**: All user data lives in `~/.hermes/`, never in the repo
3. **Service Layer Abstraction**: CLI commands are thin wrappers that delegate to services
4. **LangGraph State Machine**: The workflow is defined as a graph with conditional routing for validation loops

### LangGraph Workflow Structure

The workflow follows this sequence:

```
START → prompt_normalizer → query_generator → web_researcher →
container_processor → draft_aggregator → validation_controller ──┐
                       ├─ continue → validator → web_researcher (loop)
                       └─ complete → final_reporter → END
```

**Validation Loop Logic**:
- `validation_controller` enforces min/max loop counts from config
- `should_continue_validation()` routes based on `state.validation_complete`
- Validator node increments `state.loop_count` and loops back to `web_researcher`

### State Management

`HermesState` (Pydantic model in `hermes_cli/agents/state.py`) is the single source of truth shared across all nodes. Key fields:
- `user_prompt`: Original user input
- `generated_queries`: Search queries derived from prompt
- `research_results`: Raw web research data
- `draft_report`: Initial synthesized report
- `validated_report`: Final polished report
- `loop_count`, `validation_complete`: Control validation loop flow
- `min_validation_loops`, `max_validation_loops`: Config-driven limits

## Critical Development Patterns

### Adding a New CLI Command

1. Create `hermes_cli/commands/<feature>_cmd.py` with Typer command
2. Export function in `hermes_cli/commands/__init__.py`
3. Register in `hermes_cli/main.py`: `app.command("<name>")(<feature>_command)`
4. Keep commands thin—delegate to services

### Adding a New Service

1. Create service in `hermes_cli/services/<name>_service.py`
2. Accept dependencies (e.g., `FilePaths`) in `__init__` for DI
3. Use `logging.getLogger(__name__)` for developer logs
4. Write user-facing events via `LogRepository`
5. Export in `hermes_cli/services/__init__.py`

### Adding a LangGraph Node

1. Implement in `hermes_cli/agents/nodes/<name>.py`
2. Function signature: `def node_name(state: HermesState) -> dict[str, Any]`
3. Return partial state updates (LangGraph merges them)
4. Export in `hermes_cli/agents/nodes/__init__.py`
5. Wire into `hermes_cli/agents/graph.py`:
   - `workflow.add_node("node_name", node_name)`
   - Add edges: `workflow.add_edge("source", "node_name")`
6. Update `HermesState` if new fields are needed

### Extending Configuration

Config lives in `~/.hermes/config.yaml`. To add new settings:
1. Update dataclasses in `hermes_cli/persistence/config_repository.py`
2. Add CLI flags to relevant command (e.g., `run_cmd.py`)
3. Update `ConfigService.apply_overrides()` to handle new flags
4. Services should read from config, nodes should read from state

## Important Implementation Notes

### Ollama Integration
- Default endpoint: `http://localhost:11434/api/chat`
- Model: `gpt-oss:20b` (pull via `ollama pull gpt-oss:20b`)
- Client in `hermes_cli/tools/ollama_client.py` uses httpx with retry/timeout
- Always use context manager: `with OllamaClient(config) as client:`

### Browser Integration Status
- `BrowserUseClient` defaults to DuckDuckGo + httpx fallback
- Automatically upgrades to `browser-use` when installed
- Install from source: `pip install -e .[browser]`
- Current implementation is placeholder-aware; nodes handle empty results gracefully

### Container Integration Status
- `ContainerUseClient` is placeholder; uses local normalization fallback
- Logs warnings when Docker unavailable
- Future integration point for dagger-io isolated processing

### File Structure Conventions
- Reports: `~/.hermes/history/report-<YYYY-NNNN>.md`
- Metadata: `~/.hermes/history/report-<YYYY-NNNN>.meta.yaml`
- Tasks: `~/.hermes/task/task-<YYYY-NNNN>.yaml`
- Logs: `~/.hermes/log/hermes-YYYYMMDD.log`
- Debug logs: `~/.hermes/debug_log/hermes-YYYYMMDD.log`

### Error Handling Strategy
- CLI catches exceptions, prints Rich-formatted errors, exits with non-zero codes
- Services log via Python `logging` AND write to `LogRepository`
- Nodes append errors to `state.error_log` for diagnostics in final reports
- Placeholder integrations always return safe fallback data

## Testing Guidelines

### Unit Test Structure
- Test files mirror source structure: `tests/test_<module>.py`
- Use dependency injection to mock `FilePaths` and repositories
- Mock Ollama client factory for isolated service tests

### Integration Test Requirements
- Require `ollama serve` running locally
- Use `test_workflow.py` as smoke test for graph compilation
- Browser tests use real DuckDuckGo fallback (no mocking needed)

### Running Specific Test Suites
```bash
pytest tests/test_persistence.py      # File storage layer
pytest tests/test_run_service.py      # End-to-end workflow orchestration
pytest tests/test_nodes_ollama.py     # LLM integration nodes
pytest tests/test_browser_client.py   # Web research fallback
```

## Configuration & Validation Loop Details

### Validation Loop Flow
1. `draft_aggregator` creates initial report from research
2. `validation_controller` checks loop limits:
   - If `loop_count < min_loops`: force continue
   - If `loop_count >= max_loops`: force stop
   - Otherwise: defer to quality scoring (placeholder)
3. If continuing: `validator` critiques, generates follow-up queries
4. Loop back to `web_researcher` with new queries
5. Repeat until `validation_complete = True`

### Config Override Precedence
CLI flags → Runtime overrides → `~/.hermes/config.yaml` → Hardcoded defaults

Example:
```bash
hermes run --prompt "..." --max-validation 5 --model llama2:70b
```
Overrides only apply to that run; config file unchanged.

## Common Pitfalls to Avoid

1. **Never mutate state directly in nodes**: Return dict updates, LangGraph handles merging
2. **Always check Ollama server running**: Most mysterious errors trace to missing `ollama serve`
3. **Don't create files in repo**: All runtime data goes to `~/.hermes/`
4. **Use proper log levels**: Developer logs via `logging`, user logs via `LogRepository`
5. **Respect layer boundaries**: CLI → Services → Agents → Tools → Persistence (never skip layers)
6. **Test graph compilation**: Run `python test_workflow.py` after touching `graph.py` or node signatures

## Documentation References

- `ARCHITECTURE.md`: Detailed layer breakdown, data flow, node responsibilities
- `DEVELOPMENT.md`: Environment setup, quality gates, extension patterns
- `USAGE_GUIDE.md`: User-facing command walkthroughs
- `README.md`: Feature overview, installation, quick start
