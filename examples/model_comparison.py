#!/usr/bin/env python3
"""
Model comparison example using ModelManager.

This example compares responses from different models or parameters.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.model_manager import ModelManager


def compare_temperatures(manager, model_name, prompt):
    """Compare responses at different temperatures."""
    print("\n" + "=" * 60)
    print("Temperature Comparison")
    print("=" * 60)
    print(f"Model: {model_name}")
    print(f"Prompt: {prompt}")
    print("=" * 60)

    temperatures = [0.0, 0.5, 1.0]

    for temp in temperatures:
        print(f"\nTemperature: {temp}")
        print("-" * 60)

        response = manager.generate(
            model_name=model_name,
            prompt=prompt,
            temperature=temp,
            max_tokens=100
        )

        print(response)


def compare_models(manager, models, prompt):
    """Compare responses from different models."""
    if len(models) < 2:
        print("Need at least 2 models for comparison.")
        return

    print("\n" + "=" * 60)
    print("Model Comparison")
    print("=" * 60)
    print(f"Prompt: {prompt}")
    print("=" * 60)

    for model_name in models[:3]:  # Compare up to 3 models
        print(f"\n[{model_name}]")
        print("-" * 60)

        response = manager.generate(
            model_name=model_name,
            prompt=prompt,
            temperature=0.7,
            max_tokens=150
        )

        print(response)


def compare_system_prompts(manager, model_name, prompt):
    """Compare responses with different system prompts."""
    print("\n" + "=" * 60)
    print("System Prompt Comparison")
    print("=" * 60)
    print(f"Model: {model_name}")
    print(f"Prompt: {prompt}")
    print("=" * 60)

    task_types = ['general', 'research', 'summarize']

    for task_type in task_types:
        system_prompt = manager.get_system_prompt('en', task_type)

        print(f"\nTask Type: {task_type}")
        print(f"System: {system_prompt}")
        print("-" * 60)

        response = manager.generate(
            model_name=model_name,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=100
        )

        print(response)


def main():
    """Run comparison examples."""
    print("=" * 60)
    print("ModelManager: Model Comparison Examples")
    print("=" * 60)

    # Initialize
    manager = ModelManager()

    # Get models
    models = manager.list_models()
    if not models:
        print("No models available.")
        return 1

    print(f"Available models: {', '.join(models)}\n")

    model_name = models[0]

    # Example 1: Temperature comparison
    compare_temperatures(
        manager,
        model_name,
        "Write a creative opening line for a science fiction story."
    )

    # Example 2: Model comparison (if multiple models available)
    if len(models) > 1:
        compare_models(
            manager,
            models,
            "Explain the concept of machine learning in simple terms."
        )

    # Example 3: System prompt comparison
    compare_system_prompts(
        manager,
        model_name,
        "What is quantum computing?"
    )

    print("\n" + "=" * 60)
    print("Comparison complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
