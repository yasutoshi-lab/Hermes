# `hermes run` Command

The `hermes run` command is the main command for executing the core functionality of Hermes, the research task.

## Functionality

This command initiates a series of workflows, from information gathering and analysis to report generation, based on a specified prompt or task ID.

-   **Prompt Execution**: Immediately executes the research content passed with the `--prompt` option.
-   **Task Execution**: Executes tasks pre-registered with `hermes task`, using `--task-id` or `--task-all`.
-   **Dynamic Configuration Override**: Temporarily overrides settings in `config.yaml` (such as the LLM model to use, number of validations, etc.) through command-line options.
-   **Progress Display**: Uses `rich.progress` to display the progress of the running task with a spinner.
-   **Report Output**: After execution, the generated report is saved in the `history` directory, and can also be copied to a path specified with the `--export` option.

## Options

### Core Options

| Option | Description |
| :--- | :--- |
| `--prompt TEXT` | Directly specifies the research content as a prompt for immediate execution. |
| `--task-id TEXT` | Specifies the ID of a task registered with `hermes task` to be executed. |
| `--task-all` | Executes all registered scheduled tasks. |
| `--export PATH` | Exports (copies) the generated report to the specified path. |

### LLM Related Options

| Option | Description |
| :--- | :--- |
| `--api TEXT` | Overrides the Ollama API endpoint. |
| `--model TEXT` | Overrides the name of the LLM model to be used. |
| `--retry INT` | Overrides the number of retries when an API call to the LLM fails. |

### Validation/Search Options

| Option | Description |
| :--- | :--- |
| `--min-validation INT` | Specifies the minimum number of validation loops to ensure report quality. |
| `--max-validation INT` | Specifies the maximum number of validation loops. |
| `--min-search INT` | Specifies the minimum number of information sources to collect. |
| `--max-search INT` | Specifies the maximum number of information sources to collect. |
| `--query INT` | Specifies the number of search queries to generate. |

### Others

| Option | Description |
| :--- | :--- |
| `--language [ja\|en]` | Specifies the output language of the report. |
| `--work-dir PATH` | Specifies the path to the working directory. The default is `~/.hermes`. |

## Implementation Details

-   **CLI Framework**: `click`
-   **Services**:
    -   `hermes_cli.services.config_service.ConfigService`: Responsible for loading configurations and merging CLI options.
    -   `hermes_cli.services.run_service.RunService`: The core service that manages the execution of the research workflow.
-   **Main Logic**:
    1.  Loads basic settings from `config.yaml` using `ConfigService`.
    2.  Calls `ConfigService.merge_with_cli_args` to override settings with options passed via the command line.
    3.  Sets up logging with `hermes_cli.utils.logging.setup_logging`.
    4.  Initializes `RunService` and executes `run_service.execute()` asynchronously.
    5.  Within the `execute` method, the execution mode is determined based on one of `prompt`, `task_id`, or `task_all`.
    6.  Calls the agent workflow defined in `LangGraph` (`hermes_cli.agents.graph`) to start the research task.
    7.  When processing is complete, it displays the results (such as the path to the report) and, if necessary, copies the file to the `--export` destination.
    8.  If an exception occurs, it displays an error message and aborts the process.
