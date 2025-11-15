# Hermes Test Documentation

This directory contains documentation for the Hermes test suite.

## Test Overview

The Hermes project includes several types of tests:

| Test Type | Purpose | Location |
|-----------|---------|----------|
| **Smoke Tests** | Verify basic functionality without mocks | `tests/test_*.py` |
| **Integration Tests** | Test component interactions | `tests/test_*.py` |
| **Workflow Tests** | Verify LangGraph compilation | `test_workflow.py` (root) |

## Running Tests

### Run all tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run pytest
pytest

# With coverage
pytest --cov=hermes_cli

# Verbose output
pytest -v
```

### Run specific test file

```bash
pytest tests/test_config.py
pytest tests/test_browser_client.py
```

### Run workflow smoke test

```bash
python test_workflow.py
```

## Test Requirements

### Environment

- Python 3.10+
- Virtual environment activated
- Dependencies installed (`pip install -e .[dev]`)
- Hermes initialized (`hermes init`)

### External Services (for integration tests)

- **Ollama server**: Required for `test_nodes_ollama.py`, `test_run_service.py`
  ```bash
  ollama serve
  ollama pull gpt-oss:20b
  ```

- **Internet connection**: Required for `test_browser_client.py` (DuckDuckGo)

- **Docker**: Optional for container tests (auto-fallback if unavailable)

## Test Files

### test_browser_client.py

**Purpose**: Verify BrowserUseClient DuckDuckGo fallback functionality

**What it tests**:
- DuckDuckGo search returns results
- Result structure (title, URL, snippet, content)
- Context manager usage
- Network connectivity handling

**Requirements**:
- Internet connection
- No external mocks

**How to run**:
```bash
python tests/test_browser_client.py
# or
pytest tests/test_browser_client.py
```

**Expected output**:
```
Sample result: Example Title -> https://example.com
Snippet: Brief description of result...
Content preview: Full content preview...
Fetched 2 total sources.
```

**Common failures**:
- Network connectivity issues
- DuckDuckGo rate limiting
- DNS resolution problems

---

### test_config.py

**Purpose**: Test ConfigService loading and override logic

**What it tests**:
- Default configuration loading from `~/.hermes/config.yaml`
- CLI override application
- Immutability of original config after overrides
- Configuration dataclass structure

**Requirements**:
- Hermes initialized (`hermes init`)
- Valid `~/.hermes/config.yaml`

**How to run**:
```bash
python tests/test_config.py
# or
pytest tests/test_config.py
```

**Expected output**:
```
=== Default Configuration ===
Ollama API: http://localhost:11434/api/chat
Model: gpt-oss:20b
Language: ja
Validation loops: 1-3
Search sources: 3-8

=== After Overrides ===
Ollama API: http://localhost:11434/api/chat
Model: gpt-oss:8b
Language: en
Validation loops: 2-4
Search sources: 2-6

=== Original Config Still Intact ===
Language: ja
Validation loops: 1-3
```

**Common failures**:
- Missing `~/.hermes/config.yaml`
- Corrupted YAML syntax
- Incorrect dataclass structure

---

### test_persistence.py

**Purpose**: Test TaskService and HistoryService CRUD operations

**What it tests**:
- Task creation, update, deletion
- Task listing and filtering
- History metadata save/load
- Report file export
- Cleanup operations

**Requirements**:
- Hermes initialized
- Write permissions to `~/.hermes/`

**How to run**:
```bash
python tests/test_persistence.py
# or
pytest tests/test_persistence.py
```

**Expected output**:
```
=== TaskService CRUD ===
Created task: 2025-XXXX (scheduled)
Total tasks after create: X
Status after update: running
Deleted task: 2025-XXXX

=== HistoryService persistence ===
Saved history metadata and report for integration-test-0001
History entries available: X
Fetched history language: ja
Exported report exists: True
Cleaned up history entry integration-test-0001
```

**Common failures**:
- Permission denied on `~/.hermes/`
- Disk space issues
- Concurrent access conflicts

---

### test_run_service.py

**Purpose**: End-to-end integration test of RunService workflow execution

**What it tests**:
- Complete workflow execution
- Ollama client interaction
- History metadata creation
- Report generation
- Error handling

**Requirements**:
- **Ollama server running** (`ollama serve`)
- **Model available** (`ollama pull gpt-oss:20b`)
- Internet connection (for web research)
- Hermes initialized

**How to run**:
```bash
# Ensure Ollama is running
ollama serve &

