"""External tool clients for Hermes"""

from hermes_cli.tools.ollama_client import OllamaClient
from hermes_cli.tools.container_use_client import SearxNGClient

__all__ = ["OllamaClient", "SearxNGClient"]
