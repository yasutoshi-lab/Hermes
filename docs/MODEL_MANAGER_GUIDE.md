# ModelManager Usage Guide

This guide explains how to use the `ModelManager` class for interacting with Ollama models in the Hermes research agent system.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Initialization](#initialization)
- [Model Management](#model-management)
- [Text Generation](#text-generation)
- [Chat Completion](#chat-completion)
- [Streaming Responses](#streaming-responses)
- [System Prompts](#system-prompts)
- [Error Handling](#error-handling)
- [Advanced Usage](#advanced-usage)
- [Configuration](#configuration)

## Overview

The `ModelManager` class provides a high-level interface for working with Ollama models. It handles:

- Model availability checking and downloading
- Text generation with retry logic
- Chat completion with message history
- Streaming responses
- Multi-language system prompts (Japanese/English)
- Robust error handling

## Installation

Ensure you have Ollama installed and running:

```bash
# Install Ollama (visit https://ollama.ai for instructions)

# Pull the default model
ollama pull gpt-oss:20b

# Install Python dependencies
pip install ollama
```

## Quick Start

```python
from src.modules.model_manager import ModelManager

# Initialize manager
manager = ModelManager()

# Generate text
response = manager.generate(
    model_name="gpt-oss:20b",
    prompt="Explain quantum computing in simple terms."
)

print(response)
```

## Initialization

### Basic Initialization

```python
from src.modules.model_manager import ModelManager

# Use default settings from config
manager = ModelManager()
```

### Custom Configuration

```python
# Custom Ollama endpoint and model
manager = ModelManager(
    base_url="http://localhost:11434",
    default_model="llama2:7b",
    timeout=600,
    max_retries=5
)
```

### Configuration Options

- `base_url`: Ollama API endpoint (default: `http://localhost:11434`)
- `default_model`: Default model name (default: `gpt-oss:20b`)
- `timeout`: Request timeout in seconds (default: 300)
- `max_retries`: Maximum retry attempts (default: 3)

## Model Management

### List Available Models

```python
# Get all locally available models
models = manager.list_models()
print(f"Available models: {models}")
```

### Check Model Availability

```python
# Check if a specific model is available
is_available = manager.is_model_available("gpt-oss:20b")
if is_available:
    print("Model is ready to use!")
```

### Pull a Model

```python
# Download a model if not available
try:
    manager.pull_model("llama2:7b", show_progress=True)
    print("Model downloaded successfully!")
except Exception as e:
    print(f"Failed to download model: {e}")
```

### Ensure Model is Ready

```python
# Automatically pull model if not available
manager.ensure_model_ready("gpt-oss:20b")
# Model is now guaranteed to be available
```

### Get Model Information

```python
# Get detailed model information
info = manager.get_model_info("gpt-oss:20b")
print(f"Model info: {info}")
```

### Switch Default Model

```python
# Change the default model
manager.switch_model("llama2:7b")
print(f"Now using: {manager.default_model}")
```

## Text Generation

### Basic Generation

```python
response = manager.generate(
    model_name="gpt-oss:20b",
    prompt="What is machine learning?"
)
print(response)
```

### Generation with System Prompt

```python
system_prompt = "You are a helpful research assistant specialized in computer science."

response = manager.generate(
    model_name="gpt-oss:20b",
    prompt="Explain neural networks.",
    system_prompt=system_prompt
)
print(response)
```

### Generation with Parameters

```python
response = manager.generate(
    model_name="gpt-oss:20b",
    prompt="Write a short poem about AI.",
    system_prompt="You are a creative poet.",
    temperature=0.9,      # Higher = more creative
    max_tokens=200,       # Limit response length
    top_p=0.95           # Nucleus sampling
)
print(response)
```

### Deterministic Generation

```python
# Use temperature=0 for deterministic outputs
response = manager.generate(
    model_name="gpt-oss:20b",
    prompt="What is 2 + 2?",
    temperature=0.0,
    max_tokens=10
)
print(response)  # Will always be the same
```

## Chat Completion

### Simple Chat

```python
messages = [
    {"role": "user", "content": "Hello! Can you help me?"},
    {"role": "assistant", "content": "Of course! What do you need help with?"},
    {"role": "user", "content": "Explain Python decorators."}
]

response = manager.chat(
    model_name="gpt-oss:20b",
    messages=messages,
    temperature=0.7
)
print(response)
```

### Multi-turn Conversation

```python
conversation = []

def chat(user_message):
    # Add user message
    conversation.append({"role": "user", "content": user_message})

    # Get response
    response = manager.chat(
        model_name="gpt-oss:20b",
        messages=conversation,
        temperature=0.7
    )

    # Add assistant response to history
    conversation.append({"role": "assistant", "content": response})

    return response

# Use it
print(chat("Hi, what's your name?"))
print(chat("What can you help me with?"))
print(chat("Tell me about Python."))
```

## Streaming Responses

### Basic Streaming

```python
print("Streaming response: ", end='', flush=True)

for chunk in manager.generate_streaming(
    model_name="gpt-oss:20b",
    prompt="Write a short story about a robot."
):
    print(chunk, end='', flush=True)

print()  # New line
```

### Streaming with Processing

```python
full_response = []

for chunk in manager.generate_streaming(
    model_name="gpt-oss:20b",
    prompt="List 10 programming languages.",
    temperature=0.7
):
    full_response.append(chunk)
    print(chunk, end='', flush=True)

# Get complete response
complete_text = ''.join(full_response)
print(f"\n\nComplete response ({len(complete_text)} chars)")
```

## System Prompts

### Using Built-in System Prompts

The ModelManager includes pre-configured system prompts for different tasks and languages.

#### English Prompts

```python
# Research task
research_prompt = manager.get_system_prompt('en', 'research')
response = manager.generate(
    model_name="gpt-oss:20b",
    prompt="Summarize recent AI developments.",
    system_prompt=research_prompt
)

# Summarization task
summary_prompt = manager.get_system_prompt('en', 'summarize')
response = manager.generate(
    model_name="gpt-oss:20b",
    prompt="[Long text to summarize]",
    system_prompt=summary_prompt
)

# Verification task
verify_prompt = manager.get_system_prompt('en', 'verify')
response = manager.generate(
    model_name="gpt-oss:20b",
    prompt="Verify: The Earth is flat.",
    system_prompt=verify_prompt
)
```

#### Japanese Prompts

```python
# 研究タスク
research_prompt = manager.get_system_prompt('ja', 'research')
response = manager.generate(
    model_name="gpt-oss:20b",
    prompt="機械学習について説明してください。",
    system_prompt=research_prompt
)

# 要約タスク
summary_prompt = manager.get_system_prompt('ja', 'summarize')
response = manager.generate(
    model_name="gpt-oss:20b",
    prompt="[要約するテキスト]",
    system_prompt=summary_prompt
)
```

### Available Task Types

- `research`: Research and analysis tasks
- `summarize`: Summarization tasks
- `verify`: Fact-checking and verification tasks
- `general`: General purpose tasks

## Error Handling

### Handling Connection Errors

```python
from src.modules.model_manager import (
    ModelManager,
    OllamaConnectionError,
    ModelNotFoundError
)

try:
    manager = ModelManager(base_url="http://localhost:11434")
except OllamaConnectionError as e:
    print(f"Cannot connect to Ollama: {e}")
    print("Make sure Ollama is running!")
```

### Handling Model Errors

```python
try:
    response = manager.generate(
        model_name="nonexistent-model",
        prompt="Test"
    )
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
    print("Available models:", manager.list_models())
except OllamaConnectionError as e:
    print(f"Generation failed: {e}")
```

### Automatic Retry Logic

The ModelManager automatically retries failed requests:

```python
# This will retry up to max_retries times with exponential backoff
response = manager.generate(
    model_name="gpt-oss:20b",
    prompt="What is AI?"
)
# If all retries fail, raises OllamaConnectionError
```

## Advanced Usage

### Custom Generation Options

```python
# Use additional Ollama options
response = manager.generate(
    model_name="gpt-oss:20b",
    prompt="Generate code...",
    temperature=0.5,
    max_tokens=1000,
    top_p=0.9,
    # Additional kwargs are passed to Ollama
    stop=["```"],           # Stop at code block end
    repeat_penalty=1.1,     # Reduce repetition
    seed=42                 # For reproducibility
)
```

### Batch Processing

```python
prompts = [
    "Explain photosynthesis.",
    "What is quantum mechanics?",
    "Describe machine learning."
]

responses = []
for prompt in prompts:
    response = manager.generate(
        model_name="gpt-oss:20b",
        prompt=prompt,
        max_tokens=100
    )
    responses.append(response)

# Process responses
for prompt, response in zip(prompts, responses):
    print(f"Q: {prompt}")
    print(f"A: {response}\n")
```

### Comparing Different Temperatures

```python
prompt = "Write a creative story opening."
temperatures = [0.3, 0.7, 1.0]

for temp in temperatures:
    response = manager.generate(
        model_name="gpt-oss:20b",
        prompt=prompt,
        temperature=temp,
        max_tokens=100
    )
    print(f"\nTemperature {temp}:")
    print(response)
```

## Configuration

### Using Environment Variables

Set environment variables to configure defaults:

```bash
export HERMES_DEFAULT_MODEL="llama2:7b"
export HERMES_OLLAMA_API_ENDPOINT="http://localhost:11434"
export HERMES_MAX_RETRIES="5"
export HERMES_TIMEOUT_SECONDS="600"
```

Then use ModelManager with defaults:

```python
from src.modules.model_manager import ModelManager

# Will use environment variables
manager = ModelManager()
```

### Runtime Configuration

```python
# Initialize with custom config
manager = ModelManager(
    base_url="http://custom-host:11434",
    default_model="custom-model",
    max_retries=10
)

# Change settings later
manager.switch_model("another-model")
```

## Best Practices

### 1. Model Management

```python
# Always ensure model is ready before heavy usage
manager.ensure_model_ready("gpt-oss:20b")

# List models at startup to inform user
available = manager.list_models()
print(f"Available models: {', '.join(available)}")
```

### 2. Resource Management

```python
# Use appropriate max_tokens to avoid unnecessary computation
response = manager.generate(
    model_name="gpt-oss:20b",
    prompt="Quick question",
    max_tokens=50  # Don't generate more than needed
)
```

### 3. Error Handling

```python
# Always handle potential errors
try:
    response = manager.generate(...)
except ModelNotFoundError:
    # Handle missing model
    manager.pull_model("gpt-oss:20b")
    response = manager.generate(...)
except OllamaConnectionError as e:
    # Handle connection issues
    logging.error(f"Ollama error: {e}")
    response = "Error: Cannot connect to LLM"
```

### 4. Performance Optimization

```python
# For deterministic results, use temperature=0
# For creative tasks, use higher temperature (0.7-1.0)
# For factual tasks, use lower temperature (0.3-0.5)

# Use streaming for long responses to improve UX
for chunk in manager.generate_streaming(...):
    display_to_user(chunk)
```

## Troubleshooting

### Ollama Not Running

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start Ollama
# (Method depends on your OS)
```

### Model Not Found

```python
# List available models
print(manager.list_models())

# Pull missing model
manager.pull_model("gpt-oss:20b")
```

### Slow Performance

- Use smaller models for faster responses
- Reduce `max_tokens` to limit generation length
- Use appropriate temperature settings
- Consider using streaming for better UX

### Connection Timeout

```python
# Increase timeout for large models
manager = ModelManager(timeout=1200)  # 20 minutes
```

## Examples Directory

See the `examples/` directory for more usage examples:

- `basic_generation.py` - Simple text generation
- `chat_bot.py` - Interactive chat bot
- `streaming_demo.py` - Streaming responses
- `model_comparison.py` - Compare different models
- `research_assistant.py` - Research assistant example

## API Reference

For complete API documentation, see the docstrings in `src/modules/model_manager.py` or generate documentation with:

```bash
python -m pydoc src.modules.model_manager
```
