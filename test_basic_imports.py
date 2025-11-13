#!/usr/bin/env python3
"""
Basic Import Test

Tests that all modules can be imported and basic functionality works.
This test doesn't require external dependencies to be installed.
"""

import sys
from pathlib import Path

# Test 1: Import state module
print("Test 1: Importing state module...")
try:
    from src.state import agent_state
    print("✓ State module imported successfully")
    print(f"  - AgentState: {agent_state.AgentState}")
    print(f"  - create_initial_state: {agent_state.create_initial_state}")
except ImportError as e:
    print(f"✗ Failed to import state module: {e}")
    sys.exit(1)

# Test 2: Create initial state
print("\nTest 2: Creating initial state...")
try:
    from src.state import create_initial_state
    state = create_initial_state(
        query="Test query",
        language="ja",
        model_name="gpt-oss:20b"
    )
    print("✓ Initial state created successfully")
    print(f"  - Query: {state['query']}")
    print(f"  - Language: {state['language']}")
    print(f"  - Model: {state['model_name']}")
    print(f"  - Verification count: {state['verification_count']}")
    print(f"  - Errors: {state['errors']}")
except Exception as e:
    print(f"✗ Failed to create initial state: {e}")
    sys.exit(1)

# Test 3: Test helper functions
print("\nTest 3: Testing helper functions...")
try:
    from src.state import add_error, increment_verification_count

    # Test add_error
    error_update = add_error(state, "Test error")
    print(f"✓ add_error works: {error_update}")

    # Test increment_verification_count
    verification_update = increment_verification_count(state)
    print(f"✓ increment_verification_count works: {verification_update}")
except Exception as e:
    print(f"✗ Failed helper function test: {e}")
    sys.exit(1)

# Test 4: Import orchestrator module (will fail if langgraph not installed, but should syntax check)
print("\nTest 4: Syntax check orchestrator module...")
try:
    import py_compile
    workflow_path = Path("src/orchestrator/workflow.py")
    py_compile.compile(str(workflow_path), doraise=True)
    print(f"✓ workflow.py syntax is valid")
except Exception as e:
    print(f"✗ Syntax error in workflow.py: {e}")
    sys.exit(1)

# Test 5: Verify file structure
print("\nTest 5: Verifying file structure...")
required_files = [
    "src/__init__.py",
    "src/state/__init__.py",
    "src/state/agent_state.py",
    "src/orchestrator/__init__.py",
    "src/orchestrator/workflow.py",
    "docs/LANGGRAPH_IMPLEMENTATION.md",
    "examples/basic_workflow_example.py",
    "requirements.txt"
]

all_exist = True
for file_path in required_files:
    path = Path(file_path)
    if path.exists():
        print(f"  ✓ {file_path}")
    else:
        print(f"  ✗ {file_path} (missing)")
        all_exist = False

if not all_exist:
    print("\n✗ Some required files are missing")
    sys.exit(1)

print("\n" + "=" * 80)
print("✓ All basic tests passed!")
print("=" * 80)
print("\nNote: To run full workflow tests, install dependencies:")
print("  pip install -r requirements.txt")
