"""
Ollama API client for LLM interaction.

This module provides a client for interacting with Ollama API,
including retry logic, error handling, and proper resource management.
"""

from typing import Optional, List, Dict, Any
import httpx
from dataclasses import dataclass
import logging
import time


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
        self.logger.info(
            f"Initialized OllamaClient with model={config.model}, "
            f"api_base={config.api_base}"
        )

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
        last_exception = None

        for attempt in range(self.config.retry):
            try:
                self.logger.debug(
                    f"Chat request attempt {attempt + 1}/{self.config.retry}"
                )
                response_data = self._make_request(messages, stream)

                # Extract message content from response
                if "message" in response_data and "content" in response_data["message"]:
                    content = response_data["message"]["content"]
                    self.logger.info(
                        f"Successfully received response (length={len(content)})"
                    )
                    return content
                else:
                    raise OllamaAPIError(
                        f"Unexpected response format: {response_data}"
                    )

            except httpx.TimeoutException as e:
                last_exception = OllamaTimeoutError(
                    f"Request timed out after {self.config.timeout_sec}s: {str(e)}"
                )
                self.logger.warning(
                    f"Timeout on attempt {attempt + 1}/{self.config.retry}: {str(e)}"
                )
                if attempt < self.config.retry - 1:
                    time.sleep(1 * (attempt + 1))  # Exponential backoff

            except httpx.HTTPStatusError as e:
                last_exception = OllamaAPIError(
                    f"HTTP error {e.response.status_code}: {str(e)}"
                )
                self.logger.error(
                    f"HTTP error on attempt {attempt + 1}/{self.config.retry}: "
                    f"status={e.response.status_code}, detail={str(e)}"
                )
                if attempt < self.config.retry - 1:
                    time.sleep(1 * (attempt + 1))

            except Exception as e:
                last_exception = OllamaAPIError(f"Unexpected error: {str(e)}")
                self.logger.error(
                    f"Unexpected error on attempt {attempt + 1}/{self.config.retry}: {str(e)}"
                )
                if attempt < self.config.retry - 1:
                    time.sleep(1 * (attempt + 1))

        # All retries exhausted
        self.logger.error(
            f"All {self.config.retry} attempts failed. Raising exception."
        )
        raise last_exception

    def _make_request(
        self, messages: List[Dict[str, str]], stream: bool = False
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Ollama API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            stream: Whether to stream the response

        Returns:
            Response data as dictionary

        Raises:
            httpx.HTTPStatusError: On HTTP errors
            httpx.TimeoutException: On timeout
        """
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": stream
        }

        self.logger.debug(f"POST {self.config.api_base} with payload: {payload}")

        response = self.client.post(
            self.config.api_base,
            json=payload
        )

        # Raise exception for 4xx/5xx status codes
        response.raise_for_status()

        return response.json()

    def close(self):
        """Close HTTP client."""
        self.logger.debug("Closing OllamaClient")
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class OllamaAPIError(Exception):
    """Raised when Ollama API returns an error."""
    pass


class OllamaTimeoutError(Exception):
    """Raised when Ollama API request times out."""
    pass
