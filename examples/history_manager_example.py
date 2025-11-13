#!/usr/bin/env python3
"""
Example usage of the HistoryManager module.

This script demonstrates all major features of the HistoryManager including:
- Creating sessions
- Saving various types of data
- Loading previous sessions
- Cleanup operations
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modules.history_manager import (
    HistoryManager,
    HistoryManagerError,
    SessionNotFoundError
)


def example_1_basic_session():
    """Example 1: Create a basic research session."""
    print("=" * 70)
    print("Example 1: Basic Session Creation and Data Saving")
    print("=" * 70)

    # Initialize HistoryManager
    hm = HistoryManager()

    # Create a new session
    session_id = hm.create_session()
    print(f"✓ Created session: {session_id}\n")

    # Save user input
    prompt = "What are the latest developments in artificial intelligence?"
    config = {
        "language": "en",
        "model_name": "gpt-oss:20b",
        "max_results": 10
    }
    hm.save_input(session_id, prompt, config)
    print("✓ Saved user input\n")

    # Save search results
    search_results = [
        {
            "title": "AI Breakthrough in Natural Language Processing",
            "url": "https://example.com/ai-nlp",
            "description": "Recent advances in transformer models",
            "content": "Researchers have developed a new transformer architecture..."
        },
        {
            "title": "Machine Learning Trends 2024",
            "url": "https://example.com/ml-trends",
            "description": "Top ML trends for 2024",
            "content": "Key trends include: multimodal learning, efficient architectures..."
        }
    ]
    hm.save_search_results(session_id, search_results)
    print("✓ Saved search results\n")

    # Save processed data
    processed_data = [
        {
            "step": "Content Extraction",
            "timestamp": "2024-01-15T10:00:00",
            "input": "Raw HTML pages",
            "output": "Extracted text content",
            "logs": "Processed 2 pages successfully"
        }
    ]
    hm.save_processed_data(session_id, processed_data)
    print("✓ Saved processed data\n")

    # Save final report
    report = """# AI Development Report

## Summary
This report analyzes recent developments in artificial intelligence.

## Key Findings
1. Transformer models continue to evolve
2. Multimodal learning is gaining traction
3. Efficient architectures are becoming crucial

## Conclusion
AI research is advancing rapidly across multiple fronts.
"""
    hm.save_report(session_id, report)
    print("✓ Saved final report\n")

    # Save session state
    state = {
        "query": prompt,
        "results_found": len(search_results),
        "processing_steps": len(processed_data),
        "status": "completed"
    }
    hm.save_state(session_id, state)
    print("✓ Saved session state\n")

    return session_id


def example_2_japanese_content():
    """Example 2: Handle Japanese content."""
    print("\n" + "=" * 70)
    print("Example 2: Japanese Content Support")
    print("=" * 70)

    hm = HistoryManager()

    # Create session with Japanese content
    session_id = hm.create_session()
    print(f"✓ Created session: {session_id}\n")

    # Japanese prompt
    prompt = "量子コンピューティングの最新研究について教えてください"
    config = {
        "language": "ja",
        "model_name": "gpt-oss:20b"
    }
    hm.save_input(session_id, prompt, config)
    print("✓ Saved Japanese input\n")

    # Japanese search results
    search_results = [
        {
            "title": "量子コンピューティング最新動向",
            "url": "https://example.jp/quantum",
            "description": "日本の量子研究の現状",
            "content": "理化学研究所による量子コンピュータの開発が進んでいます..."
        }
    ]
    hm.save_search_results(session_id, search_results)
    print("✓ Saved Japanese search results\n")

    # Japanese report
    report = """# 量子コンピューティング研究レポート

## 概要
日本における量子コンピューティング研究の最新動向をまとめます。

## 主要な発見
1. エラー訂正技術の進展
2. 量子ビットの安定性向上
3. 実用化に向けた取り組み

