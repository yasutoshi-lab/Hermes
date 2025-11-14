# Task: Persistence Layer Implementation

**Task ID**: phase1_task2_persistence_layer
**Priority**: high
**Assigned to**: worker-2
**Dependencies**: phase1_task1_project_setup (directory structure)

## Objective
Implement the complete persistence layer for Hermes, including file path management and all repository classes for handling tasks, history, logs, and configuration.

## Context
The persistence layer is the foundation for data storage in Hermes. It provides file-based storage using YAML for structured data (tasks, history metadata, config) and text files for logs. All data is stored under `~/.hermes/` directory.

Reference design document: `/home/ubuntu/python_project/Hermes/詳細設計書.md` (sections 4.1, 5, 6)

## Requirements

### 1. Implement `persistence/file_paths.py`

Create a module that provides path management:

```python
from pathlib import Path
from typing import Optional

class FilePaths:
    """Manages all file paths for Hermes data storage."""

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize file paths.

        Args:
            base_path: Override default ~/.hermes/ path (useful for testing)
        """
        # Detect OS and set appropriate base path
        # Linux/Mac: ~/.hermes/
        # Windows: %USERPROFILE%\.hermes\
        pass

    @property
    def base(self) -> Path:
        """Base directory (~/.hermes/)"""
        pass

    @property
    def cache(self) -> Path:
        """Cache directory"""
        pass

    @property
    def config_file(self) -> Path:
        """Config file path (config.yaml)"""
        pass

    @property
    def task_dir(self) -> Path:
        """Task directory"""
        pass

    @property
    def log_dir(self) -> Path:
        """Log directory"""
        pass

    @property
    def debug_log_dir(self) -> Path:
        """Debug log directory"""
        pass

    @property
    def history_dir(self) -> Path:
        """History directory"""
        pass

    def ensure_directories(self) -> None:
        """Create all directories if they don't exist."""
        pass

    def task_file(self, task_id: str) -> Path:
        """Get path for specific task file."""
        pass

    def history_meta_file(self, task_id: str) -> Path:
        """Get path for history metadata file."""
        pass

    def history_report_file(self, task_id: str) -> Path:
        """Get path for history report file."""
        pass
```

### 2. Implement `persistence/config_repository.py`

Handle config.yaml read/write:

```python
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass
class OllamaConfig:
    api_base: str
    model: str
    retry: int
    timeout_sec: int

@dataclass
class ValidationConfig:
    min_loops: int
    max_loops: int

@dataclass
class SearchConfig:
    min_sources: int
    max_sources: int

@dataclass
class LoggingConfig:
    level: str
    log_dir: str
    debug_log_dir: str

@dataclass
class Config:
    ollama: OllamaConfig
    language: str
    validation: ValidationConfig
    search: SearchConfig
    logging: LoggingConfig
    cli: dict

class ConfigRepository:
    """Handles configuration file persistence."""

    def load(self, config_path: Path) -> Config:
        """Load config from YAML file."""
        pass

    def save(self, config: Config, config_path: Path) -> None:
        """Save config to YAML file."""
        pass

    def create_default(self) -> Config:
        """Create default configuration."""
        # Use values from section 5.1 of design doc
        pass
```

### 3. Implement `persistence/task_repository.py`

Handle task YAML files:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional
from pathlib import Path
import yaml

Status = Literal["scheduled", "running", "done", "failed"]

@dataclass
class Task:
    id: str
    prompt: str
    created_at: datetime
    status: Status
    options: dict

class TaskRepository:
    """Handles task file persistence."""

    def __init__(self, file_paths: FilePaths):
        self.file_paths = file_paths

    def create(self, prompt: str, options: dict) -> Task:
        """Create new task with auto-generated ID."""
        # Generate ID format: YYYY-NNNN (e.g., 2025-0001)
        pass

    def save(self, task: Task) -> None:
        """Save task to YAML file."""
        pass

    def load(self, task_id: str) -> Optional[Task]:
        """Load task from file."""
        pass

    def list_all(self) -> list[Task]:
        """List all tasks."""
        pass

    def delete(self, task_id: str) -> None:
        """Delete task file."""
        pass

    def update_status(self, task_id: str, status: Status) -> None:
        """Update task status."""
        pass
```

### 4. Implement `persistence/history_repository.py`

Handle history metadata and reports:

```python
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
import yaml

@dataclass
class HistoryMeta:
    id: str
    prompt: str
    created_at: datetime
    finished_at: datetime
    model: str
    language: str
    validation_loops: int
    source_count: int
    report_file: str

class HistoryRepository:
    """Handles history metadata and report files."""

    def __init__(self, file_paths: FilePaths):
        self.file_paths = file_paths

    def save_meta(self, meta: HistoryMeta) -> None:
        """Save history metadata."""
        pass

    def save_report(self, task_id: str, report_content: str) -> None:
        """Save report markdown file."""
        pass

    def load_meta(self, task_id: str) -> Optional[HistoryMeta]:
        """Load history metadata."""
        pass

    def load_report(self, task_id: str) -> Optional[str]:
        """Load report content."""
        pass

    def list_all(self, limit: Optional[int] = None) -> list[HistoryMeta]:
        """List all history entries, optionally limited."""
        pass

    def delete(self, task_id: str) -> None:
        """Delete history metadata and report."""
        pass

    def export_report(self, task_id: str, dest_path: Path) -> None:
        """Copy report to destination path."""
        pass
```

### 5. Implement `persistence/log_repository.py`

Handle log file operations:

```python
from pathlib import Path
from datetime import datetime
from typing import Iterator, Optional

class LogRepository:
    """Handles log file operations."""

    def __init__(self, file_paths: FilePaths):
        self.file_paths = file_paths

    def get_log_file(self, date: Optional[datetime] = None, debug: bool = False) -> Path:
        """Get log file path for specific date."""
        # Format: hermes-YYYYMMDD.log
        pass

    def write_log(self, level: str, component: str, message: str,
                  task_id: Optional[str] = None, **kwargs) -> None:
        """Write formatted log entry."""
        # Format: ISO8601時刻 [レベル] [コンポーネント] メッセージ key=value...
        pass

    def tail(self, lines: int = 10, debug: bool = False) -> list[str]:
        """Get last N lines from log file."""
        pass

    def stream(self, debug: bool = False) -> Iterator[str]:
        """Stream log file in real-time."""
        pass
```

## Expected Output

All files in `/home/ubuntu/python_project/Hermes/hermes_cli/persistence/`:
1. `file_paths.py` - Complete with OS detection
2. `config_repository.py` - With all dataclasses and methods
3. `task_repository.py` - With Task model and CRUD operations
4. `history_repository.py` - With HistoryMeta model and operations
5. `log_repository.py` - With log formatting and streaming

## Resources

- Design document sections: 4.1, 5, 6
- PyYAML documentation
- Python pathlib documentation

## Success Criteria

- All repository classes implemented with proper type hints
- YAML serialization/deserialization working correctly
- OS-specific path handling for Windows and Linux
- Proper error handling for file operations
- All methods have docstrings
