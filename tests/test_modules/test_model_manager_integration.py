"""
Integration tests for ModelManager with real Ollama instance.

These tests require Ollama to be running locally.
Run with: pytest tests/test_modules/test_model_manager_integration.py -v
Skip with: pytest -m "not integration"
"""

import pytest
from src.modules.model_manager import ModelManager, OllamaConnectionError


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestModelManagerIntegration:
    """Integration tests for ModelManager with real Ollama."""

    @pytest.fixture(scope="class")
    def model_manager(self):
        """
        Create a ModelManager instance for integration testing.

        This fixture attempts to connect to a local Ollama instance.
        Tests will be skipped if Ollama is not available.
        """
        try:
            manager = ModelManager(base_url="http://localhost:11434")
            # Verify connection by listing models
            manager.list_models()
            return manager
        except (OllamaConnectionError, Exception) as e:
            pytest.skip(f"Ollama not available: {e}")

    def test_connection(self, model_manager):
        """Test that we can connect to Ollama."""
        assert model_manager is not None
        assert model_manager.client is not None

    def test_list_models(self, model_manager):
        """Test listing available models."""
        models = model_manager.list_models()
        assert isinstance(models, list)
        # If Ollama is running but no models are installed, this might be empty
        print(f"\nAvailable models: {models}")

    def test_model_availability(self, model_manager):
        """Test checking if a model is available."""
        models = model_manager.list_models()
        if models:
            # Test with the first available model
            first_model = models[0]
            assert model_manager.is_model_available(first_model) is True

        # Test with a non-existent model
        assert model_manager.is_model_available('definitely-not-a-real-model-12345') is False

    @pytest.mark.slow
    def test_pull_small_model(self, model_manager):
        """
        Test pulling a small model (if not already available).

        This test is marked as slow since downloading models takes time.
        Skip with: pytest -m "not slow"
        """
        model_name = "tinyllama:latest"  # Small model for testing

        if not model_manager.is_model_available(model_name):
            print(f"\nPulling {model_name} for testing...")
            result = model_manager.pull_model(model_name, show_progress=True)
            assert result is True

        # Verify model is now available
        assert model_manager.is_model_available(model_name) is True

    def test_ensure_model_ready(self, model_manager):
        """Test ensure_model_ready with an available model."""
        models = model_manager.list_models()
        if not models:
            pytest.skip("No models available for testing")

        model_name = models[0]
        # Should not raise an exception
        model_manager.ensure_model_ready(model_name)

    @pytest.mark.slow
    def test_generate_simple(self, model_manager):
        """
        Test simple text generation.

        This test requires a model to be available.
        """
        models = model_manager.list_models()
        if not models:
            pytest.skip("No models available for generation testing")

        model_name = models[0]
        print(f"\nTesting generation with {model_name}")

        response = model_manager.generate(
            model_name=model_name,
            prompt="Say hello in one word.",
            max_tokens=10,
            temperature=0.7
        )

        assert isinstance(response, str)
        assert len(response) > 0
        print(f"Response: {response}")

    @pytest.mark.slow
    def test_generate_with_system_prompt(self, model_manager):
        """Test generation with a system prompt."""
        models = model_manager.list_models()
        if not models:
            pytest.skip("No models available")

        model_name = models[0]
        system_prompt = model_manager.get_system_prompt('en', 'general')

        response = model_manager.generate(
            model_name=model_name,
            prompt="What is 2+2?",
            system_prompt=system_prompt,
            max_tokens=50
        )

        assert isinstance(response, str)
        assert len(response) > 0
        print(f"\nResponse with system prompt: {response}")

    @pytest.mark.slow
    def test_generate_japanese(self, model_manager):
        """Test generation with Japanese prompt and system message."""
        models = model_manager.list_models()
        if not models:
            pytest.skip("No models available")

        model_name = models[0]
        system_prompt = model_manager.get_system_prompt('ja', 'general')

        response = model_manager.generate(
            model_name=model_name,
            prompt="こんにちは。お元気ですか？",
            system_prompt=system_prompt,
            max_tokens=100,
            temperature=0.7
        )

        assert isinstance(response, str)
        assert len(response) > 0
        print(f"\n日本語応答: {response}")

    @pytest.mark.slow
    def test_streaming_generation(self, model_manager):
        """Test streaming text generation."""
        models = model_manager.list_models()
        if not models:
            pytest.skip("No models available")

        model_name = models[0]
        print(f"\nStreaming from {model_name}:")

        chunks = []
        for chunk in model_manager.generate_streaming(
            model_name=model_name,
            prompt="Count from 1 to 5.",
            temperature=0.7
        ):
            chunks.append(chunk)
            print(chunk, end='', flush=True)

        print()  # New line after streaming

        assert len(chunks) > 0
        full_response = ''.join(chunks)
        assert len(full_response) > 0

    @pytest.mark.slow
    def test_chat_completion(self, model_manager):
        """Test chat completion with message history."""
        models = model_manager.list_models()
        if not models:
            pytest.skip("No models available")

        model_name = models[0]

        messages = [
            {"role": "user", "content": "Hello! What is your name?"},
            {"role": "assistant", "content": "I am a helpful AI assistant."},
            {"role": "user", "content": "What can you help me with?"}
        ]

        response = model_manager.chat(
            model_name=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )

        assert isinstance(response, str)
        assert len(response) > 0
        print(f"\nChat response: {response}")

    def test_get_model_info(self, model_manager):
        """Test retrieving model information."""
        models = model_manager.list_models()
        if not models:
            pytest.skip("No models available")

        model_name = models[0]
        info = model_manager.get_model_info(model_name)

        assert isinstance(info, dict)
        print(f"\nModel info for {model_name}:")
        for key, value in info.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"  {key}: {value[:100]}...")
            else:
                print(f"  {key}: {value}")

    def test_switch_model(self, model_manager):
        """Test switching between models."""
        models = model_manager.list_models()
        if len(models) < 2:
            pytest.skip("Need at least 2 models for switching test")

        original_model = model_manager.default_model
        new_model = models[1] if models[0] == original_model else models[0]

        model_manager.switch_model(new_model)
        assert model_manager.default_model == new_model

        # Switch back
        model_manager.switch_model(original_model)
        assert model_manager.default_model == original_model

    def test_temperature_variations(self, model_manager):
        """Test generation with different temperature settings."""
        models = model_manager.list_models()
        if not models:
            pytest.skip("No models available")

        model_name = models[0]
        prompt = "Say hello."

        temperatures = [0.0, 0.5, 1.0]
        for temp in temperatures:
            response = model_manager.generate(
                model_name=model_name,
                prompt=prompt,
                temperature=temp,
                max_tokens=20
            )
            assert isinstance(response, str)
            print(f"\nTemp {temp}: {response}")