## 結論
日本の量子研究は着実に進展しています。
"""
    hm.save_report(session_id, report)
    print("✓ Saved Japanese report\n")

    return session_id


def example_3_load_sessions():
    """Example 3: Load and review previous sessions."""
    print("\n" + "=" * 70)
    print("Example 3: Loading Previous Sessions")
    print("=" * 70)

    hm = HistoryManager()

    # List all sessions
    sessions = hm.list_sessions()
    print(f"✓ Found {len(sessions)} sessions\n")

    if not sessions:
        print("No sessions available to load.\n")
        return

    # Load the most recent session
    latest_session = sessions[0]
    print(f"Loading latest session: {latest_session}\n")

    try:
        session_data = hm.load_session(latest_session)

        # Display session information
        print(f"Session path: {session_data['session_path']}\n")

        if "input" in session_data:
            print("Input file found:")
            print(session_data["input"][:200] + "...\n")

        if "search_results" in session_data:
            print("Search results file found")
            lines = session_data["search_results"].split('\n')
            print(f"  Preview: {lines[0]}\n")

        if "report" in session_data:
            print("Report file found")
            lines = session_data["report"].split('\n')
            print(f"  Preview: {lines[0]}\n")

        if "state" in session_data:
            print("State file found:")
            state = session_data["state"]
            print(f"  Session ID: {state.get('session_id', 'N/A')}")
            print(f"  Saved at: {state.get('saved_at', 'N/A')}\n")

    except SessionNotFoundError as e:
        print(f"Error: {e}\n")


def example_4_session_management():
    """Example 4: Session management operations."""
    print("\n" + "=" * 70)
    print("Example 4: Session Management")
    print("=" * 70)

    hm = HistoryManager()

    # Create multiple test sessions
    print("Creating 5 test sessions...\n")
    test_sessions = []
    for i in range(5):
        sid = hm.create_session()
        test_sessions.append(sid)
        # Save minimal data to make them valid
        hm.save_input(sid, f"Test prompt {i}", {"test": i})

    print(f"✓ Created {len(test_sessions)} test sessions\n")

    # List all sessions
    all_sessions = hm.list_sessions()
    print(f"Total sessions: {len(all_sessions)}\n")

    # Cleanup - keep only last 3
    print("Cleaning up old sessions (keeping last 3)...\n")
    deleted_count = hm.cleanup_old_sessions(keep_last_n=3)
    print(f"✓ Deleted {deleted_count} sessions\n")

    # Verify remaining sessions
    remaining = hm.list_sessions()
    print(f"Remaining sessions: {len(remaining)}\n")

    # Delete a specific session
    if remaining:
        session_to_delete = remaining[-1]
        print(f"Deleting specific session: {session_to_delete}...\n")
        hm.delete_session(session_to_delete)
        print("✓ Session deleted\n")

        final_count = len(hm.list_sessions())
        print(f"Final session count: {final_count}\n")


def example_5_error_handling():
    """Example 5: Error handling."""
    print("\n" + "=" * 70)
    print("Example 5: Error Handling")
    print("=" * 70)

    hm = HistoryManager()

    # Try to load non-existent session
    print("Attempting to load non-existent session...\n")
    try:
        hm.load_session("invalid_session_id")
    except SessionNotFoundError as e:
        print(f"✓ Caught SessionNotFoundError: {e}\n")

    # Try to save to non-existent session
    print("Attempting to save to non-existent session...\n")
    try:
        hm.save_input("invalid_session_id", "test", {})
    except SessionNotFoundError as e:
        print(f"✓ Caught SessionNotFoundError: {e}\n")

    # Try invalid cleanup parameter
    print("Attempting invalid cleanup parameter...\n")
    try:
        hm.cleanup_old_sessions(keep_last_n=0)
    except ValueError as e:
        print(f"✓ Caught ValueError: {e}\n")


def example_6_complete_workflow():
    """Example 6: Complete research workflow."""
    print("\n" + "=" * 70)
    print("Example 6: Complete Research Workflow")
    print("=" * 70)

    hm = HistoryManager()

    # Step 1: Initialize session
    print("Step 1: Initialize session")
    session_id = hm.create_session()
    print(f"  Session ID: {session_id}\n")

    # Step 2: Save initial query
    print("Step 2: Save user query")
    prompt = "Analyze the impact of climate change on marine ecosystems"
    config = {"language": "en", "model_name": "gpt-oss:20b"}
    hm.save_input(session_id, prompt, config)
    print("  ✓ Query saved\n")

    # Step 3: Save search results
    print("Step 3: Save search results")
    search_results = [
        {
            "title": "Climate Change Effects on Oceans",
            "url": "https://example.com/climate-oceans",
            "description": "Impact of warming on marine life",
            "content": "Ocean temperatures have risen significantly..."
        },
        {
            "title": "Marine Biodiversity Under Threat",
            "url": "https://example.com/marine-biodiversity",
            "description": "Species at risk from climate change",
            "content": "Many marine species face extinction..."
        }
    ]
    hm.save_search_results(session_id, search_results)
    print(f"  ✓ Saved {len(search_results)} search results\n")

    # Step 4: Save processing steps
    print("Step 4: Save data processing")
    processed_data = [
        {
            "step": "Data Extraction",
            "timestamp": "2024-01-15T14:00:00",
            "input": "HTML pages",
            "output": "Structured data",
            "logs": "Extracted data from 2 sources"
        },
        {
            "step": "Analysis",
            "timestamp": "2024-01-15T14:05:00",
            "input": "Structured data",
            "output": "Analysis results",
            "logs": "Identified 5 key trends"
        }
    ]
    hm.save_processed_data(session_id, processed_data)
    print(f"  ✓ Saved {len(processed_data)} processing steps\n")

    # Step 5: Generate and save report
    print("Step 5: Generate final report")
    report = """# Climate Change Impact on Marine Ecosystems

## Executive Summary
This report analyzes the effects of climate change on marine ecosystems based on recent research.

## Key Findings
1. Ocean temperature increases are accelerating
2. Marine biodiversity is declining
3. Coral bleaching events are more frequent
4. Fish migration patterns are changing
5. Ocean acidification is intensifying

## Regional Impacts
- Arctic: Rapid ice loss affecting polar species
- Pacific: Coral reef degradation
- Atlantic: Changes in fish populations

## Recommendations
1. Reduce carbon emissions
2. Establish marine protected areas
3. Monitor ecosystem health
4. Support marine conservation efforts

## Conclusion
Immediate action is needed to protect marine ecosystems from climate change impacts.
"""
    hm.save_report(session_id, report, generate_pdf=True)
    print("  ✓ Report saved\n")

    # Step 6: Save final state
    print("Step 6: Save session state")
    state = {
        "query": prompt,
        "search_count": len(search_results),
        "processing_steps": len(processed_data),
        "report_generated": True,
        "status": "completed",
        "language": config["language"]
    }
    hm.save_state(session_id, state)
    print("  ✓ State saved\n")

    # Step 7: Verify session
    print("Step 7: Verify session data")
    loaded = hm.load_session(session_id)
    print(f"  ✓ Session verified - {len(loaded)} components saved\n")

    print(f"✓ Complete workflow finished: {session_id}\n")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "HistoryManager Examples" + " " * 30 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    try:
        # Run all examples
        example_1_basic_session()
        example_2_japanese_content()
        example_3_load_sessions()
        example_4_session_management()
        example_5_error_handling()
        example_6_complete_workflow()

        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
