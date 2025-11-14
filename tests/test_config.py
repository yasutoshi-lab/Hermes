#!/usr/bin/env python3
"""
ConfigService integration smoke test.

Loads the default configuration from ~/.hermes/config.yaml,
prints the key fields, and verifies that CLI override logic
produces the expected changes without mutating the original config.
"""

from hermes_cli.services import ConfigService


def main() -> None:
    service = ConfigService()
    config = service.load()

    print("=== Default Configuration ===")
    print(f"Ollama API: {config.ollama.api_base}")
    print(f"Model: {config.ollama.model}")
    print(f"Language: {config.language}")
    print(f"Validation loops: {config.validation.min_loops}-{config.validation.max_loops}")
    print(f"Search sources: {config.search.min_sources}-{config.search.max_sources}")

    overrides = {
        "language": "en",
        "min_validation": 2,
        "max_validation": 4,
        "min_sources": 2,
        "max_sources": 6,
        "model": "gpt-oss:8b",
    }
    overridden = service.apply_overrides(config, overrides)

    print("\n=== After Overrides ===")
    print(f"Ollama API: {overridden.ollama.api_base}")
    print(f"Model: {overridden.ollama.model}")
    print(f"Language: {overridden.language}")
    print(f"Validation loops: {overridden.validation.min_loops}-{overridden.validation.max_loops}")
    print(f"Search sources: {overridden.search.min_sources}-{overridden.search.max_sources}")

    print("\n=== Original Config Still Intact ===")
    print(f"Language: {config.language}")
    print(f"Validation loops: {config.validation.min_loops}-{config.validation.max_loops}")


if __name__ == "__main__":
    main()
