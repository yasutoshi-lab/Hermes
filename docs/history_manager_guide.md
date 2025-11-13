# History Manager Guide

## Overview

The `HistoryManager` module provides comprehensive functionality for managing research session history in the Hermes research assistant system. It enables saving and retrieving session data including prompts, search results, processing logs, and final reports.

## Features

- **Session Management**: Create, load, list, and delete research sessions
- **Structured Storage**: Organize session data in a consistent directory structure
- **Multi-format Support**: Save data as Markdown and JSON formats
- **UTF-8 Encoding**: Full support for Japanese and other Unicode characters
- **Error Handling**: Robust error handling with custom exceptions
- **Cleanup Utilities**: Automatic cleanup of old sessions

## Session Structure

Each session creates a timestamped directory with the following files:

```
sessions/session_<timestamp>/
├── input.md           # User prompt and configuration
├── search_results.md  # Web search results
├── processed_data.md  # Container processing results
├── report.md          # Final report
├── report.pdf         # PDF version (if generated)
└── state.json         # Complete session state
```

## Installation

The HistoryManager is part of the Hermes modules package:

```python
from modules.history_manager import HistoryManager
```

## Basic Usage

### Creating a HistoryManager

```python
from modules.history_manager import HistoryManager

# Use default path (./sessions)
hm = HistoryManager()

# Or specify custom path
hm = HistoryManager(base_path="/path/to/sessions")
```

### Creating a New Session

```python
# Create a new session
session_id = hm.create_session()
print(f"Created session: {session_id}")
# Output: Created session: session_20251113_123456
```

### Saving User Input

```python
# Save user prompt and configuration
prompt = "What are the latest developments in quantum computing?"
config = {
    "language": "en",
    "model_name": "gpt-oss:20b",
    "search_limit": 10
}

hm.save_input(session_id, prompt, config)
```

### Saving Search Results

```python
# Save web search results
search_results = [
    {
        "title": "Quantum Computing Breakthrough",
        "url": "https://example.com/quantum",
        "description": "Latest quantum computing developments",
        "content": "Full article content here..."
    },
    {
        "title": "Quantum Research Paper",
        "url": "https://arxiv.org/quantum",
        "description": "Recent quantum computing paper"
    }
]

hm.save_search_results(session_id, search_results)
```

### Saving Processed Data

```python
# Save processing steps and logs
processed_data = [
    {
        "step": "HTML Parsing",
        "timestamp": "2024-01-15T10:30:00",
        "input": "Raw HTML content",
        "output": "Parsed text content",
        "logs": "Parsing completed successfully"
    },
    {
        "step": "Entity Extraction",
        "timestamp": "2024-01-15T10:31:00",
        "input": "Parsed text content",
        "output": "Extracted entities: [...]",
        "logs": "Found 15 entities"
    }
]

hm.save_processed_data(session_id, processed_data)
```

### Saving Final Report

```python
# Save final report
report = """
# Research Report: Quantum Computing

## Executive Summary
This report analyzes recent developments in quantum computing...

## Key Findings
1. Breakthrough in error correction
2. New quantum algorithms developed
3. Increased qubit stability

## Conclusion
Quantum computing continues to advance rapidly...
"""

hm.save_report(session_id, report)

# Or save with PDF generation flag
hm.save_report(session_id, report, generate_pdf=True)
```

### Saving Session State

```python
# Save complete session state
state = {
    "messages": [
        {"role": "user", "content": "What is quantum computing?"},
        {"role": "assistant", "content": "Quantum computing is..."}
    ],
    "query": "quantum computing developments",
    "search_results": search_results,
    "language": "en",
    "model_name": "gpt-oss:20b"
}

hm.save_state(session_id, state)
```

## Loading Sessions

### Load a Previous Session

```python
# Load all data from a session
session_data = hm.load_session(session_id)

# Access different components
if "input" in session_data:
    print("Input:", session_data["input"])

if "search_results" in session_data:
    print("Search Results:", session_data["search_results"])

if "report" in session_data:
    print("Report:", session_data["report"])

if "state" in session_data:
    state_dict = session_data["state"]
    print("State:", state_dict)
```

