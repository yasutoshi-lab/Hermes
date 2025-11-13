# ModelManager Examples

This directory contains practical examples demonstrating how to use the ModelManager class for Ollama integration.

## Prerequisites

1. **Ollama installed and running**:
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   ```

2. **At least one model pulled**:
   ```bash
   ollama pull gpt-oss:20b
   ```

3. **Dependencies installed**:
   ```bash
   pip install -r ../requirements.txt
   ```

## Available Examples

### 1. Basic Generation (`basic_generation.py`)

Demonstrates simple text generation with different parameters.

**Features**:
- Simple question answering
- Using system prompts
- Japanese language support

**Run**:
```bash
python basic_generation.py
# or
./basic_generation.py
```

**Expected Output**:
- Three examples showing different generation scenarios
- Responses from the LLM with various prompts

---

### 2. Streaming Demo (`streaming_demo.py`)

Shows how to use streaming responses for better user experience.

**Features**:
- Real-time token streaming
- Progress indicators
- Stream processing and analysis

**Run**:
```bash
python streaming_demo.py
```

**Expected Output**:
- Tokens appearing one by one (like ChatGPT)
- Character count progress
- Final statistics

---

### 3. Chat Bot (`chat_bot.py`)

Interactive chat bot with conversation history.

**Features**:
- Multi-turn conversations
- Message history management
- English and Japanese support
- Interactive commands (/reset, /quit, /help)

**Run**:
```bash
python chat_bot.py
```

**Usage**:
```
Choose language (1=English, 2=Japanese)
Enter 1
> Hello!
Bot: Hi there! How can I help you today?
> What is AI?
Bot: AI stands for Artificial Intelligence...
> /reset
Conversation reset.
> /quit
Goodbye!
```

---

### 4. Model Comparison (`model_comparison.py`)

Compare responses from different models and parameters.

**Features**:
- Temperature comparison (creativity levels)
- Multi-model comparison (if available)
- System prompt comparison

**Run**:
```bash
python model_comparison.py
```

**Expected Output**:
- Side-by-side comparisons
- Different response styles
- Analysis of variations

---

## Quick Start

1. **Make sure Ollama is running**:
   ```bash
   ollama serve
   ```

2. **List available models**:
   ```bash
   ollama list
   ```

3. **Run any example**:
   ```bash
   cd examples
   python basic_generation.py
   ```

## Example Output

### Basic Generation Example

```
==============================================================
ModelManager: Basic Generation Example
==============================================================
✓ Connected to Ollama at http://localhost:11434
✓ Default model: gpt-oss:20b

Available models:
  - gpt-oss:20b
  - llama2:7b

Using model: gpt-oss:20b

Example 1: Simple Question
--------------------------------------------------------------
Prompt: What is artificial intelligence in one sentence?
Response: Artificial intelligence is the simulation of human intelligence
processes by machines, especially computer systems.

==============================================================
Example 2: With System Prompt
--------------------------------------------------------------
System: You are a research analyst assistant...
Prompt: Explain quantum computing.
Response: Quantum computing is a revolutionary approach to computation...
```

### Chat Bot Example

```
==============================================================
ModelManager: Interactive Chat Bot
==============================================================
Available models: gpt-oss:20b, llama2:7b

Choose language:
  1. English
  2. Japanese (日本語)
Enter choice (1 or 2): 1

Chat bot initialized with gpt-oss:20b
Language: en

==============================================================
Chat Bot Ready!
==============================================================
Commands:
  /reset  - Reset conversation
  /quit   - Exit chat bot
  /help   - Show this help
==============================================================

You: Hello!
Bot: Hi there! How can I help you today?

You: What can you do?
Bot: I can answer questions, help with research, explain concepts...

You: /quit
Goodbye!
```

## Customization

### Changing Models

Edit the example scripts to use a different model:

```python
# Instead of using the first available model
model_name = models[0]

# Specify a particular model
model_name = "llama2:7b"
```

### Adjusting Parameters

Modify generation parameters:

```python
response = manager.generate(
    model_name=model_name,
    prompt=prompt,
    temperature=0.9,      # Increase creativity
    max_tokens=500,       # Longer responses
    top_p=0.95           # Adjust diversity
)
```

### Adding New Examples

Create a new file following this template:

```python
#!/usr/bin/env python3
"""Description of your example."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.model_manager import ModelManager

def main():
    """Your example logic."""
    manager = ModelManager()
    # Your code here
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Troubleshooting

### "Cannot connect to Ollama"

**Problem**: Examples fail with connection error.

**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### "No models available"

**Problem**: No models found.

**Solution**:
```bash
# Pull a model
ollama pull gpt-oss:20b

# Or pull a smaller model for testing
ollama pull tinyllama:latest
```

### "Generation too slow"

**Problem**: Responses take too long.

**Solutions**:
- Use a smaller model (e.g., `tinyllama:latest`)
- Reduce `max_tokens` parameter
- Use streaming for better UX
- Check system resources

### Import errors

**Problem**: Module not found errors.

**Solution**:
```bash
# Make sure you're in the examples directory
cd examples

# Install dependencies
pip install -r ../requirements.txt

# Run with python -m
python -m basic_generation
```

## Performance Tips

1. **Use appropriate models**: Smaller models (7B) for simple tasks, larger (20B+) for complex reasoning
2. **Optimize token limits**: Don't request more tokens than needed
3. **Use streaming**: Better UX for long responses
4. **Cache models**: Keep frequently used models loaded in Ollama
5. **Batch processing**: Process multiple prompts efficiently

## Next Steps

After trying these examples:

1. Read the [ModelManager Guide](../docs/MODEL_MANAGER_GUIDE.md)
2. Check the [API documentation](../src/modules/model_manager.py)
3. Run the test suite: `pytest tests/test_modules/test_model_manager.py`
4. Integrate ModelManager into your own projects

## Contributing

Have a useful example? Contribute it!

1. Create a descriptive example script
2. Add documentation in this README
3. Submit a pull request

## Resources

- [Ollama Documentation](https://ollama.ai/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Hermes Project README](../README.md)
- [ModelManager Guide](../docs/MODEL_MANAGER_GUIDE.md)
