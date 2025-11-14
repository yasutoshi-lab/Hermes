"""Test script to verify LangGraph workflow can be instantiated."""

import sys
from pathlib import Path

# Add hermes_cli to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from hermes_cli.agents import create_hermes_workflow, HermesState

    print("✓ Successfully imported create_hermes_workflow and HermesState")

    # Test state creation
    state = HermesState(
        user_prompt="Test research question",
        language="ja"
    )
    print(f"✓ Successfully created HermesState: {state.user_prompt}")

    # Test workflow creation
    workflow = create_hermes_workflow()
    print("✓ Successfully created workflow graph")

    print("\n=== All tests passed! ===")

except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
