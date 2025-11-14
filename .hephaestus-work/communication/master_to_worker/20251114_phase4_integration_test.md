# Task: Integration Testing and Validation

**Task ID**: phase4_integration_test
**Priority**: high
**Assigned to**: worker-3
**Dependencies**: All Phase 3 tasks completed

## Objective
Perform comprehensive integration testing of the Hermes system to ensure all components work together correctly. Verify end-to-end functionality and fix any integration issues.

## Context
Integration testing validates that all layers (persistence, tools, services, agents, CLI) integrate correctly and the system functions as designed.

Reference design document: `/home/ubuntu/python_project/Hermes/詳細設計書.md` (all sections)

## Requirements

### 1. Dependency Installation Test

```bash
# Test dependency installation
cd /home/ubuntu/python_project/Hermes
pip install -e .

# Verify installation
python -c "import hermes_cli; print(hermes_cli.__version__)"
```

**Expected**: Version 1.0.0 printed, no import errors

### 2. CLI Help Test

Test all CLI commands display help correctly:

```bash
python -m hermes_cli.main --help
python -m hermes_cli.main --version
python -m hermes_cli.main init --help
python -m hermes_cli.main task --help
python -m hermes_cli.main run --help
python -m hermes_cli.main log --help
python -m hermes_cli.main history --help
python -m hermes_cli.main debug --help
```

**Expected**: Help text displays for each command

### 3. Init Command Test

```bash
# Clean any existing installation
rm -rf ~/.hermes

# Test init
python -m hermes_cli.main init

# Verify structure created
ls -la ~/.hermes/
ls -la ~/.hermes/config.yaml
```

**Expected**:
- Directories created: cache, task, log, debug_log, history
- config.yaml created with default values

### 4. Config Test

```python
# Test script: test_config.py
from hermes_cli.services import ConfigService

service = ConfigService()
config = service.load()

print(f"Ollama API: {config.ollama.api_base}")
print(f"Model: {config.ollama.model}")
print(f"Language: {config.language}")
print(f"Min validation: {config.validation.min_loops}")
print(f"Max validation: {config.validation.max_loops}")

# Test override
overrides = {
    'language': 'en',
    'min_validation': 2,
    'max_validation': 5,
}
config_override = service.apply_overrides(config, overrides)
print(f"\nOverridden language: {config_override.language}")
print(f"Overridden validation: {config_override.validation.min_loops}-{config_override.validation.max_loops}")
```

**Expected**: Config loads, overrides apply correctly

### 5. Persistence Layer Test

```python
# Test script: test_persistence.py
from hermes_cli.services import TaskService, HistoryService
from datetime import datetime

# Test TaskService
task_service = TaskService()

# Create task
task = task_service.create_task("Test prompt")
print(f"Created task: {task.id}")

# List tasks
tasks = task_service.list_tasks()
print(f"Total tasks: {len(tasks)}")

# Update status
task_service.update_status(task.id, "running")
updated = task_service.get_task(task.id)
print(f"Updated status: {updated.status}")

# Delete task
task_service.delete_task(task.id)
print(f"Task deleted")

# Test HistoryService
history_service = HistoryService()
from hermes_cli.persistence.history_repository import HistoryMeta

meta = HistoryMeta(
    id="test-2025-0001",
    prompt="Test prompt",
    created_at=datetime.now(),
    finished_at=datetime.now(),
    model="gpt-oss:20b",
    language="ja",
    validation_loops=2,
    source_count=10,
    report_file="report-test-2025-0001.md",
)

history_service.repository.save_meta(meta)
history_service.repository.save_report("test-2025-0001", "# Test Report\n\nTest content")

loaded_meta = history_service.get_history("test-2025-0001")
print(f"History meta loaded: {loaded_meta.id}")

report = history_service.get_report("test-2025-0001")
print(f"Report loaded: {len(report)} chars")

# Cleanup
history_service.delete_history("test-2025-0001")
```

