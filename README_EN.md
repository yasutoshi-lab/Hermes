# Hermes

> Advanced Information Gathering Agent based on Local LLM

**Hermes** is a locally executable CLI information gathering agent for researchers and engineers. It automates everything from web searches and content analysis to report generation, creating high-quality research reports.

[日本語ドキュメント](README.md)

## Overview

Hermes is a next-generation research agent that utilizes a local LLM (Large Language Model). It performs comprehensive web searches and advanced analysis while protecting privacy, automatically generating high-quality reports with citations.

Main Use Cases:
- Automatic generation of technical research reports
- Market analysis and competitive analysis
- Information gathering for academic research
- Trend analysis
- Integration of information from multiple sources

## Features

- 🔒 **Complete Local Execution**: No external API billing, complete privacy protection
- 🔍 **Intelligent Search**: Integrates multiple search engines via SearxNG
- 🤖 **Automatic Validation Loop**: Automatically detects and corrects information contradictions and deficiencies
- 📝 **High-Quality Reports**: Automatically generates reports in Markdown format with citations
- 🎯 **CLI-Focused**: Easy integration with shell scripts and automation
- 📊 **Traceability**: Optional execution trace recording with Langfuse
- **Multi-Stage Workflow**: Flexible agent flow with LangGraph
- **Parallel Search Processing**: Fast information gathering with parallel execution of multiple queries
- **Intelligent Caching**: Caching of search results with Redis
- **Quality Assurance**: High-precision output through multiple validation loops
- **Extensibility**: Easy to add new features due to modular design

## Architecture

```
┌─────────────────┐
│   User Input    │
│   (Prompt)      │
└────────┬────────┘
         │
         v
┌─────────────────────────────────────────┐
│         Prompt Normalizer               │
│  (Prompt normalization/preprocessing)   │
└────────┬────────────────────────────────┘
         │
         v
┌─────────────────────────────────────────┐
│       Query Generator                   │
│  (Search query generation by LLM)       │
└────────┬────────────────────────────────┘
         │
         v
┌─────────────────────────────────────────┐
│       Web Researcher                    │
│  (Parallel web search by SearxNG)       │
└────────┬────────────────────────────────┘
         │
         v
┌─────────────────────────────────────────┐
│    Container Processor                  │
│  (Content analysis/summary by LLM)      │
└────────┬────────────────────────────────┘
         │
         v
┌─────────────────────────────────────────┐
│      Draft Aggregator                   │
│  (Draft report creation)                │
└────────┬────────────────────────────────┘
         │
         v
┌─────────────────────────────────────────┐
│         Validator                       │
│  (Report validation/improvement proposal)│
└────────┬────────────────────────────────┘
         │
         v
    ┌───┴───┐
    │ OK?   │
    └───┬───┘
  NO │       │ YES
     │       │
     v       v
┌─────────┐ ┌─────────────────┐
│ Query   │ │ Final Reporter  │
│Generator│ │ (Final Report)  │
└─────────┘ └─────────────────┘
```

## Prerequisites

- **OS**: Ubuntu 22.04 or later
- **Python**: 3.10 or later
- **Docker**: docker and docker-compose
- **GPU**: 16GB VRAM recommended (for Ollama)

## Installation

For detailed instructions, please refer to `doc/setup`.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yasutoshi-lab/Hermes.git
    cd Hermes
    ```
2.  **Install dependencies**:
    ```bash
    uv sync
    uv pip install -e .
    ```
3.  **Set up Ollama and Hermes**:
    Please follow the guide in `doc/setup` to install Ollama and perform the initial setup for Hermes.

## Basic Usage Examples

For details on commands, please refer to `doc/command`.

```bash
# Immediate execution
hermes run --prompt "Investigate the impact of quantum computers on encryption"

# Register a task
hermes task --add "Latest trends in AI ethics"

# Display task list
hermes task --list

# Execute a task
hermes run --task-id 2025-0001
```

## Directory Structure

```
~/.hermes/
├── config.yaml              # Configuration file
├── docker-compose.yaml      # Docker settings
├── cache/                   # Cache
├── task/                    # Task definitions
├── log/                     # Normal logs
├── debug_log/               # Debug logs
├── history/                 # Execution history and reports
└── searxng/                 # SearxNG settings
```

## Configuration

For details on the configuration file, please refer to `doc/config/config.md`.

## License

MIT License

## Contributing

We welcome Issues and Pull Requests!
Please see `CONTRIBUTING.md` for details.
