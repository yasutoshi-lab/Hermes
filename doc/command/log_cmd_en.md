# `hermes log` Command

The `hermes log` command is used to display the operation logs of the Hermes application.

## Functionality

This command reads the log files stored in the `log` or `debug_log` directory within the workspace and outputs them to the console. It provides functionality similar to the `tail` command, such as displaying the end of logs or tracking them in real-time.

-   **Normal Log Display**: By default, it displays the normal log (`hermes.log`) where major events are recorded.
-   **Debug Log Display**: If the `--debug` flag is specified, it displays the debug log (`hermes_debug.log`), which contains more detailed information.
-   **Real-time Tracking**: Using the `--follow` flag, it monitors the log file and continues to display new logs in real-time as they are written (exit with Ctrl+C).
-   **Task ID Filtering**: By specifying `--task-id`, you can filter and display only the logs related to a specific task.

## Options

| Option | Short Form | Description | Default Value |
| :--- | :--- | :--- | :--- |
| `--lines` | `-n` | Specifies the number of lines to display from the end of the log. | 50 |
| `--follow` | `-f` | Monitors the log file and displays new logs in real-time. | N/A |
| `--task-id TEXT` | Filters and displays only the logs related to the specified task ID. | N/A |
| `--debug` | | Displays the detailed debug log instead of the normal log. | N/A |
| `--work-dir PATH` | | Specifies the path to the working directory. | `~/.hermes` |

## Implementation Details

-   **CLI Framework**: `click`
-   **Service**: `hermes_cli.services.log_service.LogService`
-   **Main Logic**:
    1.  Initializes the `LogService`.
    2.  Calls the `log_service.read_logs()` method. This method is a generator that returns each line of the log sequentially.
    3.  Inside the `read_logs` method, it performs the following actions based on the options:
        -   Determines which log file to read (normal or debug) based on the `--debug` flag.
        -   If the `--follow` flag is specified, it monitors the end of the file and waits for new lines to be added.
        -   If `--task-id` is specified, it checks if the log line contains the task ID and returns only matching ones.
    4.  Outputs each received log line to the console.
    5.  If a `KeyboardInterrupt` (Ctrl+C) occurs during `--follow` mode, it stops tracking.