### List All Sessions

```python
# Get list of all sessions (newest first)
sessions = hm.list_sessions()

for session_id in sessions:
    print(f"Session: {session_id}")

# Load each session to get details
for session_id in sessions[:5]:  # First 5 sessions
    session_data = hm.load_session(session_id)
    print(f"  Path: {session_data['session_path']}")
```

## Session Management

### Delete a Specific Session

```python
# Delete a session
hm.delete_session(session_id)
print(f"Deleted session: {session_id}")
```

### Cleanup Old Sessions

```python
# Keep only the 10 most recent sessions
deleted_count = hm.cleanup_old_sessions(keep_last_n=10)
print(f"Deleted {deleted_count} old sessions")

# Keep only the 5 most recent sessions
hm.cleanup_old_sessions(keep_last_n=5)
```

## Error Handling

The HistoryManager uses custom exceptions for better error handling:

```python
from modules.history_manager import (
    HistoryManager,
    HistoryManagerError,
    SessionNotFoundError
)

try:
    hm = HistoryManager()
    session_id = hm.create_session()
    hm.save_input(session_id, "Test prompt", {})

except SessionNotFoundError as e:
    print(f"Session not found: {e}")

except HistoryManagerError as e:
    print(f"History manager error: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

## Complete Example

```python
from modules.history_manager import HistoryManager, SessionNotFoundError

def run_research_session():
    """Complete research session example."""

    # Initialize history manager
    hm = HistoryManager(base_path="./sessions")

    try:
        # 1. Create new session
        session_id = hm.create_session()
        print(f"Started session: {session_id}")

        # 2. Save user input
        prompt = "日本の量子コンピューティング研究について教えてください"
        config = {
            "language": "ja",
            "model_name": "gpt-oss:20b"
        }
        hm.save_input(session_id, prompt, config)

        # 3. Perform search and save results
        search_results = [
            {
                "title": "日本の量子研究",
                "url": "https://example.jp/quantum",
                "description": "日本における量子コンピューティング研究の現状",
                "content": "詳細な研究内容..."
            }
        ]
        hm.save_search_results(session_id, search_results)

        # 4. Process data and save
        processed_data = [
            {
                "step": "データ解析",
                "timestamp": "2024-01-15T15:00:00",
                "input": "検索結果",
                "output": "解析済みデータ",
                "logs": "処理完了"
            }
        ]
        hm.save_processed_data(session_id, processed_data)

        # 5. Generate and save report
        report = """
# 量子コンピューティング研究レポート

## 概要
日本における量子コンピューティング研究の最新動向...

## 主要な発見
1. エラー訂正技術の進展
2. 新しい量子アルゴリズムの開発
3. 量子ビットの安定性向上

## 結論
日本の量子コンピューティング研究は着実に進展している...
"""
        hm.save_report(session_id, report)

        # 6. Save complete state
        state = {
            "query": prompt,
            "language": config["language"],
            "model_name": config["model_name"],
            "results_count": len(search_results)
        }
        hm.save_state(session_id, state)

        print(f"Session completed: {session_id}")
        return session_id

    except SessionNotFoundError as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def review_recent_sessions():
    """Review recent research sessions."""

    hm = HistoryManager()

    # List all sessions
    sessions = hm.list_sessions()
    print(f"Found {len(sessions)} sessions\n")

    # Review the 3 most recent sessions
    for session_id in sessions[:3]:
        print(f"=== {session_id} ===")

        try:
            session_data = hm.load_session(session_id)

            # Display input if available
            if "input" in session_data:
                lines = session_data["input"].split('\n')
                print(f"Input preview: {lines[0] if lines else 'N/A'}")

            # Display report if available
            if "report" in session_data:
                report_lines = session_data["report"].split('\n')
                print(f"Report preview: {report_lines[0] if report_lines else 'N/A'}")

            print()

        except SessionNotFoundError:
            print(f"Could not load session\n")

