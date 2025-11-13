"""Model management for Ollama integration."""

import logging
import time
from typing import Optional, List, Dict, Any, Iterator, Literal
from pathlib import Path

try:
    import ollama
except ImportError:
    ollama = None

from config import settings

# Configure logging
logger = logging.getLogger(__name__)


class ModelNotFoundError(Exception):
    """Raised when a requested model is not available."""
    pass


class OllamaConnectionError(Exception):
    """Raised when connection to Ollama fails."""
    pass


class ModelManager:
    """
    Manages Ollama model selection and interaction.

    This class provides a high-level interface for working with Ollama models,
    including model management, completion generation, and streaming support.
    """

    # System prompts for different languages and tasks
    SYSTEM_PROMPTS = {
        "ja": {
            "research": "あなたは研究者向けの分析アシスタントです。正確で詳細な情報を提供してください。",
            "summarize": "あなたは要約の専門家です。重要なポイントを簡潔にまとめてください。",
            "verify": "あなたは事実確認の専門家です。情報の正確性を検証してください。",
            "general": "あなたは親切で知識豊富なアシスタントです。"
        },
        "en": {
            "research": "You are a research analyst assistant. Provide accurate and detailed information.",
            "summarize": "You are a summarization expert. Concisely highlight the key points.",
            "verify": "You are a fact-checking expert. Verify the accuracy of information.",
            "general": "You are a helpful and knowledgeable assistant."
        }
    }

    def __init__(
        self,
        base_url: str = None,
        default_model: str = None,
        timeout: int = None,
        max_retries: int = None
    ):
        """
        Initialize ModelManager.

        Args:
            base_url: Ollama API endpoint URL. Defaults to settings.
            default_model: Default model name. Defaults to settings.
            timeout: Request timeout in seconds. Defaults to settings.
            max_retries: Maximum number of retry attempts. Defaults to settings.

        Raises:
            ImportError: If ollama package is not installed.
            OllamaConnectionError: If unable to connect to Ollama.
        """
        if ollama is None:
            raise ImportError(
                "ollama package is not installed. "
                "Install it with: pip install ollama"
            )

        self.base_url = base_url or settings.ollama_api_endpoint
        self.default_model = default_model or settings.default_model
        self.timeout = timeout or settings.timeout_seconds
        self.max_retries = max_retries or settings.max_retries

        # Initialize Ollama client
        try:
            self.client = ollama.Client(host=self.base_url)
            logger.info(f"ModelManager initialized with endpoint: {self.base_url}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            raise OllamaConnectionError(f"Cannot connect to Ollama at {self.base_url}: {e}")

    def list_models(self) -> List[str]:
        """
        List all available Ollama models.

        Returns:
            List of model names

        Raises:
            OllamaConnectionError: If unable to retrieve model list
        """
        try:
            response = self.client.list()
            models = [model['name'] for model in response.get('models', [])]
            logger.debug(f"Available models: {models}")
            return models
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            raise OllamaConnectionError(f"Failed to list models: {e}")

    def is_model_available(self, model_name: str) -> bool:
        """
        Check if a specific model is available locally.

        Args:
            model_name: Name of the model to check

        Returns:
            True if model is available, False otherwise
        """
        try:
            available_models = self.list_models()
            # Check for exact match or partial match (e.g., "gpt-oss:20b" matches "gpt-oss:20b")
            return any(model_name in model or model in model_name for model in available_models)
        except Exception as e:
            logger.warning(f"Could not check model availability: {e}")
            return False

    def pull_model(self, model_name: str, show_progress: bool = True) -> bool:
        """
        Download a model from Ollama registry.

        Args:
            model_name: Name of the model to pull
            show_progress: Whether to show download progress

        Returns:
            True if successful, False otherwise

        Raises:
            OllamaConnectionError: If unable to pull model
        """
        try:
            logger.info(f"Pulling model: {model_name}")
            if show_progress:
                print(f"Downloading {model_name}...")

            # Pull model with progress tracking
            for progress in self.client.pull(model_name, stream=True):
                if show_progress and 'status' in progress:
                    status = progress['status']
                    if 'total' in progress and 'completed' in progress:
                        pct = (progress['completed'] / progress['total']) * 100
                        print(f"\r{status}: {pct:.1f}%", end='', flush=True)
                    else:
                        print(f"\r{status}", end='', flush=True)

            if show_progress:
                print("\nDownload complete!")

            logger.info(f"Successfully pulled model: {model_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            raise OllamaConnectionError(f"Failed to pull model {model_name}: {e}")

    def ensure_model_ready(self, model_name: str) -> None:
        """
        Ensure a model is available, pulling it if necessary.

        Args:
            model_name: Name of the model to ensure is ready

        Raises:
            OllamaConnectionError: If unable to prepare model
        """
        if not self.is_model_available(model_name):
            logger.info(f"Model {model_name} not available. Attempting to pull...")
            self.pull_model(model_name)

    def generate(
        self,
        model_name: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 2000,
        top_p: float = 0.9,
        **kwargs
    ) -> str:
        """
        Generate completion from model.

        Args:
            model_name: Name of the model to use
            prompt: Input prompt
            system_prompt: System prompt to set context
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            **kwargs: Additional generation parameters

        Returns:
            Generated text

        Raises:
            ModelNotFoundError: If model is not available
            OllamaConnectionError: If generation fails
        """
        # Ensure model is available
        if not self.is_model_available(model_name):
            logger.warning(f"Model {model_name} not found. Attempting to pull...")
            try:
                self.pull_model(model_name)
            except Exception as e:
                raise ModelNotFoundError(f"Model {model_name} not available and could not be pulled: {e}")

        # Retry logic for transient failures
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Generation attempt {attempt + 1}/{self.max_retries} for model {model_name}")

                # Prepare options
                options = {
                    'temperature': temperature,
                    'top_p': top_p,
                }
                if max_tokens:
                    options['num_predict'] = max_tokens

                # Add any additional kwargs
                options.update(kwargs)

                # Generate completion
                response = self.client.generate(
                    model=model_name,
                    prompt=prompt,
                    system=system_prompt,
                    options=options
                )

                result = response.get('response', '')
                logger.info(f"Generated {len(result)} characters from {model_name}")
                return result

            except Exception as e:
                last_error = e
                logger.warning(f"Generation attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue

        raise OllamaConnectionError(f"Failed to generate after {self.max_retries} attempts: {last_error}")

    def generate_streaming(
        self,
        model_name: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> Iterator[str]:
        """
        Generate streaming completion.

        Args:
            model_name: Name of the model to use
            prompt: Input prompt
            system_prompt: System prompt to set context
            temperature: Sampling temperature
            **kwargs: Additional generation parameters

        Yields:
            Generated text chunks

        Raises:
            ModelNotFoundError: If model is not available
            OllamaConnectionError: If generation fails
        """
        # Ensure model is available
        self.ensure_model_ready(model_name)

        try:
            logger.debug(f"Starting streaming generation with {model_name}")

            # Prepare options
            options = {
                'temperature': temperature,
            }
            options.update(kwargs)

            # Stream generation
            stream = self.client.generate(
                model=model_name,
                prompt=prompt,
                system=system_prompt,
                options=options,
                stream=True
            )

            for chunk in stream:
                if 'response' in chunk:
                    yield chunk['response']

        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            raise OllamaConnectionError(f"Streaming generation failed: {e}")

    def chat(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = 2000,
        **kwargs
    ) -> str:
        """
        Chat completion with message history.

        Args:
            model_name: Name of the model to use
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            Generated response text

        Raises:
            ModelNotFoundError: If model is not available
            OllamaConnectionError: If chat fails
        """
        # Ensure model is available
        self.ensure_model_ready(model_name)

        try:
            logger.debug(f"Chat with {model_name}, {len(messages)} messages")

            # Prepare options
            options = {
                'temperature': temperature,
            }
            if max_tokens:
                options['num_predict'] = max_tokens
            options.update(kwargs)

            # Chat completion
            response = self.client.chat(
                model=model_name,
                messages=messages,
                options=options
            )

            result = response['message']['content']
            logger.info(f"Chat response: {len(result)} characters")
            return result

        except Exception as e:
            logger.error(f"Chat failed: {e}")
            raise OllamaConnectionError(f"Chat failed: {e}")

    def get_system_prompt(
        self,
        language: Literal["ja", "en"],
        task_type: str = "general"
    ) -> str:
        """
        Get system prompt for given language and task type.

        Args:
            language: Language code ('ja' or 'en')
            task_type: Type of task ('research', 'summarize', 'verify', 'general')

        Returns:
            System prompt string
        """
        lang_prompts = self.SYSTEM_PROMPTS.get(language, self.SYSTEM_PROMPTS["en"])
        return lang_prompts.get(task_type, lang_prompts["general"])

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a model.

        Args:
            model_name: Name of the model

        Returns:
            Dictionary with model information

        Raises:
            ModelNotFoundError: If model is not available
        """
        try:
            response = self.client.show(model_name)
            logger.debug(f"Retrieved info for {model_name}")
            return response
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            raise ModelNotFoundError(f"Model {model_name} not found: {e}")

    def switch_model(self, model_name: str) -> None:
        """
        Switch the default model.

        Args:
            model_name: Name of the model to switch to

        Raises:
            ModelNotFoundError: If model is not available
        """
        self.ensure_model_ready(model_name)
        self.default_model = model_name
        logger.info(f"Switched default model to: {model_name}")
