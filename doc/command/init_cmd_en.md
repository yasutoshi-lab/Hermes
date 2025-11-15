# `hermes init` Command

The `hermes init` command is used to initialize the workspace for the Hermes application.

## Functionality

This command creates the necessary directory structure and configuration files for Hermes to operate in `~/.hermes` (or a specified working directory).

Specifically, it performs the following actions:

-   Creates subdirectories for storing cache, tasks, logs, history, etc.
-   Generates a `config.yaml` file with default settings.
-   Places a `docker-compose.yaml` file to launch external services like SearxNG and Redis.

## Options

| Option | Description | Default Value |
| :--- | :--- | :--- |
| `--work-dir PATH` | Specifies the path to the directory to be used as the workspace. | `~/.hermes` |
| `--clear` | If this flag is specified, any existing workspace and settings will be deleted, and re-initialization will be performed in a completely new state. | N/A |

## Implementation Details

-   **CLI Framework**: `click`
-   **Main Logic**:
    1.  If the specified work directory exists and the `--clear` flag is not provided, it determines that it is already initialized and aborts the process.
    2.  If the `--clear` flag is specified, it deletes the existing workspace directory.
    3.  It uses `hermes_cli.persistence.file_paths.FilePaths` to create all necessary subdirectories (`cache`, `task`, `log`, `debug_log`, `history`, `searxng`).
    4.  It generates a default configuration object using `hermes_cli.models.config.HermesConfig` and saves it as `config.yaml` via `hermes_cli.persistence.config_repository.ConfigRepository`.
    5.  It copies `docker-compose.yaml` from the `.hermes_template` directory to the workspace.
    6.  After initialization is complete, it guides the user on the next steps (such as how to start the Docker containers).