class TestSystemPromptsIntegration:
    """Integration tests for system prompts."""

    @pytest.fixture
    def model_manager(self):
        """Create ModelManager instance."""
        try:
            return ModelManager(base_url="http://localhost:11434")
        except Exception as e:
            pytest.skip(f"Ollama not available: {e}")

    def test_all_language_task_combinations(self, model_manager):
        """Test all combinations of languages and task types."""
        languages = ['ja', 'en']
        task_types = ['research', 'summarize', 'verify', 'general']

        for lang in languages:
            for task in task_types:
                prompt = model_manager.get_system_prompt(lang, task)
                assert isinstance(prompt, str)
                assert len(prompt) > 0
                print(f"{lang}/{task}: {prompt[:50]}...")


@pytest.mark.benchmark
class TestPerformance:
    """Performance benchmarks for ModelManager."""

    @pytest.fixture
    def model_manager(self):
        """Create ModelManager instance."""
        try:
            manager = ModelManager()
            models = manager.list_models()
            if not models:
                pytest.skip("No models available")
            return manager
        except Exception as e:
            pytest.skip(f"Ollama not available: {e}")

    def test_generation_performance(self, model_manager, benchmark):
        """Benchmark basic generation performance."""
        models = model_manager.list_models()
        model_name = models[0]

        def generate():
            return model_manager.generate(
                model_name=model_name,
                prompt="Hello",
                max_tokens=10
            )

        if 'benchmark' in dir():
            result = benchmark(generate)
        else:
            # If pytest-benchmark is not installed, just run once
            result = generate()

        assert isinstance(result, str)


# Cleanup function
def test_cleanup():
    """Cleanup test to ensure resources are freed."""
    # This is a placeholder for any cleanup needed
    pass
