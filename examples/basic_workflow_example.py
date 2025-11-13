#!/usr/bin/env python3
"""
Basic Workflow Example

This script demonstrates how to use the Research Analyst Agent's LangGraph
workflow with stub implementations. It shows the complete execution flow from
query input to final report generation.

Usage:
    python examples/basic_workflow_example.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.state import create_initial_state, AgentState
from src.orchestrator import compile_workflow


def example_1_simple_execution():
    """
    Example 1: Simple workflow execution with minimal configuration
    """
    print("=" * 80)
    print("Example 1: Simple Workflow Execution")
    print("=" * 80)

    # Create initial state
    initial_state = create_initial_state(
        query="LangGraphの基本的な使い方を教えてください",
        language="ja",
        model_name="gpt-oss:20b"
    )

    print(f"\nQuery: {initial_state['query']}")
    print(f"Language: {initial_state['language']}")
    print(f"Model: {initial_state['model_name']}")

    # Compile workflow
    print("\nCompiling workflow...")
    app = compile_workflow()

    # Execute workflow
    print("\nExecuting workflow...\n")
    config = {"configurable": {"thread_id": "example_1"}}
    result = app.invoke(initial_state, config)

    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"\nVerification loops completed: {result['verification_count']}")
    print(f"Search results found: {len(result['search_results'])}")
    print(f"Documents processed: {len(result['processed_data'])}")
    print(f"Errors encountered: {len(result['errors'])}")

    print("\n--- Final Report ---")
    print(result['final_report'])

    return result


def example_2_english_query():
    """
    Example 2: English language query
    """
    print("\n\n" + "=" * 80)
    print("Example 2: English Language Query")
    print("=" * 80)

    initial_state = create_initial_state(
        query="What is LangGraph and how does it support durable execution?",
        language="en",
        model_name="gpt-oss:20b"
    )

    print(f"\nQuery: {initial_state['query']}")
    print(f"Language: {initial_state['language']}")

    app = compile_workflow()

    print("\nExecuting workflow...\n")
    config = {"configurable": {"thread_id": "example_2"}}
    result = app.invoke(initial_state, config)

    print("\n--- Final Report ---")
    print(result['final_report'])

    return result


def example_3_streaming_execution():
    """
    Example 3: Streaming workflow execution to see intermediate steps
    """
    print("\n\n" + "=" * 80)
    print("Example 3: Streaming Execution")
    print("=" * 80)

    initial_state = create_initial_state(
        query="Explain the verification loop in research agents",
        language="en"
    )

    app = compile_workflow()
    config = {"configurable": {"thread_id": "example_3"}}

    print("\nStreaming workflow execution:\n")

    # Stream to see each node's output
    step_count = 0
    for step in app.stream(initial_state, config):
        step_count += 1
        print(f"\n--- Step {step_count} ---")
        for node_name, node_output in step.items():
            print(f"Node: {node_name}")
            if "messages" in node_output and node_output["messages"]:
                last_msg = node_output["messages"][-1]
                print(f"Message: {last_msg.get('content', 'N/A')}")

    print(f"\n✓ Completed in {step_count} steps")


def example_4_state_inspection():
    """
    Example 4: Inspecting state at different workflow stages
    """
    print("\n\n" + "=" * 80)
    print("Example 4: State Inspection")
    print("=" * 80)

    from src.state import add_error, increment_verification_count

    # Create and inspect initial state
    state = create_initial_state(
        query="Test query",
        language="ja"
    )

    print("\n--- Initial State ---")
    print(f"Query: {state['query']}")
    print(f"Language: {state['language']}")
    print(f"Verification count: {state['verification_count']}")
    print(f"Errors: {state['errors']}")

    # Simulate state updates
    print("\n--- Simulating State Updates ---")

    # Add an error
    error_update = add_error(state, "Example error for demonstration")
    state['errors'] = error_update['errors']
    print(f"After error: {state['errors']}")

    # Increment verification count
    verification_update = increment_verification_count(state)
    state['verification_count'] = verification_update['verification_count']
    print(f"After verification: {state['verification_count']}")

    # Simulate search results
    state['search_results'] = [
        {
            "title": "Example Result",
            "url": "https://example.com",
            "content": "Example content"
        }
    ]
    print(f"Search results: {len(state['search_results'])} items")


def example_5_workflow_structure():
    """
    Example 5: Examining workflow structure
    """
    print("\n\n" + "=" * 80)
    print("Example 5: Workflow Structure")
    print("=" * 80)

    from src.orchestrator import create_workflow

    workflow = create_workflow()
    graph = workflow.get_graph()

    print("\n--- Workflow Nodes ---")
    for node in graph.nodes:
        print(f"  • {node}")

    print("\n--- Workflow Edges ---")
    for edge in graph.edges:
        print(f"  {edge[0]} → {edge[1]}")

    print("\n--- Entry Point ---")
    print(f"  {workflow.entry_point if hasattr(workflow, 'entry_point') else 'START'}")


def main():
    """
    Run all examples
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "LangGraph Workflow Examples" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        # Run examples
        example_1_simple_execution()
        example_2_english_query()
        example_3_streaming_execution()
        example_4_state_inspection()
        example_5_workflow_structure()

        print("\n\n" + "=" * 80)
        print("✓ All examples completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
