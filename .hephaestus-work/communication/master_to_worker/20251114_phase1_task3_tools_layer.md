# Task: Tools Layer Implementation

**Task ID**: phase1_task3_tools_layer
**Priority**: high
**Assigned to**: worker-3
**Dependencies**: phase1_task1_project_setup (directory structure)

## Objective
Implement client wrappers for external tools: Ollama LLM, browser-use for web automation, and container-use for containerized processing.

## Context
The tools layer abstracts external dependencies and provides clean interfaces for the agent workflow. These tools are the primary mechanisms for LLM interaction, web research, and data processing.

Reference design document: `/home/ubuntu/python_project/Hermes/詳細設計書.md` (section 10)

## Requirements

### 1. Implement `tools/ollama_client.py`

Create a client for Ollama API interaction:

```python
from typing import Optional, List, Dict, Any
import httpx
from dataclasses import dataclass
import logging

@dataclass
class OllamaConfig:
    """Configuration for Ollama client."""
    api_base: str
    model: str
    retry: int
    timeout_sec: int

class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, config: OllamaConfig):
        """
        Initialize Ollama client.

        Args:
            config: Ollama configuration including API base, model, retry, timeout
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = httpx.Client(timeout=config.timeout_sec)

    def chat(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        """
        Send chat request to Ollama API.

        Args:
            messages: List of message dicts with 'role' and 'content'
                     Example: [{"role": "user", "content": "Hello"}]
            stream: Whether to stream the response

        Returns:
            Generated text response

        Raises:
            OllamaAPIError: On API communication failure
            OllamaTimeoutError: On timeout
        """
        # Implement with retry logic
        # POST to {api_base}
        # Handle errors and retries according to config.retry
        pass

    def _make_request(self, messages: List[Dict[str, str]],
                     stream: bool = False) -> Dict[str, Any]:
        """Make HTTP request to Ollama API."""
        pass

    def close(self):
        """Close HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class OllamaAPIError(Exception):
    """Raised when Ollama API returns an error."""
    pass


class OllamaTimeoutError(Exception):
    """Raised when Ollama API request times out."""
    pass
```

### 2. Implement `tools/browser_use_client.py`

Create a wrapper for browser-use library:

```python
from typing import List, Dict, Any, Optional
import logging
# from browser_use import BrowserAgent  # Actual import when library available

@dataclass
class BrowserSearchResult:
    """Result from browser search."""
    url: str
    title: str
    content: str
    timestamp: str

class BrowserUseClient:
    """Client for web research using browser-use library."""

    def __init__(self, max_sources: int = 8):
        """
        Initialize browser client.

        Args:
            max_sources: Maximum number of sources to collect per query
        """
        self.max_sources = max_sources
        self.logger = logging.getLogger(__name__)
        # Initialize browser-use agent here

    def search(self, query: str, max_sources: Optional[int] = None) -> List[BrowserSearchResult]:
        """
        Perform web search and extract information.

        Args:
            query: Search query string
            max_sources: Override default max sources for this query

        Returns:
            List of search results with extracted content

        Raises:
            BrowserUseError: On browser automation failure
        """
        # Use browser-use to:
        # 1. Perform search
        # 2. Visit top results
        # 3. Extract relevant content
        # 4. Return structured results
        pass

    def extract_content(self, url: str) -> Optional[BrowserSearchResult]:
        """
        Extract content from a specific URL.

        Args:
            url: Target URL

        Returns:
            Extracted content or None if failed
        """
        pass

    def close(self):
        """Clean up browser resources."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class BrowserUseError(Exception):
    """Raised when browser automation fails."""
    pass
```

### 3. Implement `tools/container_use_client.py`

Create a wrapper for container-use (dagger-io):

```python
from typing import List, Optional
import logging
# import dagger  # Actual import when available

class ContainerUseClient:
    """Client for containerized processing using dagger-io."""

    def __init__(self):
        """Initialize container client."""
        self.logger = logging.getLogger(__name__)
        # Initialize dagger client

    def normalize_texts(self, texts: List[str]) -> List[str]:
        """
        Normalize and preprocess texts in container environment.

        This runs text processing tasks in an isolated container to ensure
        consistent results and security.

        Args:
            texts: List of raw text content to process

        Returns:
            List of normalized/processed texts

        Raises:
            ContainerUseError: On container execution failure
        """
        # Use dagger to:
        # 1. Create container with text processing tools
        # 2. Mount texts as input
        # 3. Run normalization script
        # 4. Extract processed results
        pass

    def execute_script(self, script: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute arbitrary script in container environment.

        Args:
            script: Script content to execute
            inputs: Input data for the script

        Returns:
            Output data from script execution

        Raises:
            ContainerUseError: On container execution failure
        """
        pass

    def close(self):
        """Clean up container resources."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class ContainerUseError(Exception):
    """Raised when container execution fails."""
    pass
```

### 4. Update `tools/__init__.py`

```python
"""
Tools package for Hermes.

This package provides client interfaces for external tools:
- OllamaClient: LLM interaction via Ollama API
- BrowserUseClient: Web research automation
- ContainerUseClient: Containerized data processing
"""

from .ollama_client import (
    OllamaClient,
    OllamaConfig,
    OllamaAPIError,
    OllamaTimeoutError,
)
from .browser_use_client import (
    BrowserUseClient,
    BrowserSearchResult,
    BrowserUseError,
)
from .container_use_client import (
    ContainerUseClient,
    ContainerUseError,
)

__all__ = [
    "OllamaClient",
    "OllamaConfig",
    "OllamaAPIError",
    "OllamaTimeoutError",
    "BrowserUseClient",
    "BrowserSearchResult",
    "BrowserUseError",
    "ContainerUseClient",
    "ContainerUseError",
]
```

## Implementation Notes

### Error Handling
- All clients should have custom exception classes
- Implement proper retry logic for transient failures
- Log all errors with appropriate detail level

### Resource Management
- Implement context manager protocol (`__enter__`/`__exit__`)
- Ensure proper cleanup of HTTP clients, browser instances, containers
- Handle connection pooling appropriately

### Logging
- Use Python logging module
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Include relevant context (query, URL, error details)

### Type Hints
- Use proper type hints for all parameters and return values
- Use Optional[] for nullable values
- Use List[], Dict[] for collections

## Expected Output

All files in `/home/ubuntu/python_project/Hermes/hermes_cli/tools/`:
1. `ollama_client.py` - Complete Ollama API client with retry logic
2. `browser_use_client.py` - Browser automation wrapper
3. `container_use_client.py` - Container execution wrapper
4. `__init__.py` - Package exports

## Resources

- Design document section: 10
- Ollama API docs: https://github.com/ollama/ollama/blob/main/docs/api.md
- httpx documentation: https://www.python-httpx.org/
- browser-use library (if available)
- dagger-io documentation: https://docs.dagger.io/

## Success Criteria

- All three client classes implemented with proper interfaces
- Error handling and retry logic in place
- Context manager protocol implemented
- Type hints and docstrings complete
- Custom exceptions defined for each client
- Can be imported without errors: `from hermes_cli.tools import OllamaClient, BrowserUseClient, ContainerUseClient`
