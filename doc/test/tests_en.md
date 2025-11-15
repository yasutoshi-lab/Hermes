# Testing Strategy

The Hermes project has introduced the following three levels of testing to ensure quality.

-   **Unit Tests**: `tests/unit`
-   **Integration Tests**: `tests/integration`
-   **End-to-End (E2E) Tests**: `tests/e2e`

Tests are run using `pytest`.

```bash
# Run all tests
pytest

# Measure coverage
pytest --cov=hermes_cli
```

## Unit Tests (`tests/unit`)

Unit tests verify that individual components (classes or functions) work as expected. Dependencies on external services (LLM, web search, database, etc.) are eliminated using mocks.

-   **Objective**:
    -   To verify the correctness of the logic of each function.
    -   To check the behavior of edge cases and anomalies.
    -   To enable fast execution and provide continuous feedback during development.
-   **Main Targets**:
    -   `services`: Business logic of each service class.
    -   `repositories`: Logic of the persistence layer (file I/O is mocked).
    -   `agents.nodes`: The pure logic of each node that makes up the workflow.
    -   `clients`: Basic request construction and response parsing of external API clients.

## Integration Tests (`tests/integration`)

Integration tests combine multiple components to verify that they work correctly in conjunction. Some of the external services (such as databases) that were mocked in unit tests are actually connected using test containers (Docker) or similar.

-   **Objective**:
    -   To verify the interaction between services and repositories.
    -   To check the actual interaction with the database or file system.
    -   To ensure that data passing and contracts between components are correct.
-   **Main Targets**:
    -   Integration of `TaskService` and `TaskRepository`.
    -   Integration of `HistoryService` and `HistoryRepository`.
    -   The entire agent workflow (however, external APIs such as LLM and web search are mocked).

## E2E Tests (`tests/e2e`)

E2E tests verify that the entire application works as expected from a user's perspective. They test the entire flow from the execution of a CLI command to the correct generation of a report. All external services such as Ollama and SearxNG are actually launched to run the tests.

-   **Objective**:
    -   To simulate actual usage scenarios and ensure the behavior of the entire system.
    -   To confirm that all integrations between configurations, commands, services, and external services function correctly.
    -   To detect regressions (bugs caused by unintentional changes).
-   **Main Targets**:
    -   Execution of the `hermes run` command.
    -   Integration of `hermes task` and `hermes run --task-id`.
    -   Reading of the configuration file (`config.yaml`) and overriding by CLI options.
    -   Generation and content verification of the final report.
