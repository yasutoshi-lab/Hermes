# GEMINI.md

## Project Overview

This project, "Hermes," is a Python CLI application that acts as a research agent. It uses a local Large Language Model (LLM) to automate the process of information gathering, analysis, and report generation. The application is designed to be run locally, ensuring privacy and control over the research process.

The core of the application is a `LangGraph`-based agent that follows a multi-stage workflow:

1.  **Prompt Normalization:** The user's input prompt is pre-processed and normalized.
2.  **Query Generation:** The LLM generates search queries based on the normalized prompt.
3.  **Web Research:** The application uses SearxNG to perform parallel web searches using the generated queries.
4.  **Content Processing:** The LLM analyzes and summarizes the content of the search results.
5.  **Draft Aggregation:** A draft report is created from the processed content.
6.  **Validation:** The draft report is validated for accuracy and completeness. This is a loop that can go back to the search step if more information is needed.
7.  **Final Report:** A final report is generated in Markdown format with citations.

The application is built with a service-oriented architecture, with services for managing tasks, history, and configuration. It uses `click` for the command-line interface, `pydantic` for data validation, and `loguru` for logging.

## Building and Running

### Prerequisites

*   Python 3.10+
*   Docker
*   `uv` (Python package installer)

### Installation

1.  **Install dependencies:**
    ```bash
    uv sync
    ```

2.  **Install the CLI:**
    ```bash
    uv pip install -e .
    ```

3.  **Initialize Hermes:**
    ```bash
    hermes init
    ```

### Running the Application

The main command is `hermes run`. It can be used in several ways:

*   **Run with a prompt:**
    ```bash
    hermes run --prompt "Your research topic"
    ```

*   **Run a specific task:**
    ```bash
    hermes run --task-id <task_id>
    ```

*   **Run all scheduled tasks:**
    ```bash
    hermes run --task-all
    ```

### Testing

The project uses `pytest` for testing.

*   **Run all tests:**
    ```bash
    pytest
    ```

*   **Run tests with coverage:**
    ```bash
    pytest --cov=hermes_cli
    ```

## Development Conventions

*   **Code Formatting:** The project uses `black` for code formatting.
    ```bash
    black hermes_cli/
    ```

*   **Linting:** The project uses `ruff` for linting.
    ```bash
    ruff check hermes_cli/
    ```

*   **Type Checking:** The project uses `mypy` for type checking.
    ```bash
    mypy hermes_cli/
    ```
