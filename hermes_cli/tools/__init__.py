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