**Expected**: All CRUD operations work correctly

### 6. Tools Layer Test

```python
# Test script: test_tools.py
from hermes_cli.tools import OllamaClient, OllamaConfig, BrowserUseClient, ContainerUseClient

# Test OllamaClient (structure only, may fail if Ollama not running)
config = OllamaConfig(
    api_base="http://localhost:11434/api/chat",
    model="gpt-oss:20b",
    retry=3,
    timeout_sec=60
)

client = OllamaClient(config)
print(f"OllamaClient created: {client.config.model}")

# Test BrowserUseClient (structure only)
browser = BrowserUseClient(max_sources=5)
print(f"BrowserUseClient created: max_sources={browser.max_sources}")

# Test ContainerUseClient (structure only)
container = ContainerUseClient()
print(f"ContainerUseClient created")

# Test normalize (should use fallback)
texts = ["Test text 1", "Test text 2"]
normalized = container.normalize_texts(texts)
print(f"Normalized {len(normalized)} texts")
```

**Expected**: Clients instantiate correctly, basic operations work

### 7. Agent Workflow Test

```python
# Test script: test_workflow.py
from hermes_cli.agents import create_hermes_workflow, HermesState

# Create workflow
workflow = create_hermes_workflow()
print("Workflow created successfully")

# Create initial state
state = HermesState(
    user_prompt="Test query about Python",
    language="ja",
    min_validation=1,
    max_validation=2,
    min_sources=3,
    max_sources=5,
)

print(f"Initial state: {state.user_prompt}")

# Test workflow execution (may use placeholders)
print("Testing workflow execution...")
try:
    # result = workflow.invoke(state)
    # print(f"Workflow completed: {len(result.validated_report)} chars")
    print("Workflow structure validated (execution skipped - requires external services)")
except Exception as e:
    print(f"Note: Full execution requires Ollama/browser: {e}")
```

**Expected**: Workflow instantiates, structure validated

### 8. CLI Task Command Test

```bash
# Test task management
python -m hermes_cli.main task --prompt "Test research query"
python -m hermes_cli.main task --list

# Get task ID from list, then delete
# python -m hermes_cli.main task --delete YYYY-NNNN
```

**Expected**: Task created, listed, can be deleted

### 9. Integration Test Report

Create `INTEGRATION_TEST_REPORT.md` with:

```markdown
# Hermes Integration Test Report

Date: YYYY-MM-DD
Tester: worker-3

## Test Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Installation | PASS/FAIL | |
| CLI Help | PASS/FAIL | |
| Init Command | PASS/FAIL | |
| Config Service | PASS/FAIL | |
| Persistence Layer | PASS/FAIL | |
| Tools Layer | PASS/FAIL | |
| Agent Workflow | PASS/FAIL | |
| CLI Commands | PASS/FAIL | |

## Detailed Results

### 1. Installation Test
[Results]

### 2. CLI Help Test
[Results]

### 3. Init Command Test
[Results]

... (for each test)

## Issues Found

1. [Issue description]
   - Component: [component name]
   - Severity: High/Medium/Low
   - Fix: [what was done]

## Recommendations

[Any recommendations for improvements]

## Conclusion

Overall system status: READY / NEEDS_FIXES

[Summary]
```

## Expected Output

1. All tests executed
2. Test scripts created in `/home/ubuntu/python_project/Hermes/tests/` or root
3. `INTEGRATION_TEST_REPORT.md` created
4. Any critical bugs fixed
5. Verification that core functionality works

## Success Criteria

- All imports work correctly
- CLI commands display help
- Init command creates structure
- Task CRUD operations work
- Config loading and overrides work
- Persistence layer operations succeed
- Agent workflow instantiates correctly
- No critical errors in integration
- Test report created with detailed results

## Notes

- Some tests may show warnings if external services (Ollama, browser) not running
- This is expected - focus on integration between internal components
- Document any external service requirements
- Fix critical bugs, document minor issues for future
