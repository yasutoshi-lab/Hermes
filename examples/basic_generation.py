#!/usr/bin/env python3
"""
Basic text generation example using ModelManager.

This example demonstrates simple text generation with Ollama.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.model_manager import ModelManager, OllamaConnectionError


def main():
    """Run basic generation examples."""
    print("=" * 60)
    print("ModelManager: Basic Generation Example")
    print("=" * 60)

    # Initialize ModelManager
    try:
        manager = ModelManager()
        print(f"✓ Connected to Ollama at {manager.base_url}")
        print(f"✓ Default model: {manager.default_model}\n")
    except OllamaConnectionError as e:
        print(f"✗ Cannot connect to Ollama: {e}")
        print("  Make sure Ollama is running: ollama serve")
        return 1

    # List available models
    print("Available models:")
    models = manager.list_models()
    if not models:
        print("  No models found. Pull a model first:")
        print("  ollama pull gpt-oss:20b")
        return 1

    for model in models:
        print(f"  - {model}")

    # Use first available model
    model_name = models[0]
    print(f"\nUsing model: {model_name}\n")

    # Example 1: Simple question
    print("Example 1: Simple Question")
    print("-" * 60)
    prompt1 = "What is artificial intelligence in one sentence?"
    print(f"Prompt: {prompt1}")
    print("Response: ", end='', flush=True)

    response1 = manager.generate(
        model_name=model_name,
        prompt=prompt1,
        max_tokens=100,
        temperature=0.7
    )
    print(response1)

    # Example 2: With system prompt
    print("\n" + "=" * 60)
    print("Example 2: With System Prompt")
    print("-" * 60)

    system_prompt = manager.get_system_prompt('en', 'research')
    prompt2 = "Explain quantum computing."

    print(f"System: {system_prompt}")
    print(f"Prompt: {prompt2}")
    print("Response: ", end='', flush=True)

    response2 = manager.generate(
        model_name=model_name,
        prompt=prompt2,
        system_prompt=system_prompt,
        max_tokens=150,
        temperature=0.5
    )
    print(response2)

    # Example 3: Japanese
    print("\n" + "=" * 60)
    print("Example 3: Japanese Language")
    print("-" * 60)

    system_prompt_ja = manager.get_system_prompt('ja', 'general')
    prompt3 = "人工知能とは何ですか？"

    print(f"システム: {system_prompt_ja}")
    print(f"プロンプト: {prompt3}")
    print("応答: ", end='', flush=True)

    response3 = manager.generate(
        model_name=model_name,
        prompt=prompt3,
        system_prompt=system_prompt_ja,
        max_tokens=150,
        temperature=0.7
    )
    print(response3)

    print("\n" + "=" * 60)
    print("Examples completed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
