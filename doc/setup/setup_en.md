# Setup Guide

This guide explains the setup procedure for all components required to run the Hermes application.

## 1. Prerequisites

-   **OS**: Ubuntu 22.04 or later
-   **Python**: 3.10 or later
-   **Docker**: `docker` and `docker-compose`
-   **GPU**: 16GB VRAM recommended (for Ollama)
-   **Git**: Required to clone the source code
-   **uv**: Recommended for installing Python packages (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

## 2. Installing the Hermes CLI

### a. Clone the Repository

First, clone the Hermes source code from GitHub.

```bash
git clone https://github.com/yasutoshi-lab/Hermes.git
cd Hermes
```

### b. Install Dependencies

Use `uv` to install the project's dependencies and install the CLI in editable mode.

```bash
# Install dependencies
uv sync

# Install the CLI
uv pip install -e .
```

## 3. Setting up Ollama

Hermes utilizes [Ollama](https://ollama.com/) to run the LLM (Large Language Model) locally.

### a. Install Ollama

Run the official installation script.

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### b. Download the LLM Model

Download the model that Hermes uses by default. If you want to use a different model, change the model name accordingly.

```bash
ollama pull gpt-oss:20b
```

### c. Start the Ollama Service

Start (or enable) the service so that Ollama always runs in the background.

```bash
# Start the service
ollama serve
```

If you want it to start automatically on system boot, run the following command:

```bash
sudo systemctl enable ollama
```

## 4. Initializing the Hermes Workspace

Finally, set up the Hermes workspace. This includes configuration files and Docker settings for external services (SearxNG, Redis).

### a. Initialize the Workspace

Run the `hermes init` command to create the necessary files in the `~/.hermes` directory.

```bash
hermes init
```

### b. Start External Services

Navigate to the created workspace and use `docker compose` to start SearxNG (meta-search engine) and Redis (cache) in the background.

```bash
cd ~/.hermes
docker compose up -d
```

## 5. Verifying the Setup

Let's run a simple research task to verify that everything is set up correctly.

```bash
hermes run --prompt "What is the capital of Japan?"
```

If you see the message "Execution completed!" and the path to the report, the setup is successful.