if __name__ == "__main__":
    # Run a complete session
    session_id = run_research_session()

    # Review sessions
    print("\n" + "="*50 + "\n")
    review_recent_sessions()

    # Cleanup old sessions (keep last 10)
    hm = HistoryManager()
    deleted = hm.cleanup_old_sessions(keep_last_n=10)
    print(f"Cleaned up {deleted} old sessions")
```

## Best Practices

1. **Always Create Sessions First**: Call `create_session()` before saving any data
2. **Use Try-Except Blocks**: Handle `SessionNotFoundError` and `HistoryManagerError`
3. **Save State Regularly**: Save session state after major processing steps
4. **Cleanup Periodically**: Use `cleanup_old_sessions()` to manage disk space
5. **UTF-8 Support**: The module fully supports Japanese and other Unicode characters
6. **Structured Data**: Use dictionaries with consistent keys for processed data

## Configuration

The HistoryManager can be configured through initialization:

```python
# Default configuration
hm = HistoryManager()  # Uses ./sessions

# Custom configuration
hm = HistoryManager(
    base_path="/custom/path/to/sessions"
)
```

## Thread Safety

The current implementation is not thread-safe. If you need to use HistoryManager in a multi-threaded environment, implement external locking:

```python
import threading

lock = threading.Lock()
hm = HistoryManager()

with lock:
    session_id = hm.create_session()
    hm.save_input(session_id, prompt, config)
```

## Performance Considerations

- **File I/O**: All operations involve file system I/O
- **Large Content**: Very long content is automatically truncated in search results
- **Session Count**: Consider regular cleanup for systems with many sessions
- **JSON Serialization**: State saving uses JSON, which may not handle all Python objects

## API Reference

### HistoryManager Class

#### `__init__(base_path: Optional[Union[str, Path]] = None)`
Initialize the HistoryManager.

#### `create_session() -> str`
Create a new session directory and return the session ID.

#### `save_input(session_id: str, prompt: str, config: Dict[str, Any]) -> None`
Save user input and configuration.

#### `save_search_results(session_id: str, results: List[Dict[str, Any]]) -> None`
Save web search results.

#### `save_processed_data(session_id: str, data: List[Dict[str, Any]]) -> None`
Save processed data and logs.

#### `save_report(session_id: str, report: str, generate_pdf: bool = False) -> None`
Save final report.

#### `save_state(session_id: str, state: Dict[str, Any]) -> None`
Save complete session state.

#### `load_session(session_id: str) -> Dict[str, Any]`
Load a previous session's data.

#### `list_sessions() -> List[str]`
List all session IDs (newest first).

#### `cleanup_old_sessions(keep_last_n: int = 10) -> int`
Delete old sessions, keeping only the last N.

#### `delete_session(session_id: str) -> None`
Delete a specific session.

### Exceptions

#### `HistoryManagerError`
Base exception for HistoryManager errors.

#### `SessionNotFoundError`
Raised when a session ID is not found.

## Troubleshooting

### "Session not found" Error
```python
# Check if session exists before operations
sessions = hm.list_sessions()
if session_id in sessions:
    hm.save_input(session_id, prompt, config)
```

### Permission Errors
```python
# Ensure write permissions for sessions directory
import os
os.chmod("./sessions", 0o755)
```

### UTF-8 Encoding Issues
The module uses UTF-8 encoding by default. If you encounter encoding issues, ensure your input data is properly encoded as UTF-8.

## Future Enhancements

Potential future improvements:

1. **PDF Generation**: Full PDF generation using reportlab or similar
2. **Compression**: Compress old sessions to save space
3. **Search**: Search through session history
4. **Export**: Export sessions in various formats
5. **Async Support**: Async/await API for non-blocking I/O
6. **Database Backend**: Optional database storage instead of files

## Support

For issues or questions about the HistoryManager module, please refer to the main Hermes documentation or contact the development team.
