"""Unit tests for ModelManager."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.modules.model_manager import (
    ModelManager,
    ModelNotFoundError,
    OllamaConnectionError
)


class TestModelManager:
    """Test suite for ModelManager class."""

    @pytest.fixture
    def mock_ollama_client(self):
        """Create a mock Ollama client."""
        with patch('src.modules.model_manager.ollama') as mock_ollama:
            mock_client = MagicMock()
            mock_ollama.Client.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def model_manager(self, mock_ollama_client):
        """Create a ModelManager instance with mocked client."""
        return ModelManager(base_url="http://localhost:11434")

    def test_initialization(self, mock_ollama_client):
        """Test ModelManager initialization."""
        manager = ModelManager(
            base_url="http://localhost:11434",
            default_model="gpt-oss:20b"
        )
        assert manager.base_url == "http://localhost:11434"
        assert manager.default_model == "gpt-oss:20b"
        assert manager.client is not None

    def test_initialization_without_ollama(self):
        """Test initialization fails gracefully without ollama package."""
        with patch('src.modules.model_manager.ollama', None):
            with pytest.raises(ImportError):
                ModelManager()

    def test_list_models(self, model_manager, mock_ollama_client):
        """Test listing available models."""
        mock_ollama_client.list.return_value = {
            'models': [
                {'name': 'gpt-oss:20b'},
                {'name': 'llama2:7b'},
                {'name': 'mistral:latest'}
            ]
        }

        models = model_manager.list_models()
        assert len(models) == 3
        assert 'gpt-oss:20b' in models
        assert 'llama2:7b' in models
        assert 'mistral:latest' in models

    def test_list_models_connection_error(self, model_manager, mock_ollama_client):
        """Test list_models handles connection errors."""
        mock_ollama_client.list.side_effect = Exception("Connection failed")

        with pytest.raises(OllamaConnectionError):
            model_manager.list_models()

    def test_is_model_available_true(self, model_manager, mock_ollama_client):
        """Test checking if model is available."""
        mock_ollama_client.list.return_value = {
            'models': [{'name': 'gpt-oss:20b'}]
        }

        assert model_manager.is_model_available('gpt-oss:20b') is True

    def test_is_model_available_false(self, model_manager, mock_ollama_client):
        """Test checking if model is not available."""
        mock_ollama_client.list.return_value = {
            'models': [{'name': 'llama2:7b'}]
        }

        assert model_manager.is_model_available('gpt-oss:20b') is False

    def test_pull_model_success(self, model_manager, mock_ollama_client):
        """Test pulling a model successfully."""
        mock_ollama_client.pull.return_value = iter([
            {'status': 'downloading', 'completed': 50, 'total': 100},
            {'status': 'downloading', 'completed': 100, 'total': 100},
            {'status': 'success'}
        ])

        result = model_manager.pull_model('gpt-oss:20b', show_progress=False)
        assert result is True

    def test_pull_model_failure(self, model_manager, mock_ollama_client):
        """Test pull_model handles errors."""
        mock_ollama_client.pull.side_effect = Exception("Download failed")

        with pytest.raises(OllamaConnectionError):
            model_manager.pull_model('invalid-model')

    def test_ensure_model_ready_already_available(self, model_manager, mock_ollama_client):
        """Test ensure_model_ready when model already exists."""
        mock_ollama_client.list.return_value = {
            'models': [{'name': 'gpt-oss:20b'}]
        }

        # Should not raise and not call pull
        model_manager.ensure_model_ready('gpt-oss:20b')
        mock_ollama_client.pull.assert_not_called()

    def test_ensure_model_ready_needs_pull(self, model_manager, mock_ollama_client):
        """Test ensure_model_ready pulls model if not available."""
        mock_ollama_client.list.return_value = {'models': []}
        mock_ollama_client.pull.return_value = iter([{'status': 'success'}])

        model_manager.ensure_model_ready('gpt-oss:20b')
        mock_ollama_client.pull.assert_called_once()

    def test_generate_basic(self, model_manager, mock_ollama_client):
        """Test basic text generation."""
        mock_ollama_client.list.return_value = {
            'models': [{'name': 'gpt-oss:20b'}]
        }
        mock_ollama_client.generate.return_value = {
            'response': 'This is a generated response.'
        }

        result = model_manager.generate(
            model_name='gpt-oss:20b',
            prompt='Hello, how are you?'
        )

        assert result == 'This is a generated response.'
        mock_ollama_client.generate.assert_called_once()

    def test_generate_with_system_prompt(self, model_manager, mock_ollama_client):
        """Test generation with system prompt."""
        mock_ollama_client.list.return_value = {
            'models': [{'name': 'gpt-oss:20b'}]
        }
        mock_ollama_client.generate.return_value = {
            'response': 'Response with context.'
        }

        result = model_manager.generate(
            model_name='gpt-oss:20b',
            prompt='Test prompt',
            system_prompt='You are a helpful assistant.'
        )

        assert result == 'Response with context.'
        call_args = mock_ollama_client.generate.call_args
        assert call_args[1]['system'] == 'You are a helpful assistant.'

    def test_generate_with_parameters(self, model_manager, mock_ollama_client):
        """Test generation with custom parameters."""
        mock_ollama_client.list.return_value = {
            'models': [{'name': 'gpt-oss:20b'}]
        }
        mock_ollama_client.generate.return_value = {
            'response': 'Parameterized response.'
        }

        result = model_manager.generate(
            model_name='gpt-oss:20b',
            prompt='Test',
            temperature=0.5,
            max_tokens=500,
            top_p=0.8
        )

        call_args = mock_ollama_client.generate.call_args
        assert call_args[1]['options']['temperature'] == 0.5
        assert call_args[1]['options']['num_predict'] == 500
        assert call_args[1]['options']['top_p'] == 0.8

    def test_generate_retry_on_failure(self, model_manager, mock_ollama_client):
        """Test generation retries on transient failures."""
        mock_ollama_client.list.return_value = {
            'models': [{'name': 'gpt-oss:20b'}]
        }

        # First call fails, second succeeds
        mock_ollama_client.generate.side_effect = [
            Exception("Temporary error"),
            {'response': 'Success after retry'}
        ]

        result = model_manager.generate(
            model_name='gpt-oss:20b',
            prompt='Test'
        )

        assert result == 'Success after retry'
        assert mock_ollama_client.generate.call_count == 2

    def test_generate_max_retries_exceeded(self, model_manager, mock_ollama_client):
        """Test generation fails after max retries."""
        mock_ollama_client.list.return_value = {
            'models': [{'name': 'gpt-oss:20b'}]
        }
        mock_ollama_client.generate.side_effect = Exception("Persistent error")

        with pytest.raises(OllamaConnectionError):
            model_manager.generate(
                model_name='gpt-oss:20b',
                prompt='Test'
            )

    def test_generate_streaming(self, model_manager, mock_ollama_client):
        """Test streaming generation."""
        mock_ollama_client.list.return_value = {
            'models': [{'name': 'gpt-oss:20b'}]
        }
        mock_ollama_client.generate.return_value = iter([
            {'response': 'Hello'},
            {'response': ' world'},
            {'response': '!'}
        ])

        chunks = list(model_manager.generate_streaming(
            model_name='gpt-oss:20b',
            prompt='Say hello'
        ))

        assert chunks == ['Hello', ' world', '!']
        call_args = mock_ollama_client.generate.call_args
        assert call_args[1]['stream'] is True

    def test_chat(self, model_manager, mock_ollama_client):
        """Test chat completion."""
        mock_ollama_client.list.return_value = {
            'models': [{'name': 'gpt-oss:20b'}]
        }
        mock_ollama_client.chat.return_value = {
            'message': {'content': 'Chat response'}
        }

        messages = [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi there!'},
            {'role': 'user', 'content': 'How are you?'}
        ]

        result = model_manager.chat(
            model_name='gpt-oss:20b',
            messages=messages
        )

        assert result == 'Chat response'
        mock_ollama_client.chat.assert_called_once()

    def test_get_system_prompt_japanese(self, model_manager):
        """Test getting Japanese system prompt."""
        prompt = model_manager.get_system_prompt('ja', 'research')
        assert 'アシスタント' in prompt or '研究者' in prompt

    def test_get_system_prompt_english(self, model_manager):
        """Test getting English system prompt."""
        prompt = model_manager.get_system_prompt('en', 'research')
        assert 'research' in prompt.lower() or 'analyst' in prompt.lower()

    def test_get_system_prompt_default_task(self, model_manager):
        """Test getting default task system prompt."""
        prompt = model_manager.get_system_prompt('en', 'general')
        assert len(prompt) > 0

    def test_get_model_info(self, model_manager, mock_ollama_client):
        """Test getting model information."""
        mock_ollama_client.show.return_value = {
            'modelfile': 'FROM gpt-oss:20b',
            'parameters': 'temperature 0.7',
            'template': 'template text'
        }

        info = model_manager.get_model_info('gpt-oss:20b')
        assert 'modelfile' in info
        assert 'parameters' in info

    def test_get_model_info_not_found(self, model_manager, mock_ollama_client):
        """Test get_model_info with non-existent model."""
        mock_ollama_client.show.side_effect = Exception("Model not found")

        with pytest.raises(ModelNotFoundError):
            model_manager.get_model_info('nonexistent-model')

    def test_switch_model(self, model_manager, mock_ollama_client):
        """Test switching default model."""
        mock_ollama_client.list.return_value = {
            'models': [{'name': 'llama2:7b'}]
        }

        initial_model = model_manager.default_model
        model_manager.switch_model('llama2:7b')

        assert model_manager.default_model == 'llama2:7b'
        assert model_manager.default_model != initial_model


class TestSystemPrompts:
    """Test system prompts functionality."""

    @pytest.fixture
    def model_manager(self):
        """Create ModelManager with mocked ollama."""
        with patch('src.modules.model_manager.ollama') as mock_ollama:
            mock_client = MagicMock()
            mock_ollama.Client.return_value = mock_client
            return ModelManager()

    def test_all_task_types_japanese(self, model_manager):
        """Test all Japanese task type prompts exist."""
        task_types = ['research', 'summarize', 'verify', 'general']
        for task_type in task_types:
            prompt = model_manager.get_system_prompt('ja', task_type)
            assert isinstance(prompt, str)
            assert len(prompt) > 0

    def test_all_task_types_english(self, model_manager):
        """Test all English task type prompts exist."""
        task_types = ['research', 'summarize', 'verify', 'general']
        for task_type in task_types:
            prompt = model_manager.get_system_prompt('en', task_type)
            assert isinstance(prompt, str)
            assert len(prompt) > 0

    def test_invalid_task_type_defaults_to_general(self, model_manager):
        """Test invalid task type returns general prompt."""
        prompt = model_manager.get_system_prompt('en', 'invalid_type')
        general_prompt = model_manager.get_system_prompt('en', 'general')
        assert prompt == general_prompt


class TestErrorHandling:
    """Test error handling in ModelManager."""

    @pytest.fixture
    def model_manager(self):
        """Create ModelManager with mocked ollama."""
        with patch('src.modules.model_manager.ollama') as mock_ollama:
            mock_client = MagicMock()
            mock_ollama.Client.return_value = mock_client
            yield ModelManager(), mock_client

    def test_connection_error_on_init(self):
        """Test connection error during initialization."""
        with patch('src.modules.model_manager.ollama') as mock_ollama:
            mock_ollama.Client.side_effect = Exception("Connection refused")
            with pytest.raises(OllamaConnectionError):
                ModelManager()

    def test_model_not_found_error(self, model_manager):
        """Test ModelNotFoundError is raised appropriately."""
        manager, mock_client = model_manager
        mock_client.list.return_value = {'models': []}
        mock_client.pull.side_effect = Exception("Pull failed")

        with pytest.raises(ModelNotFoundError):
            manager.generate('nonexistent-model', 'test prompt')

    def test_chat_error_handling(self, model_manager):
        """Test chat error handling."""
        manager, mock_client = model_manager
        mock_client.list.return_value = {'models': [{'name': 'test'}]}
        mock_client.chat.side_effect = Exception("Chat failed")

        with pytest.raises(OllamaConnectionError):
            manager.chat('test', [{'role': 'user', 'content': 'hi'}])

    def test_streaming_error_handling(self, model_manager):
        """Test streaming error handling."""
        manager, mock_client = model_manager
        mock_client.list.return_value = {'models': [{'name': 'test'}]}
        mock_client.generate.side_effect = Exception("Streaming failed")

        with pytest.raises(OllamaConnectionError):
            list(manager.generate_streaming('test', 'test prompt'))