# Run test
python tests/test_run_service.py
# or
pytest tests/test_run_service.py
```

**Expected behavior**:
- Executes full research workflow
- Creates report in `~/.hermes/history/`
- Takes 30-180 seconds depending on model and query complexity
- May timeout if Ollama is slow

**Common failures**:
- Ollama server not running
- Model not found
- Timeout (increase `timeout_sec` in config)
- Web search rate limiting

---

### test_nodes_ollama.py

**Purpose**: Test individual LangGraph nodes with Ollama integration

**What it tests**:
- Query generator node
- Draft aggregator node
- Validator node
- Ollama client retry logic
- Error handling

**Requirements**:
- **Ollama server running**
- **Model available**

**How to run**:
```bash
pytest tests/test_nodes_ollama.py -v
```

**Expected behavior**:
- Tests individual nodes in isolation
- Verifies Ollama response parsing
- Checks error handling and retries

**Common failures**:
- Ollama connection refused
- Model timeout
- Malformed prompts

---

### test_queue_service.py

**Purpose**: Test queue processing logic

**What it tests**:
- Queue ordering (FIFO)
- Task status updates
- Limit enforcement
- Error handling for failed tasks
- Sequential execution

**Requirements**:
- Hermes initialized
- Mock tasks created

**How to run**:
```bash
pytest tests/test_queue_service.py
```

**Expected behavior**:
- Processes tasks in creation order
- Updates task status correctly
- Respects limit parameter
- Continues on individual task failures

---

### test_logging.py

**Purpose**: Test LogService and LogRepository

**What it tests**:
- Log file writing
- Log rotation (daily)
- Tail functionality
- Stream functionality
- Task ID filtering

**Requirements**:
- Hermes initialized
- Write permissions to `~/.hermes/log/`

**How to run**:
```bash
pytest tests/test_logging.py
```

**Expected behavior**:
- Writes structured log lines
- Creates new files on date change
- Tail returns correct number of lines
- Stream yields new lines in real-time

---

### test_workflow.py (root)

**Purpose**: Smoke test for LangGraph graph compilation

**What it tests**:
- `create_hermes_workflow()` can be imported
- `HermesState` can be instantiated
- Workflow graph compiles without errors
- No node/edge configuration errors

**Requirements**:
- Basic Python environment
- LangGraph installed

**How to run**:
```bash
python test_workflow.py
```

**Expected output**:
```
✓ Successfully imported create_hermes_workflow and HermesState
✓ Successfully created HermesState: Test research question
✓ Successfully created workflow graph

=== All tests passed! ===
```

**Common failures**:
- Missing dependencies
- Import errors
- Graph structure errors
- Node registration issues

## Test Coverage

To check test coverage:

```bash
pytest --cov=hermes_cli --cov-report=html
open htmlcov/index.html  # View coverage report
```

Target coverage by module:

| Module | Target Coverage |
|--------|----------------|
| `commands/` | 80%+ |
| `services/` | 90%+ |
| `persistence/` | 95%+ |
| `agents/` | 70%+ |
| `tools/` | 60%+ |

## Writing New Tests

### Smoke Test Template

```python
#!/usr/bin/env python3
"""Brief description of what this test verifies."""

from hermes_cli.services import YourService

def main() -> None:
    service = YourService()
    result = service.do_something()

    if not result:
        raise SystemExit("Test failed: no result returned")

    print(f"✓ Test passed: {result}")

if __name__ == "__main__":
    main()
```

### Pytest Test Template

```python
"""Unit tests for YourModule."""

import pytest
from hermes_cli.your_module import YourClass

def test_basic_functionality():
    """Test basic functionality."""
    instance = YourClass()
    result = instance.method()
    assert result is not None

def test_error_handling():
    """Test error handling."""
    instance = YourClass()
    with pytest.raises(ValueError):
        instance.method_that_fails()
```

## Continuous Integration

Tests should be run in CI/CD pipelines with:

1. **Unit tests**: Fast, no external dependencies
2. **Integration tests**: Require Ollama, Docker, internet
3. **Smoke tests**: Quick end-to-end checks

### Example CI Configuration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e .[dev]
      - name: Run unit tests
        run: pytest tests/ -m "not integration"
      - name: Install Ollama
        run: |
          curl -sSL https://ollama.ai/install.sh | sh
          ollama serve &
          ollama pull gpt-oss:20b
      - name: Run integration tests
        run: pytest tests/ -m integration
```

## Troubleshooting Tests

### All tests failing

1. Check virtual environment:
   ```bash
   which python
   pip list | grep hermes
   ```

2. Reinstall dependencies:
   ```bash
   pip install -e .[dev]
   ```

3. Reinitialize Hermes:
   ```bash
   hermes init
   ```

### Ollama tests failing

1. Verify server:
   ```bash
   curl http://localhost:11434/api/version
   ```

2. Check model:
   ```bash
   ollama list | grep gpt-oss
   ```

3. Increase timeout:
   ```yaml
   # ~/.hermes/config.yaml
   ollama:
     timeout_sec: 300
   ```

### Network tests failing

1. Check connectivity:
   ```bash
   ping 8.8.8.8
   curl https://duckduckgo.com
   ```

2. Check for rate limiting (wait 1-2 minutes)

3. Use VPN if geo-blocked

## Test Maintenance

- **Add tests** for every new feature
- **Update tests** when behavior changes
- **Remove obsolete tests** when features are removed
- **Keep tests fast** (<30s for unit tests)
- **Document requirements** in test docstrings
- **Mock external services** when possible

## Related Documentation

- [DEVELOPMENT.md](../../DEVELOPMENT.md) - Development environment setup
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - System architecture
- Command documentation in [doc/command/](../command/)
