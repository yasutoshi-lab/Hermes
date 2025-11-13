#!/usr/bin/env python3
"""
Streaming generation example using ModelManager.

This example demonstrates how to use streaming responses for better UX.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.model_manager import ModelManager, OllamaConnectionError


def main():
    """Run streaming generation examples."""
    print("=" * 60)
    print("ModelManager: Streaming Generation Example")
    print("=" * 60)

    # Initialize
    try:
        manager = ModelManager()
        print(f"✓ Connected to Ollama")
    except OllamaConnectionError as e:
        print(f"✗ Error: {e}")
        return 1

    # Get model
    models = manager.list_models()
    if not models:
        print("No models available. Pull one first:")
        print("  ollama pull gpt-oss:20b")
        return 1

    model_name = models[0]
    print(f"✓ Using model: {model_name}\n")

    # Example 1: Basic streaming
    print("Example 1: Basic Streaming")
    print("-" * 60)
    prompt1 = "Tell me a short story about a curious robot."

    print(f"Prompt: {prompt1}\n")
    print("Streaming response:")
    print("-" * 60)

    chunks = []
    for chunk in manager.generate_streaming(
        model_name=model_name,
        prompt=prompt1,
        temperature=0.8
    ):
        chunks.append(chunk)
        print(chunk, end='', flush=True)

    print("\n" + "-" * 60)
    print(f"Total characters: {len(''.join(chunks))}")

    # Example 2: Streaming with progress indicator
    print("\n" + "=" * 60)
    print("Example 2: Streaming with Progress")
    print("-" * 60)

    prompt2 = "List 5 benefits of using local LLMs."
    print(f"Prompt: {prompt2}\n")
    print("Response:")
    print("-" * 60)

    char_count = 0
    for i, chunk in enumerate(manager.generate_streaming(
        model_name=model_name,
        prompt=prompt2,
        temperature=0.7
    )):
        print(chunk, end='', flush=True)
        char_count += len(chunk)

        # Show progress every 50 characters
        if char_count % 50 == 0:
            print(f" [{char_count}]", end='', flush=True)

    print("\n" + "-" * 60)
    print(f"Final count: {char_count} characters")

    # Example 3: Collecting and processing stream
    print("\n" + "=" * 60)
    print("Example 3: Processing Stream")
    print("-" * 60)

    prompt3 = "Count from 1 to 10 with descriptions."
    print(f"Prompt: {prompt3}\n")

    full_response = []
    word_count = 0

    print("Streaming and analyzing...\n")

    for chunk in manager.generate_streaming(
        model_name=model_name,
        prompt=prompt3,
        temperature=0.3
    ):
        full_response.append(chunk)
        print(chunk, end='', flush=True)

        # Count words
        word_count += len(chunk.split())

    complete_text = ''.join(full_response)

    print("\n" + "-" * 60)
    print(f"Statistics:")
    print(f"  Characters: {len(complete_text)}")
    print(f"  Words: {len(complete_text.split())}")
    print(f"  Lines: {len(complete_text.splitlines())}")

    print("\n" + "=" * 60)
    print("Streaming examples completed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
