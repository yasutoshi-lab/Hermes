# Hermes - Local Research Analyst Agent

Hermes is a local research analyst agent system that helps developers and researchers efficiently collect, analyze, and summarize academic papers and technical documentation. Built with LangGraph and Ollama, all processing runs locally to protect your privacy.

## Features

- **Fully Local Processing**: All LLM operations run locally via Ollama (except web search)
- **Intelligent Workflow**: LangGraph-based stateful workflow orchestration
- **Web Search Integration**: Automated information gathering via web-search-mcp
- **Isolated Execution**: Safe processing environment using container-use
- **Verification Loop**: Automated fact-checking and validation of results
- **Multi-language Support**: Japanese and English interface
- **Session History**: All searches and reports saved locally in Markdown/PDF format

## Architecture

Hermes uses a node-based workflow architecture powered by LangGraph:

```
User Input
    ↓
InputNode → SearchNode → ProcessingNode → LLMNode
                ↓            ↓             ↓
           VerificationNode (loop back if needed)
                ↓
           ReportNode → Final Output
```

Each node is a specialized component:
- **InputNode**: Accepts user queries and configuration
- **SearchNode**: Retrieves information via web-search-mcp
- **ProcessingNode**: Processes and cleans data in isolated containers
- **LLMNode**: Analyzes content using Ollama (gpt-oss:20b)
- **VerificationNode**: Validates results and triggers re-search if needed
- **ReportNode**: Generates final Markdown/PDF reports

For node-specific behavior, refer to [docs/input_node.md](docs/input_node.md) (entry + detection stage) and [docs/verification_flow.md](docs/verification_flow.md) (verification loop and routing thresholds).

## Technology Stack

### Core Components
- **LangGraph**: Stateful workflow orchestration with durable execution
- **Ollama**: Local LLM inference (gpt-oss:20b default)
- **web-search-mcp**: Web search and content extraction
- **container-use**: Isolated execution environments

### Python Dependencies
- `langgraph` - Workflow orchestration
- `langchain` + `langchain-community` - LLM framework
- `ollama` - Ollama Python client
- `mcp` - Model Context Protocol client
- `pydantic` - Data validation
- `markdown` + `reportlab` - Report generation

## Prerequisites

Before installing Hermes, ensure you have:

- **Python 3.11+**
- **Ollama** (installed locally)
- **Docker** (for container-use)
- **Git**

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Hermes
```

### 2. Install Ollama and Download Model

```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai/

# Download the default model
ollama pull gpt-oss:20b
```

### 3. Install Python Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

### 4. Configure MCP Servers

Set up the required MCP servers:

```bash
# web-search-mcp
npx -y web-search-mcp

# container-use (follow setup instructions)
# Visit: https://github.com/anthropics/anthropic-tools
```

### 5. Configure Environment (Optional)

Create a `.env` file in the project root:

```bash
HERMES_DEFAULT_MODEL=gpt-oss:20b
HERMES_DEFAULT_LANGUAGE=ja
HERMES_OLLAMA_API_ENDPOINT=http://localhost:11434
HERMES_WEB_SEARCH_MCP_ENDPOINT=http://localhost:3000
HERMES_CONTAINER_USE_MCP_ENDPOINT=http://localhost:3001
```

## Quick Start

### Basic Usage

```bash
# One-off query
hermes query "Summarize recent LangGraph progress" --language en

# Interactive loop
hermes interactive
```

See [CLI Usage](docs/cli_usage.md) for the full command reference (history management, model commands, streaming mode, etc.).

### Example Queries

```python
from src.orchestrator.workflow import create_workflow
from src.state.agent_state import AgentState

# Initialize workflow
workflow = create_workflow()

# Run a research query
initial_state = {
    "query": "Summarize recent advances in LangGraph",
    "language": "en",
    "model_name": "gpt-oss:20b"
}

result = workflow.invoke(initial_state)
print(result["final_report"])
```

## Project Structure

```
Hermes/
├── src/
│   ├── nodes/              # LangGraph workflow nodes
│   │   ├── input_node.py
│   │   ├── search_node.py
│   │   ├── processing_node.py
│   │   ├── llm_node.py
│   │   ├── verification_node.py
│   │   └── report_node.py
│   ├── state/              # State definitions
│   │   └── agent_state.py
│   ├── orchestrator/       # Workflow orchestration
│   │   └── workflow.py
│   ├── modules/            # Utility modules
│   │   ├── history_manager.py
│   │   ├── model_manager.py
│   │   └── language_detector.py
│   ├── cli/                # Command-line interface
│   │   └── main.py
│   └── config/             # Configuration
│       └── settings.py
├── tests/                  # Test suite
├── sessions/               # Session history storage
├── requirements.txt
├── setup.py
└── README.md
```

## Documentation

- `docs/LANGGRAPH_IMPLEMENTATION.md` explains each LangGraph node, shared state, and helper modules.
- `docs/verification_flow.md` shows how provisional answers, verification loops, and report artifacts interact so you can trace outputs end-to-end.

## Configuration

All configuration is managed through `src/config/settings.py`. Key settings include:

- `default_model`: Ollama model to use (default: `gpt-oss:20b`)
- `default_language`: UI language (`ja` or `en`)
- `session_storage_path`: Where to save session history
- `ollama_api_endpoint`: Ollama server URL
- `web_search_mcp_endpoint`: Web search MCP server URL
- `container_use_mcp_endpoint`: Container use MCP server URL

Settings can be overridden via environment variables with the `HERMES_` prefix.

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_nodes/test_search_node.py
```

### Project Development Status

- [x] Project structure and dependencies setup
- [ ] State management implementation
- [ ] Node implementations
- [ ] LangGraph workflow orchestration
- [ ] MCP server integrations
- [ ] CLI interface
- [ ] Session history management
- [ ] Report generation
- [ ] Comprehensive testing

## Privacy & Security

Hermes is designed with privacy in mind:

- **No Cloud Dependencies**: All LLM processing runs locally via Ollama
- **Isolated Execution**: Code runs in containers for security
- **Local Storage**: All data stays on your machine
- **No Telemetry**: No usage data sent to external services

Note: Web search functionality does make external requests to search engines.

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
ollama list

# Restart Ollama service
# On macOS/Linux: restart via system services
# On Windows: restart via Task Manager
```

### MCP Server Issues

Ensure MCP servers are running:
```bash
# Check web-search-mcp
curl http://localhost:3000/health

# Check container-use
docker ps
```

## Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for guidelines.

## License

TBD

## Acknowledgments

Built with:
- [LangGraph](https://langchain-ai.github.io/langgraph/) by LangChain
- [Ollama](https://ollama.ai/) for local LLM inference
- [web-search-mcp](https://github.com/modelcontextprotocol/servers) for web search
- [container-use](https://github.com/anthropics/anthropic-tools) for isolated execution

## References

- Design Document: `基本設計書.md`
- LangGraph Documentation: https://langchain-ai.github.io/langgraph/
- Ollama Documentation: https://ollama.ai/
- Model Context Protocol: https://modelcontextprotocol.io/
